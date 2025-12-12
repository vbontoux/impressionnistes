<template>
  <div id="app" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Session Timeout Warning -->
    <SessionTimeoutWarning 
      :show="sessionTimeout.showWarning.value" 
      :time-remaining="sessionTimeout.timeRemaining.value"
      @continue="sessionTimeout.continueSession"
    />
    
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
          <router-link to="/login" class="btn-header btn-secondary">{{ $t('nav.login') }}</router-link>
          <router-link to="/register" class="btn-header btn-primary">{{ $t('nav.register') }}</router-link>
        </template>
        <template v-else>
          <div class="user-menu" v-click-outside="closeUserMenu">
            <button class="user-menu-button" @click="toggleUserMenu">
              <span class="user-name">{{ authStore.user?.first_name }}</span>
              <svg class="dropdown-icon" :class="{ open: userMenuOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <div v-if="userMenuOpen" class="user-menu-dropdown">
              <router-link to="/profile" class="menu-item" @click="closeUserMenu">
                <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
                  <path d="M6.168 18.849A4 4 0 0 1 10 16h4a4 4 0 0 1 3.834 2.855" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ $t('nav.profile') }}
              </router-link>
              <button @click="handleLogout" class="menu-item logout">
                <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2"/>
                  <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2"/>
                  <path d="M21 12H9" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ $t('nav.logout') }}
              </button>
            </div>
          </div>
        </template>
      </div>
    </header>

    <!-- Sidebar Navigation (for authenticated users) -->
    <aside v-if="authStore.isAuthenticated" class="sidebar" @click="closeSidebarOnMobile">
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.home') }}</span>
        </router-link>

        <router-link to="/dashboard" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
              <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.dashboard') }}</span>
        </router-link>
        
        <router-link to="/crew" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.crew') }}</span>
        </router-link>
        
        <router-link to="/boats" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Rower 1 -->
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <path d="M7 4.5 L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 4.5 L8 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="7" x2="10" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Rower 2 -->
              <circle cx="17" cy="3" r="1.5" fill="currentColor"/>
              <path d="M17 4.5 L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 4.5 L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="13" y1="7" x2="20" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              
              <!-- Boat -->
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              
              <!-- Wave -->
              <path d="M1 16C1 16 3 14.5 6 14.5C9 14.5 11 16 14 16C17 16 19 14.5 22 14.5C23 14.5 24 16 24 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.boats') }}</span>
        </router-link>

        <router-link to="/boat-rentals" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Rental boat icon with key -->
              <line x1="2" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="6" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M6 6V4" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 4H7" stroke="currentColor" stroke-width="1.5"/>
              <!-- Wave -->
              <path d="M2 16C2 16 4 14.5 7 14.5C10 14.5 12 16 15 16C18 16 20 14.5 22 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.boatRentals') }}</span>
        </router-link>
        
        <router-link to="/payment" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.payment') }}</span>
        </router-link>

        <!-- Admin Section (only visible to admins) -->
        <div v-if="authStore.isAdmin" class="nav-divider"></div>
        
        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="currentColor" stroke-width="2"/>
              <path d="M8.21 13.89L7 23L12 20L17 23L15.79 13.88" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="8" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.admin') }}</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin/events" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
              <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2"/>
              <line x1="9" y1="4" x2="9" y2="9" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="4" x2="15" y2="9" stroke="currentColor" stroke-width="2"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.eventConfig') }}</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin/pricing" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6C16.5 4.5 14.5 4 12 4C8 4 5 7 5 12C5 17 8 20 12 20C14.5 20 16.5 19.5 18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="10" x2="13" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="14" x2="13" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.pricingConfig') }}</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin/boats" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="8" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="4" cy="6" r="1.5" fill="currentColor"/>
              <circle cx="4" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="4" cy="18" r="1.5" fill="currentColor"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.boatInventory') }}</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin/exports" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="18" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="9 15 12 18 15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.dataExports') }}</span>
        </router-link>

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
      <p>
        {{ copyrightText }} | 
        <a :href="`mailto:${contactEmail}`" class="footer-link">{{ $t('footer.contactUs') }}</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
