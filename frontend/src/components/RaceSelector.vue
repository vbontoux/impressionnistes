<template>
  <div class="race-selector">
    <h3>{{ $t('boat.selectRace') }}</h3>

    <div v-if="!crewMembers || crewMembers.length === 0" class="info-message">
      {{ $t('boat.assignCrewFirst') }}
    </div>

    <div v-else-if="eligibleRaces.length === 0" class="warning-message">
      {{ $t('boat.noEligibleRaces') }}
      <p class="help-text">{{ $t('boat.checkCrewComposition') }}</p>
    </div>

    <div v-else class="race-list">
      <div class="crew-summary">
        <h4>{{ $t('boat.crewComposition') }}</h4>
        <p>{{ crewDescription }}</p>
      </div>

      <div class="races">
        <div
          v-for="race in eligibleRaces"
          :key="race.race_id"
          class="race-option"
          :class="{ 'race-selected': selectedRaceId === race.race_id }"
          @click="selectRace(race)"
        >
          <div class="race-header">
            <h5>{{ getRaceDisplay(race) }}</h5>
            <span v-if="selectedRaceId === race.race_id" class="selected-badge">
              {{ $t('boat.selected') }}
            </span>
          </div>
          <div class="race-details">
            <span class="race-detail">{{ $t('boat.distance') }}: {{ race.event_type }}</span>
            <span class="race-detail">{{ $t('boat.boatType') }}: {{ race.boat_type }}</span>
            <span class="race-detail">{{ $t('boat.gender') }}: {{ $t(`boat.${race.gender_category}`) }}</span>
            <span class="race-detail">
              {{ $t('boat.ageCategory') }}: {{ $t(`boat.${race.age_category}`) }}
              <span v-if="race.master_category" class="master-category-badge">{{ race.master_category }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { analyzeCrewComposition, getEligibleRaces, getCrewDescription, getRaceDisplay } from '../utils/raceEligibility'

export default {
  name: 'RaceSelector',
  props: {
    crewMembers: {
      type: Array,
      default: () => []
    },
    availableRaces: {
      type: Array,
      required: true
    },
    selectedRaceId: {
      type: String,
      default: null
    },
    boatType: {
      type: String,
      required: true
    },
    eventType: {
      type: String,
      required: true
    }
  },
  emits: ['update:selectedRaceId'],
  setup(props, { emit }) {
    const { t } = useI18n()

    const eligibleRaces = computed(() => {
      if (!props.crewMembers || props.crewMembers.length === 0) {
        return []
      }

      // Filter races by event type and boat type first
      const filteredRaces = props.availableRaces.filter(race => {
        return race.event_type === props.eventType && race.boat_type === props.boatType
      })

      // Then filter by crew eligibility
      return getEligibleRaces(props.crewMembers, filteredRaces)
    })

    const crewDescription = computed(() => {
      if (!props.crewMembers || props.crewMembers.length === 0) {
        return ''
      }
      const analysis = analyzeCrewComposition(props.crewMembers)
      return getCrewDescription(analysis)
    })

    const selectRace = (race) => {
      emit('update:selectedRaceId', race.race_id)
    }

    return {
      eligibleRaces,
      crewDescription,
      selectRace,
      getRaceDisplay
    }
  }
}
</script>

<style scoped>
.race-selector {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.info-message,
.warning-message {
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

.info-message {
  background-color: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
}

.warning-message {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.help-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.crew-summary {
  background-color: white;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.crew-summary h4 {
  margin: 0 0 0.5rem 0;
  color: #495057;
}

.races {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.race-option {
  background-color: white;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.race-option:hover {
  border-color: #007bff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.race-selected {
  border-color: #28a745;
  background-color: #f0fff4;
}

.race-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.race-header h5 {
  margin: 0;
  color: #212529;
}

.selected-badge {
  background-color: #28a745;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.race-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.race-detail {
  font-size: 0.875rem;
  color: #6c757d;
}

.master-category-badge {
  display: inline-block;
  background-color: #6c757d;
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  margin-left: 0.5rem;
  font-size: 0.75rem;
}
</style>
