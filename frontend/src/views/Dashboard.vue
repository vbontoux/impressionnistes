<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div v-if="authStore.user">
      <p>Welcome, {{ authStore.fullName }}!</p>
      <p>Email: {{ authStore.user.email }}</p>
      <p>Club: {{ authStore.user.club_affiliation }}</p>
      <button @click="handleLogout" class="btn btn-secondary">Logout</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.btn-secondary {
  background-color: #f44336;
  color: white;
}
</style>
