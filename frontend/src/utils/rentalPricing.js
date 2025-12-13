/**
 * Utility functions for calculating rental boat pricing
 * Centralized to ensure consistency across the application
 */

/**
 * Calculate rental price based on boat type
 * @param {string} boatType - The type of boat (skiff, 4-, 4+, etc.)
 * @param {number} baseSeatPrice - The base seat price from configuration
 * @returns {number} The rental price
 */
export function calculateRentalPrice(boatType, baseSeatPrice) {
  // Skiff pricing: 2.5x Base_Seat_Price
  if (boatType === 'skiff') {
    return baseSeatPrice * 2.5
  }
  
  // Crew boat pricing: Base_Seat_Price per seat
  const seatCounts = {
    '4-': 4,
    '4+': 5,  // 4 rowers + 1 cox
    '4x-': 4,
    '4x+': 5,  // 4 rowers + 1 cox
    '8+': 9,  // 8 rowers + 1 cox
    '8x+': 9   // 8 rowers + 1 cox
  }
  
  const seats = seatCounts[boatType] || 1
  return baseSeatPrice * seats
}

/**
 * Format rental pricing for display
 * @param {Object} rental - The rental boat object
 * @param {number} baseSeatPrice - The base seat price from configuration
 * @returns {Object} Formatted pricing object
 */
export function formatRentalPricing(rental, baseSeatPrice) {
  const rentalFee = calculateRentalPrice(rental.boat_type, baseSeatPrice)
  
  return {
    rental_fee: rentalFee,
    total: rentalFee,
    currency: 'EUR'
  }
}
