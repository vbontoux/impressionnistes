"""
Test RCPM member detection logic
Verifies that the is_rcpm_member function correctly identifies RCPM members
"""


def is_rcpm_member(club_affiliation):
    """
    Determine if a crew member is an RCPM member based on club affiliation
    
    According to requirements FR-4.3, a crew member is identified as an RCPM_Member
    when their club_affiliation contains "RCPM" or "Port-Marly" or "Port Marly"
    (case-insensitive matching)
    
    Args:
        club_affiliation: Club affiliation string
        
    Returns:
        bool: True if RCPM member, False otherwise
    """
    if not club_affiliation or not isinstance(club_affiliation, str):
        return False
    
    club_lower = club_affiliation.lower()
    
    # Check for RCPM or Port-Marly variations
    return ('rcpm' in club_lower or 
            'port-marly' in club_lower or 
            'port marly' in club_lower)


def test_rcpm_detection():
    """Test various club affiliation strings"""
    
    test_cases = [
        # Should be detected as RCPM members
        ("RCPM", True),
        ("rcpm", True),
        ("Rcpm", True),
        ("RCPM Paris", True),
        ("Port-Marly", True),
        ("port-marly", True),
        ("Port Marly", True),
        ("port marly", True),
        ("Rowing Club Port-Marly", True),
        ("Club RCPM", True),
        
        # Should NOT be detected as RCPM members
        ("Aviron Club", False),
        ("Paris Rowing Club", False),
        ("", False),
        (None, False),
        ("RC", False),
        ("PM", False),
    ]
    
    print("Testing RCPM member detection logic:")
    print("-" * 60)
    
    all_passed = True
    for club_affiliation, expected in test_cases:
        result = is_rcpm_member(club_affiliation)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result != expected:
            all_passed = False
        
        print(f"{status} | '{club_affiliation}' -> {result} (expected {expected})")
    
    print("-" * 60)
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed! ✗")
    
    return all_passed


if __name__ == "__main__":
    test_rcpm_detection()
