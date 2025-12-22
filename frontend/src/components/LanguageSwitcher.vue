<template>
  <div class="language-switcher">
    <button 
      @click="changeLanguage('fr')" 
      :class="{ active: currentLocale === 'fr' }"
      class="lang-btn"
      title="Français"
    >
      🇫🇷
    </button>
    <button 
      @click="changeLanguage('en')" 
      :class="{ active: currentLocale === 'en' }"
      class="lang-btn"
      title="English"
    >
      🇬🇧
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const currentLocale = computed(() => locale.value);

const changeLanguage = (lang) => {
  locale.value = lang;
  // Store preference in localStorage
  localStorage.setItem('preferred-language', lang);
};
</script>

<style scoped>
/* Mobile-first base styles */
.language-switcher {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.lang-btn {
  background: none;
  border: 2px solid transparent;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}

/* Active state for touch devices */
.lang-btn:active {
  background-color: #e8f5e9;
  border-color: #4CAF50;
  transform: scale(0.95);
}

.lang-btn.active {
  border-color: #4CAF50;
  background-color: #e8f5e9;
}

/* Tablet and desktop hover effects */
@media (min-width: 768px) {
  .lang-btn {
    padding: 0.375rem;
  }

  .lang-btn:hover {
    border-color: #4CAF50;
    transform: scale(1.1);
  }

  .lang-btn:active {
    transform: scale(1.05);
  }
}
</style>
