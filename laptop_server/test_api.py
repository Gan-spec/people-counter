#!/usr/bin/env python3
"""Test if the API endpoints are working"""

import requests

print("Testing API endpoints...")
print("=" * 50)

try:
    # Test current_stats endpoint
    response = requests.get("http://localhost:5000/current_stats")
    print(f"\n✅ /current_stats endpoint:")
    print(f"   Status: {response.status_code}")
    print(f"   Data: {response.json()}")
    
except requests.exceptions.ConnectionError:
    print("\n❌ Flask server is not running!")
    print("   Start it with: python app.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 50)
