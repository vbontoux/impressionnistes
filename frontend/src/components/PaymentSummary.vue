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
/* Mobile-first base styles */
.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.125rem;
  font-weight: 600;
}

.summary-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #666;
  font-size: 0.875rem;
  gap: 0.5rem;
}

.summary-row span:first-child {
  flex: 1;
  word-break: break-word;
}

.summary-row.total {
  margin-top: 0.5rem;
  padding: 0.875rem;
  background-color: #f0f9f4;
  border: 2px solid #4CAF50;
}

.total-label {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.total-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: #4CAF50;
  white-space: nowrap;
}

.value {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
}

.summary-actions {
  margin-top: 0.5rem;
}

.btn-proceed {
  width: 100%;
  padding: 0.875rem 1rem;
  min-height: 44px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  touch-action: manipulation;
}

.btn-proceed:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-proceed:active:not(:disabled) {
  background-color: #3d8b40;
}

.btn-proceed:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.125rem;
}

.summary-note {
  text-align: center;
  padding-top: 0.75rem;
  border-top: 1px solid #e0e0e0;
}

.summary-note p {
  margin: 0;
  color: #666;
  font-size: 0.8125rem;
  line-height: 1.4;
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .payment-summary {
    gap: 1rem;
  }

  .summary-header h3 {
    font-size: 1.25rem;
  }

  .summary-body {
    gap: 0.75rem;
  }

  .summary-row {
    padding: 0.5rem 0;
    background-color: transparent;
    border-radius: 0;
    font-size: 0.95rem;
  }

  .summary-row.total {
    padding: 1rem 0;
    margin-top: 0.5rem;
    background-color: transparent;
    border: none;
    border-top: 2px solid #dee2e6;
  }

  .total-label {
    font-size: 1.125rem;
  }

  .total-value {
    font-size: 1.5rem;
  }

  .summary-actions {
    margin-top: 0.5rem;
  }

  .btn-proceed {
    padding: 1rem;
    font-size: 1.125rem;
  }

  .btn-proceed:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
  }

  .btn-icon {
    font-size: 1.25rem;
  }

  .summary-note {
    padding-top: 0.5rem;
  }

  .summary-note p {
    font-size: 0.875rem;
  }
}
</style>
