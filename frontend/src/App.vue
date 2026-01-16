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
        <img src="./assets/impressionnistes-logo.jpg" alt="Course des Impressionnistes Logo" class="logo-image" />
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

    <!-- Admin Impersonation Bar (only visible when actively impersonating) -->
    <AdminImpersonationBar v-if="authStore.isAdmin && authStore.isImpersonating" />

    <!-- Sidebar Navigation (for authenticated users) -->
    <aside v-if="authStore.isAuthenticated" class="sidebar" :class="{ 'with-impersonation': authStore.isImpersonating }" @click="closeSidebarOnMobile">
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
        
        <router-link to="/payment" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="1" y1="10" x2="23" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.payment') }}</span>
        </router-link>

        <router-link to="/payment/history" class="nav-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.paymentHistory') }}</span>
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

        <router-link v-if="authStore.isAdmin" to="/admin/crew" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.crewMembers') }}</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin/boat-registrations" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="7" cy="3" r="1.5" fill="currentColor"/>
              <path d="M7 4.5 L3 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 4.5 L8 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="7" x2="10" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <circle cx="17" cy="3" r="1.5" fill="currentColor"/>
              <path d="M17 4.5 L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 4.5 L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="13" y1="7" x2="20" y2="17" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="1" y1="11" x2="23" y2="11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              <path d="M1 16C1 16 3 14.5 6 14.5C9 14.5 11 16 14 16C17 16 19 14.5 22 14.5C23 14.5 24 16 24 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.boatRegistrations') }}</span>
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

        <router-link v-if="authStore.isAdmin" to="/admin/payment-analytics" class="nav-item admin-item" @click="closeSidebarOnMobile">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2V22M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">{{ $t('nav.paymentAnalytics') }}</span>
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
    <Footer 
      :class="{ 'with-sidebar': authStore.isAuthenticated }"
      @open-cookie-preferences="showCookiePreferences = true"
    />

    <!-- Cookie Preferences Modal -->
    <CookiePreferences 
      :is-open="showCookiePreferences"
      @close="showCookiePreferences = false"
    />

    <!-- Cookie Consent Banner -->
    <CookieBanner 
      @customize="showCookiePreferences = true"
      @consent-changed="handleConsentChanged"
    />

    <!-- Global Confirm Dialog -->
    <ConfirmDialog
      :show="confirmDialog.showDialog.value"
      :title="confirmDialog.dialogConfig.value.title"
      :message="confirmDialog.dialogConfig.value.message"
      :confirm-text="confirmDialog.dialogConfig.value.confirmText"
      :cancel-text="confirmDialog.dialogConfig.value.cancelText"
      :variant="confirmDialog.dialogConfig.value.variant"
      @confirm="confirmDialog.handleConfirm"
      @cancel="confirmDialog.handleCancel"
      @close="confirmDialog.handleClose"
    />
  </div>
</template>

<script setup>
const copyrightText = import.meta.env.VITE_COPYRIGHT_TEXT || '© 2024 RCPM - Course des Impressionnistes'
const contactEmail = import.meta.env.VITE_CONTACT_EMAIL || 'impressionnistes@rcpm-aviron.fr'
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from './stores/authStore';
import { useSessionTimeout } from './composables/useSessionTimeout';
import { useConfirm } from './composables/useConfirm';
import LanguageSwitcher from './components/LanguageSwitcher.vue';
import SessionTimeoutWarning from './components/SessionTimeoutWarning.vue';
import Footer from './components/layout/Footer.vue';
import CookiePreferences from './components/legal/CookiePreferences.vue';
import CookieBanner from './components/legal/CookieBanner.vue';
import AdminImpersonationBar from './components/AdminImpersonationBar.vue';
import ConfirmDialog from './components/base/ConfirmDialog.vue';
import apiClient from './services/apiClient';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const sidebarOpen = ref(false);
const userMenuOpen = ref(false);
const showCookiePreferences = ref(false);

// Initialize session timeout monitoring
const sessionTimeout = useSessionTimeout();

// Initialize global confirm dialog
const confirmDialog = useConfirm();

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

