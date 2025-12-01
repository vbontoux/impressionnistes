<template>
  <div class="boat-detail">
    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="boat" class="boat-content">
      <!-- Error Message -->
      <div v-if="error" class="error-message">
        <span>{{ error }}</span>
        <button @click="error = null" class="btn-close-error">×</button>
      </div>
      <!-- Header -->
      <div class="header">
        <div>
          <button @click="goBack" class="btn-back">← {{ $t('common.back') }}</button>
          <h1>{{ boat.event_type }} - {{ boat.boat_type }}</h1>
          <span class="status-badge" :class="`status-${boat.registration_status}`">
            {{ $t(`boat.status.${boat.registration_status}`) }}
          </span>
        </div>
      </div>

      <!-- Boat Info -->
      <div class="section">
        <h2>{{ $t('boat.boatInformation') }}</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">{{ $t('boat.eventType') }}:</span>
            <span>{{ boat.event_type }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ $t('boat.boatType') }}:</span>
            <span>{{ boat.boat_type }}</span>
          </div>
          <div class="info-item" v-if="boat.is_multi_club_crew || boat.registration_status === 'free'">
            <span class="multi-club-badge">{{ $t('boat.multiClub') }}</span>
          </div>
        </div>
      </div>

      <!-- Seat Assignment -->
      <div class="section">
        <SeatAssignment
          :seats="boat.seats"
          :boat-registration-id="boat.boat_registration_id"
          @update:seats="handleSeatsUpdate"
        />
      </div>

      <!-- Race Selection -->
      <div class="section" v-if="assignedCrewMembers.length > 0">
        <RaceSelector
          :crew-members="assignedCrewMembers"
          :available-races="availableRaces"
          :selected-race-id="boat.race_id"
          :boat-type="boat.boat_type"
          :event-type="boat.event_type"
          @update:selectedRaceId="handleRaceSelection"
        />
      </div>

      <!-- Flagged Issues -->
      <div v-if="boat.flagged_issues && boat.flagged_issues.length > 0" class="section">
        <h2>{{ $t('boat.flaggedIssues') }}</h2>
        <div class="issues-list">
          <div
            v-for="(issue, index) in boat.flagged_issues"
            :key="index"
            class="issue-item"
            :class="{ 'issue-resolved': issue.resolved }"
          >
            <div class="issue-header">
              <strong>{{ issue.issue_type }}</strong>
              <span v-if="issue.resolved" class="resolved-badge">{{ $t('boat.resolved') }}</span>
            </div>
            <p>{{ issue.description }}</p>
            <small>{{ $t('boat.flaggedAt') }}: {{ formatDate(issue.flagged_at) }}</small>
          </div>
        </div>
      </div>

      <!-- Bottom Save Button -->
      <div class="bottom-actions">
        <button @click="saveBoat" :disabled="saving" class="btn-primary btn-large">
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBoatStore } from '../stores/boatStore'
import { useCrewStore } from '../stores/crewStore'
import { useRaceStore } from '../stores/raceStore'
import { useI18n } from 'vue-i18n'
import SeatAssignment from '../components/SeatAssignment.vue'
import RaceSelector from '../components/RaceSelector.vue'

