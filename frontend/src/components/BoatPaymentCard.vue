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
        <p class="crew-preview" v-if="getCrewPreview(boat)">
          <span class="icon">👤</span>
          {{ getCrewPreview(boat) }}
        </p>
      </div>
      <div class="boat-price">
        <span class="price-amount">{{ formatPrice(boat.pricing?.total) }}</span>
      </div>
    </div>

    <div class="card-body">
      <div class="boat-details">
        <div class="detail-item">
          <span class="icon">👥</span>
          <span>{{ getFilledSeatsCount(boat) }} {{ $t('payment.seats') }}</span>
        </div>
        <div class="detail-item" v-if="boat.is_boat_rental">
          <span class="icon">🚣</span>
          <span>{{ $t('payment.rental') }}</span>
        </div>
        <div class="detail-item" v-if="boat.is_multi_club_crew">
          <span class="icon">🏛️</span>
          <span>{{ $t('payment.multiClub') }}</span>
        </div>
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

const getCrewPreview = (boat) => {
  if (!boat.seats || boat.seats.length === 0) return ''
  
  // Get filled seats sorted by position
  const filledSeats = boat.seats
    .filter(seat => seat.crew_member_id && (seat.crew_member_first_name || seat.crew_member_last_name))
    .sort((a, b) => a.position - b.position)
  
  if (filledSeats.length === 0) return ''
  
  // Show first rower and count
  const firstName = filledSeats[0].crew_member_first_name || ''
  const lastName = filledSeats[0].crew_member_last_name || ''
  const firstRower = `${firstName} ${lastName}`.trim()
  
  if (filledSeats.length === 1) {
    return firstRower
  } else if (filledSeats.length === 2) {
    const secondName = `${filledSeats[1].crew_member_first_name || ''} ${filledSeats[1].crew_member_last_name || ''}`.trim()
    return `${firstRower}, ${secondName}`
  } else {
    return `${firstRower} ${t('payment.andOthers', { count: filledSeats.length - 1 })}`
  }
}

const getRaceName = (boat) => {
  if (!boat.race_id) {
    return t('payment.noRace')
  }
  
  // Find the race in the store
  const race = raceStore.races.find(r => r.race_id === boat.race_id)
  
  if (race) {
    // Use the same display format as RaceSelector
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

.boat-details {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.875rem;
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
