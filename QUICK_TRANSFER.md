# Quick Transfer Guide - TL;DR Version

## 🎯 What You Need to Transfer

### Minimum Required (25-30 MB):
```
IOT/laptop_server/
├── app.py
├── people_counter.py  
├── requirements.txt
└── models/
    ├── yolov4-tiny.weights  ← 23MB - DON'T FORGET THIS!
    ├── yolov4-tiny.cfg
    └── coco.names
```

### Also Recommended:
- `people_log.csv` - Your historical data
- `find_esp32.py` - Find ESP32 IP tool

## 🚀 Fastest Method

### Option 1: USB Drive (2-5 minutes)
1. Copy entire `IOT` folder to USB
2. Transfer to classmate's laptop
3. Done!

### Option 2: Use the Package Creator
```bash
cd IOT
python create_transfer_package.py
```
This creates a clean package with only essential files.

## ⚙️ Setup on New Laptop (15 minutes)

```bash
# 1. Install dependencies
cd IOT/laptop_server
pip install -r requirements.txt

# 2. Find ESP32 IP
cd ..
python find_esp32.py

# 3. Update IP in people_counter.py (line 18)
# Edit: ESP32_CAPTURE_URL = "http://YOUR_IP/capture"

# 4. Run it!
cd laptop_server
python people_counter.py  # Terminal 1
python app.py             # Terminal 2

# 5. Open browser
# http://localhost:5000
```

## ⚠️ Don't Forget!

1. ✅ Transfer the YOLO weights file (23MB)
2. ✅ Update ESP32 IP address
3. ✅ Install Python dependencies
4. ✅ Both laptops on same WiFi as ESP32

## 🆘 Problems?

**"Module not found"**
→ `pip install -r requirements.txt`

**"Cannot connect to ESP32"**  
→ Update IP in `people_counter.py` line 18

**"YOLO model not found"**
→ Check `models/yolov4-tiny.weights` exists (23MB)

---

**Total Time: ~20-30 minutes** (transfer + setup)
