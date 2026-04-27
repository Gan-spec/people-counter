# Quick Deploy with ngrok - 5 Minutes

## 🎯 Make Your App Accessible Online in 5 Minutes

### What is ngrok?
Makes your localhost accessible from anywhere on the internet. Perfect for demos!

## 🚀 Step-by-Step

### 1. Download ngrok (2 minutes)
1. Go to: **https://ngrok.com/download**
2. Click "Sign up" (free account)
3. Download ngrok for Windows
4. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok\`)

### 2. Get Your Auth Token (1 minute)
1. After signing up, you'll see your authtoken
2. Copy it (looks like: `2abc123def456ghi789jkl`)

### 3. Setup ngrok (1 minute)
```bash
# Open CMD and navigate to ngrok folder
cd C:\ngrok

# Add your authtoken (replace with your actual token)
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 4. Run Your App (1 minute)
```bash
# Terminal 1: Start people counter
cd IOT/laptop_server
python people_counter.py

# Terminal 2: Start web server
cd IOT/laptop_server
python app.py
```

Wait for both to start successfully!

### 5. Start ngrok (30 seconds)
```bash
# Terminal 3: Start ngrok
cd C:\ngrok
ngrok http 5000
```

### 6. Get Your Public URL! 🎉
You'll see something like:

```
ngrok

Session Status                online
Account                       your@email.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Your public URL is:** `https://abc123.ngrok.io`

### 7. Share & Access! 🌐
- Share this URL with anyone
- They can access your app from anywhere
- Works on phones, tablets, other computers
- No installation needed for them!

## 📱 Access Your App

**From anywhere:**
```
https://abc123.ngrok.io
```

**Example:**
```
https://abc123.ngrok.io
```

Anyone with this link can see:
- Live video feed
- Real-time counting
- Historical data
- All features!

## ⚠️ Important Notes

### Keep Everything Running:
- ✅ Terminal 1: `people_counter.py` (must stay open)
- ✅ Terminal 2: `app.py` (must stay open)
- ✅ Terminal 3: `ngrok` (must stay open)
- ✅ Your laptop must stay on
- ✅ ESP32 must be powered on

### URL Changes:
- ⚠️ Free tier: URL changes each time you restart ngrok
- ⚠️ Example: `https://abc123.ngrok.io` becomes `https://xyz789.ngrok.io`
- 💰 Paid plan ($8/month): Get permanent URL

### Security:
- ✅ ngrok uses HTTPS (secure)
- ✅ Only people with the URL can access
- ⚠️ Don't share URL publicly if you have sensitive data

## 🎓 For Your Demo/Presentation

### Before Demo:
1. Start all 3 terminals
2. Get ngrok URL
3. Test it yourself first
4. Share URL with instructor/classmates

### During Demo:
- Show the ngrok URL
- Everyone can access simultaneously
- Works on their phones/laptops
- No installation needed!

### After Demo:
- Press Ctrl+C in all terminals to stop
- URL will stop working (that's okay!)

## 💡 Pro Tips

### Tip 1: Check ngrok Dashboard
Open: `http://127.0.0.1:4040`
- See all requests
- Debug issues
- Monitor traffic

### Tip 2: Custom Subdomain (Paid)
```bash
ngrok http 5000 --subdomain=myproject
# URL: https://myproject.ngrok.io (doesn't change!)
```

### Tip 3: Multiple Tunnels
```bash
# If you need multiple services
ngrok http 5000 --region=us
```

### Tip 4: Save Configuration
Create `ngrok.yml`:
```yaml
authtoken: YOUR_AUTH_TOKEN
tunnels:
  people-counter:
    proto: http
    addr: 5000
```

Then run:
```bash
ngrok start people-counter
```

## 🐛 Troubleshooting

### "Failed to start tunnel"
- Check your authtoken is correct
- Make sure app.py is running on port 5000
- Try restarting ngrok

### "Connection refused"
- Make sure `app.py` is running
- Check it's on port 5000
- Try accessing `localhost:5000` first

### "Tunnel not found"
- Your free tier might have expired
- Sign up for new account
- Or upgrade to paid plan

### URL not working for others
- Make sure all 3 terminals are running
- Check your laptop is connected to internet
- Try the URL yourself first

## 📊 What Others Will See

When someone visits your ngrok URL, they'll see:
- ✅ Live video feed from ESP32
- ✅ Real-time people counting
- ✅ Entry/Exit statistics
- ✅ Historical data table
- ✅ Search and filters
- ✅ All features working!

## 🎯 Summary

```
1. Download ngrok          → 2 min
2. Sign up & get token     → 1 min
3. Setup authtoken         → 1 min
4. Run your app            → 1 min
5. Start ngrok             → 30 sec
6. Share URL               → Done! 🎉
```

**Total time: 5 minutes**

**Result:** Your app is now accessible from anywhere in the world! 🌍

## 🔗 Useful Links

- ngrok Download: https://ngrok.com/download
- ngrok Dashboard: https://dashboard.ngrok.com
- ngrok Docs: https://ngrok.com/docs
- Local Dashboard: http://127.0.0.1:4040

---

**Need permanent deployment?** See `DEPLOYMENT_GUIDE.md` for cloud options!
