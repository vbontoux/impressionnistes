<template>
  <div v-if="strength" class="password-strength-indicator">
    <!-- Strength bar -->
    <div class="strength-bar-container">
      <div 
        class="strength-bar" 
        :class="strengthClass"
        :style="{ width: barWidth }"
      ></div>
    </div>
    
    <!-- Strength label -->
    <div class="strength-label" :class="strengthClass">
      {{ strengthLabel }}
    </div>
    
    <!-- Feedback list -->
    <ul v-if="strength.feedback && strength.feedback.length > 0" class="feedback-list">
      <li v-for="(item, index) in strength.feedback" :key="index" class="feedback-item">
        {{ item }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'PasswordStrengthIndicator',
  
  props: {
    /**
     * Strength object with score (0-4) and feedback array
     * @type {Object}
     * @property {number} score - Strength score (0=weak, 1=weak, 2=medium, 3=strong, 4=strong)
     * @property {string[]} feedback - Array of feedback messages
     */
    strength: {
      type: Object,
      required: true,
      validator: (value) => {
        return (
          typeof value.score === 'number' &&
          value.score >= 0 &&
          value.score <= 4 &&
          Array.isArray(value.feedback)
        );
      },
    },
  },
  
  computed: {
    /**
     * Get CSS class for strength level
     */
    strengthClass() {
      if (this.strength.score <= 1) return 'strength-weak';
      if (this.strength.score === 2) return 'strength-medium';
      return 'strength-strong';
    },
    
    /**
     * Get strength label text
     */
    strengthLabel() {
      if (this.strength.score <= 1) return 'Faible';
      if (this.strength.score === 2) return 'Moyen';
      return 'Fort';
    },
    
    /**
     * Calculate bar width percentage
     */
    barWidth() {
      // Map score 0-4 to percentage 0-100
      return `${(this.strength.score / 4) * 100}%`;
    },
  },
};
</script>

<style scoped>
.password-strength-indicator {
  margin-top: var(--spacing-sm);
}

.strength-bar-container {
  width: 100%;
  height: 4px;
  background-color: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
}

.strength-bar {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 2px;
}

.strength-bar.strength-weak {
  background-color: var(--color-danger);
}

.strength-bar.strength-medium {
  background-color: var(--color-warning);
}

.strength-bar.strength-strong {
  background-color: var(--color-success);
}

.strength-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
}

.strength-label.strength-weak {
  color: var(--color-danger);
}

.strength-label.strength-medium {
  color: var(--color-warning);
}

.strength-label.strength-strong {
  color: var(--color-success);
}

.feedback-list {
  list-style: none;
  padding: 0;
  margin: var(--spacing-xs) 0 0 0;
}

.feedback-item {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  margin-bottom: var(--spacing-xs);
  padding-left: var(--spacing-md);
  position: relative;
}

.feedback-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-muted);
}
</style>
