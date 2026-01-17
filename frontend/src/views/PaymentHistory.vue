<template>
  <div class="payment-history-view" :key="`payments-${payments.length}`">
    <ListHeader
      :title="$t('payment.history.title')"
      :subtitle="$t('payment.history.subtitle')"
      v-model:viewMode="viewMode"
    />

    <ListFilters
      v-model:searchQuery="searchQuery"
      :searchPlaceholder="$t('payment.history.search')"
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('payment.history.startDate') }}&nbsp;:</label>
          <input 
            type="date" 
            v-model="startDate" 
            class="filter-input"
            :max="endDate || undefined"
          />
        </div>

        <div class="filter-group">
          <label>{{ $t('payment.history.endDate') }}&nbsp;:</label>
          <input 
            type="date" 
            v-model="endDate" 
            class="filter-input"
            :min="startDate || undefined"
          />
        </div>
      </template>
    </ListFilters>

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

    <!-- Empty State - only show if NOT loading and we have 0 payments -->
    <EmptyState 
      v-else-if="!loading && filteredPayments.length === 0" 
      :message="$t('payment.history.noPayments')"
    />

    <!-- Card View (Mobile) -->
    <div v-else-if="viewMode === 'cards'" class="payment-grid-container">
      <!-- Sort controls for card view -->
      <div class="card-sort-controls">
        <label>{{ $t('common.sortBy') }}:</label>
        <select v-model="sortField" class="sort-select">
          <option value="paid_at">{{ $t('payment.history.date') }}</option>
          <option value="amount">{{ $t('payment.history.amount') }}</option>
        </select>
        <button @click="toggleSortDirection" class="sort-direction-btn">
          <span v-if="sortDirection === 'desc'">↓ {{ $t('common.newest') }}</span>
          <span v-else>↑ {{ $t('common.oldest') }}</span>
        </button>
      </div>
      
      <div class="payment-grid">
        <DataCard
          v-for="payment in sortedPayments"
          :key="payment.payment_id"
          :title="formatDate(payment.paid_at)"
        >
        <div class="card-field">
          <span class="label">{{ $t('payment.history.amount') }}:</span>
          <span class="value amount">{{ formatCurrency(payment.amount, payment.currency) }}</span>
        </div>
        
        <div class="card-field">
          <span class="label">{{ $t('payment.history.crews') }}:</span>
          <div v-if="payment.boat_details && payment.boat_details.length > 0" class="crew-details-card">
            <div v-for="(boat, index) in payment.boat_details" :key="index" class="crew-item">
              <span class="boat-number-text">{{ boat.boat_number || 'N/A' }}</span>
              <span v-if="boat.stroke_seat_name" class="stroke-name">
                ({{ boat.stroke_seat_name }})
              </span>
            </div>
          </div>
          <span v-else class="value">{{ payment.boat_registration_ids.length }}</span>
        </div>

        <template #actions>
          <BaseButton 
            size="small" 
            variant="secondary"
            @click.stop="viewReceipt(payment)"
          >
            {{ $t('payment.history.viewReceipt') }}
          </BaseButton>
          <BaseButton 
            size="small" 
            variant="primary"
            @click.stop="downloadInvoice(payment)"
          >
            {{ $t('payment.history.downloadInvoice') }}
          </BaseButton>
        </template>
      </DataCard>
    </div>
    </div>

    <!-- Table View (Desktop) -->
    <div v-else class="payment-table-container">
      <table class="payment-table">
        <thead>
          <tr>
            <th class="sortable-header" @click="handleSort('paid_at')">
              {{ $t('payment.history.date') }} {{ getSortIndicator('paid_at') }}
            </th>
            <th class="sortable-header" @click="handleSort('amount')">
              {{ $t('payment.history.amount') }} {{ getSortIndicator('amount') }}
            </th>
            <th>{{ $t('payment.history.crewDetails') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="payment in sortedPayments" 
            :key="payment.payment_id"
          >
            <td>{{ formatDate(payment.paid_at) }}</td>
            <td class="amount">{{ formatCurrency(payment.amount, payment.currency) }}</td>
            <td>
              <div v-if="payment.boat_details && payment.boat_details.length > 0" class="crew-details">
                <div v-for="(boat, index) in payment.boat_details" :key="index" class="crew-item">
                  <span class="boat-number-text">{{ boat.boat_number || 'N/A' }}</span>
                  <span v-if="boat.stroke_seat_name" class="stroke-name">
                    ({{ boat.stroke_seat_name }})
                  </span>
                </div>
              </div>
              <span v-else class="no-race-text">
                {{ payment.boat_registration_ids.length }} {{ $t('payment.history.crews') }}
              </span>
            </td>
            <td class="actions-cell">
              <BaseButton 
                size="small" 
                variant="secondary"
                @click.stop="viewReceipt(payment)"
              >
                {{ $t('payment.history.viewReceipt') }}
              </BaseButton>
              <BaseButton 
                size="small" 
                variant="primary"
                @click.stop="downloadInvoice(payment)"
              >
                {{ $t('payment.history.downloadInvoice') }}
              </BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Receipt Modal -->
  <BaseModal
    :show="showReceiptModal"
    :title="receiptUrl ? $t('payment.history.receiptTitle') : $t('payment.history.paymentDetails')"
    size="large"
    @close="showReceiptModal = false"
  >
    <!-- Stripe Receipt iframe -->
    <div v-if="receiptUrl" class="receipt-container">
      <iframe
        :src="receiptUrl"
        class="receipt-iframe"
        frameborder="0"
      ></iframe>
    </div>

    <!-- Payment Details fallback -->
    <div v-else-if="selectedPayment" class="payment-details">
      <div class="detail-row">
        <span class="detail-label">{{ $t('payment.history.paymentId') }}:</span>
        <span class="detail-value">{{ selectedPayment.payment_id }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">{{ $t('payment.history.date') }}:</span>
        <span class="detail-value">{{ formatDate(selectedPayment.paid_at) }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">{{ $t('payment.history.amount') }}:</span>
        <span class="detail-value amount">{{ formatCurrency(selectedPayment.amount, selectedPayment.currency) }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">{{ $t('payment.history.crews') }}:</span>
        <span class="detail-value">{{ selectedPayment.boat_count || 0 }}</span>
      </div>
      <div v-if="selectedPayment.stripe_payment_intent_id" class="detail-row">
        <span class="detail-label">Stripe Payment Intent:</span>
        <span class="detail-value code">{{ selectedPayment.stripe_payment_intent_id }}</span>
      </div>
      
      <div class="detail-note">
        <p>{{ $t('payment.history.noReceiptNote') }}</p>
      </div>
    </div>

    <template #footer>
      <BaseButton
        variant="secondary"
        @click="showReceiptModal = false"
      >
        {{ $t('common.close') }}
      </BaseButton>
      <BaseButton
        v-if="receiptUrl"
        variant="primary"
        @click="window.open(receiptUrl, '_blank')"
      >
        {{ $t('payment.history.openInNewTab') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import paymentService from '../services/paymentService';
import ListHeader from '../components/shared/ListHeader.vue';
import ListFilters from '../components/shared/ListFilters.vue';
import LoadingSpinner from '../components/base/LoadingSpinner.vue';
import MessageAlert from '../components/composite/MessageAlert.vue';
import EmptyState from '../components/base/EmptyState.vue';
import DataCard from '../components/composite/DataCard.vue';
import BaseButton from '../components/base/BaseButton.vue';
import BaseModal from '../components/base/BaseModal.vue';

const { t } = useI18n();

// View mode - restore from localStorage or default to 'cards'
const viewMode = ref(localStorage.getItem('paymentHistoryViewMode') || 'cards');

// Filters
const searchQuery = ref('');
const startDate = ref('');
const endDate = ref('');

// Data
const payments = ref([]);
const loading = ref(false);
const error = ref('');

// Receipt modal
const showReceiptModal = ref(false);
const receiptUrl = ref('');
const selectedPayment = ref(null);

// Sorting - initialize with correct parameters (no data array needed, we handle sorting manually)
const sortField = ref('paid_at');
const sortDirection = ref('desc');

// Get sort indicator for display
const getSortIndicator = (field) => {
  if (sortField.value !== field) return '';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

// Handle sort for table headers
const handleSort = (field) => {
  if (sortField.value === field) {
    // Toggle direction if clicking same field
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // New field, set to descending for dates (newest first)
    sortField.value = field;
    sortDirection.value = field === 'paid_at' ? 'desc' : 'asc';
  }
};

// Toggle sort direction for card view
const toggleSortDirection = () => {
  sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
};

// Fetch payments
const fetchPayments = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const params = {};
    if (startDate.value) {
      params.start_date = new Date(startDate.value).toISOString();
    }
    if (endDate.value) {
      params.end_date = new Date(endDate.value + 'T23:59:59').toISOString();
    }
    
    const response = await paymentService.getPaymentHistory(params);
    payments.value = response.payments || [];
  } catch (err) {
    console.error('Error fetching payments:', err);
    error.value = err.response?.data?.error || t('payment.history.errorLoading');
  } finally {
    loading.value = false;
  }
};

// Filtered payments
const filteredPayments = computed(() => {
  if (!searchQuery.value) {
    return payments.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return payments.value.filter(payment => {
    return (
      formatDate(payment.paid_at).toLowerCase().includes(query) ||
      formatCurrency(payment.amount, payment.currency).toLowerCase().includes(query) ||
      payment.payment_id.toLowerCase().includes(query)
    );
  });
});

// Sorted payments
const sortedPayments = computed(() => {
  const sorted = [...filteredPayments.value];
  
  sorted.sort((a, b) => {
    let aVal = a[sortField.value];
    let bVal = b[sortField.value];
    
    // Handle date sorting
    if (sortField.value === 'paid_at') {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
      
      // Debug: log if we get NaN
      if (isNaN(aVal) || isNaN(bVal)) {
        console.warn('Invalid date in payment:', { 
          a: a.paid_at, 
          b: b.paid_at,
          aVal,
          bVal
        });
      }
    }
    
    // Handle numeric sorting
    if (sortField.value === 'amount') {
      aVal = parseFloat(aVal);
      bVal = parseFloat(bVal);
    }
    
    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1;
    return 0;
  });
  
  return sorted;
});

// Format date - converts UTC to local timezone
const formatDate = (dateString) => {
  if (!dateString) return '-';
  
  // Ensure the date string is treated as UTC
  // If it doesn't end with 'Z', append it to indicate UTC
  let utcDateString = dateString;
  if (!dateString.endsWith('Z') && !dateString.includes('+')) {
    utcDateString = dateString + 'Z';
  }
  
  const date = new Date(utcDateString);
  
  // Verify the date is valid
  if (isNaN(date.getTime())) {
    console.warn('Invalid date:', dateString);
    return '-';
  }
  
  // Use the browser's locale and timezone
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
};

// Format currency
const formatCurrency = (amount, currency = 'EUR') => {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: currency
  }).format(amount);
};

// View receipt
const viewReceipt = (payment) => {
  console.log('🧾 View Receipt clicked');
  console.log('Payment data:', payment);
  console.log('stripe_receipt_url:', payment.stripe_receipt_url);
  
  selectedPayment.value = payment;
  
  if (payment.stripe_receipt_url) {
    console.log('✅ Opening receipt in modal:', payment.stripe_receipt_url);
    receiptUrl.value = payment.stripe_receipt_url;
  } else {
    console.log('⚠️ No Stripe receipt URL found - will show payment details');
    receiptUrl.value = null;
  }
  
  showReceiptModal.value = true;
};

// Download invoice - with guard to prevent double downloads
const downloadingInvoice = ref(false);

const downloadInvoice = async (payment) => {
  // Prevent multiple simultaneous downloads
  if (downloadingInvoice.value) {
    console.log('⚠️ Download already in progress, ignoring duplicate click');
    return;
  }
  
  console.log('📄 Download Invoice clicked');
  console.log('Payment ID:', payment.payment_id);
  
  downloadingInvoice.value = true;
  
  try {
    const blob = await paymentService.downloadInvoice(payment.payment_id);
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `invoice-${payment.payment_id}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('✅ Invoice downloaded successfully');
  } catch (err) {
    console.error('❌ Error downloading invoice:', err);
    error.value = err.response?.data?.error || t('payment.history.errorDownloading');
  } finally {
    // Reset the guard after a short delay to allow the download to complete
    setTimeout(() => {
      downloadingInvoice.value = false;
    }, 1000);
  }
};

// Clear filters
const clearFilters = () => {
  searchQuery.value = '';
  startDate.value = '';
  endDate.value = '';
  fetchPayments();
};

// Watch filters
watch([startDate, endDate], () => {
  fetchPayments();
});

// Watch view mode and save to localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('paymentHistoryViewMode', newMode);
});

// Load on mount
onMounted(() => {
  fetchPayments();
});
</script>

<style scoped>
.payment-history-view {
  min-height: 100vh;
  background-color: var(--color-bg-light);
  padding: var(--spacing-lg);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-group label {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  white-space: nowrap;
}

.filter-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-base);
}

/* Card View */
.payment-grid-container {
  margin-top: var(--spacing-lg);
}

.card-sort-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-white);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.card-sort-controls label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
}

.sort-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-base);
  background: var(--color-white);
  cursor: pointer;
}

.sort-direction-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-white);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: background-color 0.2s;
}

.sort-direction-btn:hover {
  background: var(--color-light);
}

.payment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.card-field {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
}

.card-field .label {
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.card-field .value {
  font-weight: var(--font-weight-medium);
}

.card-field .value.amount {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

/* Table View */
.payment-table-container {
  background: var(--color-white);
  border-radius: 8px;
  padding: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  overflow-x: auto;
}

.payment-table {
  width: 100%;
  border-collapse: collapse;
}

.payment-table thead {
  background-color: var(--color-light);
}

.payment-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: var(--color-dark);
  border-bottom: 2px solid var(--color-border);
}

.payment-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-base);
}

.payment-table td.amount {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.sortable-header {
  cursor: pointer;
  user-select: none;
}

.sortable-header:hover {
  background-color: var(--color-bg-hover);
}

.actions-cell {
  display: flex;
  gap: var(--spacing-sm);
}

/* Receipt Modal */
.receipt-container {
  width: 100%;
  height: 600px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.receipt-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: var(--border-radius);
}

/* Payment Details */
.payment-details {
  padding: var(--spacing-lg);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-of-type {
  border-bottom: none;
}

.detail-label {
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
}

.detail-value {
  color: var(--color-secondary);
}

.detail-value.amount {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
}

.detail-value.code {
  font-family: monospace;
  font-size: var(--font-size-sm);
  background: var(--color-bg-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
}

.detail-note {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--color-warning);
}

.detail-note p {
  margin: 0;
  color: var(--color-secondary);
  font-size: var(--font-size-sm);
}

/* Responsive - but respect viewMode toggle */
/* No media queries needed - viewMode handles visibility via v-if */
</style>


/* Crew Details Styling */
.crew-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.crew-details-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-xs);
}

.crew-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.stroke-name {
  color: var(--color-muted);
  font-size: var(--font-size-xs);
}
