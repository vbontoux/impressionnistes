"""
Integration tests for rental request pricing calculation
Feature: boat-rental-refactoring, Property 18: Rental Price Calculation
Validates: Requirements 5.4, 8.1-8.8
"""
import pytest
import sys
import os
from decimal import Decimal

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from pricing import calculate_rental_request_pricing


# Feature: boat-rental-refactoring, Property 18: Rental Price Calculation
# For any rental request, the calculated price should equal base_seat_price multiplied
# by the seat multiplier for that boat_type (skiff: 2.5, 4-: 4, 4+: 5, 4x-: 4, 4x+: 5, 8+: 9, 8x+: 9).


@pytest.mark.parametrize("boat_type,expected_multiplier", [
    ('skiff', Decimal('2.5')),
    ('4-', Decimal('4')),
    ('4+', Decimal('5')),
    ('4x-', Decimal('4')),
    ('4x+', Decimal('5')),
    ('8+', Decimal('9')),
    ('8x+', Decimal('9')),
])
def test_property_18_rental_price_calculation_default_config(boat_type, expected_multiplier):
    """
    Property 18: Rental Price Calculation (Default Config)
    
    Test that rental pricing is calculated correctly using default base_seat_price (20.00 EUR)
    and the correct multiplier for each boat type.
    """
    # Arrange
    default_base_price = Decimal('20.00')
    expected_price = default_base_price * expected_multiplier
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert pricing['rental_fee'] == expected_price, \
        f"Expected {expected_price} for {boat_type}, got {pricing['rental_fee']}"
    assert pricing['total'] == expected_price, \
        f"Total should equal rental_fee: {expected_price}"
    assert pricing['currency'] == 'EUR'
    assert 'breakdown' in pricing
    assert len(pricing['breakdown']) == 1
    assert pricing['breakdown'][0]['multiplier'] == float(expected_multiplier)


@pytest.mark.parametrize("boat_type,expected_multiplier", [
    ('skiff', Decimal('2.5')),
    ('4-', Decimal('4')),
    ('4+', Decimal('5')),
    ('4x-', Decimal('4')),
    ('4x+', Decimal('5')),
    ('8+', Decimal('9')),
    ('8x+', Decimal('9')),
])
def test_property_18_rental_price_calculation_custom_config(boat_type, expected_multiplier):
    """
    Property 18: Rental Price Calculation (Custom Config)
    
    Test that rental pricing is calculated correctly using custom base_seat_price
    and the correct multiplier for each boat type.
    """
    # Arrange
    custom_base_price = Decimal('25.00')
    pricing_config = {
        'base_seat_price': custom_base_price
    }
    expected_price = custom_base_price * expected_multiplier
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type, pricing_config)
    
    # Assert
    assert pricing['rental_fee'] == expected_price, \
        f"Expected {expected_price} for {boat_type}, got {pricing['rental_fee']}"
    assert pricing['total'] == expected_price, \
        f"Total should equal rental_fee: {expected_price}"
    assert pricing['currency'] == 'EUR'


@pytest.mark.parametrize("base_price", [
    Decimal('15.00'),
    Decimal('20.00'),
    Decimal('25.00'),
    Decimal('30.00'),
    Decimal('50.00'),
])
def test_property_18_pricing_scales_with_base_price(base_price):
    """
    Property 18: Rental Price Calculation - Scaling
    
    Test that rental pricing scales correctly with different base_seat_price values.
    """
    # Arrange
    boat_type = 'skiff'
    multiplier = Decimal('2.5')
    pricing_config = {'base_seat_price': base_price}
    expected_price = base_price * multiplier
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type, pricing_config)
    
    # Assert
    assert pricing['rental_fee'] == expected_price, \
        f"Expected {expected_price}, got {pricing['rental_fee']}"
    assert pricing['total'] == expected_price


def test_property_18_invalid_boat_type():
    """
    Property 18: Rental Price Calculation - Invalid Boat Type
    
    Test that invalid boat types return zero pricing with an error.
    """
    # Arrange
    invalid_boat_type = 'invalid-boat'
    
    # Act
    pricing = calculate_rental_request_pricing(invalid_boat_type)
    
    # Assert
    assert pricing['rental_fee'] == Decimal('0')
    assert pricing['total'] == Decimal('0')
    assert 'error' in pricing
    assert 'Invalid boat type' in pricing['error']


def test_property_18_skiff_specific_calculation():
    """
    Property 18: Rental Price Calculation - Skiff Specific
    
    Test the specific calculation for skiff (2.5x multiplier).
    Validates Requirement 8.1.
    """
    # Arrange
    boat_type = 'skiff'
    base_price = Decimal('20.00')
    expected_price = base_price * Decimal('2.5')  # 50.00
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert pricing['rental_fee'] == expected_price
    assert pricing['rental_fee'] == Decimal('50.00')


def test_property_18_four_minus_calculation():
    """
    Property 18: Rental Price Calculation - 4- Specific
    
    Test the specific calculation for 4- (4x multiplier).
    Validates Requirement 8.2.
    """
    # Arrange
    boat_type = '4-'
    base_price = Decimal('20.00')
    expected_price = base_price * Decimal('4')  # 80.00
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert pricing['rental_fee'] == expected_price
    assert pricing['rental_fee'] == Decimal('80.00')


def test_property_18_four_plus_calculation():
    """
    Property 18: Rental Price Calculation - 4+ Specific
    
    Test the specific calculation for 4+ (5x multiplier).
    Validates Requirement 8.3.
    """
    # Arrange
    boat_type = '4+'
    base_price = Decimal('20.00')
    expected_price = base_price * Decimal('5')  # 100.00
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert pricing['rental_fee'] == expected_price
    assert pricing['rental_fee'] == Decimal('100.00')


def test_property_18_eight_plus_calculation():
    """
    Property 18: Rental Price Calculation - 8+ Specific
    
    Test the specific calculation for 8+ (9x multiplier).
    Validates Requirement 8.6.
    """
    # Arrange
    boat_type = '8+'
    base_price = Decimal('20.00')
    expected_price = base_price * Decimal('9')  # 180.00
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert pricing['rental_fee'] == expected_price
    assert pricing['rental_fee'] == Decimal('180.00')


def test_property_18_pricing_breakdown_structure():
    """
    Property 18: Rental Price Calculation - Breakdown Structure
    
    Test that the pricing breakdown contains all required information.
    """
    # Arrange
    boat_type = '4+'
    
    # Act
    pricing = calculate_rental_request_pricing(boat_type)
    
    # Assert
    assert 'breakdown' in pricing
    assert len(pricing['breakdown']) == 1
    
    breakdown_item = pricing['breakdown'][0]
    assert 'item' in breakdown_item
    assert 'unit_price' in breakdown_item
    assert 'multiplier' in breakdown_item
    assert 'amount' in breakdown_item
    assert boat_type in breakdown_item['item']
    assert breakdown_item['amount'] == pricing['rental_fee']
