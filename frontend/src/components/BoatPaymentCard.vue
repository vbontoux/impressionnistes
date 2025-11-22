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
        <h3>{{ boat.event_type }} - {{ boat.boat_type }}</h3>
        <p class="race-name" v-if="boat.race_id">{{ getRaceName(boat) }}</p>
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
      <div class="price-breakdown" v-if="boat.pricing">
        <div class="breakdown-item">
          <span>{{ $t('payment.basePrice') }}</span>
          <span>{{ formatPrice(boat.pricing.base_price) }}</span>
        </div>
        <div class="breakdown-item" v-if="boat.pricing.rental_fee > 0">
          <span>{{ $t('payment.rentalFee') }}</span>
          <span>{{ formatPrice(boat.pricing.rental_fee) }}</span>
        </div>
        <div class="breakdown-item" v-if="boat.pricing.multi_club_fee > 0">
          <span>{{ $t('payment.multiClubFee') }}</span>
          <span>{{ formatPrice(boat.pricing.multi_club_fee) }}</span>
        </div>
        <div class="breakdown-item total">
          <span>{{ $t('payment.total') }}</span>
          <span class="total-amount">{{ formatPrice(boat.pricing.total) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

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

const getFilledSeatsCount = (boat) => {
  if (!boat.seats) return 0
  return boat.seats.filter(seat => seat.crew_member_id).length
}

const getRaceName = (boat) => {
  // TODO: Fetch race name from race_id
  return boat.race_id || t('payment.noRace')
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

.boat-info h3 {
  margin: 0 0 0.25rem 0;
  color: #333;
  font-size: 1.125rem;
}

.race-name {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
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
  font-size: 0.875rem;
  color: #666;
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
