<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>Administration</h1>
      <p class="subtitle">{{ $t('admin.dashboard.subtitle') }}</p>
    </div>

    <div class="admin-sections">
      <!-- Quick Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalRegistrations }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.totalRegistrations') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalPayments }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.totalPayments') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🚣</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.boatsAvailable }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.boatsAvailable') }}</div>
          </div>
        </div>
      </div>

      <!-- Configuration Sections -->
      <div class="config-sections">
        <h2>{{ $t('admin.dashboard.configuration') }}</h2>
        
        <div class="section-grid">
          <router-link to="/admin/events" class="section-card">
            <div class="section-icon">📅</div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.eventDates') }}</h3>
              <p>{{ $t('admin.dashboard.eventDatesDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/pricing" class="section-card">
            <div class="section-icon">💵</div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.pricing') }}</h3>
              <p>{{ $t('admin.dashboard.pricingDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/boats" class="section-card">
            <div class="section-icon">⛵</div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.boatInventory') }}</h3>
              <p>{{ $t('admin.dashboard.boatInventoryDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/exports" class="section-card">
            <div class="section-icon">📊</div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.dataExports') }}</h3>
              <p>{{ $t('admin.dashboard.dataExportsDesc') }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const stats = ref({
  totalRegistrations: 0,
  totalPayments: 0,
  boatsAvailable: 0,
});

onMounted(async () => {
  // TODO: Fetch real stats from API
  // For now, using placeholder values
  stats.value = {
    totalRegistrations: 0,
    totalPayments: 0,
    boatsAvailable: 0,
  };
});
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.admin-header {
  margin-bottom: 3rem;
}

.admin-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 0.25rem;
}

.config-sections h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  display: flex;
  gap: 1rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.section-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.section-icon {
  font-size: 2.5rem;
}

.section-content h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.section-content p {
  font-size: 0.9rem;
  color: #7f8c8d;
  line-height: 1.5;
}
</style>
