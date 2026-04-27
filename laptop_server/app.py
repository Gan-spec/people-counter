from flask import Flask, jsonify, render_template_string, Response, request
import json, os
import csv
from datetime import datetime
from collections import defaultdict
import time
import threading

app = Flask(__name__)
DATA_FILE = "count_data.json"
LOG_FILE = "people_log.csv"

# Global variable to hold the latest frame
latest_frame = None
latest_frame_time = 0
FRAME_TIMEOUT = 5  # seconds before showing "no signal"

# Cache for filtered data
data_cache = {}
cache_lock = threading.Lock()
CACHE_DURATION = 1  # seconds - reduced from 5 to make date filtering more responsive

def read_data():
    if not os.path.exists(DATA_FILE):
        return {"total_in": 0, "total_out": 0, "occupancy": 0}
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"total_in": 0, "total_out": 0, "occupancy": 0}

def get_filtered_data(filter_type="day", start_date=None, end_date=None):
    """Get data filtered by day, month, or year with optional date range (with caching)"""
    
    # Swap dates if they're backwards
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                start_date, end_date = end_date, start_date
        except ValueError:
            pass
    
    # Only use cache if no date filters are applied (to ensure date filtering is responsive)
    use_cache = (start_date is None and end_date is None)
    
    # Create cache key
    cache_key = f"{filter_type}_{start_date}_{end_date}"
    
    # Check cache only if we're using it
    if use_cache:
        with cache_lock:
            if cache_key in data_cache:
                cached_data, cached_time = data_cache[cache_key]
                if time.time() - cached_time < CACHE_DURATION:
                    return cached_data
    
    if not os.path.exists(LOG_FILE):
        return []
    
    data = defaultdict(lambda: {"in": 0, "out": 0, "hours": defaultdict(int)})
    
    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp = row.get("timestamp", "")
                if not timestamp:
                    continue
                    
                event = row.get("event", "")
                if event not in ["IN", "OUT"]:
                    continue
                    
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    
                    # Apply date range filter if provided
                    if start_date:
                        try:
                            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            if dt.date() < start_dt.date():
                                continue
                        except ValueError:
                            pass  # invalid date format, skip filter
                            
                    if end_date:
                        try:
                            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            if dt.date() > end_dt.date():
                                continue
                        except ValueError:
                            pass
                    
                    # Create key based on filter type
                    if filter_type == "day":
                        key = dt.strftime("%Y-%m-%d")
                    elif filter_type == "month":
                        key = dt.strftime("%Y-%m")
                    elif filter_type == "year":
                        key = dt.strftime("%Y")
                    else:
                        key = dt.strftime("%Y-%m-%d")
                    
                    # Count events
                    if event == "IN":
                        data[key]["in"] += 1
                    elif event == "OUT":
                        data[key]["out"] += 1
                    
                    # Track hourly activity for peak hour calculation
                    hour = dt.hour
                    data[key]["hours"][hour] += 1
                    
                except ValueError:
                    continue
    except IOError:
        return []
    
    # Convert to sorted list with peak hour calculation
    result = []
    for key in sorted(data.keys(), reverse=True):
        # Find peak hour
        peak_hour = "N/A"
        if data[key]["hours"]:
            peak_hour_num = max(data[key]["hours"], key=data[key]["hours"].get)
            peak_hour = f"{peak_hour_num:02d}:00"
        
        total_activity = data[key]["in"] + data[key]["out"]
        
        result.append({
            "period": key,
            "in": data[key]["in"],
            "out": data[key]["out"],
            "total": total_activity,
            "peak_hour": peak_hour
        })
    
    # Update cache only if we're using cache
    if use_cache:
        with cache_lock:
            data_cache[cache_key] = (result, time.time())
            # Limit cache size
            if len(data_cache) > 20:
                oldest_key = min(data_cache.keys(), key=lambda k: data_cache[k][1])
                del data_cache[oldest_key]
    
    return result

def gen_frames():
    """Generator function to stream frames with timeout handling"""
    global latest_frame, latest_frame_time
    
    # Create a placeholder "no signal" frame
    no_signal_frame = create_no_signal_frame()
    
    while True:
        current_time = time.time()
        
        # Check if frame is too old
        if latest_frame is not None and (current_time - latest_frame_time) < FRAME_TIMEOUT:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        else:
            # Show "no signal" frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + no_signal_frame + b'\r\n')
        
        time.sleep(0.1)  # Limit frame rate

