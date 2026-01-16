<template>
  <div class="admin-payment-analytics">
    <ListHeader
      :title="$t('admin.paymentAnalytics.title')"
      :subtitle="$t('admin.paymentAnalytics.subtitle')"
    />

    <ListFilters
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('admin.paymentAnalytics.startDate') }}&nbsp;:</label>
          <input 
            type="date" 
            v-model="startDate" 
            class="filter-input"
            :max="endDate || undefined"
          />
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.paymentAnalytics.endDate') }}&nbsp;:</label>
          <input 
            type="date" 
            v-model="endDate" 
            class="filter-input"
            :min="startDate || undefined"
          />
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.paymentAnalytics.groupBy') }}&nbsp;:</label>
          <select v-model="groupBy" class="filter-select">
            <option value="day">{{ $t('admin.paymentAnalytics.day') }}</option>
            <option value="week">{{ $t('admin.paymentAnalytics.week') }}</option>
            <option value="month">{{ $t('admin.paymentAnalytics.month') }}</option>
          </select>
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

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card revenue">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="card-content">
            <div class="card-label">{{ $t('admin.paymentAnalytics.totalRevenue') }}</div>
            <div class="card-value">{{ formatCurrency(analytics.total_revenue) }}</div>
          </div>
        </div>

        <div class="summary-card payments">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="card-content">
            <div class="card-label">{{ $t('admin.paymentAnalytics.totalPayments') }}</div>
            <div class="card-value">{{ analytics.total_payments || 0 }}</div>
          </div>
        </div>

        <div class="summary-card outstanding">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="card-content">
            <div class="card-label">{{ $t('admin.paymentAnalytics.outstandingBalance') }}</div>
            <div class="card-value">{{ formatCurrency(analytics.outstanding_balance) }}</div>
          </div>
        </div>

        <div class="summary-card boats">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="card-content">
            <div class="card-label">{{ $t('admin.paymentAnalytics.boatsPaid') }}</div>
            <div class="card-value">{{ analytics.total_boats_paid || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Top Payers Table -->
      <div class="top-payers-section">
        <div class="section-header">
          <h3>{{ $t('admin.paymentAnalytics.topPayers') }}</h3>
          <BaseButton 
            size="small" 
            variant="secondary"
            @click="exportToCSV"
          >
            {{ $t('admin.paymentAnalytics.exportCSV') }}
          </BaseButton>
        </div>

        <div class="table-container">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>{{ $t('admin.paymentAnalytics.rank') }}</th>
                <th>{{ $t('admin.paymentAnalytics.teamManager') }}</th>
                <th>{{ $t('admin.paymentAnalytics.totalPaid') }}</th>
                <th>{{ $t('admin.paymentAnalytics.payments') }}</th>
                <th>{{ $t('admin.paymentAnalytics.boats') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(payer, index) in analytics.top_team_managers" 
                :key="payer.team_manager_id"
              >
                <td class="rank-cell">{{ index + 1 }}</td>
                <td>{{ payer.name }}</td>
                <td class="amount-cell">{{ formatCurrency(payer.total_paid) }}</td>
                <td>{{ payer.payment_count }}</td>
                <td>{{ payer.boat_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import paymentService from '../../services/paymentService';
import ListHeader from '../../components/shared/ListHeader.vue';
import ListFilters from '../../components/shared/ListFilters.vue';
import LoadingSpinner from '../../components/base/LoadingSpinner.vue';
import MessageAlert from '../../components/composite/MessageAlert.vue';
import BaseButton from '../../components/base/BaseButton.vue';

const { t } = useI18n();

// Filters
const startDate = ref('');
const endDate = ref('');
const groupBy = ref('day');

// Data
const analytics = ref({});
const loading = ref(false);
const error = ref('');

// Format currency
const formatCurrency = (amount, currency = 'EUR') => {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: currency
  }).format(amount);
};

// Fetch analytics
const fetchAnalytics = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const params = {
      group_by: groupBy.value
    };
    
    if (startDate.value) {
      params.start_date = new Date(startDate.value).toISOString();
    }
    if (endDate.value) {
      params.end_date = new Date(endDate.value + 'T23:59:59').toISOString();
    }
    
    const response = await paymentService.getPaymentAnalytics(params);
    analytics.value = response;
  } catch (err) {
    console.error('Error fetching analytics:', err);
    error.value = err.response?.data?.error || t('admin.paymentAnalytics.errorLoading');
  } finally {
    loading.value = false;
  }
};

// Export to CSV
const exportToCSV = () => {
  if (!analytics.value.top_team_managers || analytics.value.top_team_managers.length === 0) {
    return;
  }

  const headers = ['Rank', 'Team Manager', 'Total Paid', 'Payments', 'Boats'];
  const rows = analytics.value.top_team_managers.map((payer, index) => [
    index + 1,
    payer.name,
    payer.total_paid,
    payer.payment_count,
    payer.boat_count
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `payment-analytics-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Clear filters
const clearFilters = () => {
  startDate.value = '';
  endDate.value = '';
  groupBy.value = 'day';
  fetchAnalytics();
};

// Watch filters
watch([startDate, endDate, groupBy], () => {
  fetchAnalytics();
});

// Load on mount
onMounted(() => {
  fetchAnalytics();
});
</script>

<style scoped>
.admin-payment-analytics {
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

.filter-input,
.filter-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-base);
}

.analytics-content {
  margin-top: var(--spacing-xl);
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xxl);
}

.summary-card {
  background: var(--color-white);
  border-radius: 8px;
  padding: var(--spacing-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon svg {
  width: 24px;
  height: 24px;
}

.summary-card.revenue .card-icon {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.summary-card.payments .card-icon {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

.summary-card.outstanding .card-icon {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.summary-card.boats .card-icon {
  background-color: var(--color-light);
  color: var(--color-primary);
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  margin-bottom: var(--spacing-xs);
}

.card-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-dark);
}

/* Top Payers Section */
.top-payers-section {
  background: var(--color-white);
  border-radius: 8px;
  padding: var(--spacing-xl);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.section-header h3 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.table-container {
  overflow-x: auto;
}

.analytics-table {
  width: 100%;
  border-collapse: collapse;
}

.analytics-table thead {
  background-color: var(--color-light);
}

.analytics-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: var(--color-dark);
  border-bottom: 2px solid var(--color-border);
}

.analytics-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-base);
}

.rank-cell {
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
}

.amount-cell {
  font-weight: var(--font-weight-semibold);
  color: var(--color-success);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .admin-payment-analytics {
    padding: var(--spacing-md);
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .table-container {
    margin: 0 -1rem;
  }
}
</style>
