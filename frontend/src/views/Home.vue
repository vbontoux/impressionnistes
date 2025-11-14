<template>
  <div class="home">
    <h1>Welcome to Course des Impressionnistes</h1>
    <p>Registration system for the rowing competition</p>
    <div class="actions">
      <router-link to="/register" class="btn btn-primary">Register</router-link>
      <router-link to="/login" class="btn btn-secondary">Login</router-link>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 3rem 0;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #333;
}

p {
  font-size: 1.25rem;
  color: #666;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #fff;
  color: #4CAF50;
  border: 2px solid #4CAF50;
}

.btn-secondary:hover {
  background-color: #4CAF50;
  color: white;
}
</style>
