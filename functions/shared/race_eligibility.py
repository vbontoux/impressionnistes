"""
Race Eligibility Calculation Engine
Determines which races a crew is eligible for based on age and gender composition
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional


def calculate_age(date_of_birth: str, reference_date: Optional[date] = None) -> int:
    """
    Calculate age based on date of birth
    
    Args:
        date_of_birth: Date string in YYYY-MM-DD format
        reference_date: Reference date for age calculation (defaults to today)
    
    Returns:
        Age in years
    """
    if reference_date is None:
        reference_date = date.today()
    
    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
    age = reference_date.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if reference_date.month < birth_date.month or \
       (reference_date.month == birth_date.month and reference_date.day < birth_date.day):
        age -= 1
    
    return age


def get_age_category(age: int) -> str:
    """
    Determine age category based on age
    
    Args:
        age: Age in years
    
    Returns:
        Age category string
    """
    if age < 18:
        return "youth"
    elif age < 27:
        return "senior"
    else:
        return "master"


def analyze_crew_composition(crew_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze crew composition for race eligibility
    
    Args:
        crew_members: List of crew member objects with date_of_birth and gender
    
    Returns:
        Dictionary with crew composition analysis
    """
    if not crew_members:
        return {
            'crew_size': 0,
            'genders': [],
            'ages': [],
            'age_categories': [],
            'gender_category': None,
            'age_category': None,
            'eligible_boat_types': []
        }
    
    # Calculate ages and determine categories
    ages = []
    genders = []
    age_categories = []
    
    for member in crew_members:
        age = calculate_age(member['date_of_birth'])
        ages.append(age)
        genders.append(member['gender'])
        age_categories.append(get_age_category(age))
    
    # Determine gender category
    unique_genders = set(genders)
    if len(unique_genders) == 1:
        gender_category = "men" if genders[0] == "M" else "women"
    else:
        gender_category = "mixed"
    
    # Determine age category (most restrictive - if any master, then master)
    if "master" in age_categories:
        crew_age_category = "master"
    elif "senior" in age_categories:
        crew_age_category = "senior"
    else:
        crew_age_category = "youth"
    
    # Determine eligible boat types based on crew size
    crew_size = len(crew_members)
    eligible_boat_types = []
    
    if crew_size == 1:
        eligible_boat_types = ["skiff"]
    elif crew_size == 4:
        eligible_boat_types = ["4-"]
    elif crew_size == 5:
        eligible_boat_types = ["4+"]
    elif crew_size == 8 or crew_size == 9:
        eligible_boat_types = ["8+"]
    
    return {
        'crew_size': crew_size,
        'genders': genders,
        'ages': ages,
        'age_categories': age_categories,
        'gender_category': gender_category,
        'age_category': crew_age_category,
        'eligible_boat_types': eligible_boat_types,
        'min_age': min(ages) if ages else 0,
        'max_age': max(ages) if ages else 0,
        'avg_age': sum(ages) / len(ages) if ages else 0
    }


def get_eligible_races(crew_members: List[Dict[str, Any]], available_races: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get races that a crew is eligible for
    
    Args:
        crew_members: List of crew member objects
        available_races: List of available race definitions
    
    Returns:
        List of eligible race objects
    """
    crew_analysis = analyze_crew_composition(crew_members)
    
    if not crew_analysis['eligible_boat_types']:
        return []
    
    eligible_races = []
    
    for race in available_races:
        # Check boat type compatibility
        if race['boat_type'] not in crew_analysis['eligible_boat_types']:
            continue
        
        # Check gender category compatibility
        race_gender = race['gender_category']
        crew_gender = crew_analysis['gender_category']
        
        # Mixed races accept any gender composition
        # Gender-specific races only accept that gender or mixed crews
        if race_gender != "mixed" and race_gender != crew_gender and crew_gender != "mixed":
            continue
        
        # Check age category compatibility
        race_age = race['age_category']
        crew_age = crew_analysis['age_category']
        
        # Age category rules:
        # - Youth can only compete in youth races
        # - Senior can compete in senior or master races
        # - Master can compete in master races
        if race_age == "youth" and crew_age != "youth":
            continue
        if race_age == "senior" and crew_age not in ["senior", "master"]:
            continue
        if race_age == "master" and crew_age != "master":
            continue
        
        eligible_races.append(race)
    
    return eligible_races


def validate_race_selection(crew_members: List[Dict[str, Any]], selected_race: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a crew is eligible for a selected race
    
    Args:
        crew_members: List of crew member objects
        selected_race: Selected race object
    
    Returns:
        Dictionary with validation result and details
    """
    crew_analysis = analyze_crew_composition(crew_members)
    
    # Check crew size
    if not crew_analysis['eligible_boat_types']:
        return {
            'valid': False,
            'reason': f"Invalid crew size: {crew_analysis['crew_size']}. Must be 1, 4, 5, 8, or 9 members.",
            'crew_analysis': crew_analysis
        }
    
    # Check boat type
    if selected_race['boat_type'] not in crew_analysis['eligible_boat_types']:
        return {
            'valid': False,
            'reason': f"Boat type '{selected_race['boat_type']}' not compatible with crew size {crew_analysis['crew_size']}",
            'crew_analysis': crew_analysis
        }
    
    # Check gender category
    race_gender = selected_race['gender_category']
    crew_gender = crew_analysis['gender_category']
    
    if race_gender != "mixed" and race_gender != crew_gender and crew_gender != "mixed":
        return {
            'valid': False,
            'reason': f"Gender mismatch: Race requires '{race_gender}' but crew is '{crew_gender}'",
            'crew_analysis': crew_analysis
        }
    
    # Check age category
    race_age = selected_race['age_category']
    crew_age = crew_analysis['age_category']
    
    if race_age == "youth" and crew_age != "youth":
        return {
            'valid': False,
            'reason': f"Age category mismatch: Youth race requires all youth crew members",
            'crew_analysis': crew_analysis
        }
    if race_age == "senior" and crew_age not in ["senior", "master"]:
        return {
            'valid': False,
            'reason': f"Age category mismatch: Senior race not available for {crew_age} crew",
            'crew_analysis': crew_analysis
        }
    if race_age == "master" and crew_age != "master":
        return {
            'valid': False,
            'reason': f"Age category mismatch: Master race requires at least one master crew member",
            'crew_analysis': crew_analysis
        }
    
    return {
        'valid': True,
        'reason': 'Crew is eligible for this race',
        'crew_analysis': crew_analysis
    }


# Boat type requirements for reference
BOAT_TYPE_REQUIREMENTS = {
    'skiff': {
        'crew_size': 1,
        'description': 'Single sculler'
    },
    '4-': {
        'crew_size': 4,
        'description': 'Four without coxswain'
    },
    '4+': {
        'crew_size': 5,
        'description': 'Four with coxswain'
    },
    '8+': {
        'crew_size': [8, 9],  # 8 rowers + optional cox
        'description': 'Eight with coxswain'
    }
}
