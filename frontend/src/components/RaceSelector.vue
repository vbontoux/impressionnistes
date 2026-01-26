<template>
  <div class="race-selector">
    <h3>{{ $t('boat.selectRace') }}</h3>

    <div v-if="!crewMembers || crewMembers.length === 0" class="info-message">
      {{ $t('boat.assignCrewFirst') }}
    </div>

    <div v-else-if="eligibleRaces.length === 0" class="warning-message">
      <h4>{{ $t('boat.noEligibleRaces') }}</h4>
      
      <!-- Simple reason why no races match -->
      <div v-if="noRacesReason" class="reason-text">
        <strong>{{ $t('boat.reason') }}:</strong> {{ noRacesReason }}
      </div>
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
            <h5>{{ getTranslatedRaceName(race) }}</h5>
            <span v-if="selectedRaceId === race.race_id" class="selected-badge">
              {{ $t('boat.selected') }}
            </span>
          </div>
          <div class="race-details">
            <span class="race-detail">{{ $t('boat.distance') }}&nbsp;: {{ race.event_type }}</span>
            <span class="race-detail">{{ $t('boat.boatType') }}&nbsp;: {{ race.boat_type }}</span>
            <span class="race-detail">{{ $t('boat.gender') }}&nbsp;: {{ $t(`boat.${race.gender_category}`) }}</span>
            <span class="race-detail">
              {{ $t('boat.ageCategory') }}&nbsp;: {{ $t(`boat.${race.age_category}`) }}
              <span v-if="race.master_category" class="master-category-badge">{{ race.master_category }}</span>
              <span v-if="isRacingInYoungerCategory(race)" class="younger-category-note">
                ({{ $t('boat.racingInYoungerCategory') }})
              </span>
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

    // Get boat type variants (sweep + scull)
    const getBoatTypeVariants = (boatType) => {
      const variants = [boatType] // Always include the original boat type
      
      // Map sweep boat types to their scull equivalents
      const sweepToScull = {
        '4+': '4x+',   // Coxed four → Coxed quad
        '4-': '4x-',   // Coxless four → Coxless quad
        '8+': '8x+',   // Eight → Octuple
      }
      
      // If this is a sweep boat, add the scull variant
      if (sweepToScull[boatType]) {
        variants.push(sweepToScull[boatType])
      }
      
      // If this is a scull boat, add the sweep variant
      const scullToSweep = Object.fromEntries(
        Object.entries(sweepToScull).map(([k, v]) => [v, k])
      )
      if (scullToSweep[boatType]) {
        variants.push(scullToSweep[boatType])
      }
      
      return variants
    }

    const boatTypeVariants = computed(() => getBoatTypeVariants(props.boatType))

    const crewAnalysis = computed(() => {
      if (!props.crewMembers || props.crewMembers.length === 0) {
        return null
      }
      return analyzeCrewComposition(props.crewMembers)
    })

    const eligibleRaces = computed(() => {
      if (!props.crewMembers || props.crewMembers.length === 0) {
        return []
      }

      // Filter races by event type and boat type first
      // Also include scull equivalent (e.g., if boat is 4+, also show 4x+)
      const filteredRaces = props.availableRaces.filter(race => {
        return race.event_type === props.eventType && boatTypeVariants.value.includes(race.boat_type)
      })

      // Then filter by crew eligibility
      return getEligibleRaces(props.crewMembers, filteredRaces)
    })

    // Analyze why no races are available and provide specific reason
    const noRacesReason = computed(() => {
      if (!crewAnalysis.value || eligibleRaces.value.length > 0) {
        return null
      }

      const analysis = crewAnalysis.value
      
      // Check if there are any races for this event type and boat type combination
      const racesForBoatType = props.availableRaces.filter(race => {
        return race.event_type === props.eventType && boatTypeVariants.value.includes(race.boat_type)
      })

      if (racesForBoatType.length === 0) {
        return t('boat.noRacesForBoatType', { 
          boatType: props.boatType, 
          eventType: props.eventType 
        })
      }

      // Check gender mismatch
      const availableGenders = [...new Set(racesForBoatType.map(r => r.gender_category))]
      if (!availableGenders.includes(analysis.genderCategory)) {
        return t('boat.genderMismatch', {
          crewGender: t(`boat.${analysis.genderCategory}`),
          availableGenders: availableGenders.map(g => t(`boat.${g}`)).join(', ')
        })
      }

      // Check age category mismatch
      const availableAges = [...new Set(racesForBoatType.map(r => r.age_category))]
      if (!availableAges.includes(analysis.ageCategory)) {
        return t('boat.ageMismatch', {
          crewAge: t(`boat.${analysis.ageCategory}`),
          availableAges: availableAges.map(a => t(`boat.${a}`)).join(', ')
        })
      }

      // Check master category mismatch
      if (analysis.ageCategory === 'master' && analysis.masterCategory) {
        const masterRaces = racesForBoatType.filter(r => 
          r.age_category === 'master' && r.gender_category === analysis.genderCategory
        )
        const availableMasterCats = [...new Set(masterRaces.map(r => r.master_category).filter(Boolean))]
        
        if (availableMasterCats.length > 0 && !availableMasterCats.includes(analysis.masterCategory)) {
          return t('boat.masterCategoryMismatch', {
            crewCategory: analysis.masterCategory,
            availableCategories: availableMasterCats.join(', ')
          })
        }
      }

      return t('boat.noMatchingRaces')
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

    const getTranslatedRaceName = (race) => {
      if (!race.name) {
        return getRaceDisplay(race)
      }
      // Try to get translation, fallback to original name if not found
      const translationKey = `races.${race.name}`
      const translated = t(translationKey)
      // If translation key is returned as-is, it means no translation exists
      return translated === translationKey ? race.name : translated
    }

    const isRacingInYoungerCategory = (race) => {
      if (!crewAnalysis.value || !race.master_category || !crewAnalysis.value.masterCategory) {
        return false
      }
      
      // Only show note for G racing in F (special exception)
      return crewAnalysis.value.masterCategory === 'G' && race.master_category === 'F'
    }

    return {
      eligibleRaces,
      crewDescription,
      crewAnalysis,
      boatTypeVariants,
      noRacesReason,
      selectRace,
      getRaceDisplay,
      getTranslatedRaceName,
      isRacingInYoungerCategory
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

.warning-message h4 {
  margin: 0 0 1rem 0;
  color: #856404;
  font-size: 1.1rem;
}

.reason-text {
  margin-top: 0.5rem;
  color: #495057;
  line-height: 1.5;
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

.younger-category-note {
  display: inline-block;
  color: #0c5460;
  font-style: italic;
  margin-left: 0.5rem;
  font-size: 0.75rem;
}
</style>
