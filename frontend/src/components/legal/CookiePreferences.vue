<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-container" role="dialog" aria-labelledby="modal-title" aria-modal="true">
      <div class="modal-header">
        <h2 id="modal-title">{{ $t('legal.cookiePreferencesTitle') }}</h2>
        <button 
          @click="closeModal" 
          class="close-button"
          aria-label="Close"
          type="button"
        >
          ×
        </button>
      </div>

      <div class="modal-body">
        <p class="modal-description">
          {{ $t('legal.cookiePreferencesDescription') }}
        </p>

        <div class="cookie-categories">
          <!-- Essential Cookies -->
          <div class="cookie-category">
            <div class="category-header">
              <div class="category-info">
                <h3>{{ $t('legal.essentialCookies') }}</h3>
                <p class="category-description">
                  {{ $t('legal.essentialCookiesDesc') }}
                </p>
              </div>
              <div class="toggle-container">
                <label class="toggle-switch disabled">
                  <input 
                    type="checkbox" 
                    :checked="true" 
                    disabled
                    aria-label="Essential cookies (always enabled)"
                  />
                  <span class="toggle-slider"></span>
                </label>
                <span class="always-enabled-label">
                  {{ $t('legal.alwaysEnabled') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Analytics Cookies -->
          <div class="cookie-category">
            <div class="category-header">
              <div class="category-info">
                <h3>{{ $t('legal.analyticsCookies') }}</h3>
                <p class="category-description">
                  {{ $t('legal.analyticsCookiesDesc') }}
                </p>
              </div>
              <div class="toggle-container">
                <label class="toggle-switch">
                  <input 
                    v-model="preferences.analytics" 
                    type="checkbox"
                    :aria-label="$t('legal.analyticsCookies')"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>

          <!-- Marketing Cookies -->
          <div class="cookie-category">
            <div class="category-header">
              <div class="category-info">
                <h3>{{ $t('legal.marketingCookies') }}</h3>
                <p class="category-description">
                  {{ $t('legal.marketingCookiesDesc') }}
                </p>
              </div>
              <div class="toggle-container">
                <label class="toggle-switch">
                  <input 
                    v-model="preferences.marketing" 
                    type="checkbox"
                    :aria-label="$t('legal.marketingCookies')"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="closeModal" class="btn-secondary" type="button">
          {{ $t('common.cancel') }}
        </button>
        <button @click="savePreferences" class="btn-primary" type="button">
          {{ $t('legal.savePreferences') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'preferences-changed']);

const CONSENT_KEY = 'cookie-consent';
const CONSENT_VERSION = '1.0';

const preferences = ref({
  essential: true,  // Always true
  analytics: false,
  marketing: false
});

const loadPreferences = () => {
  try {
    const stored = localStorage.getItem(CONSENT_KEY);
    if (stored) {
      const consent = JSON.parse(stored);
      preferences.value = {
        essential: true,  // Always true
        analytics: consent.analytics || false,
        marketing: consent.marketing || false
      };
    }
  } catch (error) {
    console.error('Error loading cookie preferences from localStorage:', error);
  }
};

// Load existing preferences when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    loadPreferences();
  }
}, { immediate: true });

const savePreferences = () => {
  try {
    const consent = {
      essential: true,  // Always true
      analytics: preferences.value.analytics,
      marketing: preferences.value.marketing,
      timestamp: new Date().toISOString(),
      version: CONSENT_VERSION
    };
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
    emit('preferences-changed', consent);
    closeModal();
  } catch (error) {
    console.error('Error saving cookie preferences to localStorage:', error);
  }
};

const closeModal = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
  overflow-y: auto;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1;
}

.close-button:hover {
  background-color: #f5f5f5;
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-description {
  margin: 0 0 1.5rem 0;
  color: #555;
  line-height: 1.6;
}

.cookie-categories {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cookie-category {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.25rem;
  transition: border-color 0.2s;
}

.cookie-category:hover {
  border-color: #bdbdbd;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.category-info {
  flex: 1;
}

.category-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.category-description {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.5;
}

.toggle-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
  cursor: pointer;
}

.toggle-switch.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  border-radius: 26px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #4CAF50;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.toggle-switch.disabled input:checked + .toggle-slider {
  background-color: #4CAF50;
}

.always-enabled-label {
  font-size: 0.75rem;
  color: #666;
  font-style: italic;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 44px;
  min-width: 44px;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.btn-secondary {
  background-color: transparent;
  color: #2c3e50;
  border: 1px solid #bdbdbd;
}

.btn-secondary:hover {
  background-color: #f5f5f5;
  border-color: #999;
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .modal-container {
    max-height: 95vh;
    margin: 0.5rem;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .cookie-category {
    padding: 1rem;
  }

  .category-header {
    flex-direction: column;
    align-items: stretch;
  }

  .toggle-container {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    margin-top: 0.75rem;
  }

  .always-enabled-label {
    order: -1;
  }

  .modal-footer {
    padding: 1rem;
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
