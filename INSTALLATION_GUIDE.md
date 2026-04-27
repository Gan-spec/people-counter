# Installation Guide - Python Packages & Dependencies

## 📦 What You Installed on Your Laptop

When you ran `pip install` commands, you installed these Python packages:

### Required Packages:
1. **Flask** (3.0.0) - Web server framework
2. **OpenCV** (4.8.1.78) - Computer vision library
3. **NumPy** (1.24.3) - Numerical computing
4. **SciPy** (1.11.4) - Scientific computing
5. **Requests** (2.31.0) - HTTP library

## 🔄 These Need to Be Reinstalled on New Laptop

**Important:** Python packages are installed on your system, NOT in your project folder. So your classmate needs to install them too!

## 🚀 Installation on New Laptop

### Method 1: Using requirements.txt (RECOMMENDED - Easiest)

```bash
# Navigate to the project folder
cd IOT/laptop_server

# Install all packages at once
pip install -r requirements.txt
```

**This installs everything automatically!** ✅

### Method 2: Manual Installation (If requirements.txt doesn't work)

```bash
pip install flask==3.0.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install scipy==1.11.4
pip install requests==2.31.0
```

### Method 3: Install Latest Versions (Alternative)

```bash
pip install flask opencv-python numpy scipy requests
```

## ⏱️ Installation Time

- **Fast internet:** 2-5 minutes
- **Slow internet:** 5-15 minutes
- **Total download size:** ~150-200 MB

## 🔍 Verify Installation

After installation, verify everything is installed:

```bash
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import scipy; print('SciPy:', scipy.__version__)"
python -c "import requests; print('Requests:', requests.__version__)"
```

**Expected output:**
```
Flask: 3.0.0
OpenCV: 4.8.1.78
NumPy: 1.24.3
SciPy: 1.11.4
Requests: 2.31.0
```

## 🐛 Common Installation Issues

### Issue 1: "pip is not recognized"

**Solution:** Python not in PATH or pip not installed

```bash
# Try python -m pip instead
python -m pip install -r requirements.txt

# Or install pip
python -m ensurepip --upgrade
```

### Issue 2: "Permission denied" or "Access denied"

**Solution:** Run as administrator or use --user flag

```bash
# Windows: Run CMD as Administrator
# Or use --user flag
pip install --user -r requirements.txt
```

### Issue 3: OpenCV installation fails

**Solution:** Install Visual C++ Redistributable (Windows)

Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

Then retry:
```bash
pip install opencv-python
```

### Issue 4: "No module named 'cv2'" after installation

**Solution:** Reinstall opencv-python

```bash
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

### Issue 5: Multiple Python versions installed

**Solution:** Use specific Python version

```bash
# Use Python 3 explicitly
python3 -m pip install -r requirements.txt

# Or specify full path
C:\Python39\python.exe -m pip install -r requirements.txt
```

## 📋 Pre-Installation Checklist

Before installing packages on new laptop:

- [ ] Python 3.8 or higher installed
- [ ] pip is working (`pip --version`)
- [ ] Internet connection available
- [ ] ~200 MB free disk space
- [ ] Administrator access (if needed)

## 🎯 Quick Installation Script

I've created a script to automate this! Save as `install_dependencies.py`:

```python
import subprocess
import sys

def install_packages():
    """Install all required packages"""
    
    print("=" * 60)
    print("  INSTALLING PYTHON PACKAGES")
    print("=" * 60)
    print()
    
    packages = [
        "flask==3.0.0",
        "opencv-python==4.8.1.78",
        "numpy==1.24.3",
        "scipy==1.11.4",
        "requests==2.31.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
        print()
    
    print("=" * 60)
    print("  VERIFYING INSTALLATION")
    print("=" * 60)
    print()
    
    # Verify imports
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not installed")
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy not installed")
    
    try:
        import scipy
        print(f"✅ SciPy: {scipy.__version__}")
    except ImportError:
        print("❌ SciPy not installed")
    
    try:
        import requests
        print(f"✅ Requests: {requests.__version__}")
    except ImportError:
        print("❌ Requests not installed")
    
    print()
    print("=" * 60)
    print("  INSTALLATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    install_packages()
```

Run it with:
```bash
python install_dependencies.py
```

## 🔄 What Gets Transferred vs What Gets Reinstalled

### ✅ TRANSFERRED (Copy files):
- Your Python code (.py files)
- YOLO model files
- Data files (CSV)
- Configuration files

### 🔄 REINSTALLED (Run pip install):
- Flask
- OpenCV
- NumPy
- SciPy
- Requests

**Why?** Python packages are installed system-wide, not in your project folder. They need to be installed on each computer.

## 💡 Pro Tip: Virtual Environment (Optional but Recommended)

To keep packages isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Now run your project
python people_counter.py
```

## 📝 Summary for Your Classmate

**Step-by-step:**

1. **Get Python 3.8+** (if not installed)
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Copy your IOT folder** (from USB/cloud)

3. **Open CMD/Terminal** in the `IOT/laptop_server` folder

4. **Install packages:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Wait 2-5 minutes** for installation

6. **Verify:**
   ```bash
   python -c "import cv2; print('OK')"
   ```

7. **Update ESP32 IP** in `people_counter.py`

8. **Run the system:**
   ```bash
   python people_counter.py
   python app.py
   ```

**Total time:** 10-15 minutes

## 🆘 Still Having Issues?

If installation fails:
1. Check Python version: `python --version` (need 3.8+)
2. Check pip version: `pip --version`
3. Update pip: `python -m pip install --upgrade pip`
4. Try installing one package at a time
5. Check internet connection
6. Run CMD as Administrator (Windows)

---

**Remember:** The `requirements.txt` file makes this easy - just one command installs everything! 🎉
