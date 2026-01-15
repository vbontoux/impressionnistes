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

    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <MessageAlert 
      v-else-if="error" 
      type="error" 
      :message="error"
    >
      <template #action>
        <BaseButton variant="secondary" size="small" @click="loadConfig">
          {{ $t('common.retry') }}
        </BaseButton>
      </template>
    </MessageAlert>

    <form v-else @submit.prevent="handleSubmit" class="config-form">
      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.eventDate') }}</h2>
        <FormGroup
          :label="$t('admin.eventConfig.competitionDate')"
          :error="validationErrors.event_date"
        >
          <input
            id="event_date"
            v-model="formData.event_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.event_date }"
          />
        </FormGroup>
      </div>

      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.registrationPeriod') }}</h2>
        
        <FormGroup
          :label="$t('admin.eventConfig.registrationStart')"
          :error="validationErrors.registration_start_date"
        >
          <input
            id="registration_start_date"
            v-model="formData.registration_start_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.registration_start_date }"
          />
        </FormGroup>

        <FormGroup
          :label="$t('admin.eventConfig.registrationEnd')"
          :error="validationErrors.registration_end_date"
        >
          <input
            id="registration_end_date"
            v-model="formData.registration_end_date"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.registration_end_date }"
          />
        </FormGroup>

        <FormGroup
          :label="$t('admin.eventConfig.paymentDeadline')"
          :error="validationErrors.payment_deadline"
        >
          <input
            id="payment_deadline"
            v-model="formData.payment_deadline"
            type="date"
            class="form-control"
            :class="{ 'error': validationErrors.payment_deadline }"
          />
        </FormGroup>
      </div>

      <div class="form-section">
        <h2>{{ $t('admin.eventConfig.raceTiming') }}</h2>
        
        <div class="race-config-grid">
          <!-- Marathon Configuration -->
          <div class="race-config-column">
            <h3 class="race-type-title">{{ $t('admin.eventConfig.marathon') }}</h3>
            
            <FormGroup
              :label="$t('admin.eventConfig.startTime')"
              :help-text="$t('admin.eventConfig.marathonStartTimeHelp')"
              :error="validationErrors.marathon_start_time"
            >
              <input
                id="marathon_start_time"
                v-model="formData.marathon_start_time"
                type="time"
                class="form-control"
                :class="{ 'error': validationErrors.marathon_start_time }"
              />
            </FormGroup>

            <FormGroup
              :label="$t('admin.eventConfig.bowStart')"
              :help-text="$t('admin.eventConfig.marathonBowStartHelp')"
              :error="validationErrors.marathon_bow_start"
            >
              <input
                id="marathon_bow_start"
                v-model.number="formData.marathon_bow_start"
                type="number"
                min="1"
                class="form-control"
                :class="{ 'error': validationErrors.marathon_bow_start }"
              />
            </FormGroup>
          </div>

          <!-- Semi-Marathon Configuration -->
          <div class="race-config-column">
            <h3 class="race-type-title">{{ $t('admin.eventConfig.semiMarathon') }}</h3>
            
            <FormGroup
              :label="$t('admin.eventConfig.startTime')"
              :help-text="$t('admin.eventConfig.semiMarathonStartTimeHelp')"
              :error="validationErrors.semi_marathon_start_time"
            >
              <input
                id="semi_marathon_start_time"
                v-model="formData.semi_marathon_start_time"
                type="time"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_start_time }"
              />
            </FormGroup>

            <FormGroup
              :label="$t('admin.eventConfig.bowStart')"
              :help-text="$t('admin.eventConfig.semiMarathonBowStartHelp')"
              :error="validationErrors.semi_marathon_bow_start"
            >
              <input
                id="semi_marathon_bow_start"
                v-model.number="formData.semi_marathon_bow_start"
                type="number"
                min="1"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_bow_start }"
              />
            </FormGroup>

            <FormGroup
              :label="$t('admin.eventConfig.interval')"
              :help-text="$t('admin.eventConfig.semiMarathonIntervalHelp')"
              :error="validationErrors.semi_marathon_interval_seconds"
            >
              <input
                id="semi_marathon_interval_seconds"
                v-model.number="formData.semi_marathon_interval_seconds"
                type="number"
                min="10"
                max="300"
                class="form-control"
                :class="{ 'error': validationErrors.semi_marathon_interval_seconds }"
              />
            </FormGroup>
          </div>
        </div>
      </div>

      <MessageAlert 
        v-if="saveError" 
        type="error" 
        :message="saveError"
        :dismissible="true"
        @dismiss="saveError = null"
      />

      <MessageAlert 
        v-if="saveSuccess" 
        type="success" 
        :message="$t('admin.eventConfig.saveSuccess')"
        :auto-dismiss="3000"
      />

      <div class="form-actions">
        <BaseButton 
          type="button" 
          variant="secondary" 
          size="medium"
          :disabled="saving"
          @click="handleCancel"
        >
          {{ $t('common.cancel') }}
        </BaseButton>
        <BaseButton 
          type="submit" 
          variant="primary" 
          size="medium"
          :disabled="saving || !hasChanges"
          :loading="saving"
        >
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useConfirm } from '../../composables/useConfirm';
import apiClient from '../../services/apiClient';
import BaseButton from '../../components/base/BaseButton.vue';
import FormGroup from '../../components/composite/FormGroup.vue';
import LoadingSpinner from '../../components/base/LoadingSpinner.vue';
import MessageAlert from '../../components/composite/MessageAlert.vue';

