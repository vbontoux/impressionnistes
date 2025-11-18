<template>
  <div id="app" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Top Header -->
    <header class="top-header">
      <button 
        v-if="authStore.isAuthenticated" 
        @click="toggleSidebar" 
        class="menu-toggle"
        :aria-label="$t('nav.toggleMenu')"
      >
        <span class="hamburger"></span>
      </button>
      
      <router-link to="/" class="logo">
        <img src="./assets/rcpm-logo.png" alt="RCPM Logo" class="logo-image" />
        <span class="logo-text">Course des Impressionnistes</span>
      </router-link>

      <div class="header-actions">
        <LanguageSwitcher />
        <template v-if="!authStore.isAuthenticated">
          <router-link to="/login" class="btn-header">{{ $t('nav.login') }}</router-link>
        </template>
      </div>
    </header>

    <!-- Sidebar Navigation (for authenticated users) -->
    <aside v-if="authStore.isAuthenticated" class="sidebar" @click="closeSidebarOnMobile">
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">📊</span>
          <span class="nav-text">{{ $t('nav.dashboard') }}</span>
        </router-link>
        
        <router-link to="/crew" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">👥</span>
          <span class="nav-text">{{ $t('nav.crew') }}</span>
        </router-link>
        
        <router-link to="/boats" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">🚣</span>
          <span class="nav-text">{{ $t('nav.boats') }}</span>
        </router-link>

        <div class="nav-spacer"></div>

        <button @click="handleLogout" class="nav-item nav-logout">
          <span class="nav-icon">🚪</span>
          <span class="nav-text">{{ $t('nav.logout') }}</span>
        </button>
      </nav>
    </aside>

    <!-- Overlay for mobile -->
    <div 
      v-if="authStore.isAuthenticated && sidebarOpen" 
      class="sidebar-overlay" 
      @click="closeSidebar"
    ></div>

    <!-- Main Content -->
    <main class="main-content" :class="{ 'with-sidebar': authStore.isAuthenticated }">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="footer" :class="{ 'with-sidebar': authStore.isAuthenticated }">
      <p>&copy; 2024 RCPM - Course des Impressionnistes</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from './stores/authStore';
import LanguageSwitcher from './components/LanguageSwitcher.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const sidebarOpen = ref(false);

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const closeSidebar = () => {
  sidebarOpen.value = false;
};

const closeSidebarOnMobile = () => {
  // Close sidebar on mobile after navigation
  if (window.innerWidth < 768) {
    closeSidebar();
  }
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
  closeSidebar();
};

// Close sidebar when route changes on mobile
watch(() => route.path, () => {
  if (window.innerWidth < 768) {
    closeSidebar();
  }
});
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
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Top Header */
.top-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  position: relative;
}

.hamburger {
  display: block;
  width: 24px;
  height: 2px;
  background-color: #333;
  position: relative;
  transition: background-color 0.3s;
}

.hamburger::before,
.hamburger::after {
  content: '';
  display: block;
  width: 24px;
  height: 2px;
  background-color: #333;
  position: absolute;
  left: 0;
  transition: all 0.3s;
}

.hamburger::before {
  top: -8px;
}

.hamburger::after {
  top: 8px;
}

/* X icon when sidebar is open */
.sidebar-open .hamburger {
  background-color: transparent;
}

.sidebar-open .hamburger::before {
  top: 0;
  transform: rotate(45deg);
}

.sidebar-open .hamburger::after {
  top: 0;
  transform: rotate(-45deg);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: bold;
  color: #4CAF50;
  text-decoration: none;
  flex: 1;
}

.logo-image {
  height: 36px;
  width: auto;
}

.logo-text {
  color: #4CAF50;
  display: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-header {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.btn-header:hover {
  background-color: #45a049;
}

/* Sidebar */
.sidebar {
  position: fixed;
  left: -280px;
  top: 0;
  bottom: 0;
  width: 280px;
  background-color: #2c3e50;
  padding-top: 70px;
  transition: left 0.3s ease;
  z-index: 99;
  overflow-y: auto;
}

.sidebar-open .sidebar {
  left: 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: background-color 0.3s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 1rem;
}

.nav-item:hover {
  background-color: #34495e;
}

.nav-item.router-link-active {
  background-color: #4CAF50;
  border-left: 4px solid #45a049;
}

.nav-icon {
  font-size: 1.5rem;
  width: 24px;
  text-align: center;
}

.nav-text {
  flex: 1;
}

.nav-spacer {
  flex: 1;
}

.nav-logout {
  color: #e74c3c;
  margin-top: auto;
}

.nav-logout:hover {
  background-color: #c0392b;
  color: white;
}

/* Sidebar Overlay */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 98;
  display: none;
}

.sidebar-open .sidebar-overlay {
  display: block;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.5rem;
  transition: margin-left 0.3s ease;
}

.main-content.with-sidebar {
  margin-left: 0;
}

/* Footer */
.footer {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 1.5rem;
  text-align: center;
  transition: margin-left 0.3s ease;
}

.footer.with-sidebar {
  margin-left: 0;
}

/* Tablet and Desktop */
@media (min-width: 768px) {
  .logo-text {
    display: inline;
  }

  .menu-toggle {
    display: none;
  }

  .sidebar {
    left: 0;
    padding-top: 80px;
  }

  .sidebar-overlay {
    display: none !important;
  }

  .main-content.with-sidebar {
    margin-left: 280px;
  }

  .footer.with-sidebar {
    margin-left: 280px;
  }
}

/* Large Desktop */
@media (min-width: 1200px) {
  .main-content {
    padding: 2rem;
  }
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .top-header {
    padding: 0.75rem;
  }

  .logo {
    font-size: 1rem;
  }

  .logo-image {
    height: 32px;
  }

  .main-content {
    padding: 1rem;
  }

  .btn-header {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
  }
}

/* Ensure responsive images and containers */
img {
  max-width: 100%;
  height: auto;
}

/* Responsive tables */
@media (max-width: 767px) {
  table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>
