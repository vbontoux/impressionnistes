<template>
  <div class="seat-assignment">
    <h3>{{ $t('boat.seatAssignment') }}</h3>

    <div class="boat-visual">
      <div
        v-for="seat in seats"
        :key="seat.position"
        class="seat"
        :class="{ 'seat-filled': seat.crew_member_id, 'seat-cox': seat.type === 'cox' }"
      >
        <div class="seat-header">
          <span class="seat-position">{{ $t('boat.position') }} {{ seat.position }}{{ getSeatLabel(seat) }}</span>
          <span class="seat-type">{{ seat.type === 'cox' ? $t('boat.coxswain') : $t('boat.rower') }}</span>
        </div>

        <div class="seat-content">
          <select
            v-model="seat.crew_member_id"
            @change="onSeatChange(seat)"
            class="crew-select"
          >
            <option :value="null">{{ $t('boat.selectCrewMember') }}</option>
            <option
              v-for="member in availableCrewMembers(seat)"
              :key="member.crew_member_id"
              :value="member.crew_member_id"
              :data-category="getAgeCategory(member.date_of_birth)"
            >
              {{ member.first_name }} {{ member.last_name }} - {{ formatCategoryDisplay(member.date_of_birth) }} - {{ member.club_affiliation }}
            </option>
          </select>

          <button
            v-if="seat.crew_member_id"
            @click="clearSeat(seat)"
            class="btn-clear"
            type="button"
          >
            {{ $t('common.clear') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useCrewStore } from '../stores/crewStore'
import { useI18n } from 'vue-i18n'
import { calculateAge, getAgeCategory as getAgeCategoryUtil, getMasterCategory } from '../utils/raceEligibility'

export default {
  name: 'SeatAssignment',
  props: {
    seats: {
      type: Array,
      required: true
    },
    boatRegistrationId: {
      type: String,
      default: null
    }
  },
  emits: ['update:seats'],
  setup(props, { emit }) {
    const crewStore = useCrewStore()
    const { t } = useI18n()
    const error = ref(null)

    // Fetch crew members if not already loaded
    if (crewStore.crewMembers.length === 0) {
      crewStore.fetchCrewMembers()
    }

    const filledSeatsCount = computed(() => {
      return props.seats.filter(seat => seat.crew_member_id).length
    })

    const assignedCrewMemberIds = computed(() => {
      return props.seats
        .filter(seat => seat.crew_member_id)
        .map(seat => seat.crew_member_id)
    })

    const isMultiClubCrew = computed(() => {
      const assignedMembers = props.seats
        .filter(seat => seat.crew_member_id)
        .map(seat => getCrewMemberInfo(seat.crew_member_id))
        .filter(member => member)

      const clubs = new Set(assignedMembers.map(m => m.club_affiliation))
      return clubs.size > 1
    })

    const availableCrewMembers = (currentSeat) => {
      // Show all crew members except those already assigned to other seats or other boats
      return crewStore.crewMembers.filter(member => {
        // If this seat already has this member, include them
        if (currentSeat.crew_member_id === member.crew_member_id) {
          return true
        }
        // Exclude if assigned to another seat in this boat
        if (assignedCrewMemberIds.value.includes(member.crew_member_id)) {
          return false
        }
        // Exclude if assigned to another boat (unless it's this boat)
        if (member.assigned_boat_id && member.assigned_boat_id !== props.boatRegistrationId) {
          return false
        }
        
        // J14 rowers (14-15 years old) can only be coxswains, not rowers
        if (currentSeat.type === 'rower') {
          const age = calculateAge(member.date_of_birth)
          const ageCategory = getAgeCategoryUtil(age)
          if (ageCategory === 'j14') {
            return false
          }
        }
        
        return true
      })
    }

    const getCrewMemberInfo = (crewMemberId) => {
      if (!crewMemberId) return null
      return crewStore.crewMembers.find(m => m.crew_member_id === crewMemberId)
    }

    const onSeatChange = (seat) => {
      error.value = null
      
      // Check if the selected crew member is already assigned to another boat
      if (seat.crew_member_id) {
        const selectedMember = crewStore.crewMembers.find(m => m.crew_member_id === seat.crew_member_id)
        if (selectedMember?.assigned_boat_id && selectedMember.assigned_boat_id !== props.boatRegistrationId) {
          error.value = `${selectedMember.first_name} ${selectedMember.last_name} is already assigned to another boat`
        }
      }
      
      emit('update:seats', props.seats)
    }

    const clearSeat = (seat) => {
      seat.crew_member_id = null
      emit('update:seats', props.seats)
    }

    const getAgeCategory = (dateOfBirth) => {
      const age = calculateAge(dateOfBirth)
      return getAgeCategoryUtil(age)
    }

    const formatCategoryDisplay = (dateOfBirth) => {
      const age = calculateAge(dateOfBirth)
      const category = getAgeCategoryUtil(age)
      const categoryLabel = t(`boat.${category}`)
      
      if (category === 'master') {
        const masterLetter = getMasterCategory(age)
        return `${categoryLabel} ${masterLetter}`
      }
      
      return categoryLabel
    }

    // Get seat label (bow/stroke) for multi-rower boats
    const getSeatLabel = (seat) => {
      if (seat.type === 'cox') return '' // No label for coxswain
      
      const rowerSeats = props.seats.filter(s => s.type === 'rower')
      if (rowerSeats.length <= 1) return '' // No label for single rower (skiff)
      
      const minPosition = Math.min(...rowerSeats.map(s => s.position))
      const maxPosition = Math.max(...rowerSeats.map(s => s.position))
      
      if (seat.position === minPosition) {
        return ` (${t('boat.bow')})`
      } else if (seat.position === maxPosition) {
        return ` (${t('boat.stroke')})`
      }
      
      return ''
    }

    return {
      error,
      filledSeatsCount,
      isMultiClubCrew,
      availableCrewMembers,
      getCrewMemberInfo,
      onSeatChange,
      clearSeat,
      getAgeCategory,
      getSeatLabel,
      formatCategoryDisplay
    }
  }
}
</script>

<style scoped>
.seat-assignment {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.boat-visual {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1.5rem 0;
}

.seat {
  background-color: white;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  transition: border-color 0.2s;
}

.seat-filled {
  border-color: #28a745;
}

.seat-cox {
  background-color: #fff3cd;
}

.seat-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.seat-position {
  color: #495057;
}

.seat-type {
  color: #6c757d;
  font-size: 0.875rem;
}

.seat-content {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.crew-select {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.875rem;
}

.crew-select option[data-category="j14"] {
  background-color: #E3F2FD;
  color: #1976D2;
  font-weight: 600;
}

.crew-select option[data-category="j16"] {
  background-color: #E3F2FD;
  color: #1976D2;
  font-weight: 600;
}

.crew-select option[data-category="j18"] {
  background-color: #E8F5E9;
  color: #388E3C;
  font-weight: 600;
}

.crew-select option[data-category="senior"] {
  background-color: #FFF3E0;
  color: #F57C00;
  font-weight: 600;
}

.crew-select option[data-category="master"] {
  background-color: #F3E5F5;
  color: #7B1FA2;
  font-weight: 600;
}

.btn-clear {
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-clear:hover {
  background-color: #c82333;
}

.crew-info {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-top: 1rem;
}

.assignment-summary {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: white;
  border-radius: 4px;
}

.multi-club-warning {
  color: #856404;
  background-color: #fff3cd;
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}
</style>
