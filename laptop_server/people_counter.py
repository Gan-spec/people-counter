import cv2
import numpy as np
import datetime
import csv
import os
import requests
import time
import logging
import threading
from collections import defaultdict

# ===== Setup Logging =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== Config =====
ESP32_CAPTURE_URL = "http://10.86.238.176/capture"
LOG_FILE          = "people_log.csv"
LINE_X            = 320  # vertical crossing line (left=IN, right=OUT)
CONFIDENCE        = 0.50  # Slightly lower for better detection
MAX_RETRIES       = 3    # connection retry attempts
RETRY_DELAY       = 2    # seconds between retries
MIN_DETECTION_SIZE = 2500  # Slightly larger minimum size

MODELS_DIR  = os.path.join(os.path.dirname(__file__), "models")
WEIGHTS     = os.path.join(MODELS_DIR, "yolov4-tiny.weights")
CONFIG      = os.path.join(MODELS_DIR, "yolov4-tiny.cfg")
NAMES       = os.path.join(MODELS_DIR, "coco.names")

# ===== Threading Config =====
latest_frame = None
frame_lock = threading.Lock()
running = True

# ===== Load YOLO =====
logger.info("Loading YOLO model...")
try:
    net = cv2.dnn.readNet(WEIGHTS, CONFIG)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    with open(NAMES) as f:
        classes = [line.strip() for line in f.readlines()]

    PERSON_CLASS_ID = classes.index("person")
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    exit(1)

# ===== Improved Tracker =====
class ImprovedTracker:
    def __init__(self, max_disappeared=80, max_distance=120):  # Increased for low FPS
        self.next_id = 0
        self.objects = {}  # id -> centroid
        self.disappeared = {}  # id -> frame count
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
    
    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1
        return self.next_id - 1
    
    def deregister(self, obj_id):
        del self.objects[obj_id]
        del self.disappeared[obj_id]
    
    def update(self, boxes):
        if len(boxes) == 0:
            # Mark all as disappeared
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return self.objects
        
        # Calculate centroids from boxes
        input_centroids = []
        for (x, y, w, h) in boxes:
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            input_centroids.append((cx, cy))
        
        # If no existing objects, register all
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            # Match existing objects to new centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Calculate distance matrix
            distances = np.zeros((len(object_centroids), len(input_centroids)))
            for i, obj_centroid in enumerate(object_centroids):
                for j, input_centroid in enumerate(input_centroids):
                    distances[i, j] = np.linalg.norm(
                        np.array(obj_centroid) - np.array(input_centroid)
                    )
            
            # Find best matches
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                if distances[row, col] > self.max_distance:
                    continue
                
                obj_id = object_ids[row]
                self.objects[obj_id] = input_centroids[col]
                self.disappeared[obj_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle disappeared objects
            unused_rows = set(range(len(object_centroids))) - used_rows
            for row in unused_rows:
                obj_id = object_ids[row]
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            
            # Register new objects
            unused_cols = set(range(len(input_centroids))) - used_cols
            for col in unused_cols:
                self.register(input_centroids[col])
        
        return self.objects

# ===== Tracker =====
tracker        = ImprovedTracker(max_disappeared=150, max_distance=200)  # Increased for low FPS (1-5 FPS)
prev_centroids = {}
crossed        = {}  # obj_id -> last direction crossed
zone_history   = {}  # obj_id -> list of zones they've been in
count_in       = 0
count_out      = 0
last_count_time = {}  # obj_id -> timestamp of last count (prevent double counting)

# ===== Session =====
session = requests.Session()
session.headers.update({'Connection': 'keep-alive'})

# ===== CSV Log =====
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event", "total_in", "total_out", "occupancy"])
    logger.info(f"Created new log file: {LOG_FILE}")

def log_event(event):
    """Log event to CSV and send to Flask server"""
    occupancy = max(0, count_in - count_out)  # Ensure occupancy never goes negative
    try:
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event, count_in, count_out, occupancy
            ])
    except IOError as e:
        logger.error(f"Failed to write to log file: {e}")
    
    # Send to Flask (non-blocking)
    try:
        session.post("http://127.0.0.1:5000/update", json={
            "total_in": count_in,
            "total_out": count_out,
            "occupancy": occupancy
        }, timeout=0.5)
    except Exception:
        pass  # Flask might not be running, that's ok

