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
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalCrewMembers }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.totalCrewMembers') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <path d="M7 4.5 L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 4.5 L8 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="7" x2="10" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <circle cx="17" cy="3" r="1.5" fill="currentColor"/>
              <path d="M17 4.5 L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 4.5 L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="13" y1="7" x2="20" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              <path d="M1 16C1 16 3 14.5 6 14.5C9 14.5 11 16 14 16C17 16 19 14.5 22 14.5C23 14.5 24 16 24 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalBoatRegistrations }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.totalBoatRegistrations') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalPayments }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.totalPayments') }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="8" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="4" cy="6" r="1.5" fill="currentColor"/>
              <circle cx="4" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="4" cy="18" r="1.5" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.rentalBoatsReserved }}</div>
            <div class="stat-label">{{ $t('admin.dashboard.rentalBoatsReserved') }}</div>
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
  totalCrewMembers: 0,
  totalBoatRegistrations: 0,
  totalPayments: 0,
  rentalBoatsReserved: 0,
});

onMounted(async () => {
  // TODO: Fetch real stats from API
  // For now, using placeholder values
  stats.value = {
    totalCrewMembers: 0,
    totalBoatRegistrations: 0,
    totalPayments: 0,
    rentalBoatsReserved: 0,
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
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 100%;
  height: 100%;
  color: #3498db;
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
