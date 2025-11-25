"""
Test pricing calculations to verify RCPM member detection and multi-club crew pricing
"""
from decimal import Decimal


def is_rcpm_member(club_affiliation):
    """RCPM member detection logic"""
    if not club_affiliation or not isinstance(club_affiliation, str):
        return False
    club_lower = club_affiliation.lower()
    return ('rcpm' in club_lower or 
            'port-marly' in club_lower or 
            'port marly' in club_lower)


def calculate_boat_pricing_simple(crew_members, base_seat_price=20):
    """Simplified pricing calculation for testing"""
    rcpm_seats = 0
    external_seats = 0
    
    for crew in crew_members:
        club = crew.get('club_affiliation', '')
        if is_rcpm_member(club):
            rcpm_seats += 1
        else:
            external_seats += 1
    
    # RCPM members pay 0, external members pay base_seat_price
    total = Decimal(str(base_seat_price)) * external_seats
    
    return {
        'rcpm_seats': rcpm_seats,
        'external_seats': external_seats,
        'total': total
    }


def test_pricing_scenarios():
    """Test various crew compositions"""
    
    test_cases = [
        {
            'name': 'All RCPM members (4)',
            'crew': [
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
            ],
            'expected_total': 0
        },
        {
            'name': 'All external members (4)',
            'crew': [
                {'club_affiliation': 'Paris Rowing Club'},
                {'club_affiliation': 'Lyon Aviron'},
                {'club_affiliation': 'Marseille RC'},
                {'club_affiliation': 'Bordeaux Rowing'},
            ],
            'expected_total': 80
        },
        {
            'name': 'Mixed: 2 RCPM + 2 external',
            'crew': [
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'Paris Rowing Club'},
                {'club_affiliation': 'Lyon Aviron'},
            ],
            'expected_total': 40
        },
        {
            'name': 'Eight with cox: 8 RCPM + 1 external cox',
            'crew': [
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'RCPM'},
                {'club_affiliation': 'Paris Rowing Club'},  # cox
            ],
            'expected_total': 20
        },
        {
            'name': 'Port-Marly variations',
            'crew': [
                {'club_affiliation': 'Port-Marly'},
                {'club_affiliation': 'port marly'},
                {'club_affiliation': 'RCPM Paris'},
                {'club_affiliation': 'External Club'},
            ],
            'expected_total': 20
        },
    ]
    
    print("Testing Pricing Calculations")
    print("=" * 70)
    
    all_passed = True
    for test in test_cases:
        result = calculate_boat_pricing_simple(test['crew'])
        expected = test['expected_total']
        actual = float(result['total'])
        
        status = "✓ PASS" if actual == expected else "✗ FAIL"
        if actual != expected:
            all_passed = False
        
        print(f"\n{status} | {test['name']}")
        print(f"  RCPM seats: {result['rcpm_seats']}, External seats: {result['external_seats']}")
        print(f"  Expected: {expected} EUR, Actual: {actual} EUR")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("All pricing tests passed! ✓")
    else:
        print("Some pricing tests failed! ✗")
    
    return all_passed


if __name__ == "__main__":
    test_pricing_scenarios()
