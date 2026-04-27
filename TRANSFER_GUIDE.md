# Transfer Guide - Moving to Another Laptop

This guide will help you transfer your people counter project to your classmate's laptop.

## 📦 What to Transfer

### Essential Files (MUST TRANSFER)

#### 1. **ESP32 Code** (if you need to reprogram the ESP32)
```
IOT/esp32cam_stream/
├── esp32cam_stream.ino
└── board_config.h
```

#### 2. **Laptop Server Code**
```
IOT/laptop_server/
├── app.py                    # Flask web server
├── people_counter.py         # Main detection & counting logic
├── requirements.txt          # Python dependencies
└── models/                   # YOLO model files
    ├── yolov4-tiny.weights   # ~23MB - IMPORTANT!
    ├── yolov4-tiny.cfg
    └── coco.names
```

#### 3. **Historical Data** (if you want to keep your data)
```
IOT/laptop_server/
└── people_log.csv            # All your historical counting data
```

#### 4. **Utility Scripts** (optional but useful)
```
IOT/
├── find_esp32.py             # Find ESP32 IP address on network
└── laptop_server/
    ├── populate_historical_data.py  # Generate test data
    └── test_*.py             # Test files (optional)
```

### Optional Files (Documentation)
```
IOT/
├── README.md
├── QUICK_START.md
└── laptop_server/
    ├── DATA_POPULATION_SUMMARY.md
    ├── DATE_FILTER_FIX.md
    ├── SEARCH_BAR_FIX.md
    └── UPGRADE_GUIDE.md
```

## 🚀 Transfer Methods

### Method 1: USB Drive (Recommended - Fastest)
1. Copy the entire `IOT` folder to a USB drive
2. Plug USB into classmate's laptop
3. Copy the `IOT` folder to their laptop

**Estimated time:** 2-5 minutes

### Method 2: Cloud Storage (Google Drive, OneDrive, Dropbox)
1. Compress the `IOT` folder into a ZIP file
2. Upload to cloud storage
3. Share link with classmate
4. Download and extract on their laptop

**Estimated time:** 5-15 minutes (depending on internet speed)

### Method 3: GitHub (Best for version control)
1. Initialize git repository: `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to GitHub
5. Clone on classmate's laptop: `git clone <your-repo-url>`

**Estimated time:** 5-10 minutes

### Method 4: Direct Network Transfer
1. Both laptops on same WiFi
2. Use file sharing (Windows: Nearby Sharing, Mac: AirDrop)
3. Or use Python HTTP server:
   ```bash
   # On your laptop (in IOT parent directory)
   python -m http.server 8000
   
   # On classmate's laptop
   # Open browser: http://<your-ip>:8000
   # Download the IOT folder
   ```

## 📋 Setup on New Laptop

### Step 1: Install Python
```bash
# Check if Python is installed
python --version

# Should be Python 3.8 or higher
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Install Dependencies
```bash
cd IOT/laptop_server
pip install -r requirements.txt
```

**Dependencies include:**
- Flask (web server)
- OpenCV (computer vision)
- NumPy (numerical operations)
- Requests (HTTP requests)

### Step 3: Verify YOLO Model
```bash
# Check if the weights file exists and is ~23MB
ls -lh models/yolov4-tiny.weights
```

If missing, download from: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights

### Step 4: Update ESP32 IP Address
Edit `people_counter.py` line 18:
```python
ESP32_CAPTURE_URL = "http://10.86.238.176/capture"  # Update this IP
```

To find the new IP:
```bash
python find_esp32.py
```

### Step 5: Test the Setup
```bash
# Terminal 1: Start the people counter
python people_counter.py

# Terminal 2: Start the web server
python app.py

# Open browser: http://localhost:5000
```

## ⚙️ Configuration Changes Needed

### 1. ESP32 IP Address
**File:** `IOT/laptop_server/people_counter.py`
**Line:** 18
```python
ESP32_CAPTURE_URL = "http://YOUR_ESP32_IP/capture"
```

### 2. WiFi Network (if ESP32 needs reprogramming)
**File:** `IOT/esp32cam_stream/esp32cam_stream.ino`
**Lines:** Look for WiFi credentials
```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
```

## 📊 Data Transfer Options

### Option A: Transfer Historical Data
**Pros:** Keep all your existing data
**File:** `people_log.csv` (~1-5 MB)

### Option B: Start Fresh
**Pros:** Clean slate, smaller transfer size
**Action:** Delete or don't transfer `people_log.csv`

### Option C: Transfer Sample Data
**Action:** Use `populate_historical_data.py` to generate test data on new laptop

## 🔍 Verification Checklist

After transfer, verify these files exist:

- [ ] `app.py` - Web server
- [ ] `people_counter.py` - Main logic
- [ ] `requirements.txt` - Dependencies
- [ ] `models/yolov4-tiny.weights` - YOLO model (~23MB)
- [ ] `models/yolov4-tiny.cfg` - YOLO config
- [ ] `models/coco.names` - Class names
- [ ] `people_log.csv` - Data (optional)

## 🐛 Common Issues & Solutions

### Issue 1: "Module not found" errors
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: "Cannot connect to ESP32"
**Solution:** Update ESP32 IP address in `people_counter.py`

### Issue 3: "YOLO model not found"
**Solution:** Verify `models/yolov4-tiny.weights` exists and is ~23MB

### Issue 4: "Port 5000 already in use"
**Solution:** Change port in `app.py` (last line):
```python
app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
```

## 📦 Minimal Transfer Package

If you want the absolute minimum files:

```
IOT/
├── laptop_server/
│   ├── app.py
│   ├── people_counter.py
│   ├── requirements.txt
│   └── models/
│       ├── yolov4-tiny.weights
│       ├── yolov4-tiny.cfg
│       └── coco.names
└── find_esp32.py
```

**Total size:** ~25-30 MB

## 🎯 Quick Transfer Command

If both laptops are on same network:

**On your laptop:**
```bash
cd IOT/..
python -m http.server 8000
```

**On classmate's laptop:**
```bash
# Open browser: http://<your-ip>:8000
# Download IOT folder
# Or use wget/curl:
wget -r http://<your-ip>:8000/IOT/
```

## 📝 Notes

1. **ESP32 stays the same** - No need to reprogram unless WiFi changes
2. **Data is portable** - `people_log.csv` works on any system
3. **Python version** - Ensure Python 3.8+ on new laptop
4. **Network** - Both laptops should be on same network as ESP32
5. **Firewall** - May need to allow Python through firewall

## 🆘 Need Help?

If you encounter issues:
1. Check the README.md for setup instructions
2. Verify all files transferred correctly
3. Ensure Python and dependencies are installed
4. Check ESP32 IP address is correct
5. Test with `python test_api.py` to verify setup

---

**Estimated Total Transfer Time:** 10-20 minutes
**Estimated Setup Time on New Laptop:** 15-30 minutes
