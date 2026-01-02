"""
Boat Registration Utilities
Helper functions for boat registration management and validation
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_required_seats_for_boat_type(boat_type: str) -> List[Dict[str, Any]]:
    """
    Get the required seat structure for a given boat type
    
    Args:
        boat_type: Type of boat (skiff, 4-, 4+, 8+)
    
    Returns:
        List of seat dictionaries with position and type
    """
    seat_structures = {
        'skiff': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        '4-': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ],
        '4+': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        '8+': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'rower', 'crew_member_id': None},
            {'position': 6, 'type': 'rower', 'crew_member_id': None},
            {'position': 7, 'type': 'rower', 'crew_member_id': None},
            {'position': 8, 'type': 'rower', 'crew_member_id': None},
            {'position': 9, 'type': 'cox', 'crew_member_id': None}
        ]
    }
    
    return seat_structures.get(boat_type, [])


def validate_boat_type_for_event(event_type: str, boat_type: str) -> bool:
    """
    Validate that a boat type is allowed for a given event
    
    Args:
        event_type: Event type (21km or 42km)
        boat_type: Boat type (skiff, 4-, 4+, 8+)
    
    Returns:
        True if valid combination
    """
    valid_combinations = {
        '42km': ['skiff'],
        '21km': ['4-', '4+', '8+']
    }
    
    return boat_type in valid_combinations.get(event_type, [])


def is_registration_complete(boat_registration: Dict[str, Any]) -> bool:
    """
    Check if a boat registration is complete
    
    A registration is complete when:
    - All seats have crew members assigned
    - A race has been selected
    
    Args:
        boat_registration: Boat registration dictionary
    
    Returns:
        True if registration is complete
    """
    # Check if race is selected
    if not boat_registration.get('race_id'):
        return False
    
    # Check if all seats are filled
    seats = boat_registration.get('seats', [])
    for seat in seats:
        if not seat.get('crew_member_id'):
            return False
    
    return True


def detect_multi_club_crew(crew_members: List[Dict[str, Any]]) -> bool:
    """
    Detect if a crew contains members from multiple clubs
    
    Args:
        crew_members: List of crew member objects with club_affiliation
    
    Returns:
        True if crew has members from multiple clubs
    """
    if not crew_members:
        return False
    
    clubs = set()
    for member in crew_members:
        club = member.get('club_affiliation', '').upper()
        if club:
            clubs.add(club)
    
    return len(clubs) > 1


def calculate_boat_club_info(
    crew_members: List[Dict[str, Any]], 
    team_manager_club: str
) -> Dict[str, Any]:
    """
    Calculate boat club display and club list from crew members (Option A)
    
    This function determines the appropriate club display for a boat, always
    showing the team manager's club first with additional context about crew
    composition. The format is:
    - "{team_manager_club}" - all crew from team manager's club (or no crew)
    - "{team_manager_club} (Multi-Club)" - crew from multiple clubs
    - "{team_manager_club} ({crew_club})" - all crew from one different club
    
    Args:
        crew_members: List of assigned crew member objects with club_affiliation
        team_manager_club: Team manager's club affiliation (always shown)
    
    Returns:
        Dictionary with:
        - boat_club_display: str (formatted club display)
        - club_list: List[str] (unique clubs, sorted alphabetically)
    
    Examples:
        >>> calculate_boat_club_info([{'club_affiliation': 'RCPM'}], 'RCPM')
        {'boat_club_display': 'RCPM', 'club_list': ['RCPM']}
        
        >>> calculate_boat_club_info([
        ...     {'club_affiliation': 'RCPM'},
        ...     {'club_affiliation': 'Club Elite'}
        ... ], 'RCPM')
        {'boat_club_display': 'RCPM (Multi-Club)', 'club_list': ['Club Elite', 'RCPM']}
        
        >>> calculate_boat_club_info([{'club_affiliation': 'Club Elite'}], 'RCPM')
        {'boat_club_display': 'RCPM (Club Elite)', 'club_list': ['Club Elite']}
        
        >>> calculate_boat_club_info([], 'RCPM')
        {'boat_club_display': 'RCPM', 'club_list': ['RCPM']}
    """
    # Normalize team manager's club
    team_manager_club_clean = team_manager_club.strip() if team_manager_club else ''
    team_manager_club_normalized = team_manager_club_clean.upper() if team_manager_club_clean else ''
    
    # Extract club affiliations from crew members
    # Keep track of both normalized (for comparison) and original (for display)
    club_map = {}  # normalized -> original
    
    for member in crew_members:
        club_affiliation = member.get('club_affiliation')
        # Handle None and empty strings
        if club_affiliation is None:
            continue
        club_original = club_affiliation.strip()
        if club_original:  # Exclude empty or null clubs
            club_normalized = club_original.upper()
            # Keep the first occurrence's original case
            if club_normalized not in club_map:
                club_map[club_normalized] = club_original
    
    # Build club_list (sorted alphabetically, case-insensitive)
    club_list = sorted(club_map.values(), key=lambda x: x.upper()) if club_map else []
    
    # If no crew clubs, include team manager's club in list
    if not club_list and team_manager_club_clean:
        club_list = [team_manager_club_clean]
    
    # Determine boat_club_display based on crew composition
    if len(club_map) == 0:
        # No crew members with clubs, use team manager's club
        boat_club_display = team_manager_club_clean
    elif len(club_map) == 1:
        # Single club - check if it matches team manager's club
        crew_club_normalized = list(club_map.keys())[0]
        crew_club_original = list(club_map.values())[0]
        
        if crew_club_normalized == team_manager_club_normalized:
            # All crew from team manager's club
            boat_club_display = team_manager_club_clean
        else:
            # All crew from a different single club
            boat_club_display = f"{team_manager_club_clean} ({crew_club_original})"
    else:
        # Multiple clubs
        boat_club_display = f"{team_manager_club_clean} (Multi-Club)"
    
    return {
        'boat_club_display': boat_club_display,
        'club_list': club_list
    }


def get_assigned_crew_members(seats: List[Dict[str, Any]], all_crew_members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get the crew member objects for all assigned seats
    
    Args:
        seats: List of seat dictionaries with crew_member_id and type
        all_crew_members: List of all available crew member objects
    
    Returns:
        List of crew member objects assigned to seats, with seat_type added
    """
    assigned_members = []
    crew_member_map = {member['crew_member_id']: member for member in all_crew_members}
    
    for seat in seats:
        crew_member_id = seat.get('crew_member_id')
        if crew_member_id and crew_member_id in crew_member_map:
            member = crew_member_map[crew_member_id].copy()
            # Add seat type (rower or cox) to the member object
            member['seat_type'] = seat.get('type', 'rower')
            assigned_members.append(member)
    
    return assigned_members