const router = useRouter();
const { t } = useI18n();
const { confirm } = useConfirm();

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
  
  // Confirm changes with custom dialog
  const confirmed = await confirm({
    title: t('admin.eventConfig.confirmSaveTitle'),
    message: t('admin.eventConfig.confirmSave'),
    confirmText: t('common.save'),
    cancelText: t('common.cancel'),
    variant: 'primary'
  });
  
  if (!confirmed) {
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

const handleCancel = async () => {
  if (hasChanges.value) {
    const confirmed = await confirm({
      title: t('admin.eventConfig.confirmCancelTitle'),
      message: t('admin.eventConfig.confirmCancel'),
      confirmText: t('common.yes'),
      cancelText: t('common.no'),
      variant: 'warning'
    });
    
    if (confirmed) {
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
  padding: var(--spacing-xxl);
}

.page-header {
  margin-bottom: var(--spacing-xxl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-primary);
  text-decoration: none;
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.subtitle {
  color: var(--color-muted);
  font-size: var(--font-size-lg);
}

.config-form {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
}

.form-section {
  margin-bottom: var(--spacing-xxl);
  padding-bottom: var(--spacing-xxl);
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-semibold);
}

.race-config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xxl);
}

.race-config-column {
  min-width: 0; /* Prevent grid blowout */
}

.race-type-title {
  font-size: var(--font-size-lg);
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-primary);
}

.form-control {
  width: 100%;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-normal);
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-control.error {
  border-color: var(--color-danger);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: flex-end;
  margin-top: var(--spacing-xxl);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-event-config {
    padding: var(--spacing-lg);
    max-width: 100%;
    overflow-x: hidden;
  }

  .page-header {
    margin-bottom: var(--spacing-xl);
  }

  .page-header h1 {
    font-size: var(--font-size-2xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
  }

  .back-link {
    font-size: var(--form-input-font-size-mobile);
    min-height: var(--touch-target-min-size);
    display: inline-flex;
    align-items: center;
  }

  .config-form {
    padding: var(--spacing-lg);
    max-width: 100%;
    overflow-x: hidden;
  }

  .form-section {
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-xl);
    max-width: 100%;
    overflow-x: hidden;
  }

  .form-section h2 {
    font-size: var(--font-size-lg);
  }

  .race-config-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-xl);
    max-width: 100%;
  }

  .race-config-column {
    max-width: 100%;
    overflow-x: hidden;
  }

  .race-type-title {
    font-size: var(--font-size-base);
  }

  .form-control {
    min-height: var(--form-input-min-height);
    font-size: var(--form-input-font-size-mobile);
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

  .form-actions {
    flex-direction: column-reverse;
    gap: var(--spacing-md);
  }

  .form-actions :deep(button) {
    width: 100%;
  }
}
</style>
