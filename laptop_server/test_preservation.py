"""
Preservation Property Tests for People Counter

These tests capture the baseline behavior of the unfixed code for scenarios
that should NOT be affected by the bug fix (stable IDs, no ID changes).

EXPECTED OUTCOME: These tests SHOULD PASS on unfixed code.
After implementing the fix, these tests should STILL PASS (no regressions).
"""

import sys
import os
import numpy as np
import time
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_stable_id_left_to_right_crossing():
    """
    Test: Person with stable ID crossing LEFT→RIGHT should be counted
    
    This is the baseline behavior that must be preserved.
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 1: Stable ID LEFT→RIGHT Crossing")
    print("="*70)
    
    import people_counter
    
    # Reset state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (130, 120) in LEFT zone - gets ID=0
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 1: Person at (130, 120) - ID=0 in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        time.sleep(2.1)  # Wait for cooldown
        
        # Frame 2: Same person at (200, 120) in RIGHT zone - SAME ID=0
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 2: Person at (200, 120) - ID=0 in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}")
    print(f"EXPECTED: count_in = 1 (stable ID crossing should be counted)")
    
    if people_counter.count_in == 1:
        print("✅ TEST PASSED - Baseline behavior preserved")
        return True
    else:
        print("❌ TEST FAILED - Baseline behavior broken!")
        return False


def test_stable_id_right_to_left_crossing():
    """
    Test: Person with stable ID crossing RIGHT→LEFT should be counted
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 2: Stable ID RIGHT→LEFT Crossing")
    print("="*70)
    
    import people_counter
    
    # Reset state with initial occupancy
    people_counter.count_in = 1
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (200, 120) in RIGHT zone - gets ID=0
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 1: Person at (200, 120) - ID=0 in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        time.sleep(2.1)
        
        # Frame 2: Same person at (130, 120) in LEFT zone - SAME ID=0
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        print(f"Frame 2: Person at (130, 120) - ID=0 in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_out: {people_counter.count_out}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_out = {people_counter.count_out}")
    print(f"EXPECTED: count_out = 1")
    
    if people_counter.count_out == 1:
        print("✅ TEST PASSED - Baseline behavior preserved")
        return True
    else:
        print("❌ TEST FAILED - Baseline behavior broken!")
        return False


def test_no_count_when_staying_in_zone():
    """
    Test: Person staying in single zone should not trigger any count
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 3: No Count When Staying in Zone")
    print("="*70)
    
    import people_counter
    
    # Reset state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (130, 120) in LEFT zone
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        time.sleep(2.1)
        
        # Frame 2: Same person at (120, 120) still in LEFT zone
        mock_detect.return_value = [[100, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        # Frame 3: Same person at (125, 120) still in LEFT zone
        mock_detect.return_value = [[105, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        print(f"Person stayed in LEFT zone across 3 frames")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}, count_out: {people_counter.count_out}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}, count_out = {people_counter.count_out}")
    print(f"EXPECTED: count_in = 0, count_out = 0 (no crossing occurred)")
    
    if people_counter.count_in == 0 and people_counter.count_out == 0:
        print("✅ TEST PASSED - Baseline behavior preserved")
        return True
    else:
        print("❌ TEST FAILED - Baseline behavior broken!")
        return False


def test_cooldown_prevents_double_counting():
    """
    Test: 2-second cooldown should prevent double counting for same ID
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 4: Cooldown Prevents Double Counting")
    print("="*70)
    
    import people_counter
    
    # Reset state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (130, 120) in LEFT zone
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        time.sleep(2.1)  # Wait for cooldown
        
        # Frame 2: Person at (200, 120) in RIGHT zone - should count
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        print(f"After first crossing: count_in = {people_counter.count_in}")
        
        # Frame 3: Person back at (130, 120) in LEFT zone - within cooldown
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        # Frame 4: Person at (200, 120) in RIGHT zone again - still within cooldown
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        print(f"After rapid back-and-forth: count_in = {people_counter.count_in}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}")
    print(f"EXPECTED: count_in = 1 (cooldown prevents second count)")
    
    if people_counter.count_in == 1:
        print("✅ TEST PASSED - Cooldown working correctly")
        return True
    else:
        print("❌ TEST FAILED - Cooldown not working!")
        return False


