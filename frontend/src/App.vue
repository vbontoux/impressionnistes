<template>
  <div id="app">
    <nav class="navbar">
      <div class="container">
        <router-link to="/" class="logo">
          <img src="./assets/rcpm-logo.png" alt="RCPM Logo" class="logo-image" />
          <span class="logo-text">Course des Impressionnistes</span>
        </router-link>
        <div class="nav-links">
          <LanguageSwitcher />
          <router-link to="/login">{{ $t('nav.login') }}</router-link>
          <router-link to="/register">{{ $t('nav.register') }}</router-link>
        </div>
      </div>
    </nav>

    <main class="container">
      <router-view />
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2024 RCPM - Course des Impressionnistes</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import LanguageSwitcher from './components/LanguageSwitcher.vue';
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.navbar {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem 0;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: bold;
  color: #4CAF50;
  text-decoration: none;
}

.logo-image {
  height: 40px;
  width: auto;
}

.logo-text {
  color: #4CAF50;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-links a {
  color: #666;
  text-decoration: none;
  transition: color 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #4CAF50;
}

main {
  flex: 1;
  padding: 2rem 0;
}

.footer {
  background-color: #333;
  color: #fff;
  padding: 1.5rem 0;
  margin-top: auto;
  text-align: center;
}
</style>