const copyrightText = import.meta.env.VITE_COPYRIGHT_TEXT || '© 2024 RCPM - Course des Impressionnistes'
const contactEmail = import.meta.env.VITE_CONTACT_EMAIL || 'impressionnistes@rcpm-aviron.fr'
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from './stores/authStore';
import { useSessionTimeout } from './composables/useSessionTimeout';
import LanguageSwitcher from './components/LanguageSwitcher.vue';
import SessionTimeoutWarning from './components/SessionTimeoutWarning.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const sidebarOpen = ref(false);
const userMenuOpen = ref(false);

// Initialize session timeout monitoring
const sessionTimeout = useSessionTimeout();

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

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value;
};

const closeUserMenu = () => {
  userMenuOpen.value = false;
};

const getInitials = () => {
  const firstName = authStore.user?.first_name || '';
  const lastName = authStore.user?.last_name || '';
  return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase();
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
  closeSidebar();
  closeUserMenu();
};

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};

// Close sidebar when route changes on mobile
watch(() => route.path, () => {
  if (window.innerWidth < 768) {
    closeSidebar();
  }
});

// Watch authentication state to start/stop session monitoring
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    sessionTimeout.startMonitoring();
  } else {
    sessionTimeout.stopMonitoring();
  }
}, { immediate: true });
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

h1 {
  margin-top: 0;
}

h2 {
  margin-top: 0;
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
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.btn-header.btn-primary {
  background-color: #4CAF50;
}

.btn-header.btn-primary:hover {
  background-color: #45a049;
}

.btn-header.btn-secondary {
  background-color: transparent;
  color: #4CAF50;
  border: 1px solid #4CAF50;
}

.btn-header.btn-secondary:hover {
  background-color: #f0f9f0;
}

/* User Menu */
.user-menu {
  position: relative;
}

.user-menu-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.user-menu-button:hover {
  border-color: #4CAF50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
}

.user-name {
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  transition: transform 0.2s;
  color: #666;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.user-menu-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  min-width: 200px;
  z-index: 1000;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-menu-dropdown .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  color: #333;
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s;
  font-size: 0.9rem;
}

.user-menu-dropdown .menu-item:hover {
  background-color: #f8f9fa;
}

.user-menu-dropdown .menu-item .menu-icon {
  width: 20px;
  height: 20px;
  color: #666;
  flex-shrink: 0;
}

.user-menu-dropdown .menu-item.logout {
  color: #e74c3c;
  border-top: 1px solid #f0f0f0;
}

.user-menu-dropdown .menu-item.logout .menu-icon {
  color: #e74c3c;
}

.user-menu-dropdown .menu-item.logout:hover {
  background-color: #fff5f5;
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
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
  color: #ecf0f1;
  transition: color 0.3s;
}

.nav-item:hover .nav-icon svg {
  color: #4CAF50;
}

.nav-item.router-link-active .nav-icon svg {
  color: white;
}

.nav-text {
  flex: 1;
}

.nav-divider {
  height: 1px;
  background-color: #34495e;
  margin: 1rem 1.5rem;
}

.nav-item.admin-item {
  background-color: rgba(52, 152, 219, 0.1);
}

.nav-item.admin-item:hover {
  background-color: rgba(52, 152, 219, 0.2);
}

.nav-item.admin-item.router-link-active {
  background-color: #3498db;
  border-left: 4px solid #2980b9;
}

.nav-item.admin-item:hover .nav-icon svg {
  color: #3498db;
}

.nav-item.admin-item.router-link-active .nav-icon svg {
  color: white;
}

.nav-spacer {
  flex: 1;
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
  padding: 1rem;
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

.footer-link {
  color: #3498db;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #5dade2;
  text-decoration: underline;
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
    padding: 1.5rem;
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
    padding: 0.75rem;
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
