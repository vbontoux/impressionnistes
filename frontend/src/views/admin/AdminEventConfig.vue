<template>
  <div class="admin-event-config">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <h1>{{ $t('admin.eventConfig.title') }}</h1>
      <p class="subtitle">{{ $t('admin.eventConfig.subtitle') }}</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadConfig" class="btn-secondary">{{ $t('common.retry') }}</button>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="config-form">
      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.eventDate') }}</h2>
        <div class="form-group">
          <label for="event_date">{{ $t('admin.eventConfig.competitionDate') }}</label>
          <input
            id="event_date"
            v-model="formData.event_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.event_date }"
          />
          <span v-if="validationErrors.event_date" class="error-text">
            {{ validationErrors.event_date }}
          </span>
        </div>
      </div>

      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.registrationPeriod') }}</h2>
        
        <div class="form-group">
          <label for="registration_start_date">{{ $t('admin.eventConfig.registrationStart') }}</label>
          <input
            id="registration_start_date"
            v-model="formData.registration_start_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.registration_start_date }"
          />
          <span v-if="validationErrors.registration_start_date" class="error-text">
            {{ validationErrors.registration_start_date }}
          </span>
        </div>

        <div class="form-group">
          <label for="registration_end_date">{{ $t('admin.eventConfig.registrationEnd') }}</label>
          <input
            id="registration_end_date"
            v-model="formData.registration_end_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.registration_end_date }"
          />
          <span v-if="validationErrors.registration_end_date" class="error-text">
            {{ validationErrors.registration_end_date }}
          </span>
        </div>

        <div class="form-group">
          <label for="payment_deadline">{{ $t('admin.eventConfig.paymentDeadline') }}</label>
          <input
            id="payment_deadline"
            v-model="formData.payment_deadline"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.payment_deadline }"
          />
          <span v-if="validationErrors.payment_deadline" class="error-text">
            {{ validationErrors.payment_deadline }}
          </span>
        </div>
      </div>

      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.raceTiming') }}</h2>
        
        <div class="race-config-grid">
          <!-- Marathon Configuration -->
          <div class="race-config-column">
            <h3 class="race-type-title">{{ $t('admin.eventConfig.marathon') }}</h3>
            
            <div class="form-group">
              <label for="marathon_start_time">{{ $t('admin.eventConfig.startTime') }}</label>
              <input
                id="marathon_start_time"
                v-model="formData.marathon_start_time"
                type="time"
                class="form-control"
                :class="{ 'error': validationErrors.marathon_start_time }"
              />
              <span class="help-text">{{ $t('admin.eventConfig.marathonStartTimeHelp') }}</span>
              <span v-if="validationErrors.marathon_start_time" class="error-text">
                {{ validationErrors.marathon_start_time }}
              </span>
            </div>

            <div class="form-group">
              <label for="marathon_bow_start">{{ $t('admin.eventConfig.bowStart') }}</label>
              <input
                id="marathon_bow_start"
                v-model.number="formData.marathon_bow_start"
                type="number"
                min="1"
                class="form-control"
                :class="{ 'error': validationErrors.marathon_bow_start }"
              />
              <span class="help-text">{{ $t('admin.eventConfig.marathonBowStartHelp') }}</span>
              <span v-if="validationErrors.marathon_bow_start" class="error-text">
                {{ validationErrors.marathon_bow_start }}
              </span>
            </div>
          </div>

          <!-- Semi-Marathon Configuration -->
          <div class="race-config-column">
            <h3 class="race-type-title">{{ $t('admin.eventConfig.semiMarathon') }}</h3>
            
            <div class="form-group">
              <label for="semi_marathon_start_time">{{ $t('admin.eventConfig.startTime') }}</label>
              <input
                id="semi_marathon_start_time"
                v-model="formData.semi_marathon_start_time"
                type="time"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_start_time }"
              />
              <span class="help-text">{{ $t('admin.eventConfig.semiMarathonStartTimeHelp') }}</span>
              <span v-if="validationErrors.semi_marathon_start_time" class="error-text">
                {{ validationErrors.semi_marathon_start_time }}
              </span>
            </div>

            <div class="form-group">
              <label for="semi_marathon_bow_start">{{ $t('admin.eventConfig.bowStart') }}</label>
              <input
                id="semi_marathon_bow_start"
                v-model.number="formData.semi_marathon_bow_start"
                type="number"
                min="1"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_bow_start }"
              />
              <span class="help-text">{{ $t('admin.eventConfig.semiMarathonBowStartHelp') }}</span>
              <span v-if="validationErrors.semi_marathon_bow_start" class="error-text">
                {{ validationErrors.semi_marathon_bow_start }}
              </span>
            </div>

            <div class="form-group">
              <label for="semi_marathon_interval_seconds">{{ $t('admin.eventConfig.interval') }}</label>
              <input
                id="semi_marathon_interval_seconds"
                v-model.number="formData.semi_marathon_interval_seconds"
                type="number"
                min="10"
                max="300"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_interval_seconds }"
              />
              <span class="help-text">{{ $t('admin.eventConfig.semiMarathonIntervalHelp') }}</span>
              <span v-if="validationErrors.semi_marathon_interval_seconds" class="error-text">
                {{ validationErrors.semi_marathon_interval_seconds }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="saveError" class="error-message">
        {{ saveError }}
      </div>

      <div v-if="saveSuccess" class="success-message">
        {{ $t('admin.eventConfig.saveSuccess') }}
      </div>

      <div class="form-actions">
        <button type="button" @click="handleCancel" class="btn-secondary" :disabled="saving">
          {{ $t('common.cancel') }}
        </button>
        <button type="submit" class="btn-primary" :disabled="saving || !hasChanges">
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const saveError = ref(null);
const saveSuccess = ref(false);

const originalData = ref({});
const formData = ref({
  event_date: '',
  registration_start_date: '',
  registration_end_date: '',
  payment_deadline: '',
  marathon_start_time: '07:45',
  semi_marathon_start_time: '09:00',
  semi_marathon_interval_seconds: 30,
  marathon_bow_start: 1,
  semi_marathon_bow_start: 41,
});

const validationErrors = ref({});

const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value);
});

