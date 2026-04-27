#!/usr/bin/env python3
"""
Populate people_log.csv with comprehensive sample data
Data for every month from 2024-2026
"""

import csv
from datetime import datetime

LOG_FILE = "people_log.csv"

# Generate realistic sample data for every month
events = []

# 2024 - All 12 months
months_2024 = [
    ("2024-01-15", "January"),
    ("2024-02-10", "February"),
    ("2024-03-20", "March"),
    ("2024-04-05", "April"),
    ("2024-05-18", "May"),
    ("2024-06-22", "June"),
    ("2024-07-14", "July"),
    ("2024-08-09", "August"),
    ("2024-09-25", "September"),
    ("2024-10-12", "October"),
    ("2024-11-08", "November"),
    ("2024-12-19", "December"),
]

# 2025 - All 12 months
months_2025 = [
    ("2025-01-11", "January"),
    ("2025-02-14", "February"),
    ("2025-03-05", "March"),
    ("2025-04-22", "April"),
    ("2025-05-16", "May"),
    ("2025-06-20", "June"),
    ("2025-07-08", "July"),
    ("2025-08-13", "August"),
    ("2025-09-17", "September"),
    ("2025-10-24", "October"),
    ("2025-11-19", "November"),
    ("2025-12-15", "December"),
]

# 2026 - First 4 months (current year)
months_2026 = [
    ("2026-01-09", "January"),
    ("2026-02-12", "February"),
    ("2026-03-18", "March"),
    ("2026-04-26", "April"),
]

all_months = months_2024 + months_2025 + months_2026

# Generate 6 events per day (3 IN, 3 OUT)
for date, month_name in all_months:
    # Morning entries
    events.append((f"{date} 08:30:00", "IN"))
    events.append((f"{date} 09:15:00", "IN"))
    
    # Midday
    events.append((f"{date} 11:45:00", "OUT"))
    events.append((f"{date} 13:20:00", "IN"))
    
    # Afternoon
    events.append((f"{date} 16:30:00", "OUT"))
    events.append((f"{date} 17:45:00", "OUT"))

# Sort by timestamp
events.sort(key=lambda x: x[0])

# Calculate cumulative counts
total_in = 0
total_out = 0

# Write to CSV
with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "event", "total_in", "total_out", "occupancy"])
    
    for timestamp, event in events:
        if event == "IN":
            total_in += 1
        else:
            total_out += 1
        
        occupancy = max(0, total_in - total_out)
        
        writer.writerow([timestamp, event, total_in, total_out, occupancy])

print(f"✅ Generated {len(events)} events")
print(f"📅 Date range: {events[0][0]} to {events[-1][0]}")
print(f"📊 Total IN: {total_in}, Total OUT: {total_out}")
print(f"\n📋 Summary:")
print(f"   • 2024: 12 months (Jan-Dec)")
print(f"   • 2025: 12 months (Jan-Dec)")
print(f"   • 2026: 4 months (Jan-Apr)")
print(f"   • Total: 28 months of data")
print(f"   • 6 events per day (3 IN, 3 OUT)")
print(f"\n✅ Data written to {LOG_FILE}")
