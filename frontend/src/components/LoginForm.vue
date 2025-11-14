<template>
  <div class="login-form">
    <div class="form-header">
      <img src="../assets/rcpm-logo.png" alt="RCPM Logo" class="form-logo" />
      <h2>{{ $t('auth.login.title') }}</h2>
    </div>
    
    <div class="alert alert-info">
      <p>{{ $t('auth.login.cognitoNote') }}</p>
      <p><small>{{ $t('auth.login.cognitoInstructions') }}</small></p>
    </div>

    <!-- Cognito Hosted UI Login -->
    <button @click="loginWithCognito" class="btn btn-primary" :disabled="loading">
      {{ $t('auth.login.cognitoButton') }}
    </button>

    <div class="divider">
      <span>{{ $t('common.or') }}</span>
    </div>

    <!-- Social Login Options -->
    <div class="social-login">
      <button @click="loginWithGoogle" class="btn btn-google" :disabled="loading">
        <span class="icon">G</span>
        {{ $t('auth.login.google') }}
      </button>
      
      <button @click="loginWithFacebook" class="btn btn-facebook" :disabled="loading">
        <span class="icon">f</span>
        {{ $t('auth.login.facebook') }}
      </button>
    </div>

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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const errorMessage = ref('');

// Get Cognito configuration from environment
const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN;
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;
const REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI || window.location.origin + '/callback';

const loginWithCognito = () => {
  // Redirect to Cognito Hosted UI
  const cognitoUrl = `${COGNITO_DOMAIN}/login?client_id=${COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
  window.location.href = cognitoUrl;
};

const loginWithGoogle = () => {
  // Redirect to Cognito with Google identity provider
  const cognitoUrl = `${COGNITO_DOMAIN}/oauth2/authorize?identity_provider=Google&client_id=${COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
  window.location.href = cognitoUrl;
};

const loginWithFacebook = () => {
  // Redirect to Cognito with Facebook identity provider
  const cognitoUrl = `${COGNITO_DOMAIN}/oauth2/authorize?identity_provider=Facebook&client_id=${COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
  window.location.href = cognitoUrl;
};
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.form-logo {
  height: 80px;
  width: auto;
  margin-bottom: 1rem;
}

h2 {
  margin-bottom: 1rem;
  color: #333;
  text-align: center;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-info {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
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

.btn-google {
  background-color: #fff;
  color: #757575;
  border: 1px solid #ddd;
  margin-bottom: 0.75rem;
}

.btn-google:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn-facebook {
  background-color: #1877f2;
  color: white;
}

.btn-facebook:hover:not(:disabled) {
  background-color: #166fe5;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.icon {
  font-weight: bold;
  font-size: 1.2rem;
}

.divider {
  text-align: center;
  margin: 1.5rem 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #ddd;
}

.divider span {
  background-color: white;
  padding: 0 1rem;
  position: relative;
  color: #666;
}

.social-login {
  margin-bottom: 1rem;
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