def create_no_signal_frame():
    """Create a placeholder frame for when no signal is available"""
    import cv2
    import numpy as np
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, "NO SIGNAL", (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.putText(frame, "Waiting for camera...", (180, 280), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
    
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>People Counter</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { 
      margin: 0; 
      padding: 0; 
      box-sizing: border-box; 
    }
    
    body { 
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0a0a0a;
      color: #ffffff;
      min-height: 100vh;
      padding: 2rem;
      line-height: 1.6;
    }
    
    .container { 
      max-width: 1400px; 
      margin: 0 auto; 
    }
    
    header {
      text-align: center;
      margin-bottom: 3rem;
      position: relative;
    }
    
    h1 { 
      font-size: 2.5rem; 
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .subtitle {
      font-size: 1rem;
      color: #888;
      font-weight: 400;
    }
    
    .theme-toggle {
      position: absolute;
      top: 0;
      right: 0;
      background: #111;
      border: 1px solid #333;
      border-radius: 50px;
      padding: 0.5rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
    }
    
    .theme-toggle:hover {
      border-color: #667eea;
      transform: scale(1.05);
    }
    
    .theme-icon {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      transition: all 0.3s ease;
    }
    
    /* Light mode styles */
    body.light-mode {
      background: #f5f5f5;
      color: #1a1a1a;
    }
    
    body.light-mode .video-section,
    body.light-mode .stat-card,
    body.light-mode .controls-section,
    body.light-mode .table-section {
      background: #ffffff;
      border-color: #e0e0e0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    body.light-mode .theme-toggle {
      background: #ffffff;
      border-color: #e0e0e0;
    }
    
    body.light-mode .subtitle {
      color: #666;
    }
    
    body.light-mode .stat-label {
      color: #666;
    }
    
    body.light-mode .control-group label {
      color: #666;
    }
    
    body.light-mode .control-group select,
    body.light-mode .control-group input {
      background: #f5f5f5;
      border-color: #e0e0e0;
      color: #1a1a1a;
    }
    
    body.light-mode .control-group input[type="date"] {
      color-scheme: light;
    }
    
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-month-field,
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-day-field,
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-year-field {
      color: #1a1a1a;
    }
    
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-text {
      color: #999;
    }
    
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-month-field:focus,
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-day-field:focus,
    body.light-mode .control-group input[type="date"]::-webkit-datetime-edit-year-field:focus {
      background: rgba(102, 126, 234, 0.15);
    }
    
    body.light-mode .control-group select:hover,
    body.light-mode .control-group input:hover {
      border-color: #d0d0d0;
      background: #fafafa;
    }
    
    body.light-mode .control-group select:focus,
    body.light-mode .control-group input:focus {
      background: #ffffff;
    }
    
    body.light-mode .control-group input[type="date"]::-webkit-calendar-picker-indicator {
      filter: invert(0.3);
    }
    
    body.light-mode .control-group input[type="date"]:hover::-webkit-calendar-picker-indicator {
      filter: invert(0);
      background: rgba(0, 0, 0, 0.05);
    }
    
    body.light-mode .control-group.search-group input {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cpath d='m21 21-4.35-4.35'%3E%3C/path%3E%3C/svg%3E");
    }
    
    body.light-mode .control-group input::placeholder {
      color: #999;
    }
    
    body.light-mode th {
      background: #f5f5f5;
      color: #666;
      border-bottom-color: #e0e0e0;
    }
    
    body.light-mode td {
      border-bottom-color: #f0f0f0;
    }
    
    body.light-mode tr:hover td {
      background: #fafafa;
    }
    
    body.light-mode .period-cell {
      color: #1a1a1a;
    }
    
    body.light-mode .table-header {
      color: #1a1a1a;
    }
    
    body.light-mode .no-data {
      color: #999;
    }
    
    body.light-mode .modal {
      background: rgba(0, 0, 0, 0.5);
    }
    
    body.light-mode .modal-content {
      background: #ffffff;
      border-color: #e0e0e0;
    }
    
    body.light-mode .modal-title {
      color: #1a1a1a;
    }
    
    body.light-mode .close-btn {
      background: #f5f5f5;
      border-color: #e0e0e0;
      color: #1a1a1a;
    }
    
    body.light-mode .close-btn:hover {
      background: #e0e0e0;
    }
    
    body.light-mode .event-table th {
      background: #f5f5f5;
      color: #666;
      border-bottom-color: #e0e0e0;
    }
    
    body.light-mode .event-table td {
      border-bottom-color: #f0f0f0;
    }
    
    body.light-mode .autocomplete-items {
      background: #ffffff;
      border-color: #e0e0e0;
    }
    
    body.light-mode .autocomplete-items div {
      border-bottom-color: #f0f0f0;
      color: #666;
    }
    
    body.light-mode .autocomplete-items div:hover {
      background: #f5f5f5;
      color: #1a1a1a;
    }
    
    body.light-mode .autocomplete-active {
      background: #f5f5f5 !important;
      color: #1a1a1a !important;
    }
    
    .video-section {
      background: #111;
      border-radius: 24px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      border: 1px solid #222;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    
    .video-section img {
      width: 100%;
      border-radius: 16px;
      display: block;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .stat-card {
      background: #111;
      border: 1px solid #222;
      border-radius: 20px;
      padding: 2rem;
      text-align: center;
      transition: all 0.3s ease;
    }
    
    .stat-card:hover {
      border-color: #333;
      transform: translateY(-2px);
    }
    
    .stat-value {
      font-size: 3.5rem;
      font-weight: 700;
      line-height: 1;
      margin-bottom: 0.5rem;
      font-variant-numeric: tabular-nums;
    }
    
    .stat-label {
      font-size: 0.875rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 500;
    }
    
    .stat-card.in .stat-value { color: #10b981; }
    .stat-card.out .stat-value { color: #ef4444; }
    .stat-card.occupancy .stat-value { color: #3b82f6; }
    
    .controls-section {
      background: #111;
      border: 1px solid #222;
      border-radius: 20px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .controls-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 1rem;
      align-items: end;
    }
    
    .control-group {
      position: relative;
    }
    
    .control-group label {
      display: block;
      font-size: 0.75rem;
      color: #888;
      margin-bottom: 0.5rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .control-group select,
    .control-group input {
      width: 100%;
      padding: 0.875rem 1.25rem;
      background: #0a0a0a;
      border: 1px solid #333;
      border-radius: 12px;
      color: #fff;
      font-size: 0.875rem;
      font-family: inherit;
      transition: all 0.3s ease;
      font-weight: 500;
      height: 48px;
      box-sizing: border-box;
    }
    
    .control-group input[type="date"] {
      cursor: pointer;
      position: relative;
      color-scheme: dark;
    }
    
    /* Make calendar popup larger */
    .control-group input[type="date"]::-webkit-calendar-picker-indicator {
      filter: invert(0.7);
      cursor: pointer;
      transition: all 0.2s ease;
      width: 20px;
      height: 20px;
      padding: 4px;
      border-radius: 4px;
    }
    
    .control-group input[type="date"]:hover::-webkit-calendar-picker-indicator {
      filter: invert(1);
      background: rgba(255, 255, 255, 0.1);
    }
    
    .control-group input[type="date"]::-webkit-datetime-edit {
      padding: 0;
      line-height: 1;
    }
    
    .control-group input[type="date"]::-webkit-datetime-edit-fields-wrapper {
      padding: 0;
    }
    
    .control-group input[type="date"]::-webkit-datetime-edit-text {
      color: #666;
      padding: 0 0.25rem;
    }
    
    .control-group input[type="date"]::-webkit-datetime-edit-month-field,
    .control-group input[type="date"]::-webkit-datetime-edit-day-field,
    .control-group input[type="date"]::-webkit-datetime-edit-year-field {
      color: #fff;
      padding: 0.25rem;
      border-radius: 4px;
      font-size: 0.875rem;
    }
    
    .control-group input[type="date"]::-webkit-datetime-edit-month-field:focus,
    .control-group input[type="date"]::-webkit-datetime-edit-day-field:focus,
    .control-group input[type="date"]::-webkit-datetime-edit-year-field:focus {
      background: rgba(102, 126, 234, 0.2);
      outline: none;
    }
    
    /* Style the calendar popup itself */
    input[type="date"]::-webkit-inner-spin-button,
    input[type="date"]::-webkit-clear-button {
      display: none;
    }
    
    input[type="date"]::-webkit-calendar-picker-indicator {
      background-size: 24px;
    }
    
    .control-group select:hover,
    .control-group input:hover {
      border-color: #444;
      background: #0f0f0f;
    }
    
    .control-group select:focus,
    .control-group input:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
      background: #0f0f0f;
    }
    
    .control-group input::placeholder {
      color: #555;
      font-weight: 400;
    }
    
    .table-section {
      background: #111;
      border: 1px solid #222;
      border-radius: 20px;
      padding: 1.5rem;
      overflow: hidden;
    }
    
    .table-header {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #fff;
    }
    
    .table-wrapper {
      overflow-x: auto;
      border-radius: 12px;
    }
    
    table { 
      width: 100%; 
      border-collapse: collapse;
    }
    
    th, td { 
      padding: 1rem 1.5rem; 
      text-align: left;
    }
    
    th { 
      background: #0a0a0a;
      color: #888;
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      cursor: pointer;
      user-select: none;
      border-bottom: 1px solid #222;
      transition: color 0.2s ease;
    }
    
    th:hover {
      color: #fff;
    }
    
    td {
      border-bottom: 1px solid #1a1a1a;
      font-size: 0.875rem;
    }
    
    tr:hover td {
      background: #0f0f0f;
    }
    
    .in-cell { 
      color: #10b981; 
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }
    
    .out-cell { 
      color: #ef4444; 
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }
    
    .period-cell { 
      font-weight: 500; 
      color: #fff;
    }
    
    .total-cell {
      font-weight: 600;
      color: #888;
      font-variant-numeric: tabular-nums;
    }
    
    .peak-cell {
      color: #888;
      font-variant-numeric: tabular-nums;
    }
    
    .no-data {
      text-align: center;
      color: #555;
      padding: 3rem;
      font-size: 0.875rem;
    }
    
    .sort-arrow {
      margin-left: 0.5rem;
      opacity: 0.5;
    }
    
    /* Modal styles */
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(5px);
      overflow-y: auto;
      align-items: center;
      justify-content: center;
    }
    
    .modal.show {
      display: flex;
    }
    
    .modal-content {
      background: #111;
      border: 1px solid #333;
      border-radius: 20px;
      padding: 2rem;
      width: 90%;
      max-width: 800px;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      margin: 2rem;
    }
    
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #222;
    }
    
    .modal-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #fff;
    }
    
    .close-btn {
      background: #222;
      border: 1px solid #333;
      color: #fff;
      font-size: 1.5rem;
      width: 40px;
      height: 40px;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    
    .close-btn:hover {
      background: #333;
      border-color: #444;
    }
    
    .event-table {
      width: 100%;
      font-size: 0.875rem;
    }
    
    .event-table th {
      background: #0a0a0a;
      color: #666;
      font-weight: 500;
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #222;
    }
    
    .event-table td {
      padding: 12px;
      border-bottom: 1px solid #1a1a1a;
    }
    
    .event-in {
      color: #10b981;
      font-weight: 600;
    }
    
    .event-out {
      color: #ef4444;
      font-weight: 600;
    }
    
    .clickable-row {
      cursor: pointer;
      transition: background 0.2s ease;
    }
    
    .clickable-row:hover {
      background: #0f0f0f !important;
    }
    
    /* Autocomplete dropdown */
    .autocomplete {
      position: relative;
    }
    
    .autocomplete-items {
      position: absolute;
      border: 1px solid #333;
      background: #0a0a0a;
      border-radius: 8px;
      z-index: 99;
      top: 100%;
      left: 0;
      right: 0;
      max-height: 300px;
      overflow-y: auto;
      margin-top: 4px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .autocomplete-items div {
      padding: 12px 16px;
      cursor: pointer;
      border-bottom: 1px solid #1a1a1a;
      color: #aaa;
      transition: all 0.2s ease;
    }
    
    .autocomplete-items div:hover {
      background: #111;
      color: #fff;
    }
    
    .autocomplete-items div:last-child {
      border-bottom: none;
    }
    
    .autocomplete-active {
      background: #111 !important;
      color: #fff !important;
    }
    
    @media (max-width: 768px) {
      body { padding: 1rem; }
      h1 { font-size: 2rem; }
      .stat-value { font-size: 2.5rem; }
      .stats-grid { grid-template-columns: 1fr; }
      .controls-grid { grid-template-columns: 1fr; }
      th, td { padding: 0.75rem 1rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>People Counter</h1>
      <p class="subtitle">Real-time occupancy monitoring</p>
      <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <span class="theme-icon" id="themeIcon">🌙</span>
      </button>
    </header>
    
    <div class="stats-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 1rem;">
      <div class="stat-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border: none;">
        <div class="stat-label" style="color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">OUTSIDE</div>
        <div style="font-size: 1rem; color: rgba(255,255,255,0.9);">Exit Zone</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none;">
        <div class="stat-label" style="color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">INSIDE</div>
        <div style="font-size: 1rem; color: rgba(255,255,255,0.9);">Entry Zone</div>
      </div>
    </div>
    
    <div class="video-section">
      <img src="/video_feed" alt="Live Feed" id="videoFeed">
    </div>
    
    <div class="stats-grid">
      <div class="stat-card in">
        <div class="stat-value" id="totalIn">0</div>
        <div class="stat-label">Entered</div>
      </div>
      <div class="stat-card out">
        <div class="stat-value" id="totalOut">0</div>
        <div class="stat-label">Exited</div>
      </div>
      <div class="stat-card occupancy">
        <div class="stat-value" id="occupancy">0</div>
        <div class="stat-label">Inside Now</div>
      </div>
    </div>
    
    <div class="controls-section">
      <div class="controls-grid">
        <div class="control-group autocomplete">
          <label for="searchBox">Search</label>
          <div style="position: relative;">
            <span style="position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #888; pointer-events: none; font-size: 18px;">🔍</span>
            <input type="text" id="searchBox" style="padding-left: 2.75rem;" placeholder="Search date..." oninput="handleSearch(this.value)" autocomplete="off">
          </div>
          <div id="autocomplete-list" class="autocomplete-items" style="display: none;"></div>
        </div>
        
        <div class="control-group">
          <label for="startDate">From</label>
          <input type="date" id="startDate" onchange="updateTable()">
        </div>
        
        <div class="control-group">
          <label for="endDate">To</label>
          <input type="date" id="endDate" onchange="updateTable()">
        </div>
      </div>
    </div>
    
    <div class="table-section">
      <div class="table-header">History</div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th onclick="sortTable(0)">Date <span class="sort-arrow">↕</span></th>
              <th onclick="sortTable(1)">Entered <span class="sort-arrow">↕</span></th>
              <th onclick="sortTable(2)">Exited <span class="sort-arrow">↕</span></th>
              <th onclick="sortTable(3)">Peak Hour <span class="sort-arrow">↕</span></th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <tr><td colspan="4" class="no-data">Loading...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <!-- Modal for event details -->
  <div id="detailsModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title" id="modalTitle">Event Details</div>
        <button class="close-btn" onclick="closeModal()">&times;</button>
      </div>
      <div id="modalBody">
        <div style="text-align: center; color: #666; padding: 2rem;">Loading...</div>
      </div>
    </div>
  </div>

  <script>
    let currentData = [];
    let allDates = [];
    let sortColumn = 0;
    let sortDirection = 'desc';
    let autocompleteIndex = -1;

    // Theme toggle functionality
    function toggleTheme() {
      const body = document.body;
      const themeIcon = document.getElementById('themeIcon');
      
      body.classList.toggle('light-mode');
      
      if (body.classList.contains('light-mode')) {
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'light');
      } else {
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'dark');
      }
    }
    
    // Load saved theme on page load
    function loadTheme() {
      const savedTheme = localStorage.getItem('theme');
      const body = document.body;
      const themeIcon = document.getElementById('themeIcon');
      
      if (savedTheme === 'light') {
        body.classList.add('light-mode');
        themeIcon.textContent = '☀️';
      } else {
        themeIcon.textContent = '🌙';
      }
    }
    
    // Load theme immediately
    loadTheme();

    function updateStats() {
      fetch('/current_stats')
        .then(r => r.json())
        .then(data => {
          console.log('Stats updated:', data);
          document.getElementById('totalIn').textContent = data.total_in || 0;
          document.getElementById('totalOut').textContent = data.total_out || 0;
          document.getElementById('occupancy').textContent = data.occupancy || 0;
        })
        .catch((error) => {
          console.error('Failed to fetch stats:', error);
        });
    }

    function formatDateDisplay(dateStr) {
      // Convert YYYY-MM-DD to "Month Day, Year" format
      const [year, month, day] = dateStr.split('-');
      const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December'];
      return `${monthNames[parseInt(month) - 1]} ${parseInt(day)}, ${year}`;
    }

    function updateTable() {
      const startDate = document.getElementById('startDate').value;
      const endDate = document.getElementById('endDate').value;
      
      // Always fetch daily data
      let url = `/filtered_data?filter=day`;
      if (startDate) url += `&start_date=${startDate}`;
      if (endDate) url += `&end_date=${endDate}`;
      
      fetch(url)
        .then(r => r.json())
        .then(data => {
          currentData = data;
          allDates = data.map(row => ({
            raw: row.period,
            display: formatDateDisplay(row.period)
          }));
          displayTable(data);
        })
        .catch(() => {
          document.getElementById('tableBody').innerHTML = 
            '<tr><td colspan="4" class="no-data">Error loading data</td></tr>';
        });
    }
    
    function displayTable(data) {
      const tbody = document.getElementById('tableBody');
      if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="no-data">No data available</td></tr>';
        return;
      }
      
      tbody.innerHTML = data.map((row, index) => {
        const displayPeriod = formatDateDisplay(row.period);
        
        return `
          <tr class="clickable-row" onclick="showDetails('${row.period}', '${displayPeriod}')">
            <td class="period-cell">${displayPeriod}</td>
            <td class="in-cell">${row.in}</td>
            <td class="out-cell">${row.out}</td>
            <td class="peak-cell">${row.peak_hour}</td>
          </tr>
        `;
      }).join('');
    }
    
    function handleSearch(value) {
      const autocompleteList = document.getElementById('autocomplete-list');
      
      if (!value) {
        autocompleteList.style.display = 'none';
        displayTable(currentData);
        return;
      }
      
      // Parse various date formats
      const searchLower = value.toLowerCase().trim();
      
      // Filter dates with fuzzy matching
      const matches = allDates.filter(date => {
        const displayLower = date.display.toLowerCase();
        const rawLower = date.raw.toLowerCase();
        
        // Check if search matches display format or raw format
        return displayLower.includes(searchLower) || 
               rawLower.includes(searchLower) ||
               fuzzyMatch(displayLower, searchLower);
      });
      
      if (matches.length > 0) {
        // Show autocomplete dropdown
        autocompleteList.innerHTML = matches.slice(0, 10).map((date, idx) => 
          `<div onclick="selectDate('${date.raw}')" data-index="${idx}">${date.display}</div>`
        ).join('');
        autocompleteList.style.display = 'block';
        autocompleteIndex = -1;
      } else {
        autocompleteList.style.display = 'none';
      }
      
      // Filter table in real-time
      const filteredData = currentData.filter(row => {
        const displayDate = formatDateDisplay(row.period);
        return displayDate.toLowerCase().includes(searchLower) || 
               row.period.toLowerCase().includes(searchLower) ||
               fuzzyMatch(displayDate.toLowerCase(), searchLower);
      });
      displayTable(filteredData);
    }
    
    function fuzzyMatch(str, pattern) {
      // Simple fuzzy matching - checks if all characters in pattern appear in order
      let patternIdx = 0;
      for (let i = 0; i < str.length && patternIdx < pattern.length; i++) {
        if (str[i] === pattern[patternIdx]) {
          patternIdx++;
        }
      }
      return patternIdx === pattern.length;
    }
    
    function selectDate(dateRaw) {
      const searchBox = document.getElementById('searchBox');
      const autocompleteList = document.getElementById('autocomplete-list');
      
      searchBox.value = formatDateDisplay(dateRaw);
      autocompleteList.style.display = 'none';
      
      // Filter to show only selected date
      const filteredData = currentData.filter(row => row.period === dateRaw);
      displayTable(filteredData);
    }
    
    // Keyboard navigation for autocomplete
    document.addEventListener('DOMContentLoaded', function() {
      const searchBox = document.getElementById('searchBox');
      
      searchBox.addEventListener('keydown', function(e) {
        const autocompleteList = document.getElementById('autocomplete-list');
        const items = autocompleteList.getElementsByTagName('div');
        
        if (items.length === 0) return;
        
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          autocompleteIndex = (autocompleteIndex + 1) % items.length;
          updateAutocompleteSelection(items);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          autocompleteIndex = autocompleteIndex <= 0 ? items.length - 1 : autocompleteIndex - 1;
          updateAutocompleteSelection(items);
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (autocompleteIndex >= 0 && autocompleteIndex < items.length) {
            items[autocompleteIndex].click();
          }
        } else if (e.key === 'Escape') {
          autocompleteList.style.display = 'none';
          autocompleteIndex = -1;
        }
      });
      
      // Close autocomplete when clicking outside
      document.addEventListener('click', function(e) {
        if (!e.target.closest('.autocomplete')) {
          document.getElementById('autocomplete-list').style.display = 'none';
        }
      });
    });
    
    function updateAutocompleteSelection(items) {
      // Remove previous selection
      for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('autocomplete-active');
      }
      
      // Add selection to current item
      if (autocompleteIndex >= 0 && autocompleteIndex < items.length) {
        items[autocompleteIndex].classList.add('autocomplete-active');
        items[autocompleteIndex].scrollIntoView({ block: 'nearest' });
      }
    }
    
    function showDetails(period, displayPeriod) {
      const modal = document.getElementById('detailsModal');
      const modalTitle = document.getElementById('modalTitle');
      const modalBody = document.getElementById('modalBody');
      
      modalTitle.textContent = `Event Log - ${displayPeriod}`;
      modalBody.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">Loading...</div>';
      modal.classList.add('show');
      
      // Fetch details
      fetch(`/day_details/${period}`)
        .then(r => r.json())
        .then(events => {
          if (events.length === 0) {
            modalBody.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem; font-style: italic;">No events recorded for this period</div>';
            return;
          }
          
          modalBody.innerHTML = `
            <table class="event-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>People Inside</th>
                </tr>
              </thead>
              <tbody>
                ${events.map(e => `
                  <tr>
                    <td style="color: #aaa;">${e.time}</td>
                    <td>
                      <span class="${e.event === 'IN' ? 'event-in' : 'event-out'}">
                        ${e.event === 'IN' ? '→ ENTERED' : '← EXITED'}
                      </span>
                    </td>
                    <td style="color: #3b82f6; font-weight: 600;">${e.occupancy}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        })
        .catch(() => {
          modalBody.innerHTML = '<div style="text-align: center; color: #ef4444; padding: 2rem;">Error loading details</div>';
        });
    }
    
    function closeModal() {
      document.getElementById('detailsModal').classList.remove('show');
    }
    
    // Close modal when clicking outside
    window.onclick = function(event) {
      const modal = document.getElementById('detailsModal');
      if (event.target === modal) {
        closeModal();
      }
    }
    
    function sortTable(column) {
      if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        sortColumn = column;
        sortDirection = 'desc';
      }
      
      const sortedData = [...currentData].sort((a, b) => {
        let aVal, bVal;
        switch(column) {
          case 0: aVal = a.period; bVal = b.period; break;
          case 1: aVal = a.in; bVal = b.in; break;
          case 2: aVal = a.out; bVal = b.out; break;
          case 3: aVal = a.peak_hour; bVal = b.peak_hour; break;
        }
        
        if (typeof aVal === 'string') {
          return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        } else {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        }
      });
      
      displayTable(sortedData);
    }
    
    updateTable();
    updateStats();
    
    setInterval(updateTable, 10000);
    setInterval(updateStats, 2000);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/filtered_data")
def filtered_data():
    filter_type = request.args.get('filter', 'day')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(get_filtered_data(filter_type, start_date, end_date))

@app.route("/day_details/<date>")
def day_details(date):
    """Get detailed events for a specific day"""
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    
    events = []
    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp = row.get("timestamp", "")
                if not timestamp:
                    continue
                
                if timestamp.startswith(date):
                    events.append({
                        "time": timestamp.split(" ")[1] if " " in timestamp else "",
                        "event": row.get("event", ""),
                        "occupancy": row.get("occupancy", "0")
                    })
    except IOError:
        return jsonify([])
    
    return jsonify(events)

@app.route("/current_stats")
def current_stats():
    return jsonify(read_data())

@app.route("/update", methods=["POST"])
def update():
    try:
        payload = request.get_json()
        if payload:
            with open(DATA_FILE, "w") as f:
                json.dump(payload, f)
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "No data"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/update_frame", methods=["POST"])
def update_frame():
    global latest_frame, latest_frame_time
    try:
        latest_frame = request.data
        latest_frame_time = time.time()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)