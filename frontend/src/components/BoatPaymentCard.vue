<template>
  <div 
    class="boat-payment-card" 
    :class="{ selected }"
    @click="$emit('toggle')"
  >
    <div class="card-header">
      <input 
        type="checkbox" 
        :checked="selected"
        @click.stop
        @change="$emit('toggle')"
        class="checkbox"
      />
      <div class="boat-info">
        <div class="boat-title-row">
          <h3>{{ boat.event_type }} - {{ boat.boat_type }}</h3>
          <router-link 
            :to="`/boats/${boat.boat_registration_id}`"
            class="view-details-link"
            @click.stop
          >
            {{ $t('payment.viewDetails') }}
          </router-link>
        </div>
        <p class="race-name" v-if="boat.race_id">{{ getRaceName(boat) }}</p>
      </div>
      <div class="boat-price">
        <span class="price-amount">{{ formatPrice(boat.pricing?.total) }}</span>
      </div>
    </div>

    <div class="card-body">
      <div class="boat-summary">
        <span class="summary-item">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ getFilledSeatsCount(boat) }} {{ $t('payment.seats') }}
        </span>
        <span class="separator">•</span>
        <span class="summary-item">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ getFirstRowerName(boat) }}
        </span>
        <span v-if="boat.is_multi_club_crew || boat.registration_status === 'free'" class="rcpm-indicator">
          <span class="separator">•</span>
          <span class="rcpm-badge">{{ $t('boat.multiClub') }}</span>
        </span>
      </div>

      <!-- Price Breakdown -->
      <div class="price-breakdown" v-if="boat.pricing && boat.pricing.breakdown">
        <!-- Show detailed breakdown items -->
        <div 
          v-for="(item, index) in boat.pricing.breakdown" 
          :key="index"
          class="breakdown-item"
        >
          <span class="breakdown-label">
            {{ item.item }}
            <span v-if="item.quantity > 1" class="breakdown-detail">
              ({{ item.quantity }} × {{ formatPrice(item.unit_price) }})
            </span>
          </span>
          <span :class="{ 'free-amount': item.amount === 0 }">
            {{ formatPrice(item.amount) }}
          </span>
        </div>
        
        <!-- Total -->
        <div class="breakdown-item total">
          <span>{{ $t('payment.total') }}</span>
          <span class="total-amount">{{ formatPrice(boat.pricing.total) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRaceStore } from '../stores/raceStore'
import { getRaceDisplay } from '../utils/raceEligibility'

const props = defineProps({
  boat: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])

const { t } = useI18n()
const raceStore = useRaceStore()

const getFilledSeatsCount = (boat) => {
  if (!boat.seats) return 0
  return boat.seats.filter(seat => seat.crew_member_id).length
}

const getFirstRowerName = (boat) => {
  if (!boat.seats || boat.seats.length === 0) return '-'
  
  // Count filled seats
  const filledSeatsCount = boat.seats.filter(seat => seat.crew_member_id).length
  
  // Find first rower (position 1, type 'rower')
  const firstRower = boat.seats.find(seat => seat.position === 1 && seat.type === 'rower')
  
  if (firstRower && (firstRower.crew_member_first_name || firstRower.crew_member_last_name)) {
    const firstName = firstRower.crew_member_first_name || ''
    const lastName = firstRower.crew_member_last_name || ''
    const name = `${firstName} ${lastName}`.trim()
    
    // Add ", ..." if there are more than 1 crew member
    return filledSeatsCount > 1 ? `${name}, ...` : name
  }
  
  return '-'
}

const getRaceName = (boat) => {
  if (!boat.race_id) {
    return t('payment.noRace')
  }
  
  // Find the race in the store
  const race = raceStore.races.find(r => r.race_id === boat.race_id)
  
  if (race && race.name) {
    // Try to get translation, fallback to original name if not found
    const translationKey = `races.${race.name}`
    const translated = t(translationKey)
    // If translation key is returned as-is, it means no translation exists
    return translated === translationKey ? race.name : translated
  } else if (race) {
    // Fallback to generic display if no name
    return getRaceDisplay(race)
  }
  
  // Fallback to race_id if race not found
  return boat.race_id
}

const formatPrice = (amount) => {
  if (!amount) return '0.00 €'
  const value = typeof amount === 'number' ? amount : parseFloat(amount)
  return `${value.toFixed(2)} €`
}
</script>

<style scoped>
.boat-payment-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.boat-payment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #4CAF50;
}

.boat-payment-card.selected {
  border-color: #4CAF50;
  background-color: #f1f8f4;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.boat-info {
  flex: 1;
}

.boat-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.25rem;
}

.boat-info h3 {
  margin: 0;
  color: #333;
  font-size: 1.125rem;
}

.view-details-link {
  color: #4CAF50;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border: 1px solid #4CAF50;
  border-radius: 4px;
  transition: all 0.2s;
}

.view-details-link:hover {
  background-color: #4CAF50;
  color: white;
}

.race-name {
  margin: 0.25rem 0;
  color: #666;
  font-size: 0.875rem;
}

.crew-preview {
  margin: 0.25rem 0 0 0;
  color: #555;
  font-size: 0.875rem;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.crew-preview .icon {
  font-size: 1rem;
}

.boat-price {
  text-align: right;
}

.price-amount {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4CAF50;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.boat-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  color: #666;
  font-size: 0.875rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.icon-svg {
  width: 16px;
  height: 16px;
  color: #666;
  flex-shrink: 0;
}

.separator {
  color: #ccc;
  margin: 0 0.25rem;
}

.rcpm-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rcpm-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background-color: #ffc107;
  color: #000;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.icon {
  font-size: 1.125rem;
}

.price-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 0.875rem;
  color: #666;
  gap: 1rem;
}

.breakdown-label {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.breakdown-detail {
  font-size: 0.75rem;
  color: #999;
  font-style: italic;
}

.free-amount {
  color: #4CAF50;
  font-weight: 500;
}

.breakdown-item.total {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 2px solid #dee2e6;
  font-weight: 600;
  font-size: 1rem;
  color: #333;
}

.total-amount {
  color: #4CAF50;
  font-size: 1.125rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
  }

  .boat-title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .boat-price {
    width: 100%;
    text-align: left;
    margin-top: 0.5rem;
  }

  .boat-details {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
