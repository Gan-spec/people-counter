# Web Deployment Guide

## 🎯 Goal
Make your people counter web app accessible from anywhere on the internet, not just localhost.

## ⚡ Quick Solution: ngrok (5 minutes)

### What is ngrok?
ngrok creates a secure tunnel from the internet to your localhost. Perfect for demos and testing!

### Step 1: Download ngrok
1. Go to: https://ngrok.com/download
2. Sign up for free account
3. Download ngrok for Windows

### Step 2: Install & Setup
```bash
# Extract ngrok.exe to a folder
# Add your authtoken (from ngrok dashboard)
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Run Your App
```bash
# Terminal 1: Start people counter
cd IOT/laptop_server
python people_counter.py

# Terminal 2: Start web server
python app.py
```

### Step 4: Start ngrok
```bash
# Terminal 3: Start ngrok tunnel
ngrok http 5000
```

### Step 5: Get Your Public URL
You'll see something like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

**Share this URL:** `https://abc123.ngrok.io`

Anyone can access your app now! 🎉

### Pros & Cons:
✅ Super fast setup (5 minutes)
✅ No code changes needed
✅ Works immediately
✅ Free tier available
⚠️ URL changes each restart (unless paid plan)
⚠️ Your laptop must stay on
⚠️ Temporary solution

---

## 🌐 Permanent Solution: Cloud Deployment

For a permanent deployment, you need to deploy to a cloud platform.

### Challenge: ESP32 Camera Access
Your app needs to connect to the ESP32 camera. This creates a problem:
- ESP32 is on your local network
- Cloud server can't access your local network

### Solutions:

#### Solution A: Deploy Everything Locally + Use ngrok
**Best for:** Demos, testing, short-term use

```
Your Laptop:
├── ESP32 Camera (local network)
├── people_counter.py (connects to ESP32)
├── app.py (web server)
└── ngrok (makes it public)
```

**Pros:**
- ✅ Easy setup
- ✅ No code changes
- ✅ Works with local ESP32

**Cons:**
- ⚠️ Laptop must stay on
- ⚠️ Temporary URL

#### Solution B: Deploy Web Only + Keep Processing Local
**Best for:** Permanent deployment with local camera

```
Cloud Server:
└── app.py (web server only)
    ↑
    | (receives updates via API)
    |
Your Laptop:
├── ESP32 Camera
└── people_counter.py (sends data to cloud)
```

**Pros:**
- ✅ Web app always online
- ✅ Permanent URL
- ✅ Works with local ESP32

**Cons:**
- ⚠️ Requires code modifications
- ⚠️ Laptop must stay on for camera

#### Solution C: Move ESP32 to Cloud-Accessible Network
**Best for:** Production deployment

```
Cloud Server:
├── people_counter.py
└── app.py
    ↑
    | (connects via public IP)
    |
ESP32 Camera (with public IP or VPN)
```

**Pros:**
- ✅ Fully cloud-based
- ✅ Always online
- ✅ Professional solution

**Cons:**
- ⚠️ Requires public IP or VPN
- ⚠️ Security considerations
- ⚠️ More complex setup

---

## 📦 Deployment Option 1: Render (Free)

### What You Get:
- Free tier: 750 hours/month
- Permanent URL
- Auto-deploy from GitHub

### Requirements:
- GitHub account
- Code modifications needed

### Step 1: Prepare for Deployment

Create `requirements.txt` (already exists):
```
flask==3.0.0
opencv-python-headless==4.8.1.78
numpy==1.24.3
scipy==1.11.4
requests==2.31.0
gunicorn==21.2.0
```

Create `Procfile`:
```
web: gunicorn app:app
```

Create `render.yaml`:
```yaml
services:
  - type: web
    name: people-counter
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

### Step 2: Push to GitHub
```bash
cd IOT
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to: https://render.com
2. Sign up / Log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - Name: people-counter
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Click "Create Web Service"

### Step 4: Modify Code for Cloud
You'll need to separate the web app from the camera processing.

**Problem:** Cloud server can't access your local ESP32.

**Solution:** Run `people_counter.py` locally, send data to cloud via API.

---

## 📦 Deployment Option 2: PythonAnywhere (Free)

### What You Get:
- Free tier available
- Easy Python deployment
- yourname.pythonanywhere.com URL

### Step 1: Sign Up
1. Go to: https://www.pythonanywhere.com
2. Create free account

### Step 2: Upload Files
1. Go to "Files" tab
2. Upload your IOT folder
3. Upload YOLO model files

### Step 3: Create Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose Flask
4. Point to your `app.py`

### Step 4: Install Dependencies
```bash
# In PythonAnywhere console
pip install --user flask opencv-python-headless numpy scipy requests
```

### Step 5: Configure
- Set working directory
- Reload web app

**Note:** Same issue with ESP32 access applies.

---

## 🔧 Code Modifications for Cloud Deployment

### Option: Split Architecture

**File 1: `app.py` (Deploy to cloud)**
```python
# Remove people_counter.py dependency
# Just serve web interface
# Read data from database or API
```

**File 2: `people_counter.py` (Run locally)**
```python
# Add code to send data to cloud
import requests

def send_to_cloud(data):
    requests.post("https://your-app.com/api/update", json=data)
```

### Option: Use Database
- Deploy web app to cloud
- Use cloud database (PostgreSQL, MongoDB)
- Local `people_counter.py` writes to cloud database
- Web app reads from cloud database

---

## 🎯 Recommended Approach for Your Project

### For Demo/Presentation (Quick):
**Use ngrok** - 5 minutes setup, works immediately

```bash
# Terminal 1
python people_counter.py

# Terminal 2  
python app.py

# Terminal 3
ngrok http 5000
```

Share the ngrok URL: `https://abc123.ngrok.io`

### For Permanent Deployment:
**Hybrid approach:**
1. Deploy web app to Render/PythonAnywhere
2. Run `people_counter.py` locally
3. Send data to cloud via API
4. Use cloud database for data storage

---

## 📋 Quick Deployment Checklist

### Using ngrok (Fastest):
- [ ] Download ngrok
- [ ] Sign up for account
- [ ] Add authtoken
- [ ] Run people_counter.py
- [ ] Run app.py
- [ ] Run ngrok http 5000
- [ ] Share the URL

### Using Cloud Platform:
- [ ] Choose platform (Render/PythonAnywhere)
- [ ] Create account
- [ ] Prepare code for deployment
- [ ] Upload/deploy code
- [ ] Configure environment
- [ ] Set up database (if needed)
- [ ] Modify code for cloud access
- [ ] Test deployment

---

## 🆘 Need Help?

**For quick demo:** Use ngrok
**For permanent:** Let me know which platform you prefer and I'll create detailed instructions!

**Common Questions:**

Q: Can I deploy for free?
A: Yes! ngrok, Render, and PythonAnywhere have free tiers.

Q: Will ESP32 work with cloud deployment?
A: Not directly. You need to run `people_counter.py` locally or use VPN/public IP.

Q: How long does deployment take?
A: ngrok: 5 minutes | Cloud: 30-60 minutes

Q: Which is best for my project?
A: For demo: ngrok | For production: Render + local processing