const loadConfig = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await apiClient.get('/admin/event-config');
    const config = response.data.data;
    
    formData.value = {
      event_date: config.event_date || '',
      registration_start_date: config.registration_start_date || '',
      registration_end_date: config.registration_end_date || '',
      payment_deadline: config.payment_deadline || '',
      marathon_start_time: config.marathon_start_time || '07:45',
      semi_marathon_start_time: config.semi_marathon_start_time || '09:00',
      semi_marathon_interval_seconds: config.semi_marathon_interval_seconds || 30,
      marathon_bow_start: config.marathon_bow_start || 1,
      semi_marathon_bow_start: config.semi_marathon_bow_start || 41,
    };
    
    originalData.value = { ...formData.value };
  } catch (err) {
    console.error('Failed to load event configuration:', err);
    error.value = t('admin.eventConfig.loadError');
  } finally {
    loading.value = false;
  }
};

const validateForm = () => {
  validationErrors.value = {};
  
  const dates = {
    event_date: formData.value.event_date ? new Date(formData.value.event_date) : null,
    registration_start_date: formData.value.registration_start_date ? new Date(formData.value.registration_start_date) : null,
    registration_end_date: formData.value.registration_end_date ? new Date(formData.value.registration_end_date) : null,
    payment_deadline: formData.value.payment_deadline ? new Date(formData.value.payment_deadline) : null,
  };
  
  // Validate registration dates
  if (dates.registration_start_date && dates.registration_end_date) {
    if (dates.registration_start_date >= dates.registration_end_date) {
      validationErrors.value.registration_end_date = t('admin.eventConfig.errors.endBeforeStart');
    }
  }
  
  // Validate payment deadline
  if (dates.registration_end_date && dates.payment_deadline) {
    if (dates.registration_end_date > dates.payment_deadline) {
      validationErrors.value.payment_deadline = t('admin.eventConfig.errors.paymentBeforeEnd');
    }
  }
  
  // Validate event date
  if (dates.registration_end_date && dates.event_date) {
    if (dates.registration_end_date >= dates.event_date) {
      validationErrors.value.event_date = t('admin.eventConfig.errors.eventBeforeRegistration');
    }
  }
  
  if (dates.payment_deadline && dates.event_date) {
    if (dates.payment_deadline >= dates.event_date) {
      validationErrors.value.event_date = t('admin.eventConfig.errors.eventBeforePayment');
    }
  }
  
  // Validate rental priority days
  if (formData.value.rental_priority_days < 0 || formData.value.rental_priority_days > 90) {
    validationErrors.value.rental_priority_days = t('admin.eventConfig.errors.rentalDaysRange');
  }
  
  // Validate time formats
  const timeRegex = /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/;
  if (formData.value.marathon_start_time && !timeRegex.test(formData.value.marathon_start_time)) {
    validationErrors.value.marathon_start_time = t('admin.eventConfig.errors.invalidTimeFormat');
  }
  if (formData.value.semi_marathon_start_time && !timeRegex.test(formData.value.semi_marathon_start_time)) {
    validationErrors.value.semi_marathon_start_time = t('admin.eventConfig.errors.invalidTimeFormat');
  }
  
  // Validate interval
  if (formData.value.semi_marathon_interval_seconds < 10 || formData.value.semi_marathon_interval_seconds > 300) {
    validationErrors.value.semi_marathon_interval_seconds = t('admin.eventConfig.errors.intervalRange');
  }
  
  // Validate bow start numbers
  if (formData.value.marathon_bow_start < 1) {
    validationErrors.value.marathon_bow_start = t('admin.eventConfig.errors.bowStartPositive');
  }
  if (formData.value.semi_marathon_bow_start < 1) {
    validationErrors.value.semi_marathon_bow_start = t('admin.eventConfig.errors.bowStartPositive');
  }
  
  return Object.keys(validationErrors.value).length === 0;
};