def validate_seat_assignment(
    boat_registration: Dict[str, Any],
    crew_member_id: str,
    position: int,
    all_boat_registrations: List[Dict[str, Any]],
    crew_member: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Validate that a crew member can be assigned to a seat
    
    Checks:
    - Crew member is not already assigned to another boat
    - Position is valid for the boat type
    - J14 rowers (14-15 years old) can only be coxswains
    
    Args:
        boat_registration: Current boat registration
        crew_member_id: ID of crew member to assign
        position: Seat position (1-9)
        all_boat_registrations: List of all boat registrations for this team
        crew_member: Optional crew member data (to avoid extra DB lookup)
    
    Returns:
        Dictionary with 'valid' boolean and 'reason' string
    """
    # Check if crew member is already assigned to another boat
    for other_boat in all_boat_registrations:
        # Skip the current boat registration
        if other_boat.get('boat_registration_id') == boat_registration.get('boat_registration_id'):
            continue
        
        # Check if crew member is assigned to any seat in this boat
        for seat in other_boat.get('seats', []):
            if seat.get('crew_member_id') == crew_member_id:
                boat_type = other_boat.get('boat_type', 'unknown')
                event_type = other_boat.get('event_type', 'unknown')
                return {
                    'valid': False,
                    'reason': f"This crew member is already assigned to another boat ({event_type} {boat_type})"
                }
    
    # Check if position is valid for boat type
    boat_type = boat_registration.get('boat_type')
    required_seats = get_required_seats_for_boat_type(boat_type)
    
    valid_positions = [seat['position'] for seat in required_seats]
    if position not in valid_positions:
        return {
            'valid': False,
            'reason': f"Position {position} is not valid for boat type {boat_type}"
        }
    
    # Check J14 restriction: J14 rowers can only be coxswains
    if crew_member:
        from race_eligibility import calculate_age
        from datetime import datetime
        
        # Get crew member's age
        dob_str = crew_member.get('date_of_birth')
        if dob_str:
            try:
                # Calculate the age the person will reach during the current year
                birth_date = datetime.strptime(dob_str[:10], '%Y-%m-%d').date()
                current_year = datetime.now().year
                age_this_year = current_year - birth_date.year
                
                # Find the seat type for this position
                seat_type = None
                for seat in required_seats:
                    if seat['position'] == position:
                        seat_type = seat['type']
                        break
                
                # J14 (14 years old) can only be coxswains, not rowers
                # Note: 15-year-olds compete in J16 races and can row
                if age_this_year == 14 and seat_type == 'rower':
                    return {
                        'valid': False,
                        'reason': 'J14 rowers (14 years old) can only be assigned as coxswains, not as rowers'
                    }
            except (ValueError, AttributeError) as e:
                # If date parsing fails, log but don't block assignment
                logger = logging.getLogger()
                logger.warning(f"Could not parse date of birth for J14 validation: {e}")
    
    return {
        'valid': True,
        'reason': 'Seat assignment is valid'
    }


def is_all_rcpm_crew(crew_members: List[Dict[str, Any]]) -> bool:
    """
    Check if all crew members are RCPM members
    
    Args:
        crew_members: List of crew member objects
    
    Returns:
        True if all crew members are RCPM members
    """
    if not crew_members:
        return False
    
    for member in crew_members:
        if not member.get('is_rcpm_member', False):
            return False
    
    return True


def calculate_registration_status(boat_registration: Dict[str, Any], assigned_crew_members: List[Dict[str, Any]] = None) -> str:
    """
    Calculate the registration status based on completion, payment, and crew composition
    
    Args:
        boat_registration: Boat registration dictionary
        assigned_crew_members: Optional list of assigned crew member objects
    
    Returns:
        Status string: 'incomplete', 'complete', 'free', or 'paid'
    """
    # If already marked as paid, keep that status
    if boat_registration.get('registration_status') == 'paid':
        return 'paid'
    
    # Check if registration is complete
    if is_registration_complete(boat_registration):
        # If all crew members are RCPM, the boat is free
        if assigned_crew_members and is_all_rcpm_crew(assigned_crew_members):
            return 'free'
        return 'complete'
    
    return 'incomplete'


def get_coxswain_substitutes(
    boat_registration: Dict[str, Any],
    all_crew_members: List[Dict[str, Any]],
    selected_race: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get list of crew members who can substitute as coxswain
    while maintaining race eligibility
    
    Args:
        boat_registration: Current boat registration with assigned crew
        all_crew_members: List of all available crew members
        selected_race: The selected race for this boat
    
    Returns:
        List of crew member objects who can substitute as cox
    """
    from race_eligibility import analyze_crew_composition, validate_race_selection
    
    # Get currently assigned crew members
    assigned_members = get_assigned_crew_members(
        boat_registration.get('seats', []),
        all_crew_members
    )
    
    # Find the coxswain seat
    cox_seat = None
    for seat in boat_registration.get('seats', []):
        if seat.get('type') == 'cox':
            cox_seat = seat
            break
    
    if not cox_seat:
        return []  # No coxswain seat in this boat
    
    current_cox_id = cox_seat.get('crew_member_id')
    
    # Get rowers (non-cox crew members)
    rowers = [m for m in assigned_members if m.get('crew_member_id') != current_cox_id]
    
    # Test each available crew member as potential cox substitute
    eligible_substitutes = []
    
    for potential_cox in all_crew_members:
        # Skip if already assigned as rower
        if any(r.get('crew_member_id') == potential_cox.get('crew_member_id') for r in rowers):
            continue
        
        # Test crew composition with this substitute
        test_crew = rowers + [potential_cox]
        
        # Validate race eligibility with this crew
        validation = validate_race_selection(test_crew, selected_race)
        
        if validation.get('valid'):
            eligible_substitutes.append(potential_cox)
    
    return eligible_substitutes
