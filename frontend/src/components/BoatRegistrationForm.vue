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
      boat_type: ''
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

    const handleSubmit = async () => {
      loading.value = true
      error.value = null

      try {
        const newBoat = await boatStore.createBoatRegistration(formData.value)
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

.form-group input[type="checkbox"] {
  margin-right: 0.5rem;
}

.help-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
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
