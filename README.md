# ESP32-CAM People Counter System

A real-time people counting system using ESP32-CAM, YOLOv4-tiny object detection, and Flask web interface.

## System Architecture

```
ESP32-CAM (Hardware)
    ↓ (WiFi - captures video)
Python Counter Script (laptop_server/people_counter.py)
    ↓ (processes frames, detects people, counts crossings)
Flask Web Server (laptop_server/app.py)
    ↓ (serves web interface)
Web Browser (displays live feed + data)
```

## Files Overview

### ESP32 Code
- `esp32cam_stream/esp32cam_stream.ino` - Main ESP32-CAM firmware
- `esp32cam_stream/board_config.h` - Pin definitions for AI-Thinker ESP32-CAM

### Python Server
- `laptop_server/app.py` - Flask web server
- `laptop_server/people_counter.py` - Main counting logic with YOLO detection
- `laptop_server/centroid_tracker.py` - Object tracking algorithm
- `laptop_server/models/` - YOLO model files (weights, config, class names)

### Data Files
- `people_log.csv` - Historical counting data
- `count_data.json` - Current session data (auto-generated)

## Prerequisites

### Hardware
- ESP32-CAM (AI-Thinker module)
- FTDI programmer or USB-to-Serial adapter
- 5V power supply
- WiFi network

### Software
- Arduino IDE with ESP32 board support
- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

### Step 1: Install Python Dependencies

```bash
cd IOT/laptop_server
pip install -r requirements.txt
```

### Step 2: Configure ESP32-CAM

1. Open `esp32cam_stream/esp32cam_stream.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid     = "YOUR_WIFI_SSID";      // Change this
   const char* password = "YOUR_WIFI_PASSWORD";  // Change this
   ```
3. Select board: **AI Thinker ESP32-CAM**
4. Upload to ESP32-CAM
5. Open Serial Monitor (115200 baud) to get the IP address

### Step 3: Configure Python Script

1. Open `laptop_server/people_counter.py`
2. Update ESP32 IP address (line 18):
   ```python
   ESP32_CAPTURE_URL = "http://YOUR_ESP32_IP/capture"  # Change this
   ```

### Step 4: Verify YOLO Models

Check that these files exist in `laptop_server/models/`:
- ✅ `yolov4-tiny.weights` (23.1 MB)
- ✅ `yolov4-tiny.cfg`
- ✅ `coco.names`

## Testing the System

### Test 1: ESP32-CAM Stream

1. Power on ESP32-CAM
2. Wait for WiFi connection (check Serial Monitor)
3. Note the IP address shown (e.g., `192.168.1.100`)
4. Open browser and go to: `http://ESP32_IP/stream`
5. ✅ You should see live video feed

### Test 2: Python Counter Script

```bash
cd IOT/laptop_server
python people_counter.py
```

Expected output:
```
Loading YOLO model...
YOLO model loaded successfully
Connecting to http://YOUR_ESP32_IP/capture ...
```

If working correctly, you'll see:
- Frame processing logs
- `[IN]` and `[OUT]` events when people cross the line

### Test 3: Web Interface

1. Keep `people_counter.py` running
2. Open a new terminal:
   ```bash
   cd IOT/laptop_server
   python app.py
   ```
3. Open browser: `http://localhost:5000`
4. ✅ You should see:
   - Live video feed with detection boxes
   - Red vertical line (crossing boundary)
   - Today's count data
   - Historical data table

## Configuration Options

### Adjust Counting Line Position

In `people_counter.py`, line 18:
```python
LINE_X = 320  # Vertical line position (0-640)
```
- Lower value = line moves left
- Higher value = line moves right

### Adjust Detection Confidence

In `people_counter.py`, line 19:
```python
CONFIDENCE = 0.4  # Range: 0.0 to 1.0
```
- Lower = more detections (more false positives)
- Higher = fewer detections (more accurate)

### Change Counting Direction

In `people_counter.py`, lines 175-185:
- Right-to-left = IN
- Left-to-right = OUT

Swap the logic to reverse directions.

## Troubleshooting

### ESP32-CAM won't connect to WiFi
- Check SSID and password
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check power supply (needs stable 5V, 2A minimum)

### Python script can't connect to ESP32
- Verify ESP32 IP address is correct
- Ping the ESP32: `ping ESP32_IP`
- Check firewall settings
- Ensure both devices are on same network

### YOLO model not loading
- Verify all 3 model files exist in `models/` folder
- Check file sizes (weights should be ~23MB)
- Re-download if corrupted

### Web interface shows "NO SIGNAL"
- Ensure `people_counter.py` is running
- Check Flask server logs for errors
- Verify ESP32 is streaming

### Counts are inaccurate
- Adjust `LINE_X` position
- Increase `CONFIDENCE` threshold
- Adjust `max_distance` in CentroidTracker
- Ensure good lighting conditions

## Data Files

### people_log.csv Format
```csv
timestamp,event,total_in,total_out,occupancy
2024-01-15 10:30:45,IN,1,0,1
2024-01-15 10:31:12,OUT,1,1,0
```

### Web Interface Features
- **Daily/Monthly/Yearly views** - Aggregate data by time period
- **Date range filtering** - View specific date ranges
- **Search** - Find specific dates
- **Sortable columns** - Click headers to sort
- **Peak hour tracking** - Shows busiest hour of each period
- **Auto-refresh** - Updates every 10 seconds

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- Dual-core CPU
- WiFi adapter

### Recommended
- Python 3.10+
- 8GB RAM
- Quad-core CPU
- Stable WiFi connection

## Performance Notes

- Detection runs every 2nd frame for performance
- YOLO inference: ~200-500ms per frame (CPU)
- Web interface updates: 10 FPS
- Memory usage: ~500MB (with YOLO loaded)

## Future Improvements

- [ ] Add GPU acceleration for YOLO
- [ ] Implement data export (CSV, PDF reports)
- [ ] Add email/SMS alerts for thresholds
- [ ] Multi-camera support
- [ ] Real-time occupancy dashboard
- [ ] Mobile app integration

## License

Educational project - free to use and modify.

## Credits

- YOLOv4-tiny: Alexey Bochkovskiy
- ESP32-CAM: Espressif Systems
- Centroid tracking algorithm: Adrian Rosebrock (PyImageSearch)
