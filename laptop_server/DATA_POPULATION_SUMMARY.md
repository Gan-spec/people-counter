# Historical Data Population Summary

## Overview
Successfully populated the people counter system with realistic historical data spanning 3 years.

## Data Specifications

### Time Range
- **Start Date**: April 5, 2023
- **End Date**: April 8, 2026
- **Total Duration**: ~3 years

### Coverage
- **Total Unique Days**: 74 days
- **Days per Month**: 2 randomly selected days
- **Total Months**: 37 months
- **Total Events**: 9,384 events

### Event Distribution
- **Total Entries (IN)**: 4,692
- **Total Exits (OUT)**: 4,692
- **Average Events per Day**: ~127 events

## Data Characteristics

### Realistic Patterns
The generated data includes realistic patterns:

1. **Business Hours**: 8 AM to 8 PM
2. **Peak Hours**: 
   - Morning: 9-11 AM
   - Afternoon: 2-5 PM
3. **Event Frequency**:
   - Peak hours: Events every 2-8 minutes
   - Off-peak: Events every 5-15 minutes
4. **Occupancy Management**:
   - Maximum occupancy: ~15 people
   - End-of-day: All people exit (occupancy returns to 0)
   - Prevents negative occupancy

### Data Quality
- ✅ Chronologically sorted
- ✅ Consistent occupancy tracking
- ✅ Realistic entry/exit patterns
- ✅ Peak hour activity simulation
- ✅ No negative occupancy values

## Files

### Main Data File
- **File**: `people_log.csv`
- **Format**: CSV with headers
- **Columns**: timestamp, event, total_in, total_out, occupancy

### Backup
- **Original file backed up to**: `people_log.csv.backup_20260427_023328`

## Usage

The data is immediately available in the web dashboard at `http://localhost:5000`:
- View daily statistics
- Filter by date range
- Search for specific dates
- View detailed event logs for each day
- Analyze peak hours

## Script

The population script is available at:
- **File**: `populate_historical_data.py`
- **Usage**: `python populate_historical_data.py`
- **Customizable**: Edit years and days_per_month parameters

## Sample Data

### First Entry (April 5, 2023)
```
2023-04-05 08:00:00,IN,1,0,1
2023-04-05 08:05:00,IN,2,0,2
2023-04-05 08:11:00,OUT,2,1,1
```

### Last Entry (April 8, 2026)
```
2026-04-08 20:47:00,OUT,66,64,2
2026-04-08 20:51:00,OUT,66,65,1
2026-04-08 20:56:00,OUT,66,66,0
```

## Notes

- Data generation is randomized, so each run produces different patterns
- The script automatically backs up existing data before overwriting
- All dates are randomly selected within each month
- Occupancy always returns to 0 at end of each day
