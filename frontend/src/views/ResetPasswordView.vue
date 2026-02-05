<template>
  <div class="auth-page">
    <div class="auth-container">
      <ResetPasswordForm />
    </div>
  </div>
</template>

<script setup>
import ResetPasswordForm from '../components/ResetPasswordForm.vue';
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--spacing-lg);
}

.auth-container {
  width: 100%;
  max-width: 500px;
}

/* Mobile responsiveness */
@media (max-width: 767px) {
  .auth-page {
    padding: var(--spacing-md);
  }
}
</style>
