<template>
  <div class="design-tokens-test">
    <h2>Design Tokens Test</h2>
    <p>This component tests that CSS variables from design-tokens.css are accessible.</p>
    
    <div class="test-section">
      <h3>Colors</h3>
      <div class="color-samples">
        <div class="color-box primary">Primary</div>
        <div class="color-box success">Success</div>
        <div class="color-box warning">Warning</div>
        <div class="color-box danger">Danger</div>
        <div class="color-box secondary">Secondary</div>
      </div>
    </div>
    
    <div class="test-section">
      <h3>Spacing</h3>
      <div class="spacing-samples">
        <div class="spacing-box xs">XS</div>
        <div class="spacing-box sm">SM</div>
        <div class="spacing-box md">MD</div>
        <div class="spacing-box lg">LG</div>
        <div class="spacing-box xl">XL</div>
      </div>
    </div>
    
    <div class="test-section">
      <h3>Typography</h3>
      <div class="typography-samples">
        <p class="text-xs">Extra Small Text (0.75rem)</p>
        <p class="text-sm">Small Text (0.8125rem)</p>
        <p class="text-base">Base Text (0.875rem)</p>
        <p class="text-lg">Large Text (1rem)</p>
        <p class="text-xl">Extra Large Text (1.125rem)</p>
      </div>
    </div>
    
    <div class="test-section">
      <h3>Button Tokens</h3>
      <div class="button-samples">
        <button class="test-button small">Small Button</button>
        <button class="test-button medium">Medium Button</button>
        <button class="test-button large">Large Button</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// This component is for testing design tokens only
// It will be removed after verification
</script>

<style scoped>
.design-tokens-test {
  padding: var(--spacing-xl);
  background-color: var(--color-bg-white);
  border-radius: var(--card-border-radius);
  max-width: 800px;
  margin: 0 auto;
}

.design-tokens-test h2 {
  color: var(--color-dark);
  font-size: var(--font-size-2xl);
  margin-bottom: var(--spacing-lg);
}

.design-tokens-test h3 {
  color: var(--color-dark);
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.test-section {
  margin-bottom: var(--spacing-xl);
}

/* Color Samples */
.color-samples {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.color-box {
  padding: var(--spacing-lg);
  border-radius: var(--button-border-radius);
  color: white;
  font-weight: var(--font-weight-medium);
  min-width: 100px;
  text-align: center;
}

.color-box.primary {
  background-color: var(--color-primary);
}

.color-box.success {
  background-color: var(--color-success);
}

.color-box.warning {
  background-color: var(--color-warning);
  color: var(--color-dark);
}

.color-box.danger {
  background-color: var(--color-danger);
}

.color-box.secondary {
  background-color: var(--color-secondary);
}

/* Spacing Samples */
.spacing-samples {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-end;
  flex-wrap: wrap;
}

.spacing-box {
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.spacing-box.xs {
  padding: var(--spacing-xs);
}

.spacing-box.sm {
  padding: var(--spacing-sm);
}

.spacing-box.md {
  padding: var(--spacing-md);
}

.spacing-box.lg {
  padding: var(--spacing-lg);
}

.spacing-box.xl {
  padding: var(--spacing-xl);
}

/* Typography Samples */
.typography-samples {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.text-xs {
  font-size: var(--font-size-xs);
}

.text-sm {
  font-size: var(--font-size-sm);
}

.text-base {
  font-size: var(--font-size-base);
}

.text-lg {
  font-size: var(--font-size-lg);
}

.text-xl {
  font-size: var(--font-size-xl);
}

/* Button Samples */
.button-samples {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.test-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--button-border-radius);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: var(--button-transition);
}

.test-button:hover {
  background-color: var(--color-primary-hover);
}

.test-button.small {
  padding: var(--button-padding-sm);
  min-height: var(--button-min-height-sm);
  font-size: var(--button-font-size-sm);
}

.test-button.medium {
  padding: var(--button-padding-md);
  min-height: var(--button-min-height-md);
  font-size: var(--button-font-size-md);
}

.test-button.large {
  padding: var(--button-padding-lg);
  min-height: var(--button-min-height-lg);
  font-size: var(--button-font-size-lg);
}
</style>
