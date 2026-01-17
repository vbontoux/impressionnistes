<template>
  <div class="dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Stats Grid -->
    <section v-else class="stats-section">
      <h2>{{ $t('dashboard.quickStats') }}</h2>
      <div class="stats-grid">
        <!-- Crew Members -->
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.crewMembers }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.crewMembers') }}</div>
          </div>
        </div>

        <!-- Boats -->
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Rower 1 -->
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <path d="M7 4.5 L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 4.5 L8 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="7" x2="10" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Rower 2 -->
              <circle cx="17" cy="3" r="1.5" fill="currentColor"/>
              <path d="M17 4.5 L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 4.5 L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="13" y1="7" x2="20" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Boat -->
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              
              <!-- Wave -->
              <path d="M1 20C1 20 3 18.5 6 18.5C9 18.5 11 20 14 20C17 20 19 18.5 22 18.5C23 18.5 24 20 24 20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.boats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.boats') }}</div>
          </div>
        </div>

        <!-- Complete Boats -->
        <div class="stat-card highlight">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M22 4L12 14.01L9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completeBoats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.completeBoats') }}</div>
          </div>
        </div>

        <!-- Paid Boats -->
        <div class="stat-card success">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.paidBoats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.paidBoats') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Payment Summary and Registration Status Side by Side -->
    <section v-if="stats.boats > 0" class="summary-grid-section">
      <!-- Payment Summary -->
      <div class="summary-widget">
        <h2>{{ $t('payment.summary.title') }}</h2>
        <PaymentSummaryWidget :show-title="false" />
      </div>

      <!-- Registration Status -->
      <div class="summary-widget">
        <h2>{{ $t('dashboard.registrationStatus') }}</h2>
        <div class="status-card">
          <div class="status-row">
            <span class="status-label">{{ $t('dashboard.status.incomplete') }}</span>
            <div class="status-bar">
              <div 
                class="status-fill incomplete" 
                :style="{ width: getPercentage(stats.incompleteBoats) + '%' }"
              ></div>
            </div>
            <span class="status-value">{{ stats.incompleteBoats }}</span>
          </div>
          <div class="status-row">
            <span class="status-label">{{ $t('dashboard.status.complete') }}</span>
            <div class="status-bar">
              <div 
                class="status-fill complete" 
                :style="{ width: getPercentage(stats.completeBoats) + '%' }"
              ></div>
            </div>
            <span class="status-value">{{ stats.completeBoats }}</span>
          </div>
          <div class="status-row">
            <span class="status-label">{{ $t('dashboard.status.paid') }}</span>
            <div class="status-bar">
              <div 
                class="status-fill paid" 
                :style="{ width: getPercentage(stats.paidBoats) + '%' }"
              ></div>
            </div>
            <span class="status-value">{{ stats.paidBoats }}</span>
          </div>
          <div class="status-row">
            <span class="status-label">{{ $t('dashboard.status.free') }}</span>
            <div class="status-bar">
              <div 
                class="status-fill free" 
                :style="{ width: getPercentage(stats.freeBoats) + '%' }"
              ></div>
            </div>
            <span class="status-value">{{ stats.freeBoats }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Payment Summary Only (when no boats) -->
    <section v-else class="payment-summary-section">
      <h2>{{ $t('payment.summary.title') }}</h2>
      <PaymentSummaryWidget :show-title="false" />
    </section>

    <!-- Quick Actions -->
    <section class="actions-section">
      <h2>{{ $t('dashboard.quickActions') }}</h2>
      <div class="actions-grid">
        <router-link to="/crew" class="action-card">
          <div class="action-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>{{ $t('dashboard.actions.manageCrew.title') }}</h3>
          <p>{{ $t('dashboard.actions.manageCrew.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>

        <router-link to="/boats" class="action-card">
          <div class="action-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Rower 1 -->
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <path d="M7 4.5 L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 4.5 L8 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="7" x2="10" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Rower 2 -->
              <circle cx="17" cy="3" r="1.5" fill="currentColor"/>
              <path d="M17 4.5 L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 4.5 L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="13" y1="7" x2="20" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Boat -->
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              
              <!-- Wave -->
              <path d="M1 20C1 20 3 18.5 6 18.5C9 18.5 11 20 14 20C17 20 19 18.5 22 18.5C23 18.5 24 20 24 20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>{{ $t('dashboard.actions.manageBoats.title') }}</h3>
          <p>{{ $t('dashboard.actions.manageBoats.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>

        <router-link to="/payment" class="action-card">
          <div class="action-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>{{ $t('dashboard.actions.makePayment.title') }}</h3>
          <p>{{ $t('dashboard.actions.makePayment.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>
      </div>
    </section>

    <!-- Empty State -->
    <section v-if="!loading && stats.crewMembers === 0 && stats.boats === 0" class="empty-state">
      <div class="empty-icon">🚀</div>
      <h3>{{ $t('dashboard.emptyState.title') }}</h3>
      <p>{{ $t('dashboard.emptyState.description') }}</p>
      <router-link to="/crew" class="btn btn-primary">
        {{ $t('dashboard.emptyState.getStarted') }}
      </router-link>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/authStore';
import { useCrewStore } from '../stores/crewStore';
import { useBoatStore } from '../stores/boatStore';
import PaymentSummaryWidget from '../components/PaymentSummaryWidget.vue';

const authStore = useAuthStore();
const crewStore = useCrewStore();
const boatStore = useBoatStore();

const loading = ref(true);
const stats = ref({
  crewMembers: 0,
  boats: 0,
  incompleteBoats: 0,
  completeBoats: 0,
  paidBoats: 0,
  freeBoats: 0
});

const loadDashboardData = async () => {
  try {
    loading.value = true;
    
    // Load crew members and boats
    await Promise.all([
      crewStore.fetchCrewMembers(),
      boatStore.fetchBoatRegistrations()
    ]);

    // Calculate stats
    stats.value.crewMembers = crewStore.crewMembers.length;
    stats.value.boats = boatStore.boatRegistrations.length;
    
    // Count boats by status
    stats.value.incompleteBoats = boatStore.boatRegistrations.filter(b => b.registration_status === 'incomplete').length;
    stats.value.completeBoats = boatStore.boatRegistrations.filter(b => b.registration_status === 'complete').length;
    stats.value.paidBoats = boatStore.boatRegistrations.filter(b => b.registration_status === 'paid').length;
    stats.value.freeBoats = boatStore.boatRegistrations.filter(b => b.registration_status === 'free').length;
    
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
  } finally {
    loading.value = false;
  }
};

const getPercentage = (value) => {
  if (stats.value.boats === 0) return 0;
  return (value / stats.value.boats) * 100;
};

onMounted(() => {
  loadDashboardData();
});
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

/* Loading */
.loading-container {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Sections */
section {
  margin-bottom: 2rem;
}

section h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #333;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 100%;
  height: 100%;
  color: #667eea;
}

.stat-card.highlight .stat-icon svg {
  color: white;
}

.stat-card.success .stat-icon svg {
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: #333;
  transition: all 0.3s;
  position: relative;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
}

.action-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon svg {
  width: 100%;
  height: 100%;
  color: #667eea;
  transition: color 0.3s;
}

.action-card:hover .action-icon svg {
  color: #4CAF50;
}

.action-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.action-card p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.action-arrow {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 1.5rem;
  color: #667eea;
  transition: transform 0.3s;
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
}

/* Summary Grid Section - Side by Side Layout */
.summary-grid-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-widget {
  /* Each widget takes up its grid cell */
}

.payment-summary-section {
  margin-bottom: 2rem;
}

/* Status Section */
.status-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-row {
  display: grid;
  grid-template-columns: 150px 1fr 60px;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.status-row:last-child {
  margin-bottom: 0;
}

.status-label {
  font-weight: 600;
  color: #333;
}

.status-bar {
  height: 24px;
  background: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 12px;
}

.status-fill.incomplete {
  background: #ff9800;
}

.status-fill.complete {
  background: #667eea;
}

.status-fill.paid {
  background: #4CAF50;
}

.status-fill.free {
  background: #2196F3;
}

.status-value {
  font-weight: 700;
  font-size: 1.125rem;
  text-align: right;
  color: #333;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.empty-state p {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.125rem;
}

.btn {
  display: inline-block;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 0 1rem;
  }

  /* Sections */
  section {
    margin-bottom: 1.5rem;
  }

  section h2 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  /* Summary Grid - Stack vertically on mobile */
  .summary-grid-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  /* Stats Grid - Stack vertically on mobile */
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-label {
    font-size: 0.8125rem;
  }

  /* Actions Grid - Stack vertically on mobile */
  .actions-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .action-card {
    padding: 1.5rem;
    /* Ensure touch target is accessible */
    min-height: 44px;
  }

  .action-icon {
    width: 48px;
    height: 48px;
  }

  .action-card h3 {
    font-size: 1.125rem;
  }

  .action-card p {
    font-size: 0.9375rem;
  }

  .action-arrow {
    bottom: 1rem;
    right: 1rem;
  }

  /* Status Section */
  .status-card {
    padding: 1.5rem 1rem;
  }

  .status-row {
    grid-template-columns: 80px 1fr 50px;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .status-label {
    font-size: 0.8125rem;
  }

  .status-bar {
    height: 20px;
  }

  .status-value {
    font-size: 1rem;
  }

  /* Empty State */
  .empty-state {
    padding: 3rem 1.5rem;
  }

  .empty-icon {
    font-size: 3rem;
  }

  .empty-state h3 {
    font-size: 1.25rem;
  }

  .empty-state p {
    font-size: 1rem;
  }

  .btn {
    width: 100%;
    padding: 1rem;
    /* Ensure touch target meets minimum */
    min-height: 44px;
  }

  /* Loading */
  .loading-container {
    padding: 2rem 1rem;
  }
}

/* Extra small mobile devices */
@media (max-width: 375px) {
  .dashboard {
    padding: 0 0.75rem;
  }

  section h2 {
    font-size: 1.125rem;
  }

  .stat-card {
    padding: 0.875rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .action-card {
    padding: 1.25rem;
  }

  .action-card h3 {
    font-size: 1rem;
  }

  .action-card p {
    font-size: 0.875rem;
  }

  .status-row {
    grid-template-columns: 70px 1fr 45px;
  }

  .status-label {
    font-size: 0.75rem;
  }

  .status-bar {
    height: 18px;
  }

  .status-value {
    font-size: 0.9375rem;
  }
}
</style>
