# Render Deployment Guide - TRUE HOSTING

## 🎯 What You'll Get

- ✅ **Permanent URL** (e.g., `https://people-counter.onrender.com`)
- ✅ **Always online** (24/7)
- ✅ **FREE hosting**
- ✅ **Professional deployment**
- ✅ **Historical data display**
- ⚠️ **Live video requires local processing** (ESP32 limitation)

## 📋 Prerequisites

- GitHub account (free)
- Render account (free)
- Your IOT project files

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare Your Code (5 minutes)**

Your code is already prepared! I've created:
- ✅ `requirements_render.txt` - Dependencies for cloud
- ✅ `Procfile` - Tells Render how to run your app
- ✅ `render.yaml` - Render configuration

### **Step 2: Push to GitHub (10 minutes)**

#### 2.1 Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `people-counter`
3. Make it **Public** (required for free Render)
4. Click "Create repository"

#### 2.2 Push Your Code

Open CMD in your IOT folder:

```bash
cd C:\Users\USER\Documents\Arduino\IOT\IOT

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - People Counter"

# Add your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/people-counter.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You'll need to enter your GitHub username and password (or token).

### **Step 3: Deploy on Render (5 minutes)**

#### 3.1 Sign Up for Render

1. Go to: https://render.com
2. Click "Get Started"
3. Sign up with GitHub (easiest)

#### 3.2 Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select `people-counter` repository
4. Configure:
   - **Name:** `people-counter`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** `laptop_server`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements_render.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

5. Click "Create Web Service"

#### 3.3 Wait for Deployment

Render will:
- Install dependencies (~2-3 minutes)
- Start your app
- Give you a URL: `https://people-counter.onrender.com`

### **Step 4: Access Your Hosted App! 🎉**

Your app is now live at:
```
https://people-counter.onrender.com
```

Or whatever URL Render gives you!

## 📊 What Works on Hosted Version

### ✅ Works Perfectly:
- Historical data table
- Statistics (Entered, Exited, Inside Now)
- Date filtering and search
- Peak hour analysis
- All data from CSV file

### ⚠️ Limitations:
- **Live video:** Shows "NO SIGNAL" (ESP32 is on your local network)
- **Real-time counting:** Requires local processing (see below)

## 🔄 Hybrid Setup (Best Solution)

To get real-time counting with hosted web app:

### **On Your Laptop (when camera is active):**

Run `people_counter.py` with cloud updates:

```bash
cd laptop_server
python people_counter.py
```

This will:
- Connect to ESP32 camera
- Do AI detection
- Send updates to your hosted Render app
- Update the CSV file

### **On Render (always online):**

Your web app shows:
- Latest data from CSV
- Historical statistics
- All features except live video

## 🔧 Modify Code for Cloud Updates (Optional)

If you want real-time updates from local to cloud, modify `people_counter.py`:

```python
# Add at the top
RENDER_URL = "https://people-counter.onrender.com"

# In log_event function, add:
try:
    requests.post(f"{RENDER_URL}/update", json={
        "total_in": count_in,
        "total_out": count_out,
        "occupancy": occupancy
    }, timeout=1)
except:
    pass  # Cloud might be down, that's ok
```

## 📝 Update Your App

After making changes:

```bash
git add .
git commit -m "Update for cloud deployment"
git push
```

Render will automatically redeploy! (takes 2-3 minutes)

## 🌐 Share Your App

Your permanent URL:
```
https://people-counter.onrender.com
```

Share this with:
- ✅ Instructor
- ✅ Classmates
- ✅ Anyone on the internet!

## ⚠️ Important Notes

### Free Tier Limitations:
- App "sleeps" after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (enough for most projects)

### To Keep It Always Awake:
Use a service like UptimeRobot (free) to ping your app every 5 minutes.

## 🐛 Troubleshooting

### "Build failed"
- Check `requirements_render.txt` is correct
- Make sure you're deploying from `laptop_server` folder

### "Application failed to start"
- Check logs in Render dashboard
- Verify `Procfile` is correct

### "No data showing"
- Upload `people_log.csv` to GitHub
- Make sure CSV file is in `laptop_server` folder

### "Live video not working"
- This is expected! ESP32 is on your local network
- Use ngrok for live video demos
- Or run `people_counter.py` locally

## 💡 Best Practice

### For Demo/Presentation:
1. **Show hosted version** (permanent URL, always online)
2. **Run ngrok locally** for live video demo
3. **Best of both worlds!**

### For Daily Use:
- Hosted Render app for viewing data
- Run locally when you need live camera

## 🎓 For Your Project Submission

You can say:
> "My application is deployed and hosted on Render at [your-url]. The web interface is always accessible online. For live camera functionality, I use ngrok for demonstrations due to local network constraints of the ESP32 camera."

This shows you understand both hosting and the technical limitations!

## 📚 Additional Resources

- Render Docs: https://render.com/docs
- GitHub Docs: https://docs.github.com
- Flask Deployment: https://flask.palletsprojects.com/en/2.3.x/deploying/

---

**Total Deployment Time: 20-30 minutes**
**Result: Professional, always-online web application!** 🚀
