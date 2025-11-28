<template>
  <div class="register-form">
    <div class="form-header">
      <img src="../assets/rcpm-logo.png" alt="RCPM Logo" class="form-logo" />
      <h2>{{ $t('auth.register.title') }}</h2>
      <p class="subtitle">{{ $t('auth.register.subtitle') }}</p>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Email -->
      <div class="form-group">
        <label for="email">{{ $t('auth.register.email') }} *</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          :disabled="loading"
          @blur="validateEmail"
        />
        <span v-if="errors.email" class="error">{{ errors.email }}</span>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label for="password">{{ $t('auth.register.password') }} *</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          :disabled="loading"
          @input="validatePassword"
        />
        <div class="password-requirements">
          <div class="requirement" :class="{ valid: passwordChecks.minLength }">
            <span class="icon">{{ passwordChecks.minLength ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordMinLength') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasUppercase }">
            <span class="icon">{{ passwordChecks.hasUppercase ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasUppercase') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasLowercase }">
            <span class="icon">{{ passwordChecks.hasLowercase ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasLowercase') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasNumber }">
            <span class="icon">{{ passwordChecks.hasNumber ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasNumber') }}</span>
          </div>
        </div>
      </div>

      <!-- First Name -->
      <div class="form-group">
        <label for="firstName">{{ $t('auth.register.firstName') }} *</label>
        <input
          id="firstName"
          v-model="form.first_name"
          type="text"
          required
          :disabled="loading"
        />
        <span v-if="errors.first_name" class="error">{{ errors.first_name }}</span>
      </div>

      <!-- Last Name -->
      <div class="form-group">
        <label for="lastName">{{ $t('auth.register.lastName') }} *</label>
        <input
          id="lastName"
          v-model="form.last_name"
          type="text"
          required
          :disabled="loading"
        />
        <span v-if="errors.last_name" class="error">{{ errors.last_name }}</span>
      </div>

      <!-- Club Affiliation -->
      <div class="form-group">
        <label for="clubAffiliation">{{ $t('auth.register.clubAffiliation') }} *</label>
        <input
          id="clubAffiliation"
          v-model="form.club_affiliation"
          type="text"
          required
          :disabled="loading"
        />
        <span v-if="errors.club_affiliation" class="error">{{ errors.club_affiliation }}</span>
      </div>

      <!-- Mobile Number -->
      <div class="form-group">
        <label for="mobileNumber">{{ $t('auth.register.mobileNumber') }} *</label>
        <input
          id="mobileNumber"
          v-model="form.mobile_number"
          type="tel"
          required
          :disabled="loading"
          placeholder="+33612345678"
        />
        <span v-if="errors.mobile_number" class="error">{{ errors.mobile_number }}</span>
        <small class="hint">{{ $t('auth.register.mobileHint') }}</small>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>

      <!-- Submit Button -->
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading">{{ $t('common.loading') }}</span>
        <span v-else>{{ $t('auth.register.submit') }}</span>
      </button>

      <!-- Login Link -->
      <p class="text-center">
        {{ $t('auth.register.haveAccount') }}
        <router-link to="/login">{{ $t('auth.register.loginLink') }}</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();

const form = reactive({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  club_affiliation: '',
  mobile_number: '',
});

const errors = reactive({});
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Password validation checks
const passwordChecks = reactive({
  minLength: false,
  hasUppercase: false,
  hasLowercase: false,
  hasNumber: false
});

// Validation functions
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errors.email = t('auth.validation.invalidEmail');
  } else {
    delete errors.email;
  }
};

const validatePassword = () => {
  // Update individual checks
  passwordChecks.minLength = form.password.length >= 8;
  passwordChecks.hasUppercase = /[A-Z]/.test(form.password);
  passwordChecks.hasLowercase = /[a-z]/.test(form.password);
  passwordChecks.hasNumber = /[0-9]/.test(form.password);
  
  // Set error if any check fails
  const allValid = passwordChecks.minLength && 
                   passwordChecks.hasUppercase && 
                   passwordChecks.hasLowercase && 
                   passwordChecks.hasNumber;
  
  if (!allValid) {
    errors.password = t('auth.validation.passwordRequirements');
  } else {
    delete errors.password;
  }
};

const handleSubmit = async () => {
  // Clear messages
  errorMessage.value = '';
  successMessage.value = '';

  // Validate all fields
  validateEmail();
  validatePassword();

  if (Object.keys(errors).length > 0) {
    return;
  }

  loading.value = true;

  try {
    await authStore.register(form);
    
    successMessage.value = t('auth.register.success');
    
    // Redirect to verify email page after 2 seconds
    setTimeout(() => {
      router.push({ 
        path: '/verify-email',
        query: { email: form.email }
      });
    }, 2000);
  } catch (error) {
    console.error('Registration error:', error);
    console.error('Error response:', error.response);
    
    // Show detailed error message
    if (error.response?.data?.error?.message) {
      errorMessage.value = error.response.data.error.message;
    } else if (error.response?.data?.error) {
      errorMessage.value = JSON.stringify(error.response.data.error);
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = t('auth.register.error');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-form {
  max-width: 500px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-logo {
  height: 80px;
  width: auto;
  margin-bottom: 1rem;
}

h2 {
  margin-bottom: 0.5rem;
  color: #333;
}

.subtitle {
  color: #666;
  margin-bottom: 1rem;
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

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error {
  display: block;
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.hint {
  display: block;
  color: #666;
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

.btn {
  width: 100%;
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.text-center {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

a {
  color: #4CAF50;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.password-requirements {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 0.875rem;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  color: #666;
  transition: color 0.3s;
}

.requirement.valid {
  color: #4CAF50;
  font-weight: 500;
}

.requirement .icon {
  font-weight: bold;
  font-size: 1rem;
  min-width: 1.2rem;
}

.requirement.valid .icon {
  color: #4CAF50;
}
</style>
