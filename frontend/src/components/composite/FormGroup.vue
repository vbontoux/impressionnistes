<template>
  <div class="form-group" :class="{ 'has-error': error }">
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
      <span v-if="required" class="required-indicator">*</span>
    </label>
    
    <slot></slot>
    
    <span v-if="error" class="error-message">{{ error }}</span>
    <span v-if="helpText && !error" class="help-text">{{ helpText }}</span>
  </div>
</template>

<script>
export default {
  name: 'FormGroup',
  props: {
    label: {
      type: String,
      default: ''
    },
    required: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: ''
    },
    inputId: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--form-label-gap, 0.5rem);
  margin-bottom: var(--form-group-gap, 1rem);
}

.form-label {
  font-size: var(--font-size-base, 0.875rem);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-muted, #666);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 0.25rem);
}

.required-indicator {
  color: var(--color-danger, #dc3545);
  font-weight: var(--font-weight-semibold, 600);
}

.error-message {
  font-size: var(--font-size-sm, 0.8125rem);
  color: var(--color-danger-text, #c33);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 0.25rem);
}

.error-message::before {
  content: '⚠';
  font-size: var(--font-size-base, 0.875rem);
}

.help-text {
  font-size: var(--font-size-sm, 0.8125rem);
  color: var(--color-muted, #666);
  font-style: italic;
}

/* Error state styling for the form group */
.form-group.has-error :deep(input),
.form-group.has-error :deep(select),
.form-group.has-error :deep(textarea) {
  border-color: var(--color-danger, #dc3545);
}

.form-group.has-error :deep(input):focus,
.form-group.has-error :deep(select):focus,
.form-group.has-error :deep(textarea):focus {
  outline-color: var(--color-danger, #dc3545);
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
}

/* Ensure consistent input styling within FormGroup */
.form-group :deep(input),
.form-group :deep(select),
.form-group :deep(textarea) {
  width: 100%;
  padding: var(--form-input-padding, 0.5rem);
  border: 1px solid var(--form-input-border-color, #ddd);
  border-radius: var(--form-input-border-radius, 4px);
  font-size: var(--font-size-base, 0.875rem);
  min-height: var(--form-input-min-height, 44px);
  transition: border-color var(--transition-normal, 0.2s ease),
              box-shadow var(--transition-normal, 0.2s ease);
}

.form-group :deep(input:focus),
.form-group :deep(select:focus),
.form-group :deep(textarea:focus) {
  outline: none;
  border-color: var(--color-primary, #007bff);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.form-group :deep(input:disabled),
.form-group :deep(select:disabled),
.form-group :deep(textarea:disabled) {
  background-color: var(--color-light, #f8f9fa);
  cursor: not-allowed;
  opacity: var(--opacity-disabled, 0.6);
}

/* Mobile-specific adjustments */
@media (max-width: 767px) {
  .form-group :deep(input),
  .form-group :deep(select),
  .form-group :deep(textarea) {
    font-size: var(--form-input-font-size-mobile, 16px); /* Prevents iOS zoom */
  }
}

/* Textarea specific styling */
.form-group :deep(textarea) {
  min-height: 100px;
  resize: vertical;
}

/* Select specific styling */
.form-group :deep(select) {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
  padding-right: 2.5rem;
}
</style>
