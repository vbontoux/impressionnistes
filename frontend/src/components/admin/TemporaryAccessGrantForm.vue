<template>
  <div class="temp-access-form">
    <h3>{{ $t('admin.tempAccess.grantTitle') }}</h3>
    <p class="form-description">{{ $t('admin.tempAccess.grantDescription') }}</p>

    <MessageAlert 
      v-if="error" 
      type="error" 
      :message="error"
      :dismissible="true"
      @dismiss="error = null"
    />

    <form @submit.prevent="handleSubmit">
      <FormGroup
        :label="$t('admin.tempAccess.selectUser')"
        :required="true"
        :error="errors.user_id"
      >
        <select 
          v-model="formData.user_id" 
          required
          :disabled="loading || submitting"
        >
          <option value="">{{ $t('admin.tempAccess.selectUserPlaceholder') }}</option>
          <option 
            v-for="manager in teamManagers" 
            :key="manager.user_id" 
            :value="manager.user_id"
          >
            {{ manager.last_name }}, {{ manager.first_name }} ({{ manager.email }})
          </option>
        </select>
      </FormGroup>

      <FormGroup
        :label="$t('admin.tempAccess.hours')"
        :required="true"
        :error="errors.hours"
        :help-text="$t('admin.tempAccess.hoursHelp', { default: defaultHours })"
      >
        <input
          v-model.number="formData.hours"
          type="number"
          min="1"
          max="168"
          required
          :disabled="submitting"
        />
      </FormGroup>

      <FormGroup
        :label="$t('admin.tempAccess.notes')"
        :help-text="$t('admin.tempAccess.notesHelp')"
      >
        <textarea
          v-model="formData.notes"
          rows="3"
          :placeholder="$t('admin.tempAccess.notesPlaceholder')"
          :disabled="submitting"
        ></textarea>
      </FormGroup>

      <div class="form-actions">
        <BaseButton
          type="submit"
          variant="primary"
          size="medium"
          :disabled="submitting || !isValid"
          :loading="submitting"
        >
          {{ submitting ? $t('common.granting') : $t('admin.tempAccess.grantAccess') }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '../../services/apiClient'
import BaseButton from '../base/BaseButton.vue'
import FormGroup from '../composite/FormGroup.vue'
import MessageAlert from '../composite/MessageAlert.vue'

const { t } = useI18n()
const emit = defineEmits(['grant-created'])

const loading = ref(true)
const submitting = ref(false)
const error = ref(null)
const teamManagers = ref([])
const defaultHours = ref(48)

const formData = ref({
  user_id: '',
  hours: 48,
  notes: ''
})

const errors = ref({
  user_id: null,
  hours: null
})

const isValid = computed(() => {
  return formData.value.user_id && 
         formData.value.hours > 0 && 
         formData.value.hours <= 168
})

const loadTeamManagers = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get('/admin/team-managers')
    teamManagers.value = response.data.data.team_managers || []
  } catch (err) {
    console.error('Failed to load team managers:', err)
    error.value = t('admin.tempAccess.loadManagersError')
  } finally {
    loading.value = false
  }
}

const loadDefaultHours = async () => {
  try {
    const response = await apiClient.get('/public/event-info')
    const eventInfo = response.data.data
    if (eventInfo.temporary_editing_access_hours) {
      defaultHours.value = eventInfo.temporary_editing_access_hours
      formData.value.hours = eventInfo.temporary_editing_access_hours
    }
  } catch (err) {
    console.error('Failed to load default hours:', err)
    // Keep default of 48 hours
  }
}

const validateForm = () => {
  errors.value = {
    user_id: null,
    hours: null
  }
  
  let isValid = true
  
  if (!formData.value.user_id) {
    errors.value.user_id = t('admin.tempAccess.userRequired')
    isValid = false
  }
  
  if (!formData.value.hours || formData.value.hours <= 0) {
    errors.value.hours = t('admin.tempAccess.hoursRequired')
    isValid = false
  } else if (formData.value.hours > 168) {
    errors.value.hours = t('admin.tempAccess.hoursTooLarge')
    isValid = false
  }
  
  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  error.value = null
  
  try {
    const response = await apiClient.post('/admin/temporary-access/grant', {
      user_id: formData.value.user_id,
      hours: formData.value.hours,
      notes: formData.value.notes
    })
    
    // Reset form
    formData.value = {
      user_id: '',
      hours: defaultHours.value,
      notes: ''
    }
    
    // Emit success event
    emit('grant-created', response.data.data)
  } catch (err) {
    console.error('Failed to grant temporary access:', err)
    error.value = err.response?.data?.error?.message || t('admin.tempAccess.grantError')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadTeamManagers()
  loadDefaultHours()
})
</script>

<style scoped>
.temp-access-form {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.temp-access-form h3 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.form-description {
  color: var(--color-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xl);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--color-border);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .temp-access-form {
    padding: var(--spacing-lg);
  }

  .temp-access-form h3 {
    font-size: var(--font-size-lg);
  }

  .form-actions {
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
  }

  .form-actions :deep(button) {
    width: 100%;
  }
}
</style>