const handleSubmit = async () => {
  saveError.value = null;
  saveSuccess.value = false;
  
  if (!validateForm()) {
    return;
  }
  
  // Confirm changes
  if (!confirm(t('admin.eventConfig.confirmSave'))) {
    return;
  }
  
  saving.value = true;
  
  try {
    const response = await apiClient.put('/admin/event-config', formData.value);
    const updatedConfig = response.data.data;
    
    formData.value = {
      event_date: updatedConfig.event_date || '',
      registration_start_date: updatedConfig.registration_start_date || '',
      registration_end_date: updatedConfig.registration_end_date || '',
      payment_deadline: updatedConfig.payment_deadline || '',
      rental_priority_days: updatedConfig.rental_priority_days || 15,
      marathon_start_time: updatedConfig.marathon_start_time || '07:45',
      semi_marathon_start_time: updatedConfig.semi_marathon_start_time || '09:00',
      semi_marathon_interval_seconds: updatedConfig.semi_marathon_interval_seconds || 30,
      marathon_bow_start: updatedConfig.marathon_bow_start || 1,
      semi_marathon_bow_start: updatedConfig.semi_marathon_bow_start || 41,
    };
    
    originalData.value = { ...formData.value };
    saveSuccess.value = true;
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (err) {
    console.error('Failed to save event configuration:', err);
    saveError.value = err.response?.data?.error?.message || t('admin.eventConfig.saveError');
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  if (hasChanges.value) {
    if (confirm(t('admin.eventConfig.confirmCancel'))) {
      router.push('/admin');
    }
  } else {
    router.push('/admin');
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<style scoped>
.admin-event-config {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3498db;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.config-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.race-config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.race-config-column {
  min-width: 0; /* Prevent grid blowout */
}

.race-type-title {
  font-size: 1.1rem;
  color: #3498db;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}

.form-control.error {
  border-color: #e74c3c;
}

.help-text {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-top: 0.25rem;
}

.error-text {
  display: block;
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.error-message {
  background-color: #fee;
  border: 1px solid #e74c3c;
  color: #c0392b;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.success-message {
  background-color: #d4edda;
  border: 1px solid #28a745;
  color: #155724;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d5dbdb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-event-config {
    padding: 1rem;
    max-width: 100%;
    overflow-x: hidden;
  }

  .page-header {
    margin-bottom: 1.5rem;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .back-link {
    font-size: 16px; /* Prevent iOS zoom */
    min-height: 44px;
    display: inline-flex;
    align-items: center;
  }

  .config-form {
    padding: 1.25rem;
    max-width: 100%;
    overflow-x: hidden;
  }

  .form-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    max-width: 100%;
    overflow-x: hidden;
  }

  .form-section h2 {
    font-size: 1.125rem;
  }

  .race-config-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 100%;
  }

  .race-config-column {
    max-width: 100%;
    overflow-x: hidden;
  }

  .race-type-title {
    font-size: 1rem;
  }

  .form-group {
    margin-bottom: 1.25rem;
    max-width: 100%;
  }

  .form-group label {
    font-size: 0.9rem;
  }

  .form-control {
    min-height: 44px;
    font-size: 16px; /* Prevent iOS zoom */
    padding: 0.625rem 0.75rem;
    max-width: 100%;
    box-sizing: border-box;
  }

  /* Specific fixes for date and time inputs */
  input[type="date"],
  input[type="time"],
  input[type="number"] {
    max-width: 100%;
    width: 100%;
    box-sizing: border-box;
  }

  .help-text,
  .error-text {
    font-size: 0.8rem;
    word-wrap: break-word;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 0.75rem;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    min-height: 44px;
    font-size: 16px; /* Prevent iOS zoom */
    padding: 0.875rem 1.5rem;
  }

  .error-message,
  .success-message {
    padding: 0.875rem;
    font-size: 0.9rem;
  }
}
</style>
