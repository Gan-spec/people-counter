"""
Bug Condition Exploration Test for Inconsistent Counting

This test demonstrates the bug where ID changes during crossings cause missed counts.
EXPECTED OUTCOME: This test SHOULD FAIL on unfixed code (proving the bug exists).
After the fix is implemented, this test should PASS.
"""

import sys
import os
import numpy as np
import time
from unittest.mock import Mock, patch

# Add parent directory to path to import people_counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_id_change_in_neutral_zone():
    """
    Test Case 1: ID change in neutral zone during LEFT→RIGHT crossing
    
    Scenario:
    - Frame 1: Person at (120, 120) with ID=5 in LEFT zone
    - Frame 2: Person at (160, 120) with ID=8 in neutral zone (ID changed)
    - Frame 3: Person at (200, 120) with ID=8 in RIGHT zone
    
    Expected: count_in should increment by 1 (crossing detected)
    Actual (unfixed): count_in = 0 (crossing missed because ID=8 has no LEFT history)
    """
    print("\n" + "="*70)
    print("TEST 1: ID Change in Neutral Zone")
    print("="*70)
    
    # Import after path setup
    import people_counter
    
    # Reset global state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    # Create mock frames
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    # Mock detect_people to return controlled detections
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (120, 120) - will get ID=0 (first registration) - IN LEFT ZONE
        mock_detect.return_value = [[100, 100, 40, 40]]  # x, y, w, h -> centroid at (120, 120)
        people_counter.process_frame(frame.copy())
        
        print(f"Frame 1: Person at (120, 120) - ID assigned: 0")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}, count_out: {people_counter.count_out}")
        
        # Manually force ID change by clearing tracker and registering new ID
        # This simulates the tracker assigning a new ID due to distance/disappeared threshold
        people_counter.tracker.objects.clear()
        people_counter.tracker.disappeared.clear()
        people_counter.tracker.next_id = 8  # Force next ID to be 8
        
        # Frame 2: Person at (160, 120) - will get ID=8 (new ID due to tracker reset)
        mock_detect.return_value = [[140, 100, 40, 40]]  # centroid at (160, 120)
        people_counter.process_frame(frame.copy())
        
        print(f"\nFrame 2: Person at (160, 120) - ID assigned: 8 (ID CHANGED)")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}, count_out: {people_counter.count_out}")
        
        # Wait to avoid cooldown
        time.sleep(2.1)
        
        # Frame 3: Person at (200, 120) - ID=8 enters RIGHT zone
        mock_detect.return_value = [[180, 100, 40, 40]]  # centroid at (200, 120)
        people_counter.process_frame(frame.copy())
        
        print(f"\nFrame 3: Person at (200, 120) - ID=8 in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}, count_out: {people_counter.count_out}")
    
    # Assertion: Crossing should be counted
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}")
    print(f"EXPECTED: count_in = 1 (person crossed from LEFT to RIGHT)")
    
    if people_counter.count_in == 1:
        print("✅ TEST PASSED - Crossing was counted correctly")
        return True
    else:
        print("❌ TEST FAILED - Crossing was NOT counted (BUG CONFIRMED)")
        print("   This failure confirms the bug exists: ID change causes zone history loss")
        return False