export default {
  name: 'BoatDetail',
  components: {
    SeatAssignment,
    RaceSelector
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const boatStore = useBoatStore()
    const crewStore = useCrewStore()
    const raceStore = useRaceStore()
    const { t } = useI18n()

    const loading = ref(true)
    const saving = ref(false)
    const error = ref(null)
    const boat = ref(null)
    
    // Get races from store
    const availableRaces = computed(() => raceStore.races)


    const assignedCrewMembers = computed(() => {
      if (!boat.value || !boat.value.seats) return []
      
      const assignedIds = boat.value.seats
        .filter(seat => seat.crew_member_id)
        .map(seat => seat.crew_member_id)
      
      return crewStore.crewMembers.filter(member => 
        assignedIds.includes(member.crew_member_id)
      )
    })

    const loadBoat = async () => {
      loading.value = true
      error.value = null
      try {
        const boatId = route.params.id
        await boatStore.fetchBoatRegistration(boatId)
        boat.value = boatStore.currentBoat
      } catch (err) {
        error.value = err.response?.data?.error?.message || t('boat.loadError')
      } finally {
        loading.value = false
      }
    }

    const handleSeatsUpdate = (updatedSeats) => {
      if (boat.value) {
        boat.value.seats = updatedSeats
        // Clear any previous errors when seats are updated
        error.value = null
      }
    }

    const handleRaceSelection = (raceId) => {
      if (boat.value) {
        boat.value.race_id = raceId
      }
    }

    const saveBoat = async () => {
      saving.value = true
      error.value = null
      try {
        await boatStore.updateBoatRegistration(boat.value.boat_registration_id, {
          seats: boat.value.seats,
          race_id: boat.value.race_id
        })
        // Reload to get updated status and refresh crew member assignments
        await crewStore.fetchCrewMembers()
        await loadBoat()
      } catch (err) {
        // Extract detailed error message
        const errorData = err.response?.data?.error
        if (errorData?.details) {
          // Format validation errors from details object
          const detailMessages = Object.entries(errorData.details)
            .map(([field, message]) => `${field}: ${message}`)
            .join(', ')
          error.value = detailMessages
        } else {
          error.value = errorData?.message || t('boat.saveError')
        }
      } finally {
        saving.value = false
      }
    }

    const goBack = () => {
      router.push('/boats')
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString()
    }

    // Watch for races being loaded
    watch(availableRaces, (newRaces) => {
      console.log('BoatDetail - Available races changed:', newRaces.length)
      if (newRaces.length > 0) {
        console.log('BoatDetail - First race:', newRaces[0])
        console.log('BoatDetail - 42km skiff races:', newRaces.filter(r => r.event_type === '42km' && r.boat_type === 'skiff').length)
      }
    }, { immediate: true })

    onMounted(async () => {
      // Load crew members if not already loaded
      if (crewStore.crewMembers.length === 0) {
        await crewStore.fetchCrewMembers()
      }
      // Load races if not already loaded
      if (raceStore.races.length === 0) {
        await raceStore.fetchRaces()
      }
      console.log('BoatDetail - After fetchRaces, race count:', raceStore.races.length)
      await loadBoat()
    })

    return {
      loading,
      saving,
      error,
      boat,
      availableRaces,
      assignedCrewMembers,
      handleSeatsUpdate,
      handleRaceSelection,
      saveBoat,
      goBack,
      formatDate
    }
  }
}
</script>

<style scoped>
.boat-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-bottom: 1rem;
}

.btn-close-error {
  background: none;
  border: none;
  color: #c33;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  margin-left: 1rem;
  line-height: 1;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-error:hover {
  color: #a00;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #dee2e6;
}

.header h1 {
  margin: 0.5rem 0;
}

.btn-back {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
  margin-bottom: 0.5rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  margin-left: 1rem;
}

.status-badge.status-incomplete {
  background-color: #ffc107;
  color: #000;
}

.status-badge.status-complete {
  background-color: #28a745;
  color: white;
}

.status-badge.status-paid {
  background-color: #007bff;
  color: white;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section h2 {
  margin: 0 0 1rem 0;
  color: #212529;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.info-item .label {
  font-weight: 500;
  color: #666;
}

.multi-club-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: #ffc107;
  color: #000;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.issue-item {
  padding: 1rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
}

.issue-item.issue-resolved {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.resolved-badge {
  background-color: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.issue-item p {
  margin: 0.5rem 0;
}

.issue-item small {
  color: #666;
}

.bottom-actions {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-top: 2px solid #e0e0e0;
  display: flex;
  justify-content: center;
}

.btn-large {
  padding: 1rem 3rem;
  font-size: 1.1rem;
}
</style>
