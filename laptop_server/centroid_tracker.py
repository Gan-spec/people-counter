from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker:
    def __init__(self, max_disappeared=40, max_distance=100):
        """
        Initialize centroid tracker
        
        Args:
            max_disappeared: Maximum frames an object can be missing before deregistration
            max_distance: Maximum pixel distance to consider a match (prevents wrong associations)
        """
        self.next_object_id = 0
        self.objects = OrderedDict()       # ID -> centroid
        self.disappeared = OrderedDict()   # ID -> frames missing
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance   # Maximum distance for valid match

    def register(self, centroid):
        """Register a new object with next available ID"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
        
        # Prevent ID overflow by resetting when no active objects
        if self.next_object_id > 100000 and len(self.objects) == 0:
            self.next_object_id = 0

    def deregister(self, object_id):
        """Remove an object from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        """
        Update tracked objects with new detections
        
        Args:
            rects: List of bounding boxes [(x, y, w, h), ...]
            
        Returns:
            OrderedDict of {object_id: centroid}
        """
        # Handle case with no detections
        if len(rects) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return self.objects

        # Calculate centroids from bounding boxes
        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for i, (x, y, w, h) in enumerate(rects):
            input_centroids[i] = (x + w // 2, y + h // 2)

        # If no existing objects, register all new detections
        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Compute distance matrix between existing and new centroids
            D = dist.cdist(np.array(object_centroids), input_centroids)
            
            # Find best matches (minimum distance)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()
            
            # Match existing objects to new detections
            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Check if distance is within threshold
                distance = D[row, col]
                if distance > self.max_distance:
                    # Too far away, likely not the same object
                    continue
                
                obj_id = object_ids[row]
                self.objects[obj_id] = input_centroids[col]
                self.disappeared[obj_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            # Handle unmatched existing objects (disappeared)
            unused_rows = set(range(D.shape[0])) - used_rows
            for row in unused_rows:
                obj_id = object_ids[row]
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)

            # Register new objects (unmatched detections)
            unused_cols = set(range(D.shape[1])) - used_cols
            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects
