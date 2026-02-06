<template>
  <div class="boat-detail">
    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="boat" class="boat-content">
      <!-- Error Message -->
      <MessageAlert
        v-if="error"
        type="error"
        :message="error"
        :dismissible="true"
        @dismiss="error = null"
      />
      <!-- Header -->
      <div class="header">
        <div>
          <BaseButton variant="secondary" size="small" @click="goBack" class="btn-back">
            ← {{ $t('common.back') }}
          </BaseButton>
          <h1>{{ $t('boat.crewComposition') }} - {{ boat.event_type }} - {{ boat.boat_type }}</h1>
          <p class="page-description">{{ $t('boat.crewCompositionDescription') }}</p>
        </div>
      </div>

      <!-- Boat Info -->
      <div class="section">
        <h2>{{ $t('boat.registrationDetails') }}</h2>
        <div class="registration-layout">
          <!-- Left column: Event and Boat Type -->
          <div class="registration-info">
            <div class="info-item">
              <span class="label">{{ $t('boat.eventType') }}&nbsp;:</span>
              <span>{{ boat.event_type }}</span>
            </div>
            <div class="info-item">
              <span class="label">{{ $t('boat.boatType') }}&nbsp;:</span>
              <span>{{ boat.boat_type }}</span>
            </div>
          </div>
          
          <!-- Right column: Eligible Boat Types Info -->
          <div class="boat-type-info">
            <div class="info-text">
              <strong>{{ $t('boat.eligibleBoatTypes') }}</strong>
              <p>{{ getBoatTypeExplanation(boat.boat_type) }}</p>
            </div>
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

      <!-- Boat Request Section -->
      <div class="section">
        <h2>{{ $t('boat.boatRequest.title') }}</h2>
        
        <FormGroup :help-text="$t('boat.boatRequest.helpText')">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="boat.boat_request_enabled"
              @change="handleBoatRequestToggle"
            />
            <span>{{ $t('boat.boatRequest.enableLabel') }}</span>
          </label>
        </FormGroup>
        
        <!-- Show these fields only when boat request is enabled -->
        <div v-if="boat.boat_request_enabled" class="boat-request-fields">
          <FormGroup
            :label="$t('boat.boatRequest.commentLabel')"
            input-id="boat_request_comment"
          >
            <textarea
              id="boat_request_comment"
              v-model="boat.boat_request_comment"
              :placeholder="$t('boat.boatRequest.commentPlaceholder')"
              maxlength="500"
              rows="4"
              class="form-textarea"
            ></textarea>
          </FormGroup>
          <span class="char-count">
            {{ boat.boat_request_comment?.length || 0 }} / 500
          </span>
          
          <FormGroup
            :label="$t('boat.boatRequest.assignedBoatLabel')"
            :help-text="$t('boat.boatRequest.assignedBoatHelp')"
          >
            <input
              type="text"
              :value="boat.assigned_boat_identifier || $t('boat.boatRequest.notAssigned')"
              disabled
              class="form-input read-only"
            />
          </FormGroup>
          
          <FormGroup
            v-if="boat.assigned_boat_comment"
            :label="$t('boat.boatRequest.assignedBoatCommentLabel')"
          >
            <div class="assigned-comment">
              {{ boat.assigned_boat_comment }}
            </div>
          </FormGroup>
        </div>
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
            <small>{{ $t('boat.flaggedAt') }}&nbsp;: {{ formatDate(issue.flagged_at) }}</small>
          </div>
        </div>
      </div>

      <!-- Bottom Action Buttons -->
      <div class="bottom-actions">
        <div class="button-group">
          <BaseButton variant="secondary" size="small" @click="goBack">
            {{ $t('common.cancel') }}
          </BaseButton>
          <BaseButton 
            variant="primary" 
            size="small" 
            :disabled="saving || !canSave"
            :loading="saving"
            @click="saveBoat"
          >
            {{ saving ? $t('common.saving') : $t('common.save') }}
          </BaseButton>
        </div>
        <p v-if="allSeatsFilled && !boat.race_id" class="save-hint">
          {{ $t('boat.selectRaceToSave') }}
        </p>
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
import BaseButton from '../components/base/BaseButton.vue'
import MessageAlert from '../components/composite/MessageAlert.vue'
import FormGroup from '../components/composite/FormGroup.vue'

