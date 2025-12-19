<template>
  <div class="admin-data-export">
    <div class="page-header">
      <h1>{{ $t('admin.dashboard.dataExports') }}</h1>
      <p class="subtitle">{{ $t('admin.dataExport.subtitle') }}</p>
    </div>

    <div class="export-sections">
      <!-- CrewTimer Export Section -->
      <div class="export-card crewtimer-card">
        <div class="export-header">
          <div class="export-title-row">
            <img 
              src="https://crewtimer.com/favicon.ico" 
              alt="CrewTimer" 
              class="crewtimer-icon"
              @error="handleIconError"
            />
            <h2>{{ $t('admin.dataExport.crewTimerExport') }}</h2>
          </div>
          <p class="export-description">{{ $t('admin.dataExport.crewTimerDescription') }}</p>
        </div>
        
        <div class="export-actions">
          <button 
            @click="exportCrewTimer" 
            class="btn btn-primary"
            :disabled="loadingCrewTimer"
          >
            <span v-if="!loadingCrewTimer">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="18" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="9 15 12 18 15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ $t('admin.dataExport.exportToCrewTimer') }}
            </span>
            <span v-else>
              <span class="spinner"></span>
              {{ $t('admin.dataExport.exporting') }}
            </span>
          </button>
        </div>

        <div v-if="crewTimerStats" class="export-stats">
          <div class="stat-item">
            <span class="stat-label">{{ $t('admin.dataExport.totalRaces') }}:</span>
            <span class="stat-value">{{ crewTimerStats.totalRaces }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ $t('admin.dataExport.totalBoats') }}:</span>
            <span class="stat-value">{{ crewTimerStats.totalBoats }}</span>
          </div>
        </div>
      </div>

      <!-- Standard CSV Exports Section -->
      <div class="export-card">
        <div class="export-header">
          <h2>{{ $t('admin.dataExport.standardExports') }}</h2>
          <p class="export-description">{{ $t('admin.dataExport.standardDescription') }}</p>
        </div>
        
        <div class="export-actions">
          <button 
            @click="exportCrewMembers" 
            class="btn btn-secondary"
            :disabled="loadingCrewMembers"
          >
            <span v-if="!loadingCrewMembers">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
                <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ $t('admin.dataExport.exportCrewMembers') }}
            </span>
            <span v-else>
              <span class="spinner"></span>
              {{ $t('admin.dataExport.exporting') }}
            </span>
          </button>

          <button 
            @click="exportBoatRegistrations" 
            class="btn btn-secondary"
            :disabled="loadingBoatRegistrations"
          >
            <span v-if="!loadingBoatRegistrations">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
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
              {{ $t('admin.dataExport.exportBoatRegistrations') }}
            </span>
            <span v-else>
              <span class="spinner"></span>
              {{ $t('admin.dataExport.exporting') }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="16" r="1" fill="currentColor"/>
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Success Message -->
    <div v-if="success" class="success-message">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>{{ success }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';
import {
  downloadCrewMembersCSV,
  downloadBoatRegistrationsCSV,
  downloadCrewTimerExcel
} from '../../utils/exportFormatters';

const { t } = useI18n();

const loadingCrewTimer = ref(false);
const loadingCrewMembers = ref(false);
const loadingBoatRegistrations = ref(false);
const error = ref(null);
const success = ref(null);
const crewTimerStats = ref(null);

const handleIconError = (event) => {
  // Fallback to a generic icon if CrewTimer icon fails to load
  event.target.style.display = 'none';
};

const clearMessages = () => {
  error.value = null;
  success.value = null;
};

const exportCrewTimer = async () => {
  clearMessages();
  loadingCrewTimer.value = true;
  
  try {
    const response = await apiClient.get('/admin/export/races-json');
    
    if (response.data && response.data.success) {
      const jsonData = response.data.data;
      
      // Update stats
      crewTimerStats.value = {
        totalRaces: jsonData.total_races || 0,
        totalBoats: jsonData.total_boats || 0
      };
      
      // Use formatter to generate and download Excel file
      // Pass the full response structure (with data property) to the formatter
      downloadCrewTimerExcel(response.data);
      
      success.value = t('admin.dataExport.exportSuccess');
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        success.value = null;
      }, 5000);
    }
  } catch (err) {
    console.error('Failed to export CrewTimer data:', err);
    error.value = err.response?.data?.error?.message || t('admin.dataExport.exportError');
  } finally {
    loadingCrewTimer.value = false;
  }
};

const exportCrewMembers = async () => {
  clearMessages();
  loadingCrewMembers.value = true;
  
  try {
    const response = await apiClient.get('/admin/export/crew-members-json');
    
    if (response.data && response.data.success) {
      // Use formatter to generate and download CSV file
      // Pass the full response structure (with data property) to the formatter
      downloadCrewMembersCSV(response.data);
      
      success.value = t('admin.dataExport.exportSuccess');
      
      setTimeout(() => {
        success.value = null;
      }, 5000);
    }
  } catch (err) {
    console.error('Failed to export crew members:', err);
    error.value = err.response?.data?.error?.message || t('admin.dataExport.exportError');
  } finally {
    loadingCrewMembers.value = false;
  }
};

const exportBoatRegistrations = async () => {
  clearMessages();
  loadingBoatRegistrations.value = true;
  
  try {
    const response = await apiClient.get('/admin/export/boat-registrations-json');
    
    console.log('Boat registrations response:', response.data);
    
    if (response.data && response.data.success) {
      // Use formatter to generate and download CSV file
      // Pass the full response structure (with data property) to the formatter
      downloadBoatRegistrationsCSV(response.data);
      
      success.value = t('admin.dataExport.exportSuccess');
      
      setTimeout(() => {
        success.value = null;
      }, 5000);
    }
  } catch (err) {
    console.error('Failed to export boat registrations:', err);
    console.error('Error response:', err.response);
    error.value = err.response?.data?.error?.message || t('admin.dataExport.exportError');
  } finally {
    loadingBoatRegistrations.value = false;
  }
};
</script>

<style scoped>
.admin-data-export {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.export-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.export-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.crewtimer-card {
  border: 2px solid #3498db;
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
}

.export-header {
  margin-bottom: 1.5rem;
}

.export-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.crewtimer-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.export-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.export-description {
  font-size: 0.95rem;
  color: #7f8c8d;
  line-height: 1.6;
}

.export-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

.btn-icon {
  width: 20px;
  height: 20px;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.export-stats {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  gap: 0.5rem;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.stat-value {
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.error-message,
.success-message {
  margin-top: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
}

.success-message {
  background: #efe;
  border: 1px solid #cfc;
  color: #3c3;
}

.error-message svg,
.success-message svg {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .admin-data-export {
    padding: 1rem;
  }

  .page-header h1 {
    font-size: 2rem;
  }

  .export-card {
    padding: 1.5rem;
  }

  .export-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .export-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
