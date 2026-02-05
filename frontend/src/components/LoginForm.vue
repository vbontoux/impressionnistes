<template>
  <div class="login-form">
    <div class="form-header">
      <img src="../assets/impressionnistes-logo.jpg" alt="Course des Impressionnistes Logo" class="form-logo" />
      <h2>{{ $t('auth.login.title') }}</h2>
    </div>
    
    <!-- Session Timeout Message -->
    <MessageAlert
      v-if="sessionTimeoutMessage"
      type="warning"
      :message="sessionTimeoutMessage"
      :dismissible="true"
      @dismiss="sessionTimeoutMessage = ''"
    />

    <!-- Error Message -->
    <MessageAlert
      v-if="errorMessage"
      type="error"
      :message="errorMessage"
      :dismissible="true"
      @dismiss="errorMessage = ''"
    />

    <p class="welcome-text">{{ $t('auth.login.welcomeMessage') }}</p>

    <!-- Login Form -->
    <form @submit.prevent="handleLogin">
      <FormGroup
        :label="$t('auth.login.email')"
        :required="true"
        :error="errors.email"
      >
        <input
          v-model="form.email"
          type="email"
          required
          :placeholder="$t('auth.login.emailPlaceholder')"
          @blur="validateEmail"
        />
      </FormGroup>

      <FormGroup
        :label="$t('auth.login.password')"
        :required="true"
        :error="errors.password"
      >
        <input
          v-model="form.password"
          type="password"
          required
          :placeholder="$t('auth.login.passwordPlaceholder')"
          @blur="validatePassword"
        />
      </FormGroup>

      <!-- Remember Me Checkbox -->
      <div class="remember-me">
        <label>
          <input
            v-model="form.rememberMe"
            type="checkbox"
          />
          {{ $t('auth.login.rememberMe') }}
        </label>
      </div>

      <!-- Login Button -->
      <BaseButton
        type="submit"
        variant="primary"
        size="medium"
        :full-width="true"
        :loading="loading"
        :disabled="loading"
      >
        {{ loading ? $t('auth.login.loggingIn') : $t('auth.login.loginButton') }}
      </BaseButton>
    </form>

    <!-- Links -->
    <div class="links">
      <p class="text-center">
        <router-link to="/forgot-password">{{ $t('auth.login.forgotPassword') }}</router-link>
      </p>

      <p class="text-center">
        {{ $t('auth.login.noAccount') }}
        <router-link to="/register">{{ $t('auth.login.registerLink') }}</router-link>
      </p>

      <p class="text-center">
        <router-link to="/verify-email">{{ $t('auth.login.verifyEmail') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';
import FormGroup from './composite/FormGroup.vue';
import BaseButton from './base/BaseButton.vue';
import MessageAlert from './composite/MessageAlert.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const errorMessage = ref('');
const form = ref({
  email: '',
  password: '',
  rememberMe: false,
});
const errors = ref({
  email: '',
  password: '',
});

// Check for session timeout
const sessionTimeoutMessage = computed(() => {
  if (authStore.sessionTimeoutReason === 'max_duration') {
    return t('auth.login.sessionExpiredMaxDuration');
  } else if (authStore.sessionTimeoutReason === 'inactivity') {
    return t('auth.login.sessionExpiredInactivity');
  } else if (route.query.reason === 'session_expired') {
    return t('auth.login.sessionExpired');
  }
  return '';
});

// Validate email
const validateEmail = () => {
  if (!form.value.email) {
    errors.value.email = t('auth.login.emailRequired');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = t('auth.login.emailInvalid');
  } else {
    errors.value.email = '';
  }
};

// Validate password
const validatePassword = () => {
  if (!form.value.password) {
    errors.value.password = t('auth.login.passwordRequired');
  } else {
    errors.value.password = '';
  }
};

// Handle login
const handleLogin = async () => {
  // Validate form
  validateEmail();
  validatePassword();

  if (errors.value.email || errors.value.password) {
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    const success = await authStore.login(
      form.value.email,
      form.value.password,
      form.value.rememberMe
    );

    if (success) {
      // Redirect to dashboard or intended page
      const redirectTo = route.query.redirect || '/dashboard';
      router.push(redirectTo);
    } else {
      // Error is already set in authStore
      errorMessage.value = authStore.error || t('auth.login.loginFailed');
    }
  } catch (error) {
    console.error('Login error:', error);
    errorMessage.value = authStore.error || t('auth.login.loginFailed');
  } finally {
    loading.value = false;
  }
};

// Clear session timeout reason on mount
onMounted(() => {
  authStore.sessionTimeoutReason = null;
});
</script>

<style scoped>
.login-form {
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

.welcome-text {
  text-align: center;
  color: var(--color-muted);
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.remember-me {
  margin-bottom: var(--spacing-lg);
}

.remember-me label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-dark);
}

.remember-me input[type="checkbox"] {
  cursor: pointer;
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
  .login-form {
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
