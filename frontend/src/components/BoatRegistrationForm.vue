<template>
  <div class="boat-registration-form">
    <h2>{{ $t('boat.createRegistration') }}</h2>

    <form @submit.prevent="handleSubmit">
      <!-- Event Type Selection -->
      <FormGroup
        :label="$t('boat.eventType') + ' *'"
        for-id="event_type"
      >
        <select
          id="event_type"
          v-model="formData.event_type"
          @change="onEventTypeChange"
          required
          class="form-select"
        >
          <option value="">{{ $t('boat.selectEvent') }}</option>
          <option value="21km">{{ $t('boat.semiMarathon') }} (21km)</option>
          <option value="42km">{{ $t('boat.marathon') }} (42km)</option>
        </select>
      </FormGroup>

      <!-- Boat Type Selection -->
      <FormGroup
        v-if="formData.event_type"
        :label="$t('boat.boatType') + ' *'"
        for-id="boat_type"
      >
        <select
          id="boat_type"
          v-model="formData.boat_type"
          required
          class="form-select"
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
      </FormGroup>

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
          <FormGroup
            :label="$t('boat.boatRequest.commentLabel')"
            for-id="boat_request_comment"
          >
            <textarea
              id="boat_request_comment"
              v-model="formData.boat_request_comment"
              :placeholder="$t('boat.boatRequest.commentPlaceholder')"
              maxlength="500"
              rows="4"
              class="form-textarea"
            ></textarea>
            <template #help>
              <span class="char-count">
                {{ formData.boat_request_comment?.length || 0 }} / 500
              </span>
            </template>
          </FormGroup>
          
          <FormGroup
            :label="$t('boat.boatRequest.assignedBoatLabel')"
            :help-text="$t('boat.boatRequest.assignedBoatHelp')"
          >
            <input
              type="text"
              :value="formData.assigned_boat_identifier || $t('boat.boatRequest.notAssigned')"
              disabled
              class="form-input read-only"
            />
          </FormGroup>
          
          <FormGroup
            v-if="formData.assigned_boat_comment"
            :label="$t('boat.boatRequest.assignedBoatCommentLabel')"
          >
            <div class="assigned-comment">
              {{ formData.assigned_boat_comment }}
            </div>
          </FormGroup>
        </div>
      </div>

      <!-- Error Message -->
      <MessageAlert 
        v-if="error" 
        type="error" 
        :message="error"
        :dismissible="true"
        @dismiss="error = null"
      />

      <!-- Action Buttons -->
      <div class="form-actions">
        <BaseButton 
          type="button" 
          variant="secondary" 
          size="small"
          @click="$emit('cancel')"
        >
          {{ $t('common.cancel') }}
        </BaseButton>
        <BaseButton 
          type="submit" 
          variant="primary" 
          size="small"
          :disabled="loading"
          :loading="loading"
        >
          {{ loading ? $t('common.creating') : $t('common.create') }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useBoatStore } from '../stores/boatStore'
import { useI18n } from 'vue-i18n'
import BaseButton from './base/BaseButton.vue'
import FormGroup from './composite/FormGroup.vue'
import MessageAlert from './composite/MessageAlert.vue'

export default {
  name: 'BoatRegistrationForm',
  components: {
    BaseButton,
    FormGroup,
    MessageAlert
  },
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
  padding: var(--spacing-xxl);
}

.form-section {
  margin-top: var(--spacing-xxl);
  padding-top: var(--spacing-xxl);
  border-top: 1px solid var(--color-border);
}

.form-section h3 {
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  font-weight: var(--font-weight-semibold);
}

.form-select {
  width: 100%;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-base);
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: var(--font-weight-medium);
}

.checkbox-label input[type="checkbox"] {
  margin-right: var(--spacing-sm);
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.checkbox-label span {
  user-select: none;
}

.help-text {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

.boat-request-fields {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg);
  background-color: var(--color-light);
  border-radius: var(--border-radius-sm);
}

.form-textarea {
  width: 100%;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-family: inherit;
  font-size: var(--font-size-base);
  resize: vertical;
}

.form-input {
  width: 100%;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-base);
}

.read-only {
  background-color: var(--color-light);
  cursor: not-allowed;
  color: var(--color-secondary);
}

.char-count {
  display: block;
  text-align: right;
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  margin-top: var(--spacing-xs);
}

.assigned-comment {
  padding: var(--spacing-md);
  background-color: var(--color-info-light);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--border-radius-sm);
  white-space: pre-wrap;
  font-size: var(--font-size-sm);
  color: var(--color-dark);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: flex-end;
  margin-top: var(--spacing-xxl);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .boat-registration-form {
    padding: var(--spacing-lg);
  }

  .form-section {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-xl);
  }

  .form-section h3 {
    font-size: var(--font-size-lg);
  }

  .form-select,
  .form-input,
  .form-textarea {
    min-height: var(--form-input-min-height);
    font-size: var(--form-input-font-size-mobile);
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
