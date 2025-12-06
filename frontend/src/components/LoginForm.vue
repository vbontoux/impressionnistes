<template>
  <div class="login-form">
    <div class="form-header">
      <img src="../assets/rcpm-logo.png" alt="RCPM Logo" class="form-logo" />
      <h2>{{ $t('auth.login.title') }}</h2>
    </div>
    
    <!-- Session Expired Warning -->
    <div v-if="sessionExpired" class="alert alert-warning">
      {{ $t('auth.login.sessionExpired') }}
    </div>

    <p class="welcome-text">{{ $t('auth.login.welcomeMessage') }}</p>

    <!-- Login Button -->
    <button @click="loginWithCognito" class="btn btn-primary" :disabled="loading">
      {{ $t('auth.login.loginButton') }}
    </button>

    <!-- Error Message -->
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>

    <!-- Register Link -->
    <p class="text-center">
      {{ $t('auth.login.noAccount') }}
      <router-link to="/register">{{ $t('auth.login.registerLink') }}</router-link>
    </p>

    <!-- Forgot Password Link -->
    <p class="text-center">
      <router-link to="/forgot-password">{{ $t('auth.login.forgotPassword') }}</router-link>
    </p>

    <!-- Verify Email Link -->
    <p class="text-center">
      <router-link to="/verify-email">{{ $t('auth.login.verifyEmail') }}</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const errorMessage = ref('');
const sessionExpired = ref(false);

// Check if redirected due to session expiration
onMounted(() => {
  if (route.query.reason === 'session_expired') {
    sessionExpired.value = true;
  }
});

// Get Cognito configuration from environment
const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN;
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;
const REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI || window.location.origin + '/callback';

const loginWithCognito = () => {
  // Redirect to Cognito Hosted UI
  const cognitoUrl = `${COGNITO_DOMAIN}/login?client_id=${COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
  window.location.href = cognitoUrl;
};
</script>

<style scoped>
.login-form {
  max-width: 450px;
  margin: 0 auto;
  padding: 3rem 2.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-logo {
  height: 100px;
  width: auto;
  margin-bottom: 1.5rem;
}

h2 {
  margin-bottom: 1rem;
  color: #333;
  text-align: center;
}

.welcome-text {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-size: 1rem;
  line-height: 1.5;
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

.alert-warning {
  background-color: #fff3e0;
  color: #e65100;
  border: 1px solid #ff9800;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  margin-bottom: 1rem;
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
</style>
