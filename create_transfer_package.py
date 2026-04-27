#!/usr/bin/env python3
"""
Create a minimal transfer package for the people counter project
This script copies only the essential files needed to run the system
"""

import os
import shutil
from pathlib import Path

def create_transfer_package():
    """Create a minimal transfer package"""
    
    print("=" * 60)
    print("  PEOPLE COUNTER - TRANSFER PACKAGE CREATOR")
    print("=" * 60)
    print()
    
    # Define source and destination
    source_dir = Path(__file__).parent
    dest_dir = source_dir.parent / "IOT_TRANSFER_PACKAGE"
    
    # Create destination directory
    if dest_dir.exists():
        print(f"⚠️  Destination already exists: {dest_dir}")
        response = input("Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(dest_dir)
        else:
            print("Aborted.")
            return
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {dest_dir}")
    print()
    
    # Essential files to copy
    essential_files = [
        "laptop_server/app.py",
        "laptop_server/people_counter.py",
        "laptop_server/requirements.txt",
        "laptop_server/models/yolov4-tiny.weights",
        "laptop_server/models/yolov4-tiny.cfg",
        "laptop_server/models/coco.names",
        "find_esp32.py",
        "README.md",
        "TRANSFER_GUIDE.md",
        "TRANSFER_CHECKLIST.txt",
    ]
    
    # Optional files (ask user)
    optional_files = [
        ("laptop_server/people_log.csv", "Historical data (people_log.csv)"),
        ("laptop_server/populate_historical_data.py", "Data generator script"),
        ("QUICK_START.md", "Quick start guide"),
    ]
    
    print("📦 COPYING ESSENTIAL FILES")
    print("-" * 60)
    
    total_size = 0
    copied_count = 0
    
    for file_path in essential_files:
        src = source_dir / file_path
        dst = dest_dir / file_path
        
        if src.exists():
            # Create parent directories
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dst)
            file_size = src.stat().st_size
            total_size += file_size
            copied_count += 1
            
            # Format size
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024*1024):.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"  ✅ {file_path:<50} {size_str:>10}")
        else:
            print(f"  ⚠️  {file_path:<50} NOT FOUND")
    
    print()
    print("📋 OPTIONAL FILES")
    print("-" * 60)
    
    for file_path, description in optional_files:
        src = source_dir / file_path
        if src.exists():
            response = input(f"Include {description}? (y/n): ")
            if response.lower() == 'y':
                dst = dest_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                file_size = src.stat().st_size
                total_size += file_size
                copied_count += 1
                
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024*1024):.1f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size} bytes"
                
                print(f"  ✅ {file_path:<50} {size_str:>10}")
    
    print()
    print("=" * 60)
    print(f"✅ TRANSFER PACKAGE CREATED")
    print("=" * 60)
    print(f"  Location: {dest_dir}")
    print(f"  Files copied: {copied_count}")
    print(f"  Total size: {total_size / (1024*1024):.1f} MB")
    print()
    print("📦 NEXT STEPS:")
    print("  1. Copy the 'IOT_TRANSFER_PACKAGE' folder to USB drive")
    print("  2. Transfer to classmate's laptop")
    print("  3. Follow TRANSFER_GUIDE.md for setup instructions")
    print("  4. Use TRANSFER_CHECKLIST.txt to verify everything")
    print()

if __name__ == "__main__":
    try:
        create_transfer_package()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