const handleConsentChanged = (consent) => {
  // Handle cookie consent changes
  // This can be used to enable/disable analytics or marketing cookies
  console.log('Cookie consent updated:', consent);
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

// Navigation guard: Preserve impersonation parameter across all routes
router.beforeEach((to, from, next) => {
  // If admin is impersonating, ensure team_manager_id is in ALL routes
  if (authStore.isAdmin && authStore.impersonatedTeamManagerId) {
    if (to.query.team_manager_id !== authStore.impersonatedTeamManagerId) {
      // Add the parameter to the destination route
      next({
        ...to,
        query: {
          ...to.query,
          team_manager_id: authStore.impersonatedTeamManagerId
        }
      })
      return
    }
  }
  next()
})

// Watch route query param → update store (URL → Store sync)
watch(() => route.query.team_manager_id, async (teamManagerId) => {
  console.log('🔍 App.vue watcher triggered - team_manager_id:', teamManagerId)
  console.log('🔍 Current authStore state:', {
    isAdmin: authStore.isAdmin,
    impersonatedTeamManagerId: authStore.impersonatedTeamManagerId
  })
  
  // Only process if user is admin
  if (!authStore.isAdmin) {
    console.log('🔍 User is not admin, skipping watcher')
    return;
  }

  if (teamManagerId && teamManagerId !== authStore.impersonatedTeamManagerId) {
    console.log('🔍 Need to fetch team manager details for:', teamManagerId)
    
    // Fetch team manager details from API
    try {
      const response = await apiClient.get('/admin/team-managers');
      console.log('🔍 Fetched team managers:', response.data)
      
      // API returns {success: true, data: {team_managers: [...], count: N}}
      const teamManagers = response.data?.data?.team_managers || [];
      console.log('🔍 Team managers array:', teamManagers)
      
      const teamManager = teamManagers.find(tm => tm.user_id === teamManagerId);
      console.log('🔍 Found team manager:', teamManager)
      
      if (teamManager) {
        console.log('🔍 Setting impersonation in store')
        authStore.setImpersonation(teamManagerId, teamManager);
      } else {
        console.warn('🔍 Team manager not found:', teamManagerId);
        authStore.clearImpersonation();
      }
    } catch (error) {
      console.error('🔍 Failed to fetch team manager details:', error);
      authStore.clearImpersonation();
    }
  } else if (!teamManagerId && authStore.impersonatedTeamManagerId) {
    console.log('🔍 No team_manager_id in URL but store has one - clearing')
    // Clear impersonation if parameter is removed
    authStore.clearImpersonation();
  } else {
    console.log('🔍 No action needed - states match')
  }
}, { immediate: true });

// Watch store → update route query param (Store → URL sync)
watch(() => authStore.impersonatedTeamManagerId, (teamManagerId) => {
  console.log('🔄 Store changed - impersonatedTeamManagerId:', teamManagerId)
  console.log('🔄 Current route query:', route.query)
  
  // Only process if user is admin
  if (!authStore.isAdmin) {
    console.log('🔄 User is not admin, skipping')
    return;
  }

  const currentQuery = { ...route.query };
  
  if (teamManagerId) {
    // Add or update team_manager_id parameter
    if (currentQuery.team_manager_id !== teamManagerId) {
      console.log('🔄 Adding team_manager_id to URL:', teamManagerId)
      currentQuery.team_manager_id = teamManagerId;
      router.replace({ query: currentQuery });
    } else {
      console.log('🔄 URL already has correct team_manager_id')
    }
  } else {
    // Remove team_manager_id parameter
    if (currentQuery.team_manager_id) {
      console.log('🔄 Removing team_manager_id from URL')
      delete currentQuery.team_manager_id;
      router.replace({ query: currentQuery });
    } else {
      console.log('🔄 URL already has no team_manager_id')
    }
  }
}, { immediate: true });
</script>

<style>
/* Import Design Tokens */
@import './assets/design-tokens.css';

/* Import Utility Classes */
@import './styles/utilities.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: var(--line-height-normal);
  color: var(--color-dark);
  background-color: var(--color-bg-light);
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
  background-color: var(--color-bg-white);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  position: sticky;
  top: 0;
  z-index: var(--z-index-dropdown);
}

.menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-width: var(--touch-target-min-size);
  min-height: var(--touch-target-min-size);
  width: var(--touch-target-min-size);
  height: var(--touch-target-min-size);
  position: relative;
}

.hamburger {
  display: block;
  width: 24px;
  height: 2px;
  background-color: var(--color-dark);
  position: relative;
  transition: var(--transition-slow);
}

