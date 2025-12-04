<template>
  <div class="callback-view">
    <div class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('auth.callback.processing') }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  try {
    // Get the authorization code from URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (!code) {
      console.error('No authorization code found');
      router.push('/login');
      return;
    }

    // Exchange code for tokens with Cognito
    const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN;
    const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;
    const REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI || window.location.origin + '/callback';

    const tokenResponse = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: CLIENT_ID,
        code: code,
        redirect_uri: REDIRECT_URI,
      }),
    });

    if (!tokenResponse.ok) {
      throw new Error('Failed to exchange code for tokens');
    }

    const tokens = await tokenResponse.json();
    
    // Decode the ID token to get user info
    const idTokenPayload = JSON.parse(atob(tokens.id_token.split('.')[1]));
    
    // Store tokens and user info
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('id_token', tokens.id_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    
    // Extract groups from Cognito token
    const groups = idTokenPayload['cognito:groups'] || [];
    
    // Set auth in store
    await authStore.setAuthFromCognito(tokens.access_token, {
      sub: idTokenPayload.sub,
      email: idTokenPayload.email,
      given_name: idTokenPayload.given_name,
      family_name: idTokenPayload.family_name,
      groups: groups,
    });

    // Redirect to dashboard
    router.push('/dashboard');
  } catch (error) {
    console.error('Callback error:', error);
    router.push('/login');
  }
});
</script>

<style scoped>
.callback-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.loading-container {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  color: #666;
  font-size: 1.1rem;
}
</style>
