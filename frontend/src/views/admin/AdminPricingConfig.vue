<template>
  <div class="admin-pricing-config">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <h1>{{ $t('admin.pricingConfig.title') }}</h1>
      <p class="subtitle">{{ $t('admin.pricingConfig.subtitle') }}</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadConfig" class="btn-secondary">{{ $t('common.retry') }}</button>
    </div>

    <div v-else class="config-container">
      <div class="config-form-section">
        <form @submit.prevent="handleSubmit" class="config-form">
          <div class="form-section">
            <h2>{{ $t('admin.pricingConfig.basePricing') }}</h2>
            
            <div class="form-group">
              <label for="base_seat_price">{{ $t('admin.pricingConfig.baseSeatPrice') }}</label>
              <div class="input-with-unit">
                <input
                  id="base_seat_price"
                  v-model.number="formData.base_seat_price"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1000"
                  class="form-control"
                  :class="{ 'error': validationErrors.base_seat_price }"
                />
                <span class="unit">€</span>
              </div>
              <span class="help-text">{{ $t('admin.pricingConfig.baseSeatPriceHelp') }}</span>
              <span v-if="validationErrors.base_seat_price" class="error-text">
                {{ validationErrors.base_seat_price }}
              </span>
            </div>
          </div>

          <div class="form-section">
            <h2>{{ $t('admin.pricingConfig.rentalPricing') }}</h2>
            
            <div class="form-group">
              <label for="skiff_multiplier">{{ $t('admin.pricingConfig.skiffMultiplier') }}</label>
              <div class="input-with-unit">
                <input
                  id="skiff_multiplier"
                  v-model.number="formData.boat_rental_multiplier_skiff"
                  type="number"
                  step="0.1"
                  min="1.0"
                  max="10.0"
                  class="form-control"
                  :class="{ 'error': validationErrors.boat_rental_multiplier_skiff }"
                />
                <span class="unit">x</span>
              </div>
              <span class="help-text">{{ $t('admin.pricingConfig.skiffMultiplierHelp') }}</span>
              <span v-if="validationErrors.boat_rental_multiplier_skiff" class="error-text">
                {{ validationErrors.boat_rental_multiplier_skiff }}
              </span>
            </div>

            <div class="form-group">
              <label for="crew_boat_price">{{ $t('admin.pricingConfig.crewBoatPrice') }}</label>
              <div class="input-with-unit">
                <input
                  id="crew_boat_price"
                  v-model.number="formData.boat_rental_price_crew"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1000"
                  class="form-control"
                  :class="{ 'error': validationErrors.boat_rental_price_crew }"
                />
                <span class="unit">€</span>
              </div>
              <span class="help-text">{{ $t('admin.pricingConfig.crewBoatPriceHelp') }}</span>
              <span v-if="validationErrors.boat_rental_price_crew" class="error-text">
                {{ validationErrors.boat_rental_price_crew }}
              </span>
            </div>
          </div>

          <div v-if="saveError" class="error-message">
            {{ saveError }}
          </div>

          <div v-if="saveSuccess" class="success-message">
            {{ $t('admin.pricingConfig.saveSuccess') }}
          </div>

          <div class="form-actions">
            <button type="button" @click="handleCancel" class="btn-secondary" :disabled="saving">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn-primary" :disabled="saving || !hasChanges">
              {{ saving ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Pricing Preview Calculator -->
      <div class="pricing-preview">
        <h2>{{ $t('admin.pricingConfig.pricingPreview') }}</h2>
        
        <div class="preview-scenarios">
          <div class="scenario">
            <h3>{{ $t('admin.pricingConfig.rcpmMember') }}</h3>
            <div class="price-breakdown">
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.regularSeat') }}:</span>
                <span class="price">{{ formatPrice(0) }}</span>
              </div>
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.rentalSkiff') }}:</span>
                <span class="price">{{ formatPrice(formData.base_seat_price * formData.boat_rental_multiplier_skiff) }}</span>
              </div>
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.rentalCrewBoat') }} ({{ $t('admin.pricingConfig.perSeat') }}):</span>
                <span class="price">{{ formatPrice(formData.boat_rental_price_crew) }}</span>
              </div>
            </div>
          </div>

          <div class="scenario">
            <h3>{{ $t('admin.pricingConfig.externalClub') }}</h3>
            <div class="price-breakdown">
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.regularSeat') }}:</span>
                <span class="price">{{ formatPrice(formData.base_seat_price) }}</span>
              </div>
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.rentalSkiff') }}:</span>
                <span class="price">{{ formatPrice(formData.base_seat_price * formData.boat_rental_multiplier_skiff) }}</span>
              </div>
              <div class="price-item">
                <span>{{ $t('admin.pricingConfig.rentalCrewBoat') }} ({{ $t('admin.pricingConfig.perSeat') }}):</span>
                <span class="price">{{ formatPrice(formData.base_seat_price + formData.boat_rental_price_crew) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="preview-note">
          <p>{{ $t('admin.pricingConfig.previewNote') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const saving = ref(false);
const error = ref(null);
const saveError = ref(null);
const saveSuccess = ref(false);

const originalData = ref({});
const formData = ref({
  base_seat_price: 20.0,
  boat_rental_multiplier_skiff: 2.5,
  boat_rental_price_crew: 20.0
});

const validationErrors = ref({});

const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value);
});

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2
  }).format(price || 0);
};

