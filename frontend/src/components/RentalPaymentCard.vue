<template>
  <div 
    class="rental-payment-card" 
    :class="{ selected: selected }"
    @click="$emit('toggle')"
  >
    <div class="card-header">
      <div class="checkbox-container">
        <input 
          type="checkbox" 
          :checked="selected"
          @click.stop="$emit('toggle')"
          class="selection-checkbox"
        />
      </div>
      <div class="rental-info">
        <h3 class="rental-name">{{ rental.boat_name }}</h3>
        <span class="rental-type">{{ $t(`boat.types.${rental.boat_type}`) }}</span>
      </div>
      <div class="rental-badge">
        <span class="badge rental">{{ $t('payment.rental') }}</span>
      </div>
    </div>

    <div class="card-body">
      <div class="rental-details">
        <div class="detail-row" v-if="rental.rower_weight_range">
          <span class="label">{{ $t('boatRental.weightCapacity') }}:</span>
          <span class="value">{{ rental.rower_weight_range }}</span>
        </div>
      </div>

      <div class="pricing-section">
        <div class="price-row">
          <span class="price-label">{{ $t('payment.rentalFee') }}:</span>
          <span class="price-value">{{ formatPrice(rental.pricing.rental_fee) }}</span>
        </div>
        <div class="price-row total">
          <span class="price-label">{{ $t('payment.total') }}:</span>
          <span class="price-value total-amount">{{ formatPrice(rental.pricing.total) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  rental: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])

const formatPrice = (amount) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount)
}
</script>

<style scoped>
.rental-payment-card {
  background: white;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rental-payment-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.rental-payment-card.selected {
  border-color: #4CAF50;
  background-color: #f0f9f4;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.checkbox-container {
  flex-shrink: 0;
}

.selection-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.rental-info {
  flex: 1;
}

.rental-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.rental-type {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.rental-badge {
  flex-shrink: 0;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.rental {
  background-color: #e3f2fd;
  color: #1976d2;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rental-details {
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: #5a6c7d;
}

.value {
  color: #2c3e50;
}

.pricing-section {
  border-top: 1px solid #e1e8ed;
  padding-top: 1rem;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.price-row.total {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e1e8ed;
  font-weight: 600;
  font-size: 1.1rem;
}

.price-label {
  color: #5a6c7d;
}

.price-value {
  color: #2c3e50;
}

.total-amount {
  color: #4CAF50;
  font-weight: 700;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .rental-payment-card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    gap: 0.75rem;
  }

  .checkbox-container {
    display: flex;
    align-items: center;
  }

  .selection-checkbox {
    width: 24px;
    height: 24px;
    min-width: 44px;
    min-height: 44px;
  }

  .rental-info {
    width: 100%;
  }

  .rental-name {
    font-size: 1.1rem;
  }

  .rental-type {
    font-size: 0.875rem;
  }

  .rental-badge {
    width: 100%;
  }

  .badge {
    display: block;
    text-align: center;
    padding: 0.5rem;
  }

  .rental-details {
    padding: 0.75rem;
  }

  .detail-row {
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 0.75rem;
  }

  .pricing-section {
    padding-top: 0.75rem;
  }

  .price-row {
    font-size: 0.875rem;
  }

  .price-row.total {
    font-size: 1rem;
  }
}
</style>