.hamburger::before,
.hamburger::after {
  content: '';
  display: block;
  width: 24px;
  height: 2px;
  background-color: var(--color-dark);
  position: absolute;
  left: 0;
  transition: var(--transition-slow);
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
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
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
  gap: var(--spacing-sm);
}

.btn-header {
  padding: var(--spacing-sm) var(--spacing-lg);
  color: var(--color-white);
  text-decoration: none;
  border-radius: var(--button-border-radius);
  font-size: var(--button-font-size-sm);
  transition: var(--transition-slow);
  white-space: nowrap;
  min-height: var(--touch-target-min-size);
  min-width: var(--touch-target-min-size);
  display: flex;
  align-items: center;
  justify-content: center;
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
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  background-color: var(--color-bg-white);
  color: var(--color-dark);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--button-font-size-sm);
  cursor: pointer;
  transition: var(--button-transition);
  white-space: nowrap;
  min-height: var(--touch-target-min-size);
  min-width: var(--touch-target-min-size);
}

.user-menu-button:hover {
  border-color: #4CAF50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
}

.user-name {
  font-weight: var(--font-weight-medium);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  transition: var(--transition-normal);
  color: var(--color-muted);
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.user-menu-dropdown {
  position: absolute;
  top: calc(100% + var(--spacing-sm));
  right: 0;
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  z-index: var(--z-index-modal);
  overflow: hidden;
  animation: slideDown var(--transition-normal) ease;
}

/* Ensure dropdown stays within viewport on mobile */
@media (max-width: 767px) {
  .user-menu-dropdown {
    right: 0;
    left: auto;
    max-width: calc(100vw - 2rem);
  }
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
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-dark);
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: var(--transition-fast);
  font-size: var(--button-font-size-sm);
  min-height: var(--touch-target-min-size);
}

.user-menu-dropdown .menu-item:hover {
  background-color: var(--color-light);
}

.user-menu-dropdown .menu-item .menu-icon {
  width: 20px;
  height: 20px;
  color: var(--color-muted);
  flex-shrink: 0;
}

.user-menu-dropdown .menu-item.logout {
  color: var(--color-danger);
  border-top: 1px solid var(--color-border);
}

.user-menu-dropdown .menu-item.logout .menu-icon {
  color: var(--color-danger);
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
  transition: var(--transition-slow);
  z-index: 99;
  overflow-y: auto;
}

.sidebar-open .sidebar {
  left: 0;
}

/* Add extra padding when impersonation bar is visible */
.sidebar.with-impersonation {
  padding-top: 150px; /* 70px header + ~80px impersonation bar */
}

@media (min-width: 768px) {
  .sidebar.with-impersonation {
    padding-top: 160px; /* 80px header + ~80px impersonation bar */
  }
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-lg) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg) var(--spacing-xl);
  color: #ecf0f1;
  text-decoration: none;
  transition: var(--transition-slow);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: var(--font-size-lg);
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
  transition: var(--transition-slow);
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
  margin: var(--spacing-lg) var(--spacing-xl);
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
  background-color: var(--color-bg-overlay);
  z-index: 98;
  display: none;
}

.sidebar-open .sidebar-overlay {
  display: block;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: var(--spacing-lg);
  transition: var(--transition-slow);
}

.main-content.with-sidebar {
  margin-left: 0;
}

/* Tablet and Desktop */
@media (min-width: 768px) {
  .top-header {
    padding: var(--spacing-lg);
    gap: var(--spacing-lg);
  }

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

  /* Footer with sidebar */
  .site-footer.with-sidebar {
    margin-left: 280px;
  }

  .header-actions {
    gap: var(--spacing-lg);
  }
}

/* Large Desktop */
@media (min-width: 1200px) {
  .main-content {
    padding: var(--spacing-xl);
  }
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .top-header {
    padding: var(--spacing-sm) var(--spacing-md);
    gap: var(--spacing-sm);
  }

  .logo {
    font-size: var(--button-font-size-sm);
    gap: var(--spacing-sm);
  }

  .logo-image {
    height: 32px;
  }

  .logo-text {
    display: none;
  }

  .main-content {
    padding: var(--spacing-md);
  }

  .btn-header {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
    min-height: var(--touch-target-min-size);
  }

  .user-menu-button {
    padding: var(--spacing-sm) var(--spacing-md);
    min-height: var(--touch-target-min-size);
  }

  .user-name {
    max-width: 80px;
  }

  .header-actions {
    gap: var(--spacing-sm);
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