const loadConfig = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await apiClient.get('/admin/pricing-config');
    const config = response.data.data;
    
    formData.value = {
      base_seat_price: config.base_seat_price || 20.0,
      boat_rental_multiplier_skiff: config.boat_rental_multiplier_skiff || 2.5,
      boat_rental_price_crew: config.boat_rental_price_crew || 20.0
    };
    
    originalData.value = JSON.parse(JSON.stringify(formData.value));
  } catch (err) {
    console.error('Failed to load pricing configuration:', err);
    error.value = t('admin.pricingConfig.loadError');
  } finally {
    loading.value = false;
  }
};

const validateForm = () => {
  validationErrors.value = {};
  
  // Validate base seat price
  if (formData.value.base_seat_price <= 0 || formData.value.base_seat_price > 1000) {
    validationErrors.value.base_seat_price = t('admin.pricingConfig.errors.basePriceRange');
  }
  
  // Validate skiff multiplier
  if (formData.value.boat_rental_multiplier_skiff <= 0 || formData.value.boat_rental_multiplier_skiff > 10) {
    validationErrors.value.boat_rental_multiplier_skiff = t('admin.pricingConfig.errors.multiplierRange');
  }
  
  // Validate crew boat rental price
  if (formData.value.boat_rental_price_crew < 0 || formData.value.boat_rental_price_crew > 1000) {
    validationErrors.value.boat_rental_price_crew = t('admin.pricingConfig.errors.crewPriceRange');
  }
  
  return Object.keys(validationErrors.value).length === 0;
};

const handleSubmit = async () => {
  saveError.value = null;
  saveSuccess.value = false;
  
  if (!validateForm()) {
    return;
  }
  
  // Confirm changes
  if (!confirm(t('admin.pricingConfig.confirmSave'))) {
    return;
  }
  
  saving.value = true;
  
  try {
    const response = await apiClient.put('/admin/pricing-config', formData.value);
    const updatedConfig = response.data.data;
    
    formData.value = {
      base_seat_price: updatedConfig.base_seat_price || 20.0,
      boat_rental_multiplier_skiff: updatedConfig.boat_rental_multiplier_skiff || 2.5,
      boat_rental_price_crew: updatedConfig.boat_rental_price_crew || 20.0
    };
    
    originalData.value = JSON.parse(JSON.stringify(formData.value));
    saveSuccess.value = true;
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (err) {
    console.error('Failed to save pricing configuration:', err);
    saveError.value = err.response?.data?.error?.message || t('admin.pricingConfig.saveError');
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  if (hasChanges.value) {
    if (confirm(t('admin.pricingConfig.confirmCancel'))) {
      router.push('/admin');
    }
  } else {
    router.push('/admin');
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<style scoped>
.admin-pricing-config {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3498db;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.config-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .config-container {
    grid-template-columns: 1fr;
  }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-pricing-config {
    padding: 1rem;
  }

  .page-header {
    margin-bottom: 1.5rem;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .back-link {
    font-size: 16px; /* Prevent iOS zoom */
    min-height: 44px;
    display: inline-flex;
    align-items: center;
  }

  .config-form {
    padding: 1.25rem;
  }

  .form-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
  }

  .form-section h2 {
    font-size: 1.125rem;
  }

  .form-group {
    margin-bottom: 1.25rem;
  }

  .form-group label {
    font-size: 0.9rem;
  }

  .form-control {
    min-height: 44px;
    font-size: 16px; /* Prevent iOS zoom */
    padding: 0.625rem 0.75rem;
  }

  .unit {
    padding: 0.625rem 0.875rem;
    font-size: 16px; /* Prevent iOS zoom */
  }

  .help-text,
  .error-text {
    font-size: 0.8rem;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 0.75rem;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    min-height: 44px;
    font-size: 16px; /* Prevent iOS zoom */
    padding: 0.875rem 1.5rem;
  }

  .pricing-preview {
    padding: 1.25rem;
  }

  .pricing-preview h2 {
    font-size: 1.125rem;
  }

  .scenario {
    padding: 0.875rem;
  }

  .scenario h3 {
    font-size: 1rem;
  }

  .price-item {
    font-size: 0.9rem;
    flex-wrap: wrap;
    gap: 0.25rem;
  }

  .price {
    font-size: 1rem;
  }

  .preview-note {
    padding: 0.875rem;
  }

  .preview-note p {
    font-size: 0.85rem;
  }

  .error-message,
  .success-message {
    padding: 0.875rem;
    font-size: 0.9rem;
  }
}

.config-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.input-with-unit {
  display: flex;
  align-items: center;
}

.form-control {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}

.form-control.error {
  border-color: #e74c3c;
}

.unit {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-left: none;
  border-radius: 0 4px 4px 0;
  padding: 0.75rem 1rem;
  font-weight: 500;
  color: #6c757d;
}

.help-text {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-top: 0.25rem;
}

.error-text {
  display: block;
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.error-message {
  background-color: #fee;
  border: 1px solid #e74c3c;
  color: #c0392b;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.success-message {
  background-color: #d4edda;
  border: 1px solid #28a745;
  color: #155724;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d5dbdb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Pricing Preview */
.pricing-preview {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.pricing-preview h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.preview-scenarios {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.scenario {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.scenario h3 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.price-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.price {
  font-weight: 600;
  color: #27ae60;
}

.preview-note {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.preview-note p {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
}
</style>
