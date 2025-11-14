import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createI18n } from 'vue-i18n';
import App from './App.vue';
import router from './router';

// Import translations
import en from './locales/en.json';
import fr from './locales/fr.json';

// Detect browser language
const getBrowserLocale = () => {
  const savedLocale = localStorage.getItem('preferred-language');
  if (savedLocale) {
    return savedLocale;
  }
  
  const browserLocale = navigator.language || navigator.userLanguage;
  // Extract language code (e.g., 'fr-FR' -> 'fr')
  const languageCode = browserLocale.split('-')[0];
  
  // Return 'fr' if French, otherwise default to 'en'
  return languageCode === 'fr' ? 'fr' : 'en';
};

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: getBrowserLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    fr,
  },
});

// Create app
const app = createApp(App);

// Use plugins
app.use(createPinia());
app.use(router);
app.use(i18n);

// Mount app
app.mount('#app');
