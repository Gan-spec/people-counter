# Setup Guide for Classmate

## 🎯 Quick Setup (15 minutes)

### **Step 1: Copy the IOT Folder**
Copy the entire `IOT` folder to your laptop (via USB, cloud, etc.)

### **Step 2: Install Python**
1. Check if Python is installed: `python --version`
2. Need Python 3.8 or higher
3. Download from: https://www.python.org/downloads/
4. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation

### **Step 3: Install Python Packages**
Open CMD in the IOT folder:
```bash
cd IOT/laptop_server
pip install -r requirements.txt
```

Wait 2-5 minutes for installation.

### **Step 4: Update ESP32 IP Address**
1. Open `laptop_server/people_counter.py`
2. Find line 18: `ESP32_CAPTURE_URL = "http://10.86.238.176/capture"`
3. Change the IP to your ESP32's IP
4. To find ESP32 IP: `python find_esp32.py`
5. Save the file

### **Step 5: Run Everything!**

**Option A - Easy Way (Double-click):**
```
Double-click: START_ALL.bat
```

**Option B - Manual Way (3 terminals):**
```bash
# Terminal 1
cd laptop_server
python people_counter.py

# Terminal 2
cd laptop_server
python app.py

# Terminal 3
cd ngrok-v3-stable-windows-amd64
ngrok http 5000
```

### **Step 6: Get Your Public URL**
Look at the ngrok window for:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

**That's your public URL!** Share it with anyone! 🎉

## 🌐 Access Your App

- **Local:** http://localhost:5000
- **Public:** https://abc123.ngrok.io (from ngrok window)

## 🛑 To Stop Everything

**Option A - Easy Way:**
```
Double-click: STOP_ALL.bat
```

**Option B - Manual Way:**
Press `Ctrl+C` in each terminal window

## ⚠️ Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Cannot connect to ESP32"
- Check ESP32 is powered on
- Update IP in `people_counter.py` line 18
- Run: `python find_esp32.py` to find IP

### "Port 5000 already in use"
- Close other programs using port 5000
- Or change port in `app.py` (last line)

### ngrok not working
- Make sure you're in the right folder
- The authtoken is already configured (no need to add it again)

## 📋 What's Included

```
IOT/
├── laptop_server/          ← Main code
├── ngrok-v3-stable.../     ← ngrok (already configured!)
├── START_ALL.bat           ← Start everything (easy!)
├── STOP_ALL.bat            ← Stop everything
├── find_esp32.py           ← Find ESP32 IP
└── All guides and docs
```

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Packages installed (`pip install -r requirements.txt`)
- [ ] ESP32 IP updated in `people_counter.py`
- [ ] ESP32 powered on and connected to WiFi
- [ ] Both laptops on same network as ESP32
- [ ] Run `START_ALL.bat` or manual commands
- [ ] Get ngrok URL from terminal
- [ ] Share URL and test!

## 🎓 For Demo/Presentation

1. Start everything: `START_ALL.bat`
2. Wait 10-15 seconds for all services to start
3. Check ngrok window for public URL
4. Share URL with instructor/classmates
5. Everyone can access simultaneously!

## 💡 Tips

- Keep all terminal windows open while running
- ngrok URL changes each restart (free tier)
- Your laptop must stay on for others to access
- Test the URL yourself before sharing

## 🆘 Need Help?

Check these files:
- `README.md` - Project overview
- `QUICK_START.md` - Quick start guide
- `INSTALLATION_GUIDE.md` - Detailed installation
- `DEPLOYMENT_GUIDE.md` - Deployment options

---

**Total setup time: 15-20 minutes**
**Everything is included - just install Python packages and run!** 🚀
