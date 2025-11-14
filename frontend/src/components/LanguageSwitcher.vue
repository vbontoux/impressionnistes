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
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s;
  line-height: 1;
}

.lang-btn:hover {
  border-color: #4CAF50;
  transform: scale(1.1);
}

.lang-btn.active {
  border-color: #4CAF50;
  background-color: #e8f5e9;
}
</style>
