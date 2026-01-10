/**
 * Payment Store
 * Manages payment state and boat selection for payment
 */
import { defineStore } from 'pinia'
import boatService from '../services/boatService'
import { getErrorMessage } from '../services/apiClient'

export const usePaymentStore = defineStore('payment', {
  state: () => ({
    boatsReadyForPayment: [],
    selectedBoatIds: [],
    loading: false,
    error: null,
    paymentIntent: null,
    paymentStatus: null
  }),

  getters: {
    /**
     * Get boats that are selected for payment
     */
    selectedBoats: (state) => {
      return state.boatsReadyForPayment.filter(boat =>
        state.selectedBoatIds.includes(boat.boat_registration_id)
      )
    },

    /**
     * Calculate total amount for selected boats
     */
    totalAmount: (state) => {
      // Calculate boat registration fees
      return state.boatsReadyForPayment
        .filter(boat => state.selectedBoatIds.includes(boat.boat_registration_id))
        .reduce((sum, boat) => {
          const pricing = boat.pricing
          if (pricing && pricing.total) {
            return sum + parseFloat(pricing.total)
          }
          return sum
        }, 0)
    },

    /**
     * Check if any boats are selected
     */
    hasSelection: (state) => {
      return state.selectedBoatIds.length > 0
    }
  },

  actions: {
    /**
     * Fetch boats that are ready for payment (status: complete)
     */
    async fetchBoatsReadyForPayment() {
      try {
        const response = await boatService.getBoatRegistrations()
        const allBoats = response.data.boat_registrations || []

        // Filter boats with status 'complete' (ready for payment)
        // Exclude 'free' boats (RCPM-only boats that don't need payment)
        this.boatsReadyForPayment = allBoats.filter(
          boat => boat.registration_status === 'complete'
        )

        console.log(`Found ${this.boatsReadyForPayment.length} boats ready for payment`)
      } catch (error) {
        this.error = getErrorMessage(error)
        console.error('Failed to fetch boats for payment:', error)
        throw error
      }
    },

    /**
     * Fetch boats ready for payment
     */
    async fetchAllForPayment() {
      this.loading = true
      this.error = null

      try {
        await this.fetchBoatsReadyForPayment()
      } catch (error) {
        // Errors are already handled in individual fetch methods
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Set selected boat IDs
     */
    setSelectedBoats(boatIds) {
      this.selectedBoatIds = boatIds
    },

    /**
     * Clear selection
     */
    clearSelection() {
      this.selectedBoatIds = []
    },

    /**
     * Create payment intent (placeholder for Stripe integration)
     */
    async createPaymentIntent() {
      if (!this.hasSelection) {
        throw new Error('No boats selected for payment')
      }

      this.loading = true
      this.error = null

      try {
        // TODO: Call backend to create Stripe payment intent
        // const response = await paymentService.createPaymentIntent({
        //   boat_registration_ids: this.selectedBoatIds
        // })
        // this.paymentIntent = response.data

        console.log('Creating payment intent for boats:', this.selectedBoatIds)
        console.log('Total amount:', this.totalAmount)

        // Placeholder
        throw new Error('Payment integration not yet implemented')
      } catch (error) {
        this.error = getErrorMessage(error)
        console.error('Failed to create payment intent:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Confirm payment (placeholder for Stripe integration)
     */
    async confirmPayment(paymentIntentId) {
      this.loading = true
      this.error = null

      try {
        // TODO: Handle payment confirmation
        // const response = await paymentService.confirmPayment(paymentIntentId)
        // this.paymentStatus = 'succeeded'

        console.log('Confirming payment:', paymentIntentId)

        // Placeholder
        throw new Error('Payment confirmation not yet implemented')
      } catch (error) {
        this.error = getErrorMessage(error)
        this.paymentStatus = 'failed'
        console.error('Failed to confirm payment:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null
    },

    /**
     * Reset payment state
     */
    reset() {
      this.selectedBoatIds = []
      this.paymentIntent = null
      this.paymentStatus = null
      this.error = null
    }
  }
})
