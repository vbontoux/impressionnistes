<template>
  <div class="payment-summary">
    <div class="summary-header">
      <h3>{{ $t('payment.summary') }}</h3>
    </div>

    <div class="summary-body">
      <div class="summary-row" v-if="selectedBoats.length > 0">
        <span>{{ $t('payment.boatsSelected', { count: selectedBoats.length }) }}</span>
        <span class="value">{{ selectedBoats.length }}</span>
      </div>

      <div class="summary-row" v-if="selectedRentals.length > 0">
        <span>{{ $t('payment.rentalBoatsSelected', { count: selectedRentals.length }) }}</span>
        <span class="value">{{ selectedRentals.length }}</span>
      </div>

      <div class="summary-row total">
        <span class="total-label">{{ $t('payment.totalAmount') }}</span>
        <span class="total-value">{{ formatPrice(total) }}</span>
      </div>
    </div>

    <div class="summary-actions">
      <button 
        @click="$emit('proceed')" 
        class="btn-proceed"
        :disabled="selectedBoats.length === 0 && selectedRentals.length === 0"
      >
        <span class="btn-icon">💳</span>
        {{ $t('payment.proceedToPayment') }}
      </button>
    </div>

    <div class="summary-note">
      <p>{{ $t('payment.securePayment') }}</p>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const props = defineProps({
  selectedBoats: {
    type: Array,
    required: true
  },
  selectedRentals: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    required: true
  }
})

defineEmits(['proceed'])

const { t } = useI18n()

const formatPrice = (amount) => {
  return `${amount.toFixed(2)} €`
}
</script>

<style scoped>
.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.summary-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  color: #666;
}

.summary-row.total {
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 2px solid #dee2e6;
}

.total-label {
  font-size: 1.125rem;
  font-weight: 600;
  color: #333;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4CAF50;
}

.value {
  font-weight: 500;
  color: #333;
}

.summary-actions {
  margin-top: 0.5rem;
}

.btn-proceed {
  width: 100%;
  padding: 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-proceed:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.btn-proceed:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 1.25rem;
}

.summary-note {
  text-align: center;
  padding-top: 0.5rem;
  border-top: 1px solid #e0e0e0;
}

.summary-note p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .total-value {
    font-size: 1.25rem;
  }

  .btn-proceed {
    font-size: 1rem;
  }
}
</style>
