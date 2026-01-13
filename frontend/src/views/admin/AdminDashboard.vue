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
      </div>

      <!-- Admin Impersonation Card -->
      <AdminImpersonationCard />

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

          <router-link to="/admin/crew" class="section-card">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.crewMembers') }}</h3>
              <p>{{ $t('admin.dashboard.crewMembersDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/boat-registrations" class="section-card">
            <div class="section-icon">
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
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.boatRegistrations') }}</h3>
              <p>{{ $t('admin.dashboard.boatRegistrationsDesc') }}</p>
            </div>
          </router-link>

          <router-link to="/admin/club-managers" class="section-card">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Single baseball cap (larger, centered) -->
                <g transform="translate(0, 2) scale(0.045)">
                  <path fill="currentColor" fill-rule="nonzero" d="M46.5 287.865c10.067-2.112 20.076-3.449 29.992-4.029 3.145-.184 6.279-.291 9.4-.322 42.371-.686 72.594 13.091 111.097 33.321 25.909 13.612 49.915 26.225 78.75 25.82 23.076-.325 46.832-7.37 68.81-18.557 20.374-10.37 39.15-24.266 54.415-39.661-15.074.177-30.862-1.911-47.075-5.343-27.013-5.31-53.697-14.021-79.736-22.523-13.061-4.265-25.959-8.477-38.61-12.16-9.563-2.655-19.005-5.014-28.242-6.888-15.172-3.078-31.847-6.568-47.409-5.105-11.46 1.076-23.589 4.67-39.308 12.151-6.645 3.463-13.901 7.643-22.326 12.531-15.287 8.868-31.636 18.968-45.34 27.874l-4.418 2.891zm73.801 8.825l-62.933 33.616C42 338.155 29.722 340.741 20.71 340.039c-4.51-.352-8.317-1.526-11.387-3.296-16.384-9.435-8.967-30.139 5.278-38.472.095-.097.196-.191.3-.282 4.92-4.285 16.386-12.287 30.522-21.473 13.922-9.047 30.437-19.253 45.776-28.152a1990.26 1990.26 0 016.98-4.035c2.667-34.677 8.678-67.162 19.567-96.033 11.203-29.703 27.561-55.56 50.726-76.023 25.078-22.156 55.843-36.499 88.35-43.321 17.275-3.625 35.05-5.128 52.728-4.555 1.236-12.416 11.873-22.11 23.889-24.026A28.273 28.273 0 01337.88 0c4.64 0 8.925 1.155 12.647 3.15 8.507 4.556 13.934 13.477 13.934 23.144 0 2.164-.278 4.362-.857 6.553 3.092.888 6.165 1.845 9.205 2.869a206.94 206.94 0 0111.014 4.055c13.779 5.526 26.98 12.355 39.112 20.301 11.882 7.781 22.79 16.67 32.269 26.486 20.495 21.223 35.266 46.818 44.603 76.547 9.238 29.413 13.142 62.884 11.999 100.186l-.01.567c-.491 6.598-2.207 11.53-5.274 15.004-3.302 3.741-7.823 5.529-13.7 5.592l-79.709-.327c-17.115 19.096-39.463 36.503-63.98 48.982-23.235 11.827-48.511 19.276-73.274 19.625-31.405.443-56.495-12.741-83.574-26.968-21.442-11.266-44.184-23.216-71.984-29.076zm-6.251-61.143c9.114-4.746 17.241-8.25 25.789-10.524 18.442-4.907 36.513-3.136 55.015-.104 13.965 2.289 28.211 5.895 42.696 10.142 14.86 4.157 29.902 8.971 44.945 13.787 23.844 7.63 47.687 15.259 70.483 20.158 17.582 3.505 35.224 5.528 52.779 5.016.434-3.308.833-6.598 1.196-9.868 2.082-22.735 3.113-45.277 2.258-67.467-.878-17.095-2.932-33.568-6.178-49.414-6.294-30.724-17.076-59.119-32.427-85.138a251.813 251.813 0 00-14.539-20.798 5.078 5.078 0 01-.499-.103c-6.413-1.671-13.143-3.041-19.917-4.099-25.77-4.03-51.012-3.709-76.773 1.698-30.864 6.476-60.023 20.049-83.726 40.99-21.84 19.294-37.312 43.803-47.959 72.03-9.791 25.963-15.512 55.098-18.353 86.25a259.246 259.246 0 015.21-2.556z"/>
                </g>
              </svg>
            </div>
            <div class="section-content">
              <h3>{{ $t('admin.dashboard.clubManagers') }}</h3>
              <p>{{ $t('admin.dashboard.clubManagersDesc') }}</p>
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
import apiClient from '../../services/apiClient';
import AdminImpersonationCard from '../../components/AdminImpersonationCard.vue';

const { t } = useI18n();

const stats = ref({
  totalCrewMembers: 0,
  totalBoatRegistrations: 0,
  totalPayments: 0,
});

const loading = ref(true);
const error = ref(null);

const loadStats = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await apiClient.get('/admin/stats');
    const data = response.data.data;
    
    stats.value = {
      totalCrewMembers: data.total_crew_members || 0,
      totalBoatRegistrations: data.total_boat_registrations || 0,
      totalPayments: data.total_payments || 0,
    };
  } catch (err) {
    console.error('Failed to load stats:', err);
    error.value = t('admin.dashboard.statsError');
    // Keep zeros on error
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadStats();
});
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xxl);
}

.admin-header {
  margin-bottom: var(--spacing-3xl);
}

.admin-header h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-3xl);
}

.stat-card {
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  border: 1px solid var(--color-border);
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
  color: var(--color-primary);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-dark);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  margin-top: var(--spacing-xs);
}

.config-sections h2 {
  font-size: var(--font-size-2xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-semibold);
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-xl);
}

.section-card {
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  text-decoration: none;
  display: flex;
  gap: var(--spacing-lg);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.section-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
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
  color: var(--color-primary);
  transition: color 0.3s;
}

.section-card:hover .section-icon svg {
  color: var(--color-primary-dark);
}

.section-content h3 {
  font-size: var(--font-size-lg);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.section-content p {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  line-height: 1.5;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: var(--spacing-lg);
  }

  .admin-header h1 {
    font-size: var(--font-size-2xl);
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }

  .section-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }

  .stat-card,
  .section-card {
    padding: var(--spacing-lg);
  }
}
</style>
