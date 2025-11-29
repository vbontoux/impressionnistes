/**
 * Session Timeout Composable
 * Manages inactivity-based session timeout with the following rules:
 * - Logs out after 30 minutes of inactivity
 * - Renews session when user is active
 * - Maximum 5 hours of continuous work without re-login
 */
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds
const MAX_SESSION_DURATION = 5 * 60 * 60 * 1000; // 5 hours in milliseconds
const WARNING_TIME = 2 * 60 * 1000; // Show warning 2 minutes before timeout

export function useSessionTimeout() {
  const router = useRouter();
  const authStore = useAuthStore();
  
  const showWarning = ref(false);
  const timeRemaining = ref(0);
  
  let inactivityTimer = null;
  let warningTimer = null;
  let maxSessionTimer = null;
  let sessionStartTime = null;
  let warningInterval = null;

  /**
   * Events that indicate user activity
   */
  const activityEvents = [
    'mousedown',
    'mousemove',
    'keypress',
    'scroll',
    'touchstart',
    'click',
  ];

  /**
   * Reset the inactivity timer
   */
  const resetInactivityTimer = () => {
    // Clear existing timers
    if (inactivityTimer) clearTimeout(inactivityTimer);
    if (warningTimer) clearTimeout(warningTimer);
    if (warningInterval) clearInterval(warningInterval);
    
    // Hide warning if shown
    showWarning.value = false;

    // Check if we've exceeded max session duration
    if (sessionStartTime) {
      const sessionDuration = Date.now() - sessionStartTime;
      if (sessionDuration >= MAX_SESSION_DURATION) {
        handleSessionExpired('maximum session duration');
        return;
      }
    }

    // Set warning timer (2 minutes before logout)
    warningTimer = setTimeout(() => {
      showWarning.value = true;
      timeRemaining.value = Math.floor(WARNING_TIME / 1000);
      
      // Update countdown every second
      warningInterval = setInterval(() => {
        timeRemaining.value--;
        if (timeRemaining.value <= 0) {
          clearInterval(warningInterval);
        }
      }, 1000);
    }, INACTIVITY_TIMEOUT - WARNING_TIME);

    // Set inactivity timer
    inactivityTimer = setTimeout(() => {
      handleSessionExpired('inactivity');
    }, INACTIVITY_TIMEOUT);
  };

  /**
   * Handle session expiration
   */
  const handleSessionExpired = (reason) => {
    console.log(`Session expired due to ${reason}`);
    
    // Clear all timers
    cleanup();
    
    // Logout user
    authStore.logout();
    
    // Redirect to login with message
    router.push({
      path: '/login',
      query: { 
        expired: 'true',
        reason: reason === 'inactivity' ? 'inactivity' : 'duration'
      }
    });
  };

  /**
   * Handle user activity
   */
  const handleActivity = () => {
    // Only track activity if user is authenticated
    if (!authStore.isAuthenticated) return;
    
    // Throttle activity tracking to avoid excessive timer resets
    if (!handleActivity.lastCall || Date.now() - handleActivity.lastCall > 1000) {
      resetInactivityTimer();
      handleActivity.lastCall = Date.now();
    }
  };

  /**
   * Continue session (dismiss warning)
   */
  const continueSession = () => {
    showWarning.value = false;
    if (warningInterval) clearInterval(warningInterval);
    resetInactivityTimer();
  };

  /**
   * Start monitoring session
   */
  const startMonitoring = () => {
    if (!authStore.isAuthenticated) return;

    // Set session start time
    sessionStartTime = Date.now();

    // Start inactivity timer
    resetInactivityTimer();

    // Set max session timer
    maxSessionTimer = setTimeout(() => {
      handleSessionExpired('maximum session duration');
    }, MAX_SESSION_DURATION);

    // Add activity listeners
    activityEvents.forEach(event => {
      window.addEventListener(event, handleActivity, { passive: true });
    });
  };

  /**
   * Stop monitoring session
   */
  const stopMonitoring = () => {
    cleanup();
    
    // Remove activity listeners
    activityEvents.forEach(event => {
      window.removeEventListener(event, handleActivity);
    });
  };

  /**
   * Cleanup all timers
   */
  const cleanup = () => {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    if (warningTimer) clearTimeout(warningTimer);
    if (maxSessionTimer) clearTimeout(maxSessionTimer);
    if (warningInterval) clearInterval(warningInterval);
    
    inactivityTimer = null;
    warningTimer = null;
    maxSessionTimer = null;
    warningInterval = null;
    sessionStartTime = null;
  };

  /**
   * Initialize on mount
   */
  onMounted(() => {
    if (authStore.isAuthenticated) {
      startMonitoring();
    }
  });

  /**
   * Cleanup on unmount
   */
  onUnmounted(() => {
    stopMonitoring();
  });

  return {
    showWarning,
    timeRemaining,
    continueSession,
    startMonitoring,
    stopMonitoring,
  };
}