def frame_grabber_thread():
    """Background thread that continuously grabs latest frame from ESP32"""
    global latest_frame, running
    
    logger.info("Frame grabber thread started")
    consecutive_failures = 0
    max_consecutive_failures = 10
    
    while running:
        try:
            resp = session.get(ESP32_CAPTURE_URL, timeout=3)
            if resp.status_code == 200:
                arr = np.frombuffer(resp.content, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    # Update latest frame (thread-safe)
                    with frame_lock:
                        latest_frame = frame
                    consecutive_failures = 0
                else:
                    logger.warning("Failed to decode frame")
                    consecutive_failures += 1
            else:
                logger.warning(f"Invalid response: {resp.status_code}")
                consecutive_failures += 1
                
        except requests.exceptions.Timeout:
            logger.warning("Timeout grabbing frame")
            consecutive_failures += 1
        except requests.exceptions.ConnectionError:
            logger.warning("Connection error")
            consecutive_failures += 1
        except Exception as e:
            logger.error(f"Unexpected error in frame grabber: {e}")
            consecutive_failures += 1
        
        if consecutive_failures >= max_consecutive_failures:
            logger.error("Too many consecutive failures in frame grabber")
            running = False
            break
        
        # Small delay to prevent hammering the ESP32
        time.sleep(0.05)  # 20 FPS max grab rate
    
    logger.info("Frame grabber thread stopped")

def detect_people(frame):
    """Detect people in frame using YOLO with size filtering"""
    h, w = frame.shape[:2]
    
    # Use smaller blob size for faster processing
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (320, 320), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes, confidences = [], []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if class_id == PERSON_CLASS_ID and confidence > CONFIDENCE:
                cx = int(detection[0] * w)
                cy = int(detection[1] * h)
                bw = int(detection[2] * w)
                bh = int(detection[3] * h)
                x  = int(cx - bw / 2)
                y  = int(cy - bh / 2)
                
                # Filter out very small detections (likely false positives)
                box_area = bw * bh
                if box_area >= MIN_DETECTION_SIZE:
                    boxes.append([x, y, bw, bh])
                    confidences.append(float(confidence))

    # Non-max suppression to remove duplicate boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE, 0.4)
    result  = []
    if len(indices) > 0:
        for i in indices.flatten():
            result.append(boxes[i])
    return result

def process_frame(frame):
    """Process frame with YOLO + improved tracker + zone-based counting"""
    global count_in, count_out, prev_centroids, crossed, zone_history, last_count_time
    
    # Resize to smaller size for faster processing
    frame = cv2.resize(frame, (320, 240))
    
    # Detect people
    boxes = detect_people(frame)
    objects = tracker.update(boxes)
    
    # ID change detection: Compare current objects with previous centroids
    ID_CHANGE_THRESHOLD = 100  # pixels
    id_changes = {}  # old_id -> new_id mapping
    
    current_ids = set(objects.keys())
    previous_ids = set(prev_centroids.keys())
    
    # Find new IDs that might be reassignments of old IDs
    new_ids = current_ids - previous_ids
    disappeared_ids = previous_ids - current_ids
    
    for new_id in new_ids:
        new_centroid = objects[new_id]
        for old_id in disappeared_ids:
            if old_id in prev_centroids:
                old_centroid = prev_centroids[old_id]
                distance = np.linalg.norm(np.array(new_centroid) - np.array(old_centroid))
                
                if distance < ID_CHANGE_THRESHOLD:
                    id_changes[old_id] = new_id
                    logger.info(f"🔄 ID change detected: {old_id} → {new_id} at position {new_centroid}, distance: {distance:.1f}px")
                    break
    
    # Transfer zone history, crossed state, and cooldown time for ID changes
    for old_id, new_id in id_changes.items():
        if old_id in zone_history:
            # Transfer zone history from old ID to new ID
            if new_id not in zone_history:
                zone_history[new_id] = []
            # Prepend old history to new history
            zone_history[new_id] = zone_history[old_id] + zone_history[new_id]
            logger.info(f"  Transferred zone_history from ID {old_id}: {zone_history[old_id]} → ID {new_id}")
        
        if old_id in crossed:
            crossed[new_id] = crossed[old_id]
        
        if old_id in last_count_time:
            last_count_time[new_id] = last_count_time[old_id]
    
    # Define zones
    line_x = 160  # Center line
    left_zone = (0, line_x - 30)  # Outside zone
    right_zone = (line_x + 30, 320)  # Inside zone
    
    # Draw crossing line and zones
    cv2.line(frame, (line_x, 0), (line_x, 240), (0, 0, 255), 2)
    cv2.rectangle(frame, (left_zone[0], 0), (left_zone[1], 240), (255, 0, 0), 1)  # Blue - Outside
    cv2.rectangle(frame, (right_zone[0], 0), (right_zone[1], 240), (0, 255, 0), 1)  # Green - Inside
    
    current_time = time.time()
    
    # Process tracked objects
    for obj_id, centroid in objects.items():
        cx, cy = centroid
        cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
        cv2.putText(frame, f"ID {obj_id}", (cx - 10, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Determine current zone
        current_zone = None
        if left_zone[0] <= cx <= left_zone[1]:
            current_zone = "LEFT"
        elif right_zone[0] <= cx <= right_zone[1]:
            current_zone = "RIGHT"
        
        # Initialize zone history for new IDs
        if obj_id not in zone_history:
            zone_history[obj_id] = []
            last_count_time[obj_id] = 0
        
        # Add to zone history if in a zone
        if current_zone:
            if len(zone_history[obj_id]) == 0 or zone_history[obj_id][-1] != current_zone:
                zone_history[obj_id].append(current_zone)
        
        # Check for zone transitions (prevent counting within 2 seconds)
        if len(zone_history[obj_id]) >= 2 and (current_time - last_count_time[obj_id]) > 2:
            last_zone = zone_history[obj_id][-2]
            curr_zone = zone_history[obj_id][-1]
            
            # LEFT to RIGHT = IN (entering)
            if last_zone == "LEFT" and curr_zone == "RIGHT":
                if crossed.get(obj_id) != "IN":
                    count_in += 1
                    crossed[obj_id] = "IN"
                    last_count_time[obj_id] = current_time
                    logger.info(f"✅ [IN]  ID {obj_id} entered (zone transition) | In:{count_in} Out:{count_out} Inside:{max(0, count_in - count_out)}")
                    log_event("IN")
                    cv2.putText(frame, "ENTERED!", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # RIGHT to LEFT = OUT (exiting)
            elif last_zone == "RIGHT" and curr_zone == "LEFT":
                if crossed.get(obj_id) != "OUT":
                    current_occupancy = count_in - count_out
                    if current_occupancy > 0:
                        count_out += 1
                        crossed[obj_id] = "OUT"
                        last_count_time[obj_id] = current_time
                        logger.info(f"❌ [OUT] ID {obj_id} exited (zone transition) | In:{count_in} Out:{count_out} Inside:{max(0, count_in - count_out)}")
                        log_event("OUT")
                        cv2.putText(frame, "EXITED!", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        logger.warning(f"⚠️  ID {obj_id} tried to exit but occupancy is 0 - ignoring")
                        crossed[obj_id] = "OUT"
                        last_count_time[obj_id] = current_time

        prev_centroids[obj_id] = centroid

    # Draw bounding boxes
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
    
    # Cleanup old IDs
    current_ids = set(objects.keys())
    for obj_id in list(prev_centroids.keys()):
        if obj_id not in current_ids:
            del prev_centroids[obj_id]
    for obj_id in list(crossed.keys()):
        if obj_id not in current_ids:
            del crossed[obj_id]
    for obj_id in list(zone_history.keys()):
        if obj_id not in current_ids:
            del zone_history[obj_id]
    for obj_id in list(last_count_time.keys()):
        if obj_id not in current_ids:
            del last_count_time[obj_id]
    
    # Resize back to 640x480 for display
    frame = cv2.resize(frame, (640, 480))
    
    return frame

def main():
    global latest_frame, running
    
    logger.info(f"Connecting to {ESP32_CAPTURE_URL} ...")
    
    # Start frame grabber thread
    grabber_thread = threading.Thread(target=frame_grabber_thread, daemon=True)
    grabber_thread.start()
    
    # Wait for first frame
    logger.info("Waiting for first frame...")
    while latest_frame is None and running:
        time.sleep(0.1)
    
    if not running:
        logger.error("Frame grabber failed to start")
        return
    
    logger.info("Processing started!")
    
    frame_count = 0
    last_process_time = time.time()
    
    while running:
        # Get latest frame (thread-safe)
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.01)
                continue
            frame = latest_frame.copy()
        
        try:
            # Process frame
            processed_frame = process_frame(frame)
            frame_count += 1
            
            # Calculate FPS
            current_time = time.time()
            if current_time - last_process_time >= 5.0:
                fps = frame_count / (current_time - last_process_time)
                logger.info(f"Processing FPS: {fps:.1f}")
                frame_count = 0
                last_process_time = current_time
            
            # Send frame to Flask
            try:
                _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()
                session.post("http://127.0.0.1:5000/update_frame", data=frame_bytes, timeout=0.3)
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
        
        # Small delay
        time.sleep(0.03)  # ~30 FPS processing rate
    
    logger.info("Shutting down...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        running = False
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        running = False
