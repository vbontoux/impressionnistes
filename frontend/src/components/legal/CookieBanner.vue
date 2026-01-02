<template>
  <div v-if="showBanner" class="cookie-banner">
    <div class="cookie-banner-content">
      <div class="cookie-banner-text">
        <p>{{ $t('legal.cookieBannerText') }}</p>
        <router-link to="/privacy-policy" class="cookie-banner-link" target="_blank">
          {{ $t('legal.learnMore') }}
        </router-link>
      </div>
      <div class="cookie-banner-actions">
        <button @click="rejectAll" class="btn-cookie btn-secondary">
          {{ $t('legal.rejectAll') }}
        </button>
        <button @click="showCustomize" class="btn-cookie btn-secondary">
          {{ $t('legal.customize') }}
        </button>
        <button @click="acceptAll" class="btn-cookie btn-primary">
          {{ $t('legal.acceptAll') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const showBanner = ref(false);
const emit = defineEmits(['consent-changed', 'customize']);

const CONSENT_KEY = 'cookie-consent';
const CONSENT_VERSION = '1.0';

onMounted(() => {
  // Check if consent preference already exists
  const existingConsent = getConsentPreference();
  if (!existingConsent) {
    showBanner.value = true;
  }
});

const getConsentPreference = () => {
  try {
    const stored = localStorage.getItem(CONSENT_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Error reading cookie consent from localStorage:', error);
    return null;
  }
};

const saveConsentPreference = (preferences) => {
  try {
    const consent = {
      ...preferences,
      timestamp: new Date().toISOString(),
      version: CONSENT_VERSION
    };
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
    emit('consent-changed', consent);
  } catch (error) {
    console.error('Error saving cookie consent to localStorage:', error);
  }
};

const acceptAll = () => {
  const preferences = {
    essential: true,
    analytics: true,
    marketing: true
  };
  saveConsentPreference(preferences);
  showBanner.value = false;
};

const rejectAll = () => {
  const preferences = {
    essential: true,  // Essential cookies always enabled
    analytics: false,
    marketing: false
  };
  saveConsentPreference(preferences);
  showBanner.value = false;
};

const showCustomize = () => {
  emit('customize');
  showBanner.value = false;
};
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #2c3e50;
  color: white;
  padding: 1.5rem;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.cookie-banner-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cookie-banner-text {
  flex: 1;
}

.cookie-banner-text p {
  margin: 0 0 0.5rem 0;
  line-height: 1.6;
}

.cookie-banner-link {
  color: #3498db;
  text-decoration: underline;
  transition: color 0.2s;
}

.cookie-banner-link:hover {
  color: #5dade2;
}

.cookie-banner-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-cookie {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-height: 44px;
  min-width: 44px;
}

.btn-cookie.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-cookie.btn-primary:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.btn-cookie.btn-secondary {
  background-color: transparent;
  color: white;
  border: 1px solid white;
}

.btn-cookie.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Tablet and Desktop */
@media (min-width: 768px) {
  .cookie-banner-content {
    flex-direction: row;
    align-items: center;
    gap: 2rem;
  }

  .cookie-banner-actions {
    flex-shrink: 0;
  }
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .cookie-banner {
    padding: 1rem;
  }

  .cookie-banner-actions {
    flex-direction: column;
  }

  .btn-cookie {
    width: 100%;
  }
}
</style>
