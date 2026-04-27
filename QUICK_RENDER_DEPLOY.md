# Quick Render Deployment - 20 Minutes

## 🚀 Fast Track to TRUE Hosting

### **Step 1: GitHub (10 min)**

```bash
# In your IOT folder
cd C:\Users\USER\Documents\Arduino\IOT\IOT

git init
git add .
git commit -m "People Counter"
git remote add origin https://github.com/YOUR_USERNAME/people-counter.git
git push -u origin main
```

### **Step 2: Render (5 min)**

1. Go to: https://render.com
2. Sign up with GitHub
3. New + → Web Service
4. Connect `people-counter` repo
5. Settings:
   - Root Directory: `laptop_server`
   - Build: `pip install -r requirements_render.txt`
   - Start: `gunicorn app:app`
   - Plan: **Free**
6. Create!

### **Step 3: Done! (5 min)**

Wait for deployment, then get your URL:
```
https://people-counter.onrender.com
```

## ✅ What You Get

- Permanent URL
- Always online
- FREE hosting
- Professional deployment

## ⚠️ Note

Live video won't work (ESP32 is local). Use ngrok for live demos!

---

**See RENDER_DEPLOYMENT.md for detailed guide**
