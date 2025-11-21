<template>
  <div class="verify-email">
    <div class="form-header">
      <img src="../assets/rcpm-logo.png" alt="RCPM Logo" class="form-logo" />
      <h2>{{ $t('auth.verify.title') }}</h2>
      <p class="subtitle">{{ $t('auth.verify.subtitle') }}</p>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Email -->
      <div class="form-group">
        <label for="email">{{ $t('auth.verify.email') }} *</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          :disabled="loading"
        />
      </div>

      <!-- Verification Code -->
      <div class="form-group">
        <label for="code">{{ $t('auth.verify.code') }} *</label>
        <input
          id="code"
          v-model="form.code"
          type="text"
          required
          :disabled="loading"
          placeholder="123456"
          maxlength="6"
        />
        <small class="hint">{{ $t('auth.verify.codeHint') }}</small>
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
        <span v-else>{{ $t('auth.verify.submit') }}</span>
      </button>

      <!-- Resend Code -->
      <button 
        type="button" 
        @click="resendCode" 
        class="btn btn-secondary"
        :disabled="loading || resendDisabled"
      >
        {{ $t('auth.verify.resend') }}
        <span v-if="resendTimer > 0">({{ resendTimer }}s)</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();

const form = reactive({
  email: '',
  code: '',
});

// Pre-populate email from URL parameter
onMounted(() => {
  if (route.query.email) {
    form.email = route.query.email;
  }
});

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const resendDisabled = ref(false);
const resendTimer = ref(0);

// Get Cognito configuration
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  loading.value = true;

  try {
    // Use AWS Cognito SDK to confirm sign up
    const { CognitoIdentityProviderClient, ConfirmSignUpCommand } = await import('@aws-sdk/client-cognito-identity-provider');
    
    const client = new CognitoIdentityProviderClient({ region: 'eu-west-3' });
    const command = new ConfirmSignUpCommand({
      ClientId: COGNITO_CLIENT_ID,
      Username: form.email,
      ConfirmationCode: form.code,
    });

    await client.send(command);
    
    successMessage.value = t('auth.verify.success');
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } catch (error) {
    console.error('Verification error:', error);
    
    if (error.name === 'CodeMismatchException') {
      errorMessage.value = t('auth.verify.invalidCode');
    } else if (error.name === 'ExpiredCodeException') {
      errorMessage.value = t('auth.verify.expiredCode');
    } else {
      errorMessage.value = error.message || t('auth.verify.error');
    }
  } finally {
    loading.value = false;
  }
};

const resendCode = async () => {
  errorMessage.value = '';
  loading.value = true;
  resendDisabled.value = true;

  try {
    const { CognitoIdentityProviderClient, ResendConfirmationCodeCommand } = await import('@aws-sdk/client-cognito-identity-provider');
    
    const client = new CognitoIdentityProviderClient({ region: 'eu-west-3' });
    const command = new ResendConfirmationCodeCommand({
      ClientId: COGNITO_CLIENT_ID,
      Username: form.email,
    });

    await client.send(command);
    
    successMessage.value = t('auth.verify.resendSuccess');
    
    // Start countdown timer (60 seconds)
    resendTimer.value = 60;
    const interval = setInterval(() => {
      resendTimer.value--;
      if (resendTimer.value <= 0) {
        clearInterval(interval);
        resendDisabled.value = false;
      }
    }, 1000);
  } catch (error) {
    console.error('Resend error:', error);
    errorMessage.value = error.message || t('auth.verify.resendError');
    resendDisabled.value = false;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.verify-email {
  max-width: 400px;
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
  margin-bottom: 0.75rem;
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
  color: #4CAF50;
  border: 1px solid #4CAF50;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
