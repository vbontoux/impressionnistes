<template>
  <div class="payment-checkout-page">
    <div class="page-header">
      <button @click="goBack" class="btn-back">
        <span class="back-icon">←</span>
        {{ $t('common.back') }}
      </button>
      <h1>{{ $t('payment.checkout.pageTitle') }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-error">
      {{ error }}
      <button @click="goBack" class="btn-secondary">
        {{ $t('payment.checkout.backToPayment') }}
      </button>
    </div>

    <!-- Checkout Form -->
    <div v-else-if="selectedBoats.length > 0">
      <StripeCheckout
        :selected-boats="selectedBoats"
        :total-amount="totalAmount"
        @payment-success="handlePaymentSuccess"
        @payment-error="handlePaymentError"
      />
    </div>

    <!-- No Selection State -->
    <div v-else class="empty-state">
      <div class="empty-icon">💳</div>
      <h3>{{ $t('payment.checkout.noSelection') }}</h3>
      <p>{{ $t('payment.checkout.noSelectionDescription') }}</p>
      <button @click="goBack" class="btn-primary">
        {{ $t('payment.checkout.backToPayment') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePaymentStore } from '../stores/paymentStore'
import { useI18n } from 'vue-i18n'
import StripeCheckout from '../components/StripeCheckout.vue'

const router = useRouter()
const paymentStore = usePaymentStore()
const { t } = useI18n()

const loading = ref(true)
const error = ref(null)

// Computed
const selectedBoats = computed(() => paymentStore.selectedBoats)
const totalAmount = computed(() => paymentStore.totalAmount)

// Methods
const goBack = () => {
  router.push('/payment')
}

const handlePaymentSuccess = (paymentData) => {
  console.log('Payment successful:', paymentData)
  // Clear selection after successful payment
  paymentStore.clearSelection()
}

const handlePaymentError = (error) => {
  console.error('Payment error:', error)
  // Error is already displayed in the StripeCheckout component
}

// Lifecycle
onMounted(async () => {
  try {
    // Ensure we have boats data
    if (paymentStore.boatsReadyForPayment.length === 0) {
      await paymentStore.fetchBoatsReadyForPayment()
    }
    
    // Check if user has selected boats
    if (selectedBoats.value.length === 0) {
      error.value = t('payment.checkout.noSelection')
    }
  } catch (err) {
    console.error('Failed to load payment data:', err)
    error.value = t('payment.checkout.errors.loadFailed')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.payment-checkout-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s;
  margin-bottom: 1rem;
}

.btn-back:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
}

.back-icon {
  font-size: 1.2rem;
}

.page-header h1 {
  color: #2c3e50;
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert-error {
  padding: 1.5rem;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  margin-top: 1rem;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .payment-checkout-page {
    padding: 1rem;
  }
}
</style>
