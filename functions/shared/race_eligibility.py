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
        Age category string (j16, j18, senior, master)
    """
    if age <= 16:
        return "j16"
    elif age <= 18:
        return "j18"
    elif age < 27:
        return "senior"
    else:
        return "master"


def get_master_category(avg_age: float) -> str:
    """
    Determine master category letter based on average age of crew
    
    Args:
        avg_age: Average age of crew members
    
    Returns:
        Master category letter (A, B, C, D, E, F, G, H)
    """
    if avg_age < 36:
        return "A"  # 27-35
    elif avg_age < 43:
        return "B"  # 36-42
    elif avg_age < 50:
        return "C"  # 43-49
    elif avg_age < 55:
        return "D"  # 50-54
    elif avg_age < 60:
        return "E"  # 55-59
    elif avg_age < 65:
        return "F"  # 60-64
    elif avg_age < 70:
        return "G"  # 65-69
    else:
        return "H"  # 70+


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
    
    # Determine age category (most restrictive)
    # Priority: master > senior > j18 > j16
    if "master" in age_categories:
        crew_age_category = "master"
    elif "senior" in age_categories:
        crew_age_category = "senior"
    elif "j18" in age_categories:
        crew_age_category = "j18"
    else:
        crew_age_category = "j16"
    
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
    
    avg_age = sum(ages) / len(ages) if ages else 0
    master_category = get_master_category(avg_age) if crew_age_category == "master" else None
    
    return {
        'crew_size': crew_size,
        'genders': genders,
        'ages': ages,
        'age_categories': age_categories,
        'gender_category': gender_category,
        'age_category': crew_age_category,
        'master_category': master_category,
        'eligible_boat_types': eligible_boat_types,
        'min_age': min(ages) if ages else 0,
        'max_age': max(ages) if ages else 0,
        'avg_age': avg_age
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
        # - J16 can only compete in j16 races
        # - J18 can only compete in j18 races
        # - Senior can compete in senior races
        # - Master can compete in master races with matching category
        if race_age == "j16" and crew_age != "j16":
            continue
        if race_age == "j18" and crew_age != "j18":
            continue
        if race_age == "senior" and crew_age != "senior":
            continue
        if race_age == "master" and crew_age != "master":
            continue
        
        # For master races, check if the race has a specific master category
        if crew_age == "master" and 'master_category' in race:
            crew_master_cat = crew_analysis.get('master_category')
            race_master_cat = race['master_category']
            if crew_master_cat != race_master_cat:
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
    
    if race_age == "j16" and crew_age != "j16":
        return {
            'valid': False,
            'reason': f"Age category mismatch: J16 race requires crew members aged 15-16",
            'crew_analysis': crew_analysis
        }
    if race_age == "j18" and crew_age != "j18":
        return {
            'valid': False,
            'reason': f"Age category mismatch: J18 race requires crew members aged 17-18",
            'crew_analysis': crew_analysis
        }
    if race_age == "senior" and crew_age != "senior":
        return {
            'valid': False,
            'reason': f"Age category mismatch: Senior race requires crew members aged 19-26",
            'crew_analysis': crew_analysis
        }
    if race_age == "master" and crew_age != "master":
        return {
            'valid': False,
            'reason': f"Age category mismatch: Master race requires crew members aged 27+",
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
