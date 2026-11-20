<template>
  <div class="admin-database-management">
    <ListHeader
      :title="$t('admin.database.title')"
      :subtitle="$t('admin.database.subtitle')"
    />
    <div ref="backupArea" class="backup-area" tabindex="-1">
      <BackupRestoreSection
        ref="backupSection"
        :external-busy="resetBusy"
        @busy-change="backupBusy = $event"
      />
    </div>
    <div class="reset-area">
      <DatabaseResetSection
        :external-busy="backupBusy"
        @busy-change="resetBusy = $event"
        @restore-backup="onRestoreBackup"
        @purged="onPurged"
      />
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick } from 'vue'
import ListHeader from '@/components/shared/ListHeader.vue'
import BackupRestoreSection from '@/components/admin/BackupRestoreSection.vue'
import DatabaseResetSection from '@/components/admin/DatabaseResetSection.vue'

const backupSection = ref(null)
const backupArea = ref(null)
const backupBusy = ref(false)
const resetBusy = ref(false)

async function onRestoreBackup(id) {
  // The pre-reset backup is not in the loaded list yet
  await backupSection.value?.reload()
  backupSection.value?.selectById(id)
  await nextTick()
  backupArea.value?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  backupArea.value?.focus?.({ preventScroll: true })
}

async function onPurged() {
  await backupSection.value?.reload()
}
</script>
<style scoped>
.admin-database-management {
  padding: var(--spacing-lg);
  max-width: 100%;
}
.backup-area:focus {
  outline: none;
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
