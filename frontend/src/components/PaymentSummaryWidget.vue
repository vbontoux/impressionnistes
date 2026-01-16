<template>
  <div class="payment-summary-widget">
    <div class="widget-header">
      <h3>{{ $t('payment.summary.title') }}</h3>
      <router-link to="/payment/history" class="view-all-link">
        {{ $t('payment.summary.viewAll') }}
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="arrow-icon">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </router-link>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <!-- Error State -->
    <MessageAlert
      v-else-if="error"
      type="error"
      :message="error"
      :dismissible="true"
      @dismiss="error = ''"
    />

    <!-- Summary Content -->
    <div v-else class="summary-content">
      <div class="summary-row">
        <div class="summary-label">{{ $t('payment.summary.totalPaid') }}</div>
        <div class="summary-value paid">
          {{ formatCurrency(summary.paid?.total_amount || 0, summary.paid?.currency || 'EUR') }}
        </div>
      </div>

      <div class="summary-row">
        <div class="summary-label">{{ $t('payment.summary.paymentCount') }}</div>
        <div class="summary-value">
          {{ summary.paid?.payment_count || 0 }}
        </div>
      </div>

      <div class="summary-row">
        <div class="summary-label">{{ $t('payment.summary.boatsPaid') }}</div>
        <div class="summary-value">
          {{ summary.paid?.boat_count || 0 }}
        </div>
      </div>

      <div class="summary-divider"></div>

      <div class="summary-row" :class="{ 'has-outstanding': hasOutstanding }">
        <div class="summary-label">{{ $t('payment.summary.outstanding') }}</div>
        <div class="summary-value outstanding" :class="{ 'highlight': hasOutstanding }">
          {{ formatCurrency(summary.outstanding?.total_amount || 0, summary.outstanding?.currency || 'EUR') }}
        </div>
      </div>

      <div v-if="hasOutstanding" class="summary-row">
        <div class="summary-label">{{ $t('payment.summary.unpaidBoats') }}</div>
        <div class="summary-value">
          {{ summary.outstanding?.boat_count || 0 }}
        </div>
      </div>

      <!-- Action Button -->
      <div v-if="hasOutstanding" class="widget-action">
        <BaseButton 
          variant="primary" 
          size="medium"
          :full-width="true"
          @click="goToPayment"
        >
          {{ $t('payment.summary.makePayment') }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import paymentService from '../services/paymentService';
import LoadingSpinner from './base/LoadingSpinner.vue';
import MessageAlert from './composite/MessageAlert.vue';
import BaseButton from './base/BaseButton.vue';

const { t } = useI18n();
const router = useRouter();

// Data
const summary = ref({});
const loading = ref(false);
const error = ref('');

// Computed
const hasOutstanding = computed(() => {
  return summary.value.outstanding?.total_amount > 0;
});

// Format currency
const formatCurrency = (amount, currency = 'EUR') => {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: currency
  }).format(amount);
};

// Fetch summary
const fetchSummary = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await paymentService.getPaymentSummary();
    summary.value = response;
  } catch (err) {
    console.error('Error fetching payment summary:', err);
    error.value = err.response?.data?.error || t('payment.summary.errorLoading');
  } finally {
    loading.value = false;
  }
};

// Go to payment
const goToPayment = () => {
  router.push('/payment');
};

// Load on mount
onMounted(() => {
  fetchSummary();
});
</script>

<style scoped>
.payment-summary-widget {
  background: var(--color-white);
  border-radius: 8px;
  padding: var(--spacing-xl);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.widget-header h3 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
}

.view-all-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: color 0.2s ease;
}

.view-all-link:hover {
  color: var(--color-primary-hover);
}

.arrow-icon {
  width: 16px;
  height: 16px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-row.has-outstanding {
  margin-top: var(--spacing-sm);
}

.summary-label {
  font-size: var(--font-size-base);
  color: var(--color-muted);
}

.summary-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
}

.summary-value.paid {
  color: var(--color-success);
}

.summary-value.outstanding {
  color: var(--color-muted);
}

.summary-value.outstanding.highlight {
  color: var(--color-warning);
  font-size: var(--font-size-xl);
}

.summary-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: var(--spacing-sm) 0;
}

.widget-action {
  margin-top: var(--spacing-lg);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .payment-summary-widget {
    padding: var(--spacing-lg);
  }

  .widget-header h3 {
    font-size: var(--font-size-lg);
  }

  .summary-value {
    font-size: var(--font-size-base);
  }

  .summary-value.outstanding.highlight {
    font-size: var(--font-size-lg);
  }
}
</style>
