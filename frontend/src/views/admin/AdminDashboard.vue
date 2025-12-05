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
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2"/>
                <line x1="9" y1="4" x2="9" y2="9" stroke="currentColor" stroke-width="2"/>
                <line x1="15" y1="4" x2="15" y2="9" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.eventDates') }}</h3>
              <p>{{ $t('admin.dashboard.eventDatesDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/pricing" class="section-card">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6C16.5 4.5 14.5 4 12 4C8 4 5 7 5 12C5 17 8 20 12 20C14.5 20 16.5 19.5 18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="3" y1="10" x2="13" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="3" y1="14" x2="13" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.pricing') }}</h3>
              <p>{{ $t('admin.dashboard.pricingDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/boats" class="section-card">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="8" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="8" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="8" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <circle cx="4" cy="6" r="1.5" fill="currentColor"/>
                <circle cx="4" cy="12" r="1.5" fill="currentColor"/>
                <circle cx="4" cy="18" r="1.5" fill="currentColor"/>
              </svg>
            </div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.boatInventory') }}</h3>
              <p>{{ $t('admin.dashboard.boatInventoryDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/exports" class="section-card">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="18" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="9 15 12 18 15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
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
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-icon svg {
  width: 100%;
  height: 100%;
  color: #3498db;
  transition: color 0.3s;
}

.section-card:hover .section-icon svg {
  color: #2980b9;
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