export default {
  name: 'BoatDetail',
  components: {
    SeatAssignment,
    RaceSelector,
    BaseButton,
    MessageAlert,
    FormGroup
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
      
      // Build a map of crew_member_id to seat_type
      const seatTypeMap = {}
      boat.value.seats.forEach(seat => {
        if (seat.crew_member_id) {
          seatTypeMap[seat.crew_member_id] = seat.type
        }
      })
      
      const assignedIds = Object.keys(seatTypeMap)
      
      // Add seat_type to each crew member
      return crewStore.crewMembers
        .filter(member => assignedIds.includes(member.crew_member_id))
        .map(member => ({
          ...member,
          seat_type: seatTypeMap[member.crew_member_id]
        }))
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

    const handleBoatRequestToggle = () => {
      if (!boat.value.boat_request_enabled) {
        // Clear fields when disabling boat request
        boat.value.boat_request_comment = ''
        // Note: assigned_boat_identifier and assigned_boat_comment are read-only, backend will clear them
      }
    }

    // Check if all seats are filled
    const allSeatsFilled = computed(() => {
      if (!boat.value || !boat.value.seats) return false
      return boat.value.seats.every(seat => seat.crew_member_id)
    })

    // Check if save button should be disabled
    const canSave = computed(() => {
      if (!boat.value) return false
      // If all seats are filled, require a race to be selected
      if (allSeatsFilled.value && !boat.value.race_id) {
        return false
      }
      return true
    })

    const saveBoat = async () => {
      // Validate before saving
      if (!canSave.value) {
        error.value = t('boat.selectRaceRequired')
        return
      }

      saving.value = true
      error.value = null
      try {
        await boatStore.updateBoatRegistration(boat.value.boat_registration_id, {
          seats: boat.value.seats,
          race_id: boat.value.race_id,
          boat_request_enabled: boat.value.boat_request_enabled,
          boat_request_comment: boat.value.boat_request_comment
          // Don't send assigned_boat_identifier or assigned_boat_comment (read-only for team managers)
        })
        // Reload crew members to refresh assignments
        await crewStore.fetchCrewMembers()
        // Redirect to boats list after successful save
        router.push('/boats')
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

    const getBoatTypeExplanation = (boatType) => {
      const explanations = {
        '4-': t('boat.boatTypeExplanations.4-'),
        '4+': t('boat.boatTypeExplanations.4+'),
        '8+': t('boat.boatTypeExplanations.8+'),
        'skiff': t('boat.boatTypeExplanations.skiff'),
        '2-': t('boat.boatTypeExplanations.2-'),
        '2+': t('boat.boatTypeExplanations.2+')
      }
      return explanations[boatType] || ''
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
      allSeatsFilled,
      canSave,
      handleSeatsUpdate,
      handleRaceSelection,
      handleBoatRequestToggle,
      saveBoat,
      goBack,
      formatDate,
      getBoatTypeExplanation
    }
  }
}
</script>

<style scoped>
.boat-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-muted);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: var(--spacing-xxl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-border);
}

.header h1 {
  margin: var(--spacing-sm) 0;
}

.page-description {
  margin-top: var(--spacing-md);
  color: var(--color-secondary);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.btn-back {
  margin-bottom: var(--spacing-sm);
}

.section {
  background-color: white;
  border-radius: var(--card-border-radius);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--card-shadow);
}

.section h2 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--color-dark);
}

.registration-layout {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.registration-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--color-light);
  border-radius: var(--card-border-radius);
}

.info-item .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
}

.boat-type-info {
  padding: var(--spacing-lg);
  background-color: #e7f3ff;
  border-left: 4px solid var(--color-primary);
  border-radius: var(--card-border-radius);
}

/* Desktop: Two-column layout */
@media (min-width: 768px) {
  .registration-layout {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: var(--spacing-xl);
    align-items: start;
  }
}

.info-text strong {
  display: block;
  margin-bottom: var(--spacing-xs);
  color: var(--color-dark);
}

.info-text p {
  margin: 0;
  color: var(--color-dark);
  line-height: 1.5;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.issue-item {
  padding: var(--spacing-lg);
  background-color: var(--color-warning-bg, #fff3cd);
  border: var(--card-border-width) solid var(--color-warning-border, #ffeaa7);
  border-radius: var(--card-border-radius);
}

.issue-item.issue-resolved {
  background-color: var(--color-success-bg, #d4edda);
  border-color: var(--color-success-border, #c3e6cb);
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.resolved-badge {
  background-color: var(--color-success);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--badge-border-radius);
  font-size: var(--font-size-xs);
}

.issue-item p {
  margin: var(--spacing-sm) 0;
}

.issue-item small {
  color: var(--color-muted);
}

.bottom-actions {
  margin-top: var(--spacing-xxl);
  padding: var(--spacing-xl);
  background-color: var(--color-light);
  border-top: 2px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.button-group {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
}

.save-hint {
  color: var(--color-warning-text, #856404);
  background-color: var(--color-warning-bg, #fff3cd);
  border: var(--card-border-width) solid var(--color-warning-border, #ffeaa7);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--card-border-radius);
  margin: 0;
  font-size: var(--font-size-base);
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: var(--font-weight-medium);
}

.checkbox-label input[type="checkbox"] {
  margin-right: var(--spacing-sm);
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.checkbox-label span {
  user-select: none;
}

.boat-request-fields {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg);
  background-color: var(--color-light);
  border-radius: var(--card-border-radius);
}

.form-textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: var(--card-border-width) solid var(--color-border);
  border-radius: var(--card-border-radius);
  font-family: inherit;
  font-size: var(--font-size-base);
  resize: vertical;
}

.form-input {
  width: 100%;
  padding: var(--spacing-md);
  border: var(--card-border-width) solid var(--color-border);
  border-radius: var(--card-border-radius);
  font-size: var(--font-size-base);
}

.read-only {
  background-color: var(--color-light);
  cursor: not-allowed;
  color: var(--color-secondary);
}

.char-count {
  display: block;
  text-align: right;
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  margin-top: var(--spacing-xs);
}

.assigned-comment {
  padding: var(--spacing-md);
  background-color: var(--color-info-bg, #e7f3ff);
  border-left: calc(var(--card-border-width) * 4) solid var(--color-primary);
  border-radius: var(--card-border-radius);
  white-space: pre-wrap;
  font-size: var(--font-size-base);
  color: var(--color-dark);
}
</style>
