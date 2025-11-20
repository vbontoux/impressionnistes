  /**
 * Race Store
 * Manages race state using Pinia
 */
import { defineStore } from 'pinia'
import raceService from '../services/raceService'

export const useRaceStore = defineStore('race', {
  state: () => ({
    races: [],
    loading: false,
    error: null,
    lastFetched: null
  }),

  getters:
{
    /**
     * Get races by event type
     */
    getRacesByEventType: (state) => (eventType) => {
      return state.races.filter(race => race.event_type === eventType)
    },

    /**
     * Get races by boat type
     */
    getRacesByBoatType: (state) => (boatType) => {
      return state.races.filter(race => race.boat_type === boatType)
    },

    /**
     * Get races by event and boat type
     */
    getRacesByEventAndBoatType: (state) => (eventType, boatType) => {
      return state.races.filter(
        race => race.event_type === eventType && race.boat_type === boatType
      )
    },

    /**
     * Get race by ID
     */
    getRaceById: (state) => (raceId) => {
      return state.races.find(race => race.race_id === raceId)
    },

    /**
     * Get marathon races (42km)
     */
    marathonRaces: (state) => {
      return state.races.filter(race => race.event_type === '42km')
    },

    /**
     * Get semi-marathon races (21km)
     */
    semiMarathonRaces: (state) => {
      return state.races.filter(race => race.event_type === '21km')
    }
  },

  actions: {
    /**
     * Fetch all races from API
     * @param {boolean} force - Force refresh even if recently fetched
     */
    async fetchRaces(force = false) {
      // Don't refetch if we have data and it's recent (within 5 minutes)
      if (!force && this.races.length > 0 && this.lastFetched) {
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000
        if (this.lastFetched > fiveMinutesAgo) {
          console.log('Race store: Using cached races', this.races.length)
          return
        }
      }

      this.loading = true
      this.error = null

      try {
        console.log('Race store: Fetching races from API...')
        const response = await raceService.listRaces()
        console.log('Race store: API response:', response.data)
        // API returns {success: true, data: {races: [...]}}
        this.races = response.data.data?.races || response.data.races || []
        this.lastFetched = Date.now()
        console.log('Race store: Loaded', this.races.length, 'races')
      } catch (error) {
        console.error('Race store: Failed to fetch races:', error)
        console.error('Race store: Error details:', error.response?.data)
        this.error = error.response?.data?.error?.message || error.message || 'Failed to fetch races'
        // Don't throw - let the UI handle the empty state
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear error state
     */
    clearError() {
      this.error = null
    }
  }
})
