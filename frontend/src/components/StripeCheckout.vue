<template>
  <div class="stripe-checkout">
    <div class="checkout-header">
      <h2>{{ $t('payment.checkout.title') }}</h2>
      <p class="checkout-subtitle">{{ $t('payment.checkout.subtitle') }}</p>
    </div>

    <!-- Order Summary -->
    <div class="order-summary">
      <h3>{{ $t('payment.checkout.orderSummary') }}</h3>
      <div class="summary-items">
        <div v-for="boat in selectedBoats" :key="boat.boat_registration_id" class="summary-item">
          <span class="item-name">{{ boat.event_type }} - {{ boat.boat_type }}</span>
          <span class="item-price">{{ formatPrice(boat.pricing?.total) }}</span>
        </div>
        <div v-for="rental in selectedRentals" :key="rental.rental_request_id" class="summary-item">
          <span class="item-name">{{ $t('payment.rental') }}: {{ $t(`boat.types.${rental.boat_type}`) }}</span>
          <span class="item-price">{{ formatPrice(rental.pricing?.total) }}</span>
        </div>
      </div>
      <div class="summary-total">
        <span class="total-label">{{ $t('payment.checkout.total') }}</span>
        <span class="total-amount">{{ formatPrice(totalAmount) }}</span>
      </div>
    </div>

    <!-- Payment Form -->
    <form @submit.prevent="handleSubmit" class="payment-form">
      <div class="form-section">
        <h3>{{ $t('payment.checkout.paymentDetails') }}</h3>
        
        <!-- Stripe Card Element -->
        <div id="card-element" class="card-element"></div>
        <div v-if="cardError" class="card-error">{{ cardError }}</div>
      </div>

      <!-- Submit Button -->
      <button 
        type="submit" 
        class="btn-pay"
        :disabled="processing || !cardComplete"
      >
        <span v-if="!processing" class="btn-content">
          <span class="btn-icon">🔒</span>
          {{ $t('payment.checkout.payNow', { amount: formatPrice(totalAmount) }) }}
        </span>
        <span v-else class="btn-content">
          <span class="spinner-small"></span>
          {{ $t('payment.checkout.processing') }}
        </span>
      </button>

      <!-- Error Message -->
      <div v-if="paymentError" class="alert alert-error">
        {{ paymentError }}
      </div>

      <!-- Security Notice -->
      <div class="security-notice">
        <span class="security-icon">🔒</span>
        <span>{{ $t('payment.checkout.securePayment') }}</span>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { loadStripe } from '@stripe/stripe-js'
import { useI18n } from 'vue-i18n'
import paymentService from '../services/paymentService'

