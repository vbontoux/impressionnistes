<template>
  <DataCard class="reset-placeholder" :title="$t('admin.database.reset.placeholderTitle')" :status-badge="false">
    <p class="reset-placeholder__text">{{ $t('admin.database.reset.placeholderDescription') }}</p>
    <template #actions>
      <BaseButton size="small" variant="secondary" :disabled="true">
        {{ $t('admin.database.reset.placeholderBadge') }}
      </BaseButton>
    </template>
  </DataCard>
</template>

<script setup>
import DataCard from '../composite/DataCard.vue'
import BaseButton from '../base/BaseButton.vue'
</script>

<style scoped>
.reset-placeholder {
  opacity: 0.6;
}

.reset-placeholder__text {
  margin: 0;
  color: var(--color-secondary);
}
</style>
