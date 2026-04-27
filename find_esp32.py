#!/usr/bin/env python3
"""
ESP32-CAM IP Finder
Scans your local network to find the ESP32-CAM device
"""

import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

def get_local_network():
    """Get the local network IP range"""
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Convert to network
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return network, local_ip
    except Exception as e:
        print(f"Error getting local network: {e}")
        return None, None

def check_esp32(ip):
    """Check if IP is an ESP32-CAM by trying to access /stream endpoint"""
    try:
        url = f"http://{ip}/stream"
        response = requests.get(url, timeout=1, stream=True)
        if response.status_code == 200:
            return ip, True
    except:
        pass
    return ip, False

def scan_network():
    """Scan local network for ESP32-CAM devices"""
    network, local_ip = get_local_network()
    
    if not network:
        print("Could not determine local network")
        return
    
    print(f"Your computer IP: {local_ip}")
    print(f"Scanning network: {network}")
    print("This may take 1-2 minutes...\n")
    
    found_devices = []
    checked = 0
    total = network.num_addresses - 2  # Exclude network and broadcast
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_esp32, str(ip)): ip 
                   for ip in network.hosts()}
        
        for future in as_completed(futures):
            checked += 1
            ip, is_esp32 = future.result()
            
            if is_esp32:
                found_devices.append(ip)
                print(f"✅ FOUND ESP32-CAM at: {ip}")
            
            # Progress indicator
            if checked % 50 == 0:
                print(f"Scanned {checked}/{total} addresses...")
    
    print("\n" + "="*60)
    if found_devices:
        print(f"✅ Found {len(found_devices)} ESP32-CAM device(s):")
        for device in found_devices:
            print(f"   • http://{device}/stream")
            print(f"   • Update people_counter.py line 18 to:")
            print(f'     ESP32_CAPTURE_URL = "http://{device}/capture"')
    else:
        print("❌ No ESP32-CAM devices found on network")
        print("\nTroubleshooting:")
        print("1. Check ESP32 is powered on (needs 5V, 2A)")
        print("2. Open Serial Monitor (115200 baud) to see connection status")
        print("3. Verify WiFi credentials in esp32cam_stream.ino")
        print("4. Press RESET button on ESP32 and check Serial Monitor")
        print("5. Ensure ESP32 and computer are on same WiFi network")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("ESP32-CAM Network Scanner")
    print("="*60 + "\n")
    scan_network()