def test_negative_occupancy_prevention():
    """
    Test: System should ignore exit when occupancy is 0
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 5: Negative Occupancy Prevention")
    print("="*70)
    
    import people_counter
    
    # Reset state with zero occupancy
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person at (200, 120) in RIGHT zone
        mock_detect.return_value = [[180, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        time.sleep(2.1)
        
        # Frame 2: Person at (130, 120) in LEFT zone - trying to exit
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        print(f"Person tried to exit when occupancy was 0")
        print(f"  count_in: {people_counter.count_in}, count_out: {people_counter.count_out}")
        print(f"  occupancy: {people_counter.count_in - people_counter.count_out}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_out = {people_counter.count_out}")
    print(f"EXPECTED: count_out = 0 (exit ignored when occupancy=0)")
    
    if people_counter.count_out == 0:
        print("✅ TEST PASSED - Negative occupancy prevention working")
        return True
    else:
        print("❌ TEST FAILED - Negative occupancy prevention broken!")
        return False


def test_multi_person_independent_tracking():
    """
    Test: Multiple people should be tracked and counted independently
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 6: Multi-Person Independent Tracking")
    print("="*70)
    
    import people_counter
    
    # Reset state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=80, max_distance=120)
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Two people in LEFT zone
        mock_detect.return_value = [
            [110, 80, 40, 40],   # Person 1 at (130, 100)
            [110, 120, 40, 40]   # Person 2 at (130, 140)
        ]
        people_counter.process_frame(frame.copy())
        print(f"Frame 1: Two people in LEFT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        
        time.sleep(2.1)
        
        # Frame 2: Both people move to RIGHT zone
        mock_detect.return_value = [
            [180, 80, 40, 40],   # Person 1 at (200, 100)
            [180, 120, 40, 40]   # Person 2 at (200, 140)
        ]
        people_counter.process_frame(frame.copy())
        print(f"Frame 2: Both people in RIGHT zone")
        print(f"  zone_history: {people_counter.zone_history}")
        print(f"  count_in: {people_counter.count_in}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: count_in = {people_counter.count_in}")
    print(f"EXPECTED: count_in = 2 (both people counted independently)")
    
    if people_counter.count_in == 2:
        print("✅ TEST PASSED - Multi-person tracking working")
        return True
    else:
        print("❌ TEST FAILED - Multi-person tracking broken!")
        return False


def test_cleanup_on_deregistration():
    """
    Test: Data structures should be cleaned up when tracker deregisters IDs
    
    Note: Cleanup happens in process_frame when current_ids don't include old IDs
    """
    print("\n" + "="*70)
    print("PRESERVATION TEST 7: Cleanup on Deregistration")
    print("="*70)
    
    import people_counter
    
    # Reset state
    people_counter.count_in = 0
    people_counter.count_out = 0
    people_counter.zone_history = {}
    people_counter.crossed = {}
    people_counter.last_count_time = {}
    people_counter.prev_centroids = {}
    people_counter.tracker = people_counter.ImprovedTracker(max_disappeared=2, max_distance=120)  # Low threshold for quick deregistration
    
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    
    with patch.object(people_counter, 'detect_people') as mock_detect:
        # Frame 1: Person detected
        mock_detect.return_value = [[110, 100, 40, 40]]
        people_counter.process_frame(frame.copy())
        
        initial_id = list(people_counter.zone_history.keys())[0]
        print(f"Frame 1: Person detected with ID={initial_id}")
        print(f"  zone_history keys: {list(people_counter.zone_history.keys())}")
        print(f"  tracker objects: {list(people_counter.tracker.objects.keys())}")
        
        # Frames 2-4: Person disappears (exceed max_disappeared=2)
        mock_detect.return_value = []
        for i in range(3):
            people_counter.process_frame(frame.copy())
        
        print(f"\nAfter 3 frames with no detection:")
        print(f"  zone_history keys: {list(people_counter.zone_history.keys())}")
        print(f"  tracker objects: {list(people_counter.tracker.objects.keys())}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: Data structures after deregistration")
    print(f"  zone_history empty: {len(people_counter.zone_history) == 0}")
    print(f"  tracker empty: {len(people_counter.tracker.objects) == 0}")
    print(f"EXPECTED: All data structures should be empty after tracker deregisters ID")
    
    if (len(people_counter.zone_history) == 0 and 
        len(people_counter.tracker.objects) == 0):
        print("✅ TEST PASSED - Cleanup working correctly")
        return True
    else:
        print("❌ TEST FAILED - Cleanup not working!")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PRESERVATION PROPERTY TESTS")
    print("Testing baseline behavior on UNFIXED code")
    print("="*70)
    print("\nIMPORTANT: These tests should PASS on unfixed code.")
    print("They capture the baseline behavior that must be preserved")
    print("after implementing the fix.\n")
    
    results = []
    
    # Run all preservation tests
    results.append(("Stable ID LEFT→RIGHT", test_stable_id_left_to_right_crossing()))
    results.append(("Stable ID RIGHT→LEFT", test_stable_id_right_to_left_crossing()))
    results.append(("No Count in Zone", test_no_count_when_staying_in_zone()))
    results.append(("Cooldown Prevention", test_cooldown_prevents_double_counting()))
    results.append(("Negative Occupancy", test_negative_occupancy_prevention()))
    results.append(("Multi-Person Tracking", test_multi_person_independent_tracking()))
    results.append(("Cleanup on Deregister", test_cleanup_on_deregistration()))
    
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
    
    if passed == total:
        print("\n🟢 ALL PRESERVATION TESTS PASSED")
        print("Baseline behavior captured successfully.")
        print("These tests must continue to pass after implementing the fix.")
    else:
        print("\n🔴 SOME PRESERVATION TESTS FAILED")
        print("This indicates issues with the baseline implementation.")
    
    sys.exit(0 if passed == total else 1)
