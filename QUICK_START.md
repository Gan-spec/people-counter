# Quick Start Guide

## Files Status

### ✅ Files Present
- ESP32 firmware: `esp32cam_stream/esp32cam_stream.ino`
- Board config: `esp32cam_stream/board_config.h` ✨ (just created)
- Python server: `laptop_server/app.py`
- Counter logic: `laptop_server/people_counter.py`
- Tracker: `laptop_server/centroid_tracker.py`
- YOLO models: All 3 files in `laptop_server/models/`
- Requirements: `laptop_server/requirements.txt` ✨ (just created)
- Test script: `laptop_server/test_setup.py` ✨ (just created)

### ⚠️ Configuration Needed
1. **ESP32 WiFi** - Update in `esp32cam_stream.ino`:
   - Line 7: `const char* ssid = "YOUR_WIFI_SSID";`
   - Line 8: `const char* password = "YOUR_WIFI_PASSWORD";`

2. **ESP32 IP Address** - Update in `laptop_server/people_counter.py`:
   - Line 18: `ESP32_CAPTURE_URL = "http://YOUR_ESP32_IP/capture"`

## Testing Steps

### Step 1: Run Setup Test
```bash
cd IOT/laptop_server
python test_setup.py
```

This will check:
- ✅ Python version
- ✅ All dependencies installed
- ✅ YOLO model files present
- ✅ Configuration files exist
- ⚠️ ESP32 IP configured
- ⚠️ ESP32 connection working

### Step 2: Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 3: Upload ESP32 Firmware
1. Open Arduino IDE
2. Load `esp32cam_stream/esp32cam_stream.ino`
3. Update WiFi credentials
4. Select board: **AI Thinker ESP32-CAM**
5. Upload
6. Open Serial Monitor (115200 baud)
7. Note the IP address

### Step 4: Update Python Config
1. Edit `laptop_server/people_counter.py`
2. Change line 18 to your ESP32's IP
3. Save

### Step 5: Test ESP32 Stream
Open browser: `http://YOUR_ESP32_IP/stream`
- Should see live video

### Step 6: Run Counter Script
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

### Step 7: Run Web Server
Open new terminal:
```bash
cd IOT/laptop_server
python app.py
```

### Step 8: Open Web Interface
Browser: `http://localhost:5000`

Should see:
- Live video feed
- Red counting line
- Detection boxes around people
- Today's data
- Historical table

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Connection refused" to ESP32
- Check ESP32 IP address
- Ping ESP32: `ping YOUR_ESP32_IP`
- Ensure same WiFi network

### "Camera init failed"
- Check power supply (5V, 2A)
- Re-upload firmware
- Try different USB cable

### No detections showing
- Check lighting (needs good light)
- Adjust CONFIDENCE in people_counter.py
- Verify YOLO models loaded

## Quick Commands

```bash
# Install dependencies
cd IOT/laptop_server
pip install -r requirements.txt

# Test setup
python test_setup.py

# Run counter (Terminal 1)
python people_counter.py

# Run web server (Terminal 2)
python app.py

# View web interface
# Browser: http://localhost:5000
```

## System Flow

```
1. ESP32-CAM captures video → WiFi stream
2. people_counter.py grabs frames → YOLO detection → counts crossings
3. app.py serves web interface → displays live feed + data
4. Browser shows everything in real-time
```

## Next Steps After Testing

Once everything works:
- Adjust counting line position (LINE_X in people_counter.py)
- Tune detection confidence
- Mount camera at entrance
- Monitor data in web interface
- Export CSV data for analysis

## Need Help?

Check `README.md` for detailed documentation and troubleshooting.
