<template>
  <div class="reset-password-form">
    <div class="form-header">
      <img src="../assets/impressionnistes-logo.jpg" alt="Course des Impressionnistes Logo" class="form-logo" />
      <h2>{{ $t('auth.resetPassword.title') }}</h2>
    </div>

    <!-- Success Message -->
    <MessageAlert
      v-if="successMessage"
      type="success"
      :message="successMessage"
      :dismissible="false"
    />

    <!-- Error Message -->
    <MessageAlert
      v-if="errorMessage"
      type="error"
      :message="errorMessage"
      :dismissible="true"
      @dismiss="errorMessage = ''"
    />

    <p v-if="!successMessage" class="instructions">
      {{ $t('auth.resetPassword.instructions') }}
    </p>

    <!-- Reset Password Form -->
    <form v-if="!successMessage" @submit.prevent="handleSubmit">
      <FormGroup
        :label="$t('auth.resetPassword.email')"
        :required="true"
        :error="errors.email"
      >
        <input
          v-model="form.email"
          type="email"
          required
          :placeholder="$t('auth.resetPassword.emailPlaceholder')"
          @blur="validateEmail"
        />
      </FormGroup>

      <FormGroup
        :label="$t('auth.resetPassword.code')"
        :required="true"
        :error="errors.code"
        :help-text="$t('auth.resetPassword.codeHint')"
      >
        <input
          v-model="form.code"
          type="text"
          required
          :placeholder="$t('auth.resetPassword.codePlaceholder')"
          @blur="validateCode"
        />
      </FormGroup>

      <FormGroup
        :label="$t('auth.resetPassword.newPassword')"
        :required="true"
        :error="errors.newPassword"
      >
        <input
          v-model="form.newPassword"
          type="password"
          required
          :placeholder="$t('auth.resetPassword.newPasswordPlaceholder')"
          @input="checkPasswordStrength"
          @blur="validateNewPassword"
        />
      </FormGroup>

      <!-- Password Strength Indicator -->
      <PasswordStrengthIndicator
        v-if="form.newPassword"
        :strength="passwordStrength"
      />

      <FormGroup
        :label="$t('auth.resetPassword.confirmPassword')"
        :required="true"
        :error="errors.confirmPassword"
      >
        <input
          v-model="form.confirmPassword"
          type="password"
          required
          :placeholder="$t('auth.resetPassword.confirmPasswordPlaceholder')"
          @blur="validateConfirmPassword"
        />
      </FormGroup>

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        variant="primary"
        size="medium"
        :full-width="true"
        :loading="loading"
        :disabled="loading || !isFormValid"
      >
        {{ loading ? $t('auth.resetPassword.resetting') : $t('auth.resetPassword.submitButton') }}
      </BaseButton>
    </form>

    <!-- Links -->
    <div class="links">
      <p class="text-center">
        <router-link to="/login">{{ $t('auth.resetPassword.backToLogin') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';
import { calculatePasswordStrength, isPasswordValid } from '../utils/passwordStrength';
import FormGroup from './composite/FormGroup.vue';
import BaseButton from './base/BaseButton.vue';
import MessageAlert from './composite/MessageAlert.vue';
import PasswordStrengthIndicator from './PasswordStrengthIndicator.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const form = ref({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: '',
});
const errors = ref({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: '',
});
const passwordStrength = ref({
  score: 0,
  feedback: [],
});

// Pre-fill email from query parameter
onMounted(() => {
  if (route.query.email) {
    form.value.email = route.query.email;
  }
});

// Check if form is valid
const isFormValid = computed(() => {
  return (
    form.value.email &&
    form.value.code &&
    form.value.newPassword &&
    form.value.confirmPassword &&
    !errors.value.email &&
    !errors.value.code &&
    !errors.value.newPassword &&
    !errors.value.confirmPassword &&
    isPasswordValid(form.value.newPassword) &&
    form.value.newPassword === form.value.confirmPassword
  );
});

// Validate email
const validateEmail = () => {
  if (!form.value.email) {
    errors.value.email = t('auth.resetPassword.emailRequired');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = t('auth.resetPassword.emailInvalid');
  } else {
    errors.value.email = '';
  }
};

// Validate code
const validateCode = () => {
  if (!form.value.code) {
    errors.value.code = t('auth.resetPassword.codeRequired');
  } else if (form.value.code.length < 6) {
    errors.value.code = t('auth.resetPassword.codeInvalid');
  } else {
    errors.value.code = '';
  }
};

// Check password strength
const checkPasswordStrength = () => {
  passwordStrength.value = calculatePasswordStrength(form.value.newPassword);
};

// Validate new password
const validateNewPassword = () => {
  if (!form.value.newPassword) {
    errors.value.newPassword = t('auth.resetPassword.newPasswordRequired');
  } else if (!isPasswordValid(form.value.newPassword)) {
    errors.value.newPassword = t('auth.resetPassword.passwordWeak');
  } else {
    errors.value.newPassword = '';
  }
};

// Validate confirm password
const validateConfirmPassword = () => {
  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.resetPassword.confirmPasswordRequired');
  } else if (form.value.newPassword !== form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.resetPassword.passwordMismatch');
  } else {
    errors.value.confirmPassword = '';
  }
};

// Handle form submission
const handleSubmit = async () => {
  // Validate all fields
  validateEmail();
  validateCode();
  validateNewPassword();
  validateConfirmPassword();

  if (
    errors.value.email ||
    errors.value.code ||
    errors.value.newPassword ||
    errors.value.confirmPassword
  ) {
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    await authStore.resetPassword(
      form.value.email,
      form.value.code,
      form.value.newPassword
    );
    
    // Show success message
    successMessage.value = t('auth.resetPassword.successMessage');
    
    // Redirect to login page after 3 seconds
    setTimeout(() => {
      router.push('/login');
    }, 3000);
  } catch (error) {
    console.error('Reset password error:', error);
    errorMessage.value = authStore.error || t('auth.resetPassword.errorMessage');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reset-password-form {
  max-width: 450px;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.form-logo {
  height: 100px;
  width: auto;
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
  color: var(--color-dark);
  text-align: center;
  font-size: var(--font-size-xl);
}

.instructions {
  text-align: center;
  color: var(--color-muted);
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.links {
  margin-top: var(--spacing-xl);
}

.text-center {
  text-align: center;
  margin-top: var(--spacing-md);
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

a:hover {
  text-decoration: underline;
}

/* Mobile responsiveness */
@media (max-width: 767px) {
  .reset-password-form {
    padding: var(--spacing-lg) var(--spacing-md);
    margin: var(--spacing-md);
  }

  .form-logo {
    height: 80px;
  }

  h2 {
    font-size: var(--font-size-lg);
  }
}
</style>
