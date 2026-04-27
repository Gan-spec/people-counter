#!/usr/bin/env python3
"""
Automated installation script for People Counter dependencies
Run this on the new laptop to install all required packages
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have Python {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("\n📦 Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to upgrade pip (continuing anyway)")
        return False

def install_from_requirements():
    """Install packages from requirements.txt"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found!")
        print("   Make sure you're in the IOT/laptop_server directory")
        return False
    
    print(f"\n📦 Installing packages from {requirements_file}...")
    print("   This may take 2-5 minutes...")
    print()
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("\n✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Installation failed!")
        return False

def install_packages_individually():
    """Install packages one by one (fallback method)"""
    packages = [
        ("Flask", "flask==3.0.0"),
        ("OpenCV", "opencv-python==4.8.1.78"),
        ("NumPy", "numpy==1.24.3"),
        ("SciPy", "scipy==1.11.4"),
        ("Requests", "requests==2.31.0")
    ]
    
    print("\n📦 Installing packages individually...")
    print()
    
    failed = []
    
    for name, package in packages:
        print(f"Installing {name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print(f"  ✅ {name} installed")
        except subprocess.CalledProcessError:
            print(f"  ❌ {name} failed")
            failed.append(name)
        print()
    
    if failed:
        print(f"❌ Failed to install: {', '.join(failed)}")
        return False
    else:
        print("✅ All packages installed successfully!")
        return True

def verify_installation():
    """Verify all packages are installed correctly"""
    print("\n🔍 Verifying installation...")
    print()
    
    packages = [
        ("Flask", "flask"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("SciPy", "scipy"),
        ("Requests", "requests")
    ]
    
    all_ok = True
    
    for name, module in packages:
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "unknown")
            print(f"  ✅ {name}: {version}")
        except ImportError:
            print(f"  ❌ {name}: NOT INSTALLED")
            all_ok = False
    
    return all_ok

def main():
    """Main installation process"""
    print("=" * 70)
    print("  PEOPLE COUNTER - DEPENDENCY INSTALLER")
    print("=" * 70)
    print()
    
    # Check Python version
    print("🔍 Checking Python version...")
    if not check_python_version():
        print("\n❌ Please install Python 3.8 or higher")
        print("   Download from: https://www.python.org/downloads/")
        return
    print()
    
    # Check pip
    print("🔍 Checking pip...")
    if not check_pip():
        print("\n❌ pip is not available")
        print("   Try: python -m ensurepip --upgrade")
        return
    print()
    
    # Upgrade pip
    upgrade_pip()
    
    # Try installing from requirements.txt
    success = install_from_requirements()
    
    # If that fails, try individual installation
    if not success:
        print("\n⚠️  Trying individual package installation...")
        success = install_packages_individually()
    
    # Verify installation
    if success:
        if verify_installation():
            print("\n" + "=" * 70)
            print("  ✅ INSTALLATION COMPLETE!")
            print("=" * 70)
            print()
            print("📝 Next steps:")
            print("   1. Update ESP32 IP in people_counter.py (line 18)")
            print("   2. Run: python people_counter.py")
            print("   3. Run: python app.py (in another terminal)")
            print("   4. Open: http://localhost:5000")
            print()
        else:
            print("\n" + "=" * 70)
            print("  ⚠️  INSTALLATION INCOMPLETE")
            print("=" * 70)
            print()
            print("Some packages failed to install.")
            print("Try installing them manually:")
            print("  pip install flask opencv-python numpy scipy requests")
            print()
    else:
        print("\n" + "=" * 70)
        print("  ❌ INSTALLATION FAILED")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("  2. Run CMD as Administrator (Windows)")
        print("  3. Try: python -m pip install --upgrade pip")
        print("  4. Try: pip install --user -r requirements.txt")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("   Please install manually using:")
        print("   pip install -r requirements.txt")
