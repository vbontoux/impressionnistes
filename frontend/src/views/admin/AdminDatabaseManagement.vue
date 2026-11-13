<template>
  <div class="admin-database-management">
    <ListHeader
      :title="$t('admin.database.title')"
      :subtitle="$t('admin.database.subtitle')"
    />

    <BackupRestoreSection />

    <!-- Area reserved for the future database reset section -->
    <div class="reset-area">
      <DatabaseResetPlaceholder />
    </div>
  </div>
</template>

<script setup>
import ListHeader from '@/components/shared/ListHeader.vue'
import BackupRestoreSection from '@/components/admin/BackupRestoreSection.vue'
import DatabaseResetPlaceholder from '@/components/admin/DatabaseResetPlaceholder.vue'
</script>

<style scoped>
.admin-database-management {
  padding: var(--spacing-lg);
  max-width: 100%;
}

.reset-area {
  margin-top: var(--spacing-xxl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--color-border);
}

@media (min-width: 768px) {
  .admin-database-management {
    padding: var(--spacing-xl);
  }
}
</style>
