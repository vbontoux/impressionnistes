<template>
  <div class="boat-registration-form">
    <h2>{{ $t('boat.createRegistration') }}</h2>

    <form @submit.prevent="handleSubmit">
      <!-- Event Type Selection -->
      <div class="form-group">
        <label for="event_type">{{ $t('boat.eventType') }} *</label>
        <select
          id="event_type"
          v-model="formData.event_type"
          @change="onEventTypeChange"
          required
        >
          <option value="">{{ $t('boat.selectEvent') }}</option>
          <option value="21km">{{ $t('boat.semiMarathon') }} (21km)</option>
          <option value="42km">{{ $t('boat.marathon') }} (42km)</option>
        </select>
      </div>

      <!-- Boat Type Selection -->
      <div class="form-group" v-if="formData.event_type">
        <label for="boat_type">{{ $t('boat.boatType') }} *</label>
        <select
          id="boat_type"
          v-model="formData.boat_type"
          required
        >
          <option value="">{{ $t('boat.selectBoatType') }}</option>
          <option
            v-for="boatType in availableBoatTypes"
            :key="boatType.value"
            :value="boatType.value"
          >
            {{ boatType.label }}
          </option>
        </select>
      </div>

      <!-- Boat Request Section -->
      <div class="form-section boat-request-section" v-if="formData.boat_type">
        <h3>{{ $t('boat.boatRequest.title') }}</h3>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="formData.boat_request_enabled"
              @change="handleBoatRequestToggle"
            />
            <span>{{ $t('boat.boatRequest.enableLabel') }}</span>
          </label>
          <p class="help-text">{{ $t('boat.boatRequest.helpText') }}</p>
        </div>
        
        <!-- Show these fields only when boat request is enabled -->
        <div v-if="formData.boat_request_enabled" class="boat-request-fields">
          <div class="form-group">
            <label for="boat_request_comment">
              {{ $t('boat.boatRequest.commentLabel') }}
            </label>
            <textarea
              id="boat_request_comment"
              v-model="formData.boat_request_comment"
              :placeholder="$t('boat.boatRequest.commentPlaceholder')"
              maxlength="500"
              rows="4"
              class="form-textarea"
            ></textarea>
            <span class="char-count">
              {{ formData.boat_request_comment?.length || 0 }} / 500
            </span>
          </div>
          
          <div class="form-group">
            <label>{{ $t('boat.boatRequest.assignedBoatLabel') }}</label>
            <input
              type="text"
              :value="formData.assigned_boat_identifier || $t('boat.boatRequest.notAssigned')"
              disabled
              class="form-input read-only"
            />
            <p class="help-text">{{ $t('boat.boatRequest.assignedBoatHelp') }}</p>
          </div>
          
          <div v-if="formData.assigned_boat_comment" class="form-group">
            <label>{{ $t('boat.boatRequest.assignedBoatCommentLabel') }}</label>
            <div class="assigned-comment">
              {{ formData.assigned_boat_comment }}
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="btn-secondary">
          {{ $t('common.cancel') }}
        </button>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? $t('common.creating') : $t('common.create') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useBoatStore } from '../stores/boatStore'
import { useI18n } from 'vue-i18n'

export default {
  name: 'BoatRegistrationForm',
  emits: ['created', 'cancel'],
  setup(props, { emit }) {
    const { t } = useI18n()
    const boatStore = useBoatStore()

    const formData = ref({
      event_type: '',
      boat_type: '',
      boat_request_enabled: false,
      boat_request_comment: '',
      assigned_boat_identifier: null,
      assigned_boat_comment: null
    })

    const loading = ref(false)
    const error = ref(null)

    const availableBoatTypes = computed(() => {
      if (formData.value.event_type === '42km') {
        return [
          { value: 'skiff', label: t('boat.skiff') }
        ]
      } else if (formData.value.event_type === '21km') {
        return [
          { value: '4-', label: t('boat.fourWithoutCox') },
          { value: '4+', label: t('boat.fourWithCox') },
          { value: '8+', label: t('boat.eightWithCox') }
        ]
      }
      return []
    })

    const onEventTypeChange = () => {
      // Reset boat type when event type changes
      formData.value.boat_type = ''
    }

    const handleBoatRequestToggle = () => {
      if (!formData.value.boat_request_enabled) {
        // Clear fields when disabling boat request
        formData.value.boat_request_comment = ''
        // Note: assigned_boat_identifier and assigned_boat_comment are read-only, backend will clear them
      }
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = null

      try {
        const payload = {
          event_type: formData.value.event_type,
          boat_type: formData.value.boat_type,
          boat_request_enabled: formData.value.boat_request_enabled,
          boat_request_comment: formData.value.boat_request_comment
          // Don't send assigned_boat_identifier or assigned_boat_comment (read-only for team managers)
        }
        
        const newBoat = await boatStore.createBoatRegistration(payload)
        emit('created', newBoat)
      } catch (err) {
        error.value = err.response?.data?.error?.message || t('boat.createError')
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      error,
      availableBoatTypes,
      onEventTypeChange,
      handleBoatRequestToggle,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.boat-registration-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

.form-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.form-section h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group select,
.form-group input[type="text"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 0.5rem;
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.checkbox-label span {
  user-select: none;
}

.help-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.boat-request-fields {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
}

.read-only {
  background-color: #e9ecef;
  cursor: not-allowed;
  color: #6c757d;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.875rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.assigned-comment {
  padding: 0.75rem;
  background-color: #e7f3ff;
  border-left: 4px solid #007bff;
  border-radius: 4px;
  white-space: pre-wrap;
  font-size: 0.9rem;
  color: #333;
}

.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
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
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}
</style>
