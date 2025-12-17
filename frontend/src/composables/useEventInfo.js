/**
 * Composable for fetching public event information
 * No authentication required - used for home page
 */
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export function useEventInfo() {
  const eventInfo = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchEventInfo = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get(`${API_URL}/public/event-info`)
      eventInfo.value = response.data.data
      return eventInfo.value
    } catch (err) {
      console.error('Failed to fetch event info:', err)
      error.value = err.message || 'Failed to fetch event information'
      // Return null on error so component can use fallback dates
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    eventInfo,
    loading,
    error,
    fetchEventInfo
  }
}
