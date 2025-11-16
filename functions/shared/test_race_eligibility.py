"""
Unit tests for race eligibility calculation engine
"""
import unittest
from datetime import date
from race_eligibility import (
    calculate_age,
    get_age_category,
    analyze_crew_composition,
    get_eligible_races,
    validate_race_selection
)


class TestRaceEligibility(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.reference_date = date(2024, 6, 15)  # Mid-year reference
        
        # Sample crew members
        self.young_male = {
            'date_of_birth': '2008-03-15',  # 16 years old
            'gender': 'M'
        }
        
        self.senior_male = {
            'date_of_birth': '1999-03-15',  # 25 years old in 2024
            'gender': 'M'
        }
        
        self.master_male = {
            'date_of_birth': '1985-03-15',  # 39 years old
            'gender': 'M'
        }
        
        self.senior_female = {
            'date_of_birth': '2000-03-15',  # 24 years old
            'gender': 'F'
        }
        
        # Sample races
        self.sample_races = [
            {
                'race_id': 'M01',
                'event_type': '42km',
                'boat_type': 'skiff',
                'age_category': 'senior',
                'gender_category': 'men'
            },
            {
                'race_id': 'SM01',
                'event_type': '21km',
                'boat_type': '4-',
                'age_category': 'senior',
                'gender_category': 'mixed'
            },
            {
                'race_id': 'SM02',
                'event_type': '21km',
                'boat_type': '4-',
                'age_category': 'youth',
                'gender_category': 'mixed'
            }
        ]
    
    def test_calculate_age(self):
        """Test age calculation"""
        # Test exact birthday
        age = calculate_age('1990-06-15', self.reference_date)
        self.assertEqual(age, 34)
        
        # Test before birthday this year
        age = calculate_age('1990-08-15', self.reference_date)
        self.assertEqual(age, 33)
        
        # Test after birthday this year
        age = calculate_age('1990-03-15', self.reference_date)
        self.assertEqual(age, 34)
    
    def test_get_age_category(self):
        """Test age category determination"""
        self.assertEqual(get_age_category(16), 'youth')
        self.assertEqual(get_age_category(17), 'youth')
        self.assertEqual(get_age_category(18), 'senior')
        self.assertEqual(get_age_category(26), 'senior')
        self.assertEqual(get_age_category(27), 'master')
        self.assertEqual(get_age_category(50), 'master')
    
    def test_analyze_crew_composition_single(self):
        """Test crew analysis for single sculler"""
        crew = [self.senior_male]
        analysis = analyze_crew_composition(crew)
        
        self.assertEqual(analysis['crew_size'], 1)
        self.assertEqual(analysis['gender_category'], 'men')
        self.assertEqual(analysis['age_category'], 'senior')
        self.assertEqual(analysis['eligible_boat_types'], ['skiff'])
    
    def test_analyze_crew_composition_four(self):
        """Test crew analysis for four"""
        crew = [self.senior_male, self.senior_male, self.senior_male, self.senior_male]
        analysis = analyze_crew_composition(crew)
        
        self.assertEqual(analysis['crew_size'], 4)
        self.assertEqual(analysis['gender_category'], 'men')
        self.assertEqual(analysis['age_category'], 'senior')
        self.assertEqual(analysis['eligible_boat_types'], ['4-'])
    
    def test_analyze_crew_composition_mixed_gender(self):
        """Test crew analysis for mixed gender crew"""
        crew = [self.senior_male, self.senior_female, self.senior_male, self.senior_female]
        analysis = analyze_crew_composition(crew)
        
        self.assertEqual(analysis['gender_category'], 'mixed')
    
    def test_analyze_crew_composition_mixed_age(self):
        """Test crew analysis for mixed age crew"""
        crew = [self.senior_male, self.master_male, self.senior_male, self.senior_male]
        analysis = analyze_crew_composition(crew)
        
        # Should be master category (most restrictive)
        self.assertEqual(analysis['age_category'], 'master')
    
    def test_get_eligible_races_skiff(self):
        """Test eligible races for single sculler"""
        crew = [self.senior_male]
        eligible = get_eligible_races(crew, self.sample_races)
        
        # Should only be eligible for skiff races
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['boat_type'], 'skiff')
    
    def test_get_eligible_races_youth(self):
        """Test eligible races for youth crew"""
        crew = [self.young_male, self.young_male, self.young_male, self.young_male]
        eligible = get_eligible_races(crew, self.sample_races)
        
        # Should only be eligible for youth races
        youth_races = [r for r in eligible if r['age_category'] == 'youth']
        self.assertEqual(len(youth_races), 1)
    
    def test_validate_race_selection_valid(self):
        """Test valid race selection"""
        crew = [self.senior_male]
        race = self.sample_races[0]  # Senior men's skiff
        
        result = validate_race_selection(crew, race)
        self.assertTrue(result['valid'])
    
    def test_validate_race_selection_invalid_boat_type(self):
        """Test invalid race selection - wrong boat type"""
        crew = [self.senior_male]  # Single sculler
        race = self.sample_races[1]  # 4- race
        
        result = validate_race_selection(crew, race)
        self.assertFalse(result['valid'])
        self.assertIn('Boat type', result['reason'])
    
    def test_validate_race_selection_invalid_age(self):
        """Test invalid race selection - wrong age category"""
        crew = [self.young_male, self.young_male, self.young_male, self.young_male]
        race = self.sample_races[1]  # Senior race
        
        result = validate_race_selection(crew, race)
        self.assertFalse(result['valid'])
        self.assertIn('Age category', result['reason'])


if __name__ == '__main__':
    unittest.main()
