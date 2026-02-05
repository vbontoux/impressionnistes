<template>
  <div class="forgot-password-form">
    <div class="form-header">
      <img src="../assets/impressionnistes-logo.jpg" alt="Course des Impressionnistes Logo" class="form-logo" />
      <h2>{{ $t('auth.forgotPassword.title') }}</h2>
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
      {{ $t('auth.forgotPassword.instructions') }}
    </p>

    <!-- Forgot Password Form -->
    <form v-if="!successMessage" @submit.prevent="handleSubmit">
      <FormGroup
        :label="$t('auth.forgotPassword.email')"
        :required="true"
        :error="errors.email"
      >
        <input
          v-model="form.email"
          type="email"
          required
          :placeholder="$t('auth.forgotPassword.emailPlaceholder')"
          @blur="validateEmail"
        />
      </FormGroup>

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        variant="primary"
        size="medium"
        :full-width="true"
        :loading="loading"
        :disabled="loading"
      >
        {{ loading ? $t('auth.forgotPassword.sending') : $t('auth.forgotPassword.submitButton') }}
      </BaseButton>
    </form>

    <!-- Links -->
    <div class="links">
      <p class="text-center">
        <router-link to="/login">{{ $t('auth.forgotPassword.backToLogin') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';
import FormGroup from './composite/FormGroup.vue';
import BaseButton from './base/BaseButton.vue';
import MessageAlert from './composite/MessageAlert.vue';

const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const form = ref({
  email: '',
});
const errors = ref({
  email: '',
});

// Validate email
const validateEmail = () => {
  if (!form.value.email) {
    errors.value.email = t('auth.forgotPassword.emailRequired');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = t('auth.forgotPassword.emailInvalid');
  } else {
    errors.value.email = '';
  }
};

// Handle form submission
const handleSubmit = async () => {
  // Validate form
  validateEmail();

  if (errors.value.email) {
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    await authStore.forgotPassword(form.value.email);
    
    // Show success message
    successMessage.value = t('auth.forgotPassword.successMessage');
    
    // Redirect to reset password page after 3 seconds with email pre-filled
    setTimeout(() => {
      router.push({
        path: '/reset-password',
        query: { email: form.value.email },
      });
    }, 3000);
  } catch (error) {
    console.error('Forgot password error:', error);
    errorMessage.value = authStore.error || t('auth.forgotPassword.errorMessage');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-password-form {
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
  .forgot-password-form {
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
