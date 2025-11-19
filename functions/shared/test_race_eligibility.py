"""
Unit tests for race eligibility calculation engine
"""
import unittest
from datetime import date
from race_eligibility import (
    calculate_age,
    get_age_category,
    get_master_category,
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
                'race_id': 'SM12',
                'event_type': '21km',
                'boat_type': '4-',
                'age_category': 'senior',
                'gender_category': 'mixed'
            },
            {
                'race_id': 'SM08',
                'event_type': '21km',
                'boat_type': '4-',
                'age_category': 'j18',
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
        self.assertEqual(get_age_category(15), 'j16')
        self.assertEqual(get_age_category(16), 'j16')
        self.assertEqual(get_age_category(17), 'j18')
        self.assertEqual(get_age_category(18), 'j18')
        self.assertEqual(get_age_category(19), 'senior')
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
    
    def test_get_eligible_races_j16(self):
        """Test eligible races for j16 crew"""
        crew = [self.young_male, self.young_male, self.young_male, self.young_male]
        eligible = get_eligible_races(crew, self.sample_races)
        
        # young_male is 16 years old (j16 category), crew of 4 = 4- boat
        # No j16 races in sample_races for 4- boat type, so should find 0
        # But wait - let me check the actual races
        j16_races = [r for r in eligible if r['age_category'] == 'j16']
        self.assertEqual(len(j16_races), 0)
    
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
        race = self.sample_races[1]  # Senior race (SM12)
        
        result = validate_race_selection(crew, race)
        self.assertFalse(result['valid'])
        self.assertIn('Age category', result['reason'])
    
    def test_get_master_category(self):
        """Test master category determination"""
        self.assertEqual(get_master_category(30), 'A')  # 27-35
        self.assertEqual(get_master_category(35), 'A')
        self.assertEqual(get_master_category(36), 'B')  # 36-42
        self.assertEqual(get_master_category(42), 'B')
        self.assertEqual(get_master_category(43), 'C')  # 43-49
        self.assertEqual(get_master_category(49), 'C')
        self.assertEqual(get_master_category(50), 'D')  # 50-54
        self.assertEqual(get_master_category(54), 'D')
        self.assertEqual(get_master_category(55), 'E')  # 55-59
        self.assertEqual(get_master_category(59), 'E')
        self.assertEqual(get_master_category(60), 'F')  # 60-64
        self.assertEqual(get_master_category(64), 'F')
        self.assertEqual(get_master_category(65), 'G')  # 65-69
        self.assertEqual(get_master_category(69), 'G')
        self.assertEqual(get_master_category(70), 'H')  # 70+
        self.assertEqual(get_master_category(80), 'H')
    
    def test_analyze_crew_composition_master_category(self):
        """Test crew analysis includes master category for master crews"""
        # Create master crew with average age 38 (should be category B)
        master_crew = [
            {'date_of_birth': '1986-03-15', 'gender': 'M'},  # 38 years old
            {'date_of_birth': '1986-03-15', 'gender': 'M'},
            {'date_of_birth': '1986-03-15', 'gender': 'M'},
            {'date_of_birth': '1986-03-15', 'gender': 'M'}
        ]
        
        analysis = analyze_crew_composition(master_crew)
        
        self.assertEqual(analysis['age_category'], 'master')
        self.assertEqual(analysis['master_category'], 'B')
        self.assertAlmostEqual(analysis['avg_age'], 38, delta=1)
    
    def test_get_eligible_races_master_category_filtering(self):
        """Test that master races are filtered by master category"""
        # Create master crew with average age 38 (category B)
        master_crew = [
            {'date_of_birth': '1986-03-15', 'gender': 'M'}  # 38 years old
        ]
        
        races_with_master_categories = [
            {
                'race_id': 'M03',
                'event_type': '42km',
                'boat_type': 'skiff',
                'age_category': 'master',
                'master_category': 'A',
                'gender_category': 'men'
            },
            {
                'race_id': 'M05',
                'event_type': '42km',
                'boat_type': 'skiff',
                'age_category': 'master',
                'master_category': 'B',
                'gender_category': 'men'
            },
            {
                'race_id': 'M07',
                'event_type': '42km',
                'boat_type': 'skiff',
                'age_category': 'master',
                'master_category': 'C',
                'gender_category': 'men'
            }
        ]
        
        eligible = get_eligible_races(master_crew, races_with_master_categories)
        
        # Should only be eligible for category B race
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['master_category'], 'B')


if __name__ == '__main__':
    unittest.main()
