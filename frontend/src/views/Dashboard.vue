<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <div class="welcome-content">
        <h1>{{ $t('dashboard.welcome') }}, {{ authStore.fullName }}! 👋</h1>
        <p class="welcome-subtitle">{{ $t('dashboard.subtitle') }}</p>
        <div class="user-info">
          <div class="info-item">
            <span class="info-icon">📧</span>
            <span>{{ authStore.user?.email }}</span>
          </div>
          <div class="info-item">
            <span class="info-icon">🏛️</span>
            <span>{{ authStore.user?.club_affiliation }}</span>
          </div>
        </div>
      </div>
    </section>

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
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.crewMembers }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.crewMembers') }}</div>
          </div>
        </div>

        <!-- Boats -->
        <div class="stat-card">
          <div class="stat-icon">🚣</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.boats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.boats') }}</div>
          </div>
        </div>

        <!-- Complete Boats -->
        <div class="stat-card highlight">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completeBoats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.completeBoats') }}</div>
          </div>
        </div>

        <!-- Paid Boats -->
        <div class="stat-card success">
          <div class="stat-icon">💳</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.paidBoats }}</div>
            <div class="stat-label">{{ $t('dashboard.stats.paidBoats') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="actions-section">
      <h2>{{ $t('dashboard.quickActions') }}</h2>
      <div class="actions-grid">
        <router-link to="/crew" class="action-card">
          <div class="action-icon">👥</div>
          <h3>{{ $t('dashboard.actions.manageCrew.title') }}</h3>
          <p>{{ $t('dashboard.actions.manageCrew.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>

        <router-link to="/boats" class="action-card">
          <div class="action-icon">🚣</div>
          <h3>{{ $t('dashboard.actions.manageBoats.title') }}</h3>
          <p>{{ $t('dashboard.actions.manageBoats.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>

        <router-link to="/payment" class="action-card">
          <div class="action-icon">💳</div>
          <h3>{{ $t('dashboard.actions.makePayment.title') }}</h3>
          <p>{{ $t('dashboard.actions.makePayment.description') }}</p>
          <span class="action-arrow">→</span>
        </router-link>
      </div>
    </section>

    <!-- Registration Status -->
    <section v-if="stats.boats > 0" class="status-section">
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
      </div>
    </section>

    <!-- Empty State -->
    <section v-if="!loading && stats.boats === 0" class="empty-state">
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

const authStore = useAuthStore();
const crewStore = useCrewStore();
const boatStore = useBoatStore();

const loading = ref(true);
const stats = ref({
  crewMembers: 0,
  boats: 0,
  incompleteBoats: 0,
  completeBoats: 0,
  paidBoats: 0
});

const loadDashboardData = async () => {
  try {
    loading.value = true;
    
    // Load crew members and boats
    await Promise.all([
      crewStore.fetchCrewMembers(),
      boatStore.fetchBoats()
    ]);

    // Calculate stats
    stats.value.crewMembers = crewStore.crewMembers.length;
    stats.value.boats = boatStore.boats.length;
    
    // Count boats by status
    stats.value.incompleteBoats = boatStore.boats.filter(b => b.status === 'incomplete').length;
    stats.value.completeBoats = boatStore.boats.filter(b => b.status === 'complete').length;
    stats.value.paidBoats = boatStore.boats.filter(b => b.status === 'paid').length;
    
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

/* Welcome Section */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.welcome-content h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.welcome-subtitle {
  font-size: 1.125rem;
  opacity: 0.95;
  margin-bottom: 1.5rem;
}

.user-info {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.info-icon {
  font-size: 1.25rem;
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
  font-size: 2.5rem;
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
  font-size: 3rem;
  margin-bottom: 1rem;
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
  .welcome-section {
    padding: 2rem 1.5rem;
  }

  .welcome-content h1 {
    font-size: 1.5rem;
  }

  .user-info {
    flex-direction: column;
    gap: 0.75rem;
  }

  .stats-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }

  .status-row {
    grid-template-columns: 100px 1fr 50px;
    gap: 0.75rem;
  }

  .status-label {
    font-size: 0.875rem;
  }
}
</style>
