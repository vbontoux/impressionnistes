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

    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <MessageAlert 
      v-else-if="error" 
      type="error" 
      :message="error"
    >
      <template #action>
        <BaseButton variant="secondary" size="small" @click="loadConfig">
          {{ $t('common.retry') }}
        </BaseButton>
      </template>
    </MessageAlert>

    <div v-else class="config-container">
      <div class="config-form-section">
        <form @submit.prevent="handleSubmit" class="config-form">
          <div class="form-section">
            <h2>{{ $t('admin.pricingConfig.basePricing') }}</h2>
            
            <FormGroup
              :label="$t('admin.pricingConfig.baseSeatPrice')"
              :help-text="$t('admin.pricingConfig.baseSeatPriceHelp')"
              :error="validationErrors.base_seat_price"
            >
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
            </FormGroup>
          </div>

          <div class="form-section">
            <h2>{{ $t('admin.pricingConfig.rentalPricing') }}</h2>
            
            <FormGroup
              :label="$t('admin.pricingConfig.skiffMultiplier')"
              :help-text="$t('admin.pricingConfig.skiffMultiplierHelp')"
              :error="validationErrors.boat_rental_multiplier_skiff"
            >
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
            </FormGroup>

            <FormGroup
              :label="$t('admin.pricingConfig.crewBoatPrice')"
              :help-text="$t('admin.pricingConfig.crewBoatPriceHelp')"
              :error="validationErrors.boat_rental_price_crew"
            >
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
            </FormGroup>
          </div>

          <MessageAlert 
            v-if="saveError" 
            type="error" 
            :message="saveError"
            :dismissible="true"
            @dismiss="saveError = null"
          />

          <MessageAlert 
            v-if="saveSuccess" 
            type="success" 
            :message="$t('admin.pricingConfig.saveSuccess')"
            :auto-dismiss="3000"
          />

          <div class="form-actions">
            <BaseButton 
              type="button" 
              variant="secondary" 
              size="medium"
              :disabled="saving"
              @click="handleCancel"
            >
              {{ $t('common.cancel') }}
            </BaseButton>
            <BaseButton 
              type="submit" 
              variant="primary" 
              size="medium"
              :disabled="saving || !hasChanges"
              :loading="saving"
            >
              {{ saving ? $t('common.saving') : $t('common.save') }}
            </BaseButton>
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
import { useConfirm } from '../../composables/useConfirm';
import apiClient from '../../services/apiClient';
import BaseButton from '../../components/base/BaseButton.vue';
import FormGroup from '../../components/composite/FormGroup.vue';
import LoadingSpinner from '../../components/base/LoadingSpinner.vue';
import MessageAlert from '../../components/composite/MessageAlert.vue';

const router = useRouter();
const { t } = useI18n();
const { confirm } = useConfirm();

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
  
  // Confirm changes with custom dialog
  const confirmed = await confirm({
    title: t('admin.pricingConfig.confirmSaveTitle'),
    message: t('admin.pricingConfig.confirmSave'),
    confirmText: t('common.save'),
    cancelText: t('common.cancel'),
    variant: 'primary'
  });
  
  if (!confirmed) {
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

const handleCancel = async () => {
  if (hasChanges.value) {
    const confirmed = await confirm({
      title: t('admin.pricingConfig.confirmCancelTitle'),
      message: t('admin.pricingConfig.confirmCancel'),
      confirmText: t('common.yes'),
      cancelText: t('common.no'),
      variant: 'warning'
    });
    
    if (confirmed) {
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
  padding: var(--spacing-xxl);
}

.page-header {
  margin-bottom: var(--spacing-xxl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-primary);
  text-decoration: none;
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.subtitle {
  color: var(--color-muted);
  font-size: var(--font-size-lg);
}

.input-with-unit {
  display: flex;
  align-items: center;
}

.config-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: var(--spacing-xxl);
}

@media (max-width: 1024px) {
  .config-container {
    grid-template-columns: 1fr;
  }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-pricing-config {
    padding: var(--spacing-lg);
  }

  .page-header {
    margin-bottom: var(--spacing-xl);
  }

  .page-header h1 {
    font-size: var(--font-size-2xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
  }

  .back-link {
    font-size: var(--form-input-font-size-mobile);
    min-height: var(--touch-target-min-size);
    display: inline-flex;
    align-items: center;
  }

  .config-form {
    padding: var(--spacing-lg);
  }

  .form-section {
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-xl);
  }

  .form-section h2 {
    font-size: var(--font-size-lg);
  }

  .form-control {
    min-height: var(--form-input-min-height);
    font-size: var(--form-input-font-size-mobile);
    padding: 0.625rem 0.75rem;
  }

  .unit {
    padding: 0.625rem 0.875rem;
    font-size: var(--form-input-font-size-mobile);
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: var(--spacing-md);
  }

  .form-actions :deep(button) {
    width: 100%;
  }

  .pricing-preview {
    padding: var(--spacing-lg);
  }

  .pricing-preview h2 {
    font-size: var(--font-size-lg);
  }

  .scenario {
    padding: var(--spacing-md);
  }

  .scenario h3 {
    font-size: var(--font-size-base);
  }

  .price-item {
    font-size: var(--font-size-sm);
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }

  .price {
    font-size: var(--font-size-base);
  }

  .preview-note {
    padding: var(--spacing-md);
  }

  .preview-note p {
    font-size: var(--font-size-xs);
  }
}

.config-form {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
}

.form-section {
  margin-bottom: var(--spacing-xxl);
  padding-bottom: var(--spacing-xxl);
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-semibold);
}

.input-with-unit {
  display: flex;
  align-items: center;
}

.form-control {
  flex: 1;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius) 0 0 var(--form-input-border-radius);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-normal);
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-control.error {
  border-color: var(--color-danger);
}

.unit {
  background-color: var(--color-light);
  border: 1px solid var(--form-input-border-color);
  border-left: none;
  border-radius: 0 var(--form-input-border-radius) var(--form-input-border-radius) 0;
  padding: var(--form-input-padding);
  padding-left: var(--spacing-lg);
  padding-right: var(--spacing-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-secondary);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: flex-end;
  margin-top: var(--spacing-xxl);
}

/* Pricing Preview */
.pricing-preview {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
  height: fit-content;
}

.pricing-preview h2 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-semibold);
}

.preview-scenarios {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.scenario {
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-lg);
}

.scenario h3 {
  font-size: var(--font-size-lg);
  color: var(--color-dark);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-light);
  font-weight: var(--font-weight-semibold);
}

.price-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) 0;
}

.price {
  font-weight: var(--font-weight-semibold);
  color: var(--color-success);
}

.preview-note {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--color-light);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-primary);
}

.preview-note p {
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  margin: 0;
}
</style>
