<template>
  <div class="payment-view">
    <div class="header">
      <h1>{{ $t('payment.title') }}</h1>
      <p class="subtitle">{{ $t('payment.subtitle') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="paymentStore.loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <!-- Error State -->
    <div v-if="paymentStore.error" class="alert alert-error">
      {{ paymentStore.error }}
    </div>

    <!-- Empty State -->
    <div v-if="!paymentStore.loading && boatsReadyForPayment.length === 0 && rentalsReadyForPayment.length === 0" class="empty-state">
      <div class="empty-icon">💳</div>
      <h2>{{ $t('payment.noBoatsReady') }}</h2>
      <p>{{ $t('payment.noBoatsReadyDescription') }}</p>
      <router-link to="/boats" class="btn-primary">
        {{ $t('payment.goToBoats') }}
      </router-link>
    </div>

    <!-- Payment Content -->
    <div v-else-if="!paymentStore.loading" class="payment-content">
      <!-- Selection Controls -->
      <div class="selection-controls">
        <button 
          @click="selectAll" 
          class="btn-secondary btn-small"
          :disabled="allSelected"
        >
          {{ $t('payment.selectAll') }}
        </button>
        <button 
          @click="deselectAll" 
          class="btn-secondary btn-small"
          :disabled="noneSelected"
        >
          {{ $t('payment.deselectAll') }}
        </button>
        <span class="selection-count">
          {{ $t('payment.selectedCount', { count: totalSelectedCount, total: totalItemsCount }) }}
        </span>
      </div>

      <!-- Boat Registrations Section -->
      <div v-if="boatsReadyForPayment.length > 0" class="payment-section">
        <h2 class="section-title">{{ $t('payment.boatRegistrations') }}</h2>
        <div class="boats-list">
          <BoatPaymentCard
            v-for="boat in boatsReadyForPayment"
            :key="boat.boat_registration_id"
            :boat="boat"
            :selected="isBoatSelected(boat.boat_registration_id)"
            @toggle="toggleBoatSelection(boat.boat_registration_id)"
          />
        </div>
      </div>

      <!-- Rental Boats Section -->
      <div v-if="rentalsReadyForPayment.length > 0" class="payment-section">
        <h2 class="section-title">{{ $t('payment.rentalBoats') }}</h2>
        <div class="boats-list">
          <RentalPaymentCard
            v-for="rental in rentalsReadyForPayment"
            :key="rental.rental_boat_id"
            :rental="rental"
            :selected="isRentalSelected(rental.rental_boat_id)"
            @toggle="toggleRentalSelection(rental.rental_boat_id)"
          />
        </div>
      </div>

      <!-- Payment Summary (Sticky) -->
      <div class="payment-summary-container" v-if="totalSelectedCount > 0">
        <PaymentSummary
          :selected-boats="selectedBoats"
          :selected-rentals="selectedRentals"
          :total="totalAmount"
          @proceed="proceedToCheckout"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePaymentStore } from '../stores/paymentStore'
import { useRaceStore } from '../stores/raceStore'
import { useI18n } from 'vue-i18n'
import BoatPaymentCard from '../components/BoatPaymentCard.vue'
import RentalPaymentCard from '../components/RentalPaymentCard.vue'
import PaymentSummary from '../components/PaymentSummary.vue'

const router = useRouter()
const paymentStore = usePaymentStore()
const raceStore = useRaceStore()

const selectedBoatIds = ref(new Set())
const selectedRentalIds = ref(new Set())

// Computed properties
const boatsReadyForPayment = computed(() => paymentStore.boatsReadyForPayment)
const rentalsReadyForPayment = computed(() => paymentStore.rentalsReadyForPayment)

const selectedBoats = computed(() => 
  boatsReadyForPayment.value.filter(boat => 
    selectedBoatIds.value.has(boat.boat_registration_id)
  )
)

const selectedRentals = computed(() => 
  rentalsReadyForPayment.value.filter(rental => 
    selectedRentalIds.value.has(rental.rental_boat_id)
  )
)

const totalSelectedCount = computed(() => selectedBoatIds.value.size + selectedRentalIds.value.size)

const totalItemsCount = computed(() => boatsReadyForPayment.value.length + rentalsReadyForPayment.value.length)

const allSelected = computed(() => 
  totalSelectedCount.value === totalItemsCount.value && totalItemsCount.value > 0
)

const noneSelected = computed(() => totalSelectedCount.value === 0)

const totalAmount = computed(() => paymentStore.totalAmount)

// Methods
const isBoatSelected = (boatId) => {
  return selectedBoatIds.value.has(boatId)
}

const isRentalSelected = (rentalId) => {
  return selectedRentalIds.value.has(rentalId)
}

const toggleBoatSelection = (boatId) => {
  if (selectedBoatIds.value.has(boatId)) {
    selectedBoatIds.value.delete(boatId)
  } else {
    selectedBoatIds.value.add(boatId)
  }
  selectedBoatIds.value = new Set(selectedBoatIds.value)
  paymentStore.setSelectedBoats(Array.from(selectedBoatIds.value))
}

const toggleRentalSelection = (rentalId) => {
  if (selectedRentalIds.value.has(rentalId)) {
    selectedRentalIds.value.delete(rentalId)
  } else {
    selectedRentalIds.value.add(rentalId)
  }
  selectedRentalIds.value = new Set(selectedRentalIds.value)
  paymentStore.setSelectedRentals(Array.from(selectedRentalIds.value))
}

const selectAll = () => {
  selectedBoatIds.value = new Set(
    boatsReadyForPayment.value.map(boat => boat.boat_registration_id)
  )
  selectedRentalIds.value = new Set(
    rentalsReadyForPayment.value.map(rental => rental.rental_boat_id)
  )
  paymentStore.setSelectedBoats(Array.from(selectedBoatIds.value))
  paymentStore.setSelectedRentals(Array.from(selectedRentalIds.value))
}

const deselectAll = () => {
  selectedBoatIds.value = new Set()
  selectedRentalIds.value = new Set()
  paymentStore.setSelectedBoats([])
  paymentStore.setSelectedRentals([])
}

const proceedToCheckout = () => {
  // Store selected boats and rentals in payment store
  paymentStore.setSelectedBoats(Array.from(selectedBoatIds.value))
  paymentStore.setSelectedRentals(Array.from(selectedRentalIds.value))
  // Navigate to checkout
  router.push('/payment/checkout')
}

// Load boats, rentals, and races on mount
onMounted(async () => {
  // Load races first so they're available for display
  if (raceStore.races.length === 0) {
    await raceStore.fetchRaces()
  }
  await paymentStore.fetchAllForPayment()
  
  console.log('Payment page loaded')
  console.log('Boats ready for payment:', boatsReadyForPayment.value.length)
  console.log('Rentals ready for payment:', rentalsReadyForPayment.value.length)
  console.log('Rentals data:', rentalsReadyForPayment.value)
})
</script>

<style scoped>
.payment-view {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.subtitle {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.alert-error {
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
  border-radius: 4px;
  margin-bottom: 1rem;
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

.empty-state h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 2rem;
}

.payment-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.payment-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e1e8ed;
}

.selection-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.selection-count {
  margin-left: auto;
  color: #666;
  font-weight: 500;
}

.boats-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.payment-summary-container {
  position: sticky;
  bottom: 0;
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
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
}

.btn-secondary {
  background-color: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .payment-view {
    padding: 1rem;
  }

  .selection-controls {
    flex-wrap: wrap;
  }

  .selection-count {
    width: 100%;
    margin-left: 0;
    margin-top: 0.5rem;
    text-align: center;
  }
}
</style>
