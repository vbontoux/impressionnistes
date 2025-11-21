import { defineStore } from 'pinia'
import boatService from '../services/boatService'
import { getErrorMessage } from '../services/apiClient'

export const useBoatStore = defineStore('boat', {
  state: () => ({
    boatRegistrations: [],
    currentBoat: null,
    loading: false,
    error: null
  }),

  getters: {
    getBoatById: (state) => (id) => {
      return state.boatRegistrations.find(boat => boat.boat_registration_id === id)
    },

    incompleteBoats: (state) => {
      return state.boatRegistrations.filter(boat => boat.registration_status === 'incomplete')
    },

    completeBoats: (state) => {
      return state.boatRegistrations.filter(boat => boat.registration_status === 'complete')
    },

    paidBoats: (state) => {
      return state.boatRegistrations.filter(boat => boat.registration_status === 'paid')
    }
  },

  actions: {
    async fetchBoatRegistrations() {
      this.loading = true
      this.error = null
      try {
        const response = await boatService.getBoatRegistrations()
        this.boatRegistrations = response.data.boat_registrations || []
      } catch (error) {
        this.error = getErrorMessage(error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchBoatRegistration(id) {
      this.loading = true
      this.error = null
      try {
        const response = await boatService.getBoatRegistration(id)
        this.currentBoat = response.data
        
        // Update in list if exists
        const index = this.boatRegistrations.findIndex(b => b.boat_registration_id === id)
        if (index !== -1) {
          this.boatRegistrations[index] = response.data
        }
      } catch (error) {
        this.error = getErrorMessage(error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async createBoatRegistration(boatData) {
      this.loading = true
      this.error = null
      try {
        const response = await boatService.createBoatRegistration(boatData)
        this.boatRegistrations.push(response.data)
        this.currentBoat = response.data
        return response.data
      } catch (error) {
        this.error = getErrorMessage(error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateBoatRegistration(id, updates) {
      this.loading = true
      this.error = null
      try {
        const response = await boatService.updateBoatRegistration(id, updates)
        
        // Update in list
        const index = this.boatRegistrations.findIndex(b => b.boat_registration_id === id)
        if (index !== -1) {
          this.boatRegistrations[index] = response.data
        }
        
        // Update current if it's the same boat
        if (this.currentBoat?.boat_registration_id === id) {
          this.currentBoat = response.data
        }
        
        // If seats were updated, refresh crew members to update their assignment status
        if (updates.seats) {
          const { useCrewStore } = await import('./crewStore')
          const crewStore = useCrewStore()
          await crewStore.fetchCrewMembers()
        }
        
        return response.data
      } catch (error) {
        this.error = getErrorMessage(error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteBoatRegistration(id) {
      this.loading = true
      this.error = null
      try {
        await boatService.deleteBoatRegistration(id)
        
        // Remove from list
        this.boatRegistrations = this.boatRegistrations.filter(b => b.boat_registration_id !== id)
        
        // Clear current if it's the same boat
        if (this.currentBoat?.boat_registration_id === id) {
          this.currentBoat = null
        }
        
        // Refresh crew members to update their assignment status
        const { useCrewStore } = await import('./crewStore')
        const crewStore = useCrewStore()
        await crewStore.fetchCrewMembers()
      } catch (error) {
        this.error = getErrorMessage(error)
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentBoat(boat) {
      this.currentBoat = boat
    },

    clearError() {
      this.error = null
    }
  }
})
