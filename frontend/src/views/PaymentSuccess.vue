<template>
  <div class="payment-success-page">
    <div class="success-container">
      <div class="success-icon">✅</div>
      <h1>{{ $t('payment.success.title') }}</h1>
      <p class="success-message">{{ $t('payment.success.message') }}</p>

      <div v-if="paymentIntent" class="payment-details">
        <h3>{{ $t('payment.success.details') }}</h3>
        <div class="detail-item">
          <span class="detail-label">{{ $t('payment.success.paymentId') }}</span>
          <span class="detail-value">{{ paymentIntent }}</span>
        </div>
      </div>

      <div class="success-actions">
        <router-link to="/boats" class="btn-primary">
          {{ $t('payment.success.viewBoats') }}
        </router-link>
        <router-link to="/dashboard" class="btn-secondary">
          {{ $t('payment.success.goToDashboard') }}
        </router-link>
      </div>

      <div class="info-box">
        <p>{{ $t('payment.success.receiptInfo') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const paymentIntent = ref(null)

onMounted(() => {
  // Get payment intent ID from query params
  paymentIntent.value = route.query.payment_intent || null
  
  console.log('Payment successful! Payment Intent:', paymentIntent.value)
})
</script>

<style scoped>
.payment-success-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.success-container {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 12px;
  padding: 3rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.success-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.success-container h1 {
  color: #4CAF50;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.success-message {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.payment-details {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: left;
}

.payment-details h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #2c3e50;
  font-family: monospace;
  font-size: 0.9rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
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
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.btn-secondary {
  background-color: #fff;
  color: #666;
  border: 1px solid #dee2e6;
}

.btn-secondary:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
}

.info-box {
  padding: 1rem;
  background-color: #e3f2fd;
  border-left: 4px solid #2196F3;
  border-radius: 4px;
  text-align: left;
}

.info-box p {
  margin: 0;
  color: #1565c0;
  font-size: 0.95rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .success-container {
    padding: 2rem 1.5rem;
  }

  .success-container h1 {
    font-size: 1.5rem;
  }

  .success-message {
    font-size: 1rem;
  }

  .success-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
