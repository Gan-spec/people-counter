#!/usr/bin/env python3
"""
Setup verification script for ESP32-CAM People Counter
Checks all dependencies and files before running the system
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")
    required = {
        'flask': 'Flask',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'requests': 'requests'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Run: pip install {package}")
            all_ok = False
    
    return all_ok

def check_model_files():
    """Check if YOLO model files exist"""
    print("\nChecking YOLO model files...")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    
    files = {
        'yolov4-tiny.weights': 23000000,  # ~23MB
        'yolov4-tiny.cfg': 1000,          # ~1KB
        'coco.names': 600                  # ~600 bytes
    }
    
    all_ok = True
    for filename, min_size in files.items():
        filepath = os.path.join(models_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size >= min_size:
                print(f"  ✅ {filename} ({size:,} bytes)")
            else:
                print(f"  ⚠️  {filename} ({size:,} bytes) - File seems too small")
                all_ok = False
        else:
            print(f"  ❌ {filename} - File not found")
            all_ok = False
    
    return all_ok

def check_config_files():
    """Check if configuration files exist"""
    print("\nChecking configuration files...")
    
    files = [
        'app.py',
        'people_counter.py',
        'centroid_tracker.py'
    ]
    
    all_ok = True
    for filename in files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - File not found")
            all_ok = False
    
    return all_ok

def check_esp32_config():
    """Check ESP32 configuration in people_counter.py"""
    print("\nChecking ESP32 configuration...")
    
    try:
        with open('people_counter.py', 'r') as f:
            content = f.read()
            
        # Check if ESP32 URL is configured
        if 'ESP32_CAPTURE_URL = "http://10.238.120.176/capture"' in content:
            print("  ⚠️  ESP32 IP still set to default (10.238.120.176)")
            print("     Update this in people_counter.py line 18")
            return False
        else:
            print("  ✅ ESP32 IP configured")
            return True
    except FileNotFoundError:
        print("  ❌ people_counter.py not found")
        return False

def test_esp32_connection():
    """Test connection to ESP32-CAM"""
    print("\nTesting ESP32-CAM connection...")
    
    try:
        import requests
        from people_counter import ESP32_CAPTURE_URL
        
        print(f"  Attempting to connect to: {ESP32_CAPTURE_URL}")
        response = requests.get(ESP32_CAPTURE_URL, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ ESP32-CAM responding ({len(response.content)} bytes)")
            return True
        else:
            print(f"  ❌ ESP32-CAM returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("  ❌ Connection timeout - Check ESP32 IP and network")
        return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection failed - Is ESP32 powered on?")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("ESP32-CAM People Counter - Setup Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Model Files", check_model_files()))
    results.append(("Config Files", check_config_files()))
    results.append(("ESP32 Config", check_esp32_config()))
    
    # Only test connection if other checks pass
    if all(r[1] for r in results):
        results.append(("ESP32 Connection", test_esp32_connection()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! System ready to run.")
        print("\nNext steps:")
        print("1. Terminal 1: python people_counter.py")
        print("2. Terminal 2: python app.py")
        print("3. Browser: http://localhost:5000")
    else:
        print("❌ Some checks failed. Fix issues above before running.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Update ESP32 IP in people_counter.py")
        print("- Ensure ESP32-CAM is powered on and connected to WiFi")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