def test_id_change_after_zone_entry():
    """
    Test Case 2: ID change after entering LEFT zone
    
    Scenario:
    - Frame 1: Person at (130, 120) with ID=3 in LEFT zone
    - Frame 2: Person at (150, 120) with ID=3 still in LEFT zone
    - Frame 3: Person at (170, 120) with ID=7 in neutral zone (ID changed)
    - Frame 4: Person at (200, 120) with ID=7 in RIGHT zone
    
    Expected: count_in should increment by 1
    Actual (unfixed): count_in = 0 (ID=7 has no LEFT history)
    """
    print("\n" + "="*70)
    print("TEST 2: ID Change After Zone Entry")
    print("="*70)
    
    import people_counter
    
    # Reset global state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (130, 120) - ID=0
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 1: Person at (130, 120) - ID=0 in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        # Frame 2: Person at (150, 120) - ID=0 still in LEFT zone
        mock_detect.return_value = [[130, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 2: Person at (150, 120) - ID=0 still in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        # Force ID change
        people_counter.tracker.objects.clear()
        people_counter.tracker.disappeared.clear()
        people_counter.tracker.next_id = 7
        
        # Frame 3: Person at (170, 120) - ID=7 (new ID)
        mock_detect.return_value = [[150, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"\nFrame 3: Person at (170, 120) - ID=7 (ID CHANGED)")
        print(f"  zone_history: {people_counter.zone_history}")
        
        time.sleep(2.1)
        
        # Frame 4: Person at (200, 120) - ID=7 in RIGHT zone
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 4: Person at (200, 120) - ID=7 in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}")
    print(f"EXPECTED: count_in = 1")
    
    if people_counter.count_in == 1:
        print("✅ TEST PASSED")
        return True
    else:
        print("❌ TEST FAILED - BUG CONFIRMED")
        return False


def test_id_change_during_exit():
    """
    Test Case 3: ID change during RIGHT→LEFT exit
    
    Scenario:
    - Frame 1: Person at (200, 120) with ID=9 in RIGHT zone
    - Frame 2: Person at (170, 120) with ID=14 in neutral zone (ID changed)
    - Frame 3: Person at (130, 120) with ID=14 in LEFT zone
    
    Expected: count_out should increment by 1
    Actual (unfixed): count_out = 0 (ID=14 has no RIGHT history)
    """
    print("\n" + "="*70)
    print("TEST 3: ID Change During Exit")
    print("="*70)
    
    import people_counter
    
    # Reset and set initial occupancy
    people_counter.count_in = 1  # Simulate someone already inside
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (200, 120) - ID=0 in RIGHT zone
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 1: Person at (200, 120) - ID=0 in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        # Force ID change
        people_counter.tracker.objects.clear()
        people_counter.tracker.disappeared.clear()
        people_counter.tracker.next_id = 14
        
        # Frame 2: Person at (170, 120) - ID=14 (new ID)
        mock_detect.return_value = [[150, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"\nFrame 2: Person at (170, 120) - ID=14 (ID CHANGED)")
        print(f"  zone_history: {people_counter.zone_history}")
        
        time.sleep(2.1)
        
        # Frame 3: Person at (130, 120) - ID=14 in LEFT zone
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 3: Person at (130, 120) - ID=14 in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_out = {people_counter.count_out}")
    print(f"EXPECTED: count_out = 1")
    
    if people_counter.count_out == 1:
        print("✅ TEST PASSED")
        return True
    else:
        print("❌ TEST FAILED - BUG CONFIRMED")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BUG CONDITION EXPLORATION TEST")
    print("Testing ID changes during crossings on UNFIXED code")
    print("="*70)
    print("\nIMPORTANT: These tests are EXPECTED TO FAIL on unfixed code.")
    print("Failures confirm the bug exists. After implementing the fix,")
    print("these same tests should PASS.\n")
    
    results = []
    
    # Run all test cases
    results.append(("ID Change in Neutral Zone", test_id_change_in_neutral_zone()))
    results.append(("ID Change After Zone Entry", test_id_change_after_zone_entry()))
    results.append(("ID Change During Exit", test_id_change_during_exit()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == 0:
        print("\n🔴 ALL TESTS FAILED - BUG CONFIRMED")
        print("This is the EXPECTED outcome on unfixed code.")
        print("The bug exists: ID changes during crossings cause missed counts.")
    elif passed == total:
        print("\n🟢 ALL TESTS PASSED - BUG FIXED")
        print("The fix is working correctly!")
    else:
        print("\n🟡 PARTIAL SUCCESS")
        print("Some tests passed, some failed. Further investigation needed.")
    
    sys.exit(0 if passed == total else 1)
