<template>
  <div class="admin-permission-config">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <h1>{{ $t('admin.permissions.title') }}</h1>
      <p class="subtitle">{{ $t('admin.permissions.subtitle') }}</p>
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
        :message="$t('admin.permissions.saveSuccess')"
        :auto-dismiss="3000"
      />

      <div class="matrix-section">
        <PermissionMatrixTable
          v-model:permissions="formData"
          :disabled="saving"
        />
      </div>

      <div class="form-actions">
        <BaseButton 
          type="button" 
          variant="secondary" 
          size="medium"
          :disabled="saving"
          @click="handleReset"
        >
          {{ $t('admin.permissions.resetToDefaults') }}
        </BaseButton>
        <div class="action-group">
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
            type="button" 
            variant="primary" 
            size="medium"
            :disabled="saving || !hasChanges"
            :loading="saving"
            @click="handleSave"
          >
            {{ saving ? $t('common.saving') : $t('common.save') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useConfirm } from '../../composables/useConfirm'
import { usePermissions } from '../../composables/usePermissions'
import { clearPermissionCache } from '../../composables/usePermissions'
import apiClient from '../../services/apiClient'
import BaseButton from '../../components/base/BaseButton.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import MessageAlert from '../../components/composite/MessageAlert.vue'
import PermissionMatrixTable from '../../components/admin/PermissionMatrixTable.vue'

const router = useRouter()
const { t } = useI18n()
const { confirm } = useConfirm()
const { refresh: refreshPermissions } = usePermissions()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const saveError = ref(null)
const saveSuccess = ref(false)

const originalData = ref({})
const formData = ref({})

const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value)
})

const loadConfig = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get('/admin/permissions/config')
    const permissions = response.data.permissions || {}
    
    formData.value = { ...permissions }
    originalData.value = JSON.parse(JSON.stringify(permissions))
  } catch (err) {
    console.error('Failed to load permission configuration:', err)
    error.value = t('admin.permissions.loadError')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saveError.value = null
  saveSuccess.value = false
  
  // Confirm changes with custom dialog
  const confirmed = await confirm({
    title: t('admin.permissions.confirmSaveTitle'),
    message: t('admin.permissions.confirmSave'),
    confirmText: t('common.save'),
    cancelText: t('common.cancel'),
    variant: 'primary'
  })
  
  if (!confirmed) {
    return
  }
  
  saving.value = true
  
  try {
    const response = await apiClient.put('/admin/permissions/config', {
      permissions: formData.value
    })
    
    const updatedPermissions = response.data.permissions || {}
    formData.value = { ...updatedPermissions }
    originalData.value = JSON.parse(JSON.stringify(updatedPermissions))
    
    // Clear permission cache globally so all components get fresh permissions
    clearPermissionCache()
    
    // Refresh permissions in this component's instance
    await refreshPermissions()
    
    saveSuccess.value = true
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('Failed to save permission configuration:', err)
    saveError.value = err.response?.data?.error?.message || t('admin.permissions.saveError')
  } finally {
    saving.value = false
  }
}

const handleReset = async () => {
  // Confirm reset with custom dialog
  const confirmed = await confirm({
    title: t('admin.permissions.confirmResetTitle'),
    message: t('admin.permissions.confirmReset'),
    confirmText: t('admin.permissions.resetToDefaults'),
    cancelText: t('common.cancel'),
    variant: 'warning'
  })
  
  if (!confirmed) {
    return
  }
  
  saveError.value = null
  saveSuccess.value = false
  saving.value = true
  
  try {
    const response = await apiClient.post('/admin/permissions/reset')
    const defaultPermissions = response.data.permissions || {}
    
    formData.value = { ...defaultPermissions }
    originalData.value = JSON.parse(JSON.stringify(defaultPermissions))
    
    saveSuccess.value = true
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('Failed to reset permission configuration:', err)
    saveError.value = err.response?.data?.error?.message || t('admin.permissions.saveError')
  } finally {
    saving.value = false
  }
}

const handleCancel = async () => {
  if (hasChanges.value) {
    const confirmed = await confirm({
      title: t('admin.eventConfig.confirmCancelTitle'),
      message: t('admin.eventConfig.confirmCancel'),
      confirmText: t('common.yes'),
      cancelText: t('common.no'),
      variant: 'warning'
    })
    
    if (confirmed) {
      router.push('/admin')
    }
  } else {
    router.push('/admin')
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.admin-permission-config {
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

.config-container {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
}

.matrix-section {
  margin-bottom: var(--spacing-xxl);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-xxl);
  border-top: 1px solid var(--color-border);
}

.action-group {
  display: flex;
  gap: var(--spacing-lg);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-permission-config {
    padding: var(--spacing-lg);
    max-width: 100%;
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

  .config-container {
    padding: var(--spacing-lg);
    max-width: 100%;
  }

  .matrix-section {
    margin-bottom: var(--spacing-xl);
  }

  .form-actions {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }

  .action-group {
    flex-direction: column-reverse;
    gap: var(--spacing-md);
  }

  .form-actions :deep(button) {
    width: 100%;
  }
}
</style>
