<template>
  <div class="crew-member-form">
    <h3>{{ isEdit ? $t('crew.form.editTitle') : $t('crew.form.createTitle') }}</h3>

    <form @submit.prevent="handleSubmit">
      <!-- First Name -->
      <div class="form-group">
        <label for="firstName">{{ $t('crew.form.firstName') }} *</label>
        <input
          id="firstName"
          v-model="form.first_name"
          type="text"
          required
          :disabled="loading"
          @blur="validateField('first_name')"
        />
        <span v-if="errors.first_name" class="error">{{ errors.first_name }}</span>
      </div>

      <!-- Last Name -->
      <div class="form-group">
        <label for="lastName">{{ $t('crew.form.lastName') }} *</label>
        <input
          id="lastName"
          v-model="form.last_name"
          type="text"
          required
          :disabled="loading"
          @blur="validateField('last_name')"
        />
        <span v-if="errors.last_name" class="error">{{ errors.last_name }}</span>
      </div>

      <!-- Date of Birth -->
      <div class="form-group">
        <label for="dateOfBirth">{{ $t('crew.form.dateOfBirth') }} *</label>
        <input
          id="dateOfBirth"
          v-model="form.date_of_birth"
          type="date"
          required
          :disabled="loading"
          @blur="validateField('date_of_birth')"
        />
        <span v-if="errors.date_of_birth" class="error">{{ errors.date_of_birth }}</span>
      </div>

      <!-- Gender -->
      <div class="form-group">
        <label for="gender">{{ $t('crew.form.gender') }} *</label>
        <select
          id="gender"
          v-model="form.gender"
          required
          :disabled="loading"
        >
          <option value="">{{ $t('crew.form.selectGender') }}</option>
          <option value="M">{{ $t('crew.form.male') }}</option>
          <option value="F">{{ $t('crew.form.female') }}</option>
        </select>
        <span v-if="errors.gender" class="error">{{ errors.gender }}</span>
      </div>

      <!-- License Number -->
      <div class="form-group">
        <label for="licenseNumber">{{ $t('crew.form.licenseNumber') }} *</label>
        <input
          id="licenseNumber"
          v-model="form.license_number"
          type="text"
          required
          :disabled="loading"
          placeholder="ABC123456"
          maxlength="12"
          @blur="validateField('license_number')"
        />
        <small class="hint">{{ $t('crew.form.licenseHint') }}</small>
        <span v-if="errors.license_number" class="error">{{ errors.license_number }}</span>
      </div>

      <!-- Club Affiliation -->
      <div class="form-group">
        <label for="clubAffiliation">{{ $t('crew.form.clubAffiliation') }}</label>
        <input
          id="clubAffiliation"
          v-model="form.club_affiliation"
          type="text"
          :disabled="loading"
          :placeholder="$t('crew.form.clubPlaceholder')"
        />
        <small class="hint">{{ $t('crew.form.clubHint') }}</small>
        <span v-if="errors.club_affiliation" class="error">{{ errors.club_affiliation }}</span>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>

      <!-- Action Buttons -->
      <div class="button-group">
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading">{{ $t('common.loading') }}</span>
          <span v-else>{{ isEdit ? $t('crew.form.update') : $t('crew.form.create') }}</span>
        </button>
        <button type="button" class="btn btn-secondary" @click="handleCancel" :disabled="loading">
          {{ $t('common.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCrewStore } from '../stores/crewStore';
import { useAuthStore } from '../stores/authStore';

const props = defineProps({
  crewMember: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['success', 'cancel']);

const { t } = useI18n();
const crewStore = useCrewStore();
const authStore = useAuthStore();

const isEdit = computed(() => !!props.crewMember);

// Get the team manager's club as default
const defaultClub = authStore.user?.club_affiliation || '';

const form = reactive({
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: '',
  license_number: '',
  club_affiliation: defaultClub,
});

const errors = reactive({});
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Initialize form with crew member data if editing
onMounted(() => {
  if (props.crewMember) {
    Object.assign(form, {
      first_name: props.crewMember.first_name,
      last_name: props.crewMember.last_name,
      date_of_birth: props.crewMember.date_of_birth,
      gender: props.crewMember.gender,
      license_number: props.crewMember.license_number,
      club_affiliation: props.crewMember.club_affiliation || '',
    });
  }
});

// Validation functions
const validateField = (field) => {
  delete errors[field];

  if (field === 'first_name' && form.first_name.length < 1) {
    errors.first_name = t('crew.validation.firstNameRequired');
  }

  if (field === 'last_name' && form.last_name.length < 1) {
    errors.last_name = t('crew.validation.lastNameRequired');
  }

  if (field === 'date_of_birth') {
    if (!form.date_of_birth) {
      errors.date_of_birth = t('crew.validation.dateOfBirthRequired');
    } else {
      const birthDate = new Date(form.date_of_birth);
      const today = new Date();
      const currentYear = today.getFullYear();
      
      // Calculate minimum birth year for J14 (14 years old in current season)
      // For 2025 season, J14 must be born in 2011 or later
      const minBirthYear = currentYear - 14;
      const minDate = new Date(minBirthYear, 0, 1); // January 1st of min year
      
      // Maximum date is today (can't be born in the future)
      if (birthDate > today) {
        errors.date_of_birth = t('crew.validation.dateInFuture');
      } else if (birthDate > minDate) {
        // Born AFTER minDate means they're TOO YOUNG (not old enough)
        errors.date_of_birth = t('crew.validation.dateTooOld', { year: minBirthYear });
      }
    }
  }

  if (field === 'license_number') {
    const licenseRegex = /^[A-Z0-9]{6,12}$/i;
    if (!licenseRegex.test(form.license_number)) {
      errors.license_number = t('crew.validation.licenseInvalid');
    }
  }
};

const validateForm = () => {
  // Clear all errors first
  Object.keys(errors).forEach(key => delete errors[key]);
  
  // Validate all fields
  Object.keys(form).forEach(validateField);
  
  console.log('Form validation result:', {
    errors: { ...errors },
    hasErrors: Object.keys(errors).length > 0
  });
  
  return Object.keys(errors).length === 0;
};

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!validateForm()) {
    return;
  }

  loading.value = true;

  try {
    if (isEdit.value) {
      await crewStore.updateCrewMember(props.crewMember.crew_member_id, form);
      successMessage.value = t('crew.form.updateSuccess');
    } else {
      await crewStore.createCrewMember(form);
      successMessage.value = t('crew.form.createSuccess');
      
      // Reset form after creation
      Object.keys(form).forEach(key => form[key] = '');
    }

    setTimeout(() => {
      emit('success');
    }, 1500);
  } catch (error) {
    console.error('Crew member form error:', error);
    console.error('Error response:', error.response);
    
    // Try to extract detailed error message
    let detailedError = t('crew.form.error');
    
    if (error.response?.data?.error) {
      const errorData = error.response.data.error;
      
      // Check for specific error codes that need translation
      if (errorData.code === 'DUPLICATE_LICENSE') {
        detailedError = t('crew.validation.licenseDuplicate');
      }
      // Check if it's a validation error with field-specific messages
      else if (typeof errorData === 'object' && !errorData.message) {
        // Format validation errors
        const errorMessages = Object.entries(errorData)
          .map(([field, msg]) => `${field}: ${msg}`)
          .join(', ');
        detailedError = errorMessages;
      } else if (errorData.message) {
        detailedError = errorData.message;
      } else if (typeof errorData === 'string') {
        detailedError = errorData;
      }
    } else if (error.message) {
      detailedError = error.message;
    }
    
    errorMessage.value = detailedError;
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  // Clear error messages when cancelling
  errorMessage.value = '';
  successMessage.value = '';
  emit('cancel');
};
</script>

<style scoped>
.crew-member-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

input, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus, select:focus {
  outline: none;
  border-color: #4CAF50;
}

input:disabled, select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.hint {
  display: block;
  color: #666;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.error {
  display: block;
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #66bb6a;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
