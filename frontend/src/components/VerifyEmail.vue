<template>
  <div class="verify-email">
    <div class="form-header">
      <img src="../assets/impressionnistes-logo.jpg" alt="Course des Impressionnistes Logo" class="form-logo" />
      <h2>{{ $t('auth.verify.title') }}</h2>
      <p class="subtitle">{{ $t('auth.verify.subtitle') }}</p>
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

    <form v-if="!successMessage" @submit.prevent="handleSubmit">
      <!-- Email -->
      <FormGroup
        :label="$t('auth.verify.email')"
        :required="true"
      >
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          :disabled="loading"
        />
      </FormGroup>

      <!-- Verification Code -->
      <FormGroup
        :label="$t('auth.verify.code')"
        :required="true"
        :help-text="$t('auth.verify.codeHint')"
      >
        <input
          id="code"
          v-model="form.code"
          type="text"
          required
          :disabled="loading"
          placeholder="123456"
          maxlength="6"
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
        {{ loading ? $t('common.loading') : $t('auth.verify.submit') }}
      </BaseButton>

      <!-- Resend Code -->
      <div class="resend-button">
        <BaseButton
          type="button"
          variant="secondary"
          size="medium"
          :full-width="true"
          :disabled="loading || resendDisabled"
          @click="resendCode"
        >
          {{ $t('auth.verify.resend') }}
          <span v-if="resendTimer > 0">({{ resendTimer }}s)</span>
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import FormGroup from './composite/FormGroup.vue';
import BaseButton from './base/BaseButton.vue';
import MessageAlert from './composite/MessageAlert.vue';

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

.subtitle {
  text-align: center;
  color: var(--color-muted);
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.resend-button {
  margin-top: var(--spacing-md);
}

/* Mobile responsiveness */
@media (max-width: 767px) {
  .verify-email {
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
