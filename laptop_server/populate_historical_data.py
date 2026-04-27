#!/usr/bin/env python3
"""
Populate historical data for people counter system
Generates realistic data for 2 days per month over 3 years
"""

import csv
import random
from datetime import datetime, timedelta
import os

LOG_FILE = "people_log.csv"

def generate_realistic_day_data(date):
    """Generate realistic entry/exit events for a single day"""
    events = []
    
    # Business hours: 8 AM to 8 PM
    start_hour = 8
    end_hour = 20
    
    # Peak hours: 9-11 AM and 2-5 PM
    peak_hours = list(range(9, 12)) + list(range(14, 18))
    
    # Track occupancy to ensure it doesn't go negative
    current_occupancy = 0
    total_in = 0
    total_out = 0
    
    # Generate events throughout the day
    current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour)
    end_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=end_hour)
    
    while current_time < end_time:
        hour = current_time.hour
        
        # Determine event frequency based on time of day
        if hour in peak_hours:
            # Peak hours: more frequent events (every 2-8 minutes)
            interval = random.randint(2, 8)
            # Higher chance of entries during peak hours
            entry_probability = 0.6
        else:
            # Off-peak: less frequent (every 5-15 minutes)
            interval = random.randint(5, 15)
            entry_probability = 0.5
        
        # Decide event type
        if current_occupancy == 0:
            # If empty, must be an entry
            event_type = "IN"
        elif current_occupancy > 15:
            # If too crowded, bias towards exits
            event_type = "OUT" if random.random() < 0.7 else "IN"
        else:
            # Normal operation
            event_type = "IN" if random.random() < entry_probability else "OUT"
        
        # Update counters
        if event_type == "IN":
            total_in += 1
            current_occupancy += 1
        else:
            total_out += 1
            current_occupancy -= 1
        
        # Record event
        events.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_type,
            "total_in": total_in,
            "total_out": total_out,
            "occupancy": current_occupancy
        })
        
        # Move to next event
        current_time += timedelta(minutes=interval)
    
    # End of day: ensure everyone exits
    while current_occupancy > 0:
        current_time += timedelta(minutes=random.randint(1, 5))
        total_out += 1
        current_occupancy -= 1
        
        events.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "OUT",
            "total_in": total_in,
            "total_out": total_out,
            "occupancy": current_occupancy
        })
    
    return events

def populate_historical_data(years=3, days_per_month=2):
    """
    Populate historical data for specified years
    
    Args:
        years: Number of years to generate data for (default: 3)
        days_per_month: Number of days per month to generate (default: 2)
    """
    print(f"Generating historical data for {years} years ({days_per_month} days per month)...")
    
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=years * 365)
    
    all_events = []
    
    # Generate data for each month
    current_date = start_date
    month_count = 0
    
    while current_date <= end_date:
        # Get first and last day of current month
        year = current_date.year
        month = current_date.month
        
        # Generate random days in the month
        if month == 12:
            next_month = datetime(year + 1, 1, 1).date()
        else:
            next_month = datetime(year, month + 1, 1).date()
        
        days_in_month = (next_month - datetime(year, month, 1).date()).days
        
        # Select random days (avoid selecting the same day twice)
        selected_days = random.sample(range(1, days_in_month + 1), min(days_per_month, days_in_month))
        selected_days.sort()
        
        for day in selected_days:
            date = datetime(year, month, day).date()
            
            # Don't generate data for future dates
            if date > end_date:
                break
            
            print(f"  Generating data for {date.strftime('%Y-%m-%d')}...")
            day_events = generate_realistic_day_data(date)
            all_events.extend(day_events)
        
        month_count += 1
        
        # Move to next month
        if month == 12:
            current_date = datetime(year + 1, 1, 1).date()
        else:
            current_date = datetime(year, month + 1, 1).date()
    
    # Sort all events by timestamp
    all_events.sort(key=lambda x: x["timestamp"])
    
    # Check if log file exists and back it up
    if os.path.exists(LOG_FILE):
        backup_file = f"{LOG_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\nBacking up existing log file to {backup_file}...")
        os.rename(LOG_FILE, backup_file)
    
    # Write to CSV
    print(f"\nWriting {len(all_events)} events to {LOG_FILE}...")
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "event", "total_in", "total_out", "occupancy"])
        writer.writeheader()
        writer.writerows(all_events)
    
    print(f"\n✅ Successfully generated historical data!")
    print(f"   Total events: {len(all_events)}")
    print(f"   Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Months covered: {month_count}")
    print(f"   Days per month: {days_per_month}")
    
    # Calculate statistics
    total_in = sum(1 for e in all_events if e["event"] == "IN")
    total_out = sum(1 for e in all_events if e["event"] == "OUT")
    print(f"\n📊 Statistics:")
    print(f"   Total entries: {total_in}")
    print(f"   Total exits: {total_out}")
    print(f"   Average events per day: {len(all_events) / (days_per_month * month_count):.1f}")

if __name__ == "__main__":
    populate_historical_data(years=3, days_per_month=2)