const props = defineProps({
  selectedBoats: {
    type: Array,
    required: true
  },
  selectedRentals: {
    type: Array,
    default: () => []
  },
  totalAmount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['payment-success', 'payment-error'])

const router = useRouter()
const { t } = useI18n()

// Stripe instances
let stripe = null
let cardElement = null

// Component state
const processing = ref(false)
const cardComplete = ref(false)
const cardError = ref('')
const paymentError = ref('')

// Computed
const boatRegistrationIds = computed(() => 
  props.selectedBoats.map(boat => boat.boat_registration_id)
)

const rentalRequestIds = computed(() => 
  props.selectedRentals.map(rental => rental.rental_request_id)
)

// Methods
const formatPrice = (amount) => {
  if (!amount) return '0.00 €'
  const value = typeof amount === 'number' ? amount : parseFloat(amount)
  return `${value.toFixed(2)} €`
}

const initializeStripe = async () => {
  try {
    // Load Stripe.js
    // TODO: Get publishable key from environment variable
    const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_placeholder'
    stripe = await loadStripe(publishableKey)

    if (!stripe) {
      throw new Error('Failed to load Stripe')
    }

    // Create card element with mobile-optimized styling
    const elements = stripe.elements()
    cardElement = elements.create('card', {
      style: {
        base: {
          fontSize: '16px', // Prevents zoom on iOS
          color: '#32325d',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          '::placeholder': {
            color: '#aab7c4'
          },
          // Mobile-friendly padding
          padding: '12px'
        },
        invalid: {
          color: '#fa755a',
          iconColor: '#fa755a'
        }
      },
      // Disable autocomplete for better mobile experience
      hidePostalCode: false
    })

    // Mount card element
    cardElement.mount('#card-element')

    // Listen for card changes
    cardElement.on('change', (event) => {
      cardComplete.value = event.complete
      cardError.value = event.error ? event.error.message : ''
    })

    console.log('Stripe initialized successfully')
  } catch (error) {
    console.error('Failed to initialize Stripe:', error)
    paymentError.value = t('payment.checkout.errors.stripeInit')
  }
}

const handleSubmit = async () => {
  if (processing.value || !cardComplete.value) {
    return
  }

  processing.value = true
  paymentError.value = ''
  cardError.value = ''

  try {
    // Step 1: Create payment intent on backend
    console.log('Creating payment intent for boats:', boatRegistrationIds.value)
    console.log('Creating payment intent for rentals:', rentalRequestIds.value)
    console.log('Selected rentals data:', props.selectedRentals)
    console.log('Rental request IDs being sent:', rentalRequestIds.value)
    
    const response = await paymentService.createPaymentIntent(
      boatRegistrationIds.value,
      rentalRequestIds.value
    )
    
    console.log('Payment intent response:', response)
    
    // Extract data from response (backend wraps in {success: true, data: {...}})
    const paymentIntentData = response.data || response
    
    // Validate response
    if (!paymentIntentData || !paymentIntentData.client_secret) {
      console.error('Invalid response structure:', response)
      throw new Error('Invalid payment intent response: missing client_secret')
    }
    
    console.log('Payment intent created:', paymentIntentData.payment_intent_id)
    console.log('Client secret:', paymentIntentData.client_secret)

    // Step 2: Confirm payment with Stripe
    const { error, paymentIntent } = await stripe.confirmCardPayment(
      paymentIntentData.client_secret,
      {
        payment_method: {
          card: cardElement
        }
      }
    )

    if (error) {
      // Payment failed
      console.error('Payment failed:', error)
      paymentError.value = error.message
      emit('payment-error', error)
    } else if (paymentIntent.status === 'succeeded') {
      // Payment succeeded
      console.log('Payment succeeded:', paymentIntent.id)
      emit('payment-success', {
        paymentIntentId: paymentIntent.id,
        amount: paymentIntent.amount / 100,
        currency: paymentIntent.currency
      })
      
      // Navigate to success page
      router.push({
        name: 'PaymentSuccess',
        query: { payment_intent: paymentIntent.id }
      })
    } else {
      // Unexpected status
      console.warn('Unexpected payment status:', paymentIntent.status)
      paymentError.value = t('payment.checkout.errors.unexpectedStatus')
    }
  } catch (error) {
    console.error('Payment error:', error)
    console.error('Error response:', error.response)
    console.error('Error data:', error.response?.data)
    
    // Detailed error message
    let errorMessage = t('payment.checkout.errors.generic')
    
    if (error.response) {
      // Server responded with error
      errorMessage = error.response.data?.message || error.response.data?.error || errorMessage
      console.error(`API Error (${error.response.status}):`, errorMessage)
    } else if (error.request) {
      // Request made but no response
      errorMessage = 'No response from server. Please check your connection.'
      console.error('No response received:', error.request)
    } else {
      // Error in request setup
      errorMessage = error.message
      console.error('Request setup error:', error.message)
    }
    
    paymentError.value = errorMessage
    emit('payment-error', error)
  } finally {
    processing.value = false
  }
}

// Lifecycle
onMounted(() => {
  initializeStripe()
})
</script>

<style scoped>
/* Mobile-first base styles */
.stripe-checkout {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  width: 100%;
}

.checkout-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.checkout-header h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}

.checkout-subtitle {
  color: #666;
  font-size: 0.875rem;
}

.order-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.order-summary h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.summary-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.item-name {
  color: #495057;
  font-size: 0.875rem;
  flex: 1;
  word-break: break-word;
}

.item-price {
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.875rem;
  white-space: nowrap;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
}

.total-label {
  color: #2c3e50;
  font-weight: 600;
}

.total-amount {
  color: #4CAF50;
  font-weight: 700;
  font-size: 1.1rem;
}

.payment-form {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.card-element {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
  transition: border-color 0.2s;
  min-height: 44px;
  /* Ensure Stripe element is properly sized for mobile */
}

.card-element:focus-within {
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.card-error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.btn-pay {
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
  transition: all 0.3s;
  margin-bottom: 1rem;
  /* Ensure button is easily tappable on mobile */
  touch-action: manipulation;
}

.btn-pay:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-pay:active:not(:disabled) {
  background-color: #3d8b40;
}

.btn-pay:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-icon {
  font-size: 1.1rem;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert-error {
  padding: 0.875rem;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  word-break: break-word;
}

.security-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.8125rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.security-icon {
  font-size: 0.875rem;
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .stripe-checkout {
    padding: 2rem;
  }

  .checkout-header {
    margin-bottom: 2rem;
  }

  .checkout-header h2 {
    font-size: 1.5rem;
  }

  .checkout-subtitle {
    font-size: 0.95rem;
  }

  .order-summary {
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .order-summary h3 {
    font-size: 1.1rem;
  }

  .item-name {
    font-size: 0.95rem;
  }

  .item-price {
    font-size: 0.95rem;
  }

  .summary-total {
    font-size: 1.1rem;
  }

  .total-amount {
    font-size: 1.3rem;
  }

  .payment-form {
    padding: 2rem;
  }

  .form-section {
    margin-bottom: 2rem;
  }

  .form-section h3 {
    font-size: 1.1rem;
  }

  .card-element {
    padding: 1rem;
  }

  .btn-pay {
    padding: 1rem;
    font-size: 1.1rem;
    /* Add hover transform on larger screens */
  }

  .btn-pay:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  }

  .btn-icon {
    font-size: 1.2rem;
  }

  .alert-error {
    padding: 1rem;
    font-size: 0.95rem;
  }

  .security-notice {
    font-size: 0.875rem;
  }

  .security-icon {
    font-size: 1rem;
  }
}
</style>
