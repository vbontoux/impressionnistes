<template>
  <footer class="site-footer">
    <div class="footer-content">
      <div class="footer-links">
        <router-link to="/privacy-policy" class="footer-link">
          {{ $t('legal.privacyPolicy') }}
        </router-link>
        <span class="footer-separator">|</span>
        <router-link to="/terms-conditions" class="footer-link">
          {{ $t('legal.termsConditions') }}
        </router-link>
        <span class="footer-separator">|</span>
        <a href="#" @click.prevent="openCookiePreferences" class="footer-link">
          {{ $t('legal.cookiePreferences') }}
        </a>
      </div>
      <div class="footer-copyright">
        © {{ currentYear }} Course des Impressionnistes
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());

const emit = defineEmits(['open-cookie-preferences']);

const openCookiePreferences = () => {
  emit('open-cookie-preferences');
};
</script>

<style scoped>
.site-footer {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 2rem 1rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-link {
  color: #3498db;
  text-decoration: none;
  transition: color 0.3s ease;
  font-size: 0.9rem;
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
}

.footer-link:hover {
  color: #5dade2;
  text-decoration: underline;
}

.footer-link:focus {
  outline: 2px solid #3498db;
  outline-offset: 2px;
}

.footer-separator {
  color: #7f8c8d;
  user-select: none;
}

.footer-copyright {
  color: #95a5a6;
  font-size: 0.85rem;
  text-align: center;
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .site-footer {
    padding: 1.5rem 1rem;
  }

  .footer-content {
    gap: 0.75rem;
  }

  .footer-links {
    gap: 0.5rem;
    font-size: 0.85rem;
  }

  .footer-link {
    font-size: 0.85rem;
    padding: 0.375rem;
  }

  .footer-copyright {
    font-size: 0.8rem;
  }
}

/* Tablet and Desktop */
@media (min-width: 768px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
  }

  .footer-links {
    justify-content: flex-start;
  }
}
</style>
