"""
Race Eligibility Gender Category Tests
Verify gender category logic matches requirements
"""
from race_eligibility import analyze_crew_composition
from datetime import datetime, timedelta


def create_crew_member(gender, age):
    """Helper to create crew member with specific gender and age"""
    birth_year = datetime.now().year - age
    return {
        'gender': gender,
        'date_of_birth': f'{birth_year}-01-01'
    }


def test_gender_categories():
    """Test all gender category scenarios"""
    
    print('=== Testing Gender Category Logic ===\n')
    
    # Test 1: 100% Women -> Women's crew
    print('Test 1: 100% Women (4 women)')
    test1 = analyze_crew_composition([
        create_crew_member('F', 25),
        create_crew_member('F', 26),
        create_crew_member('F', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test1['gender_category']}")
    print(f"Expected: women")
    print(f"✓ PASS: {test1['gender_category'] == 'women'}\n")
    
    # Test 2: More than 50% men -> Men's crew
    print('Test 2: More than 50% men (3 men, 1 woman = 75% men)')
    test2 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('M', 26),
        create_crew_member('M', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test2['gender_category']}")
    print(f"Male %: {test2['male_percentage']}%, Female %: {test2['female_percentage']}%")
    print(f"Expected: men")
    print(f"✓ PASS: {test2['gender_category'] == 'men'}\n")
    
    # Test 3: At least 1 man AND at least 50% women -> Mixed crew
    print('Test 3: Mixed (2 men, 2 women = 50% women)')
    test3 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('M', 26),
        create_crew_member('F', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test3['gender_category']}")
    print(f"Male %: {test3['male_percentage']}%, Female %: {test3['female_percentage']}%")
    print(f"Expected: mixed")
    print(f"✓ PASS: {test3['gender_category'] == 'mixed'}\n")
    
    # Test 4: At least 1 man AND more than 50% women -> Mixed crew
    print('Test 4: Mixed (1 man, 3 women = 75% women)')
    test4 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('F', 26),
        create_crew_member('F', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test4['gender_category']}")
    print(f"Male %: {test4['male_percentage']}%, Female %: {test4['female_percentage']}%")
    print(f"Expected: mixed")
    print(f"✓ PASS: {test4['gender_category'] == 'mixed'}\n")
    
    # Test 5: 100% Men -> Men's crew
    print('Test 5: 100% Men (4 men)')
    test5 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('M', 26),
        create_crew_member('M', 27),
        create_crew_member('M', 28)
    ])
    print(f"Result: {test5['gender_category']}")
    print(f"Expected: men")
    print(f"✓ PASS: {test5['gender_category'] == 'men'}\n")
    
    # Test 6: Edge case - 8+ boat with mixed crew
    print('Test 6: 8+ boat (5 men, 4 women = 55.5% men)')
    test6 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('M', 26),
        create_crew_member('M', 27),
        create_crew_member('M', 28),
        create_crew_member('M', 29),
        create_crew_member('F', 25),
        create_crew_member('F', 26),
        create_crew_member('F', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test6['gender_category']}")
    print(f"Male %: {test6['male_percentage']}%, Female %: {test6['female_percentage']}%")
    print(f"Expected: men (more than 50% men)")
    print(f"✓ PASS: {test6['gender_category'] == 'men'}\n")
    
    # Test 7: Edge case - 8+ boat with exactly 50% women and at least 1 man
    print('Test 7: 8+ boat (4 men, 4 women = 50% women)')
    test7 = analyze_crew_composition([
        create_crew_member('M', 25),
        create_crew_member('M', 26),
        create_crew_member('M', 27),
        create_crew_member('M', 28),
        create_crew_member('F', 25),
        create_crew_member('F', 26),
        create_crew_member('F', 27),
        create_crew_member('F', 28)
    ])
    print(f"Result: {test7['gender_category']}")
    print(f"Male %: {test7['male_percentage']}%, Female %: {test7['female_percentage']}%")
    print(f"Expected: mixed (at least 1 man AND at least 50% women)")
    print(f"✓ PASS: {test7['gender_category'] == 'mixed'}\n")
    
    print('=== Summary ===')
    print('Gender Category Rules:')
    print('- Women\'s crews: 100% women')
    print('- Men\'s crews: More than 50% men')
    print('- Mixed-gender crews: At least 1 man AND at least 50% women')


if __name__ == '__main__':
    test_gender_categories()
