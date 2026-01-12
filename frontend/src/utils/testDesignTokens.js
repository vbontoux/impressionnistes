/**
 * Test utility to verify design tokens are accessible
 * This can be run in the browser console or as part of automated tests
 */

export function testDesignTokens() {
  const results = {
    passed: [],
    failed: [],
  };

  // Get computed styles from root element
  const rootStyles = getComputedStyle(document.documentElement);

  // Test color tokens
  const colorTokens = [
    '--color-primary',
    '--color-success',
    '--color-warning',
    '--color-danger',
    '--color-secondary',
  ];

  colorTokens.forEach(token => {
    const value = rootStyles.getPropertyValue(token).trim();
    if (value) {
      results.passed.push({ token, value });
    } else {
      results.failed.push({ token, error: 'Token not found or empty' });
    }
  });

  // Test spacing tokens
  const spacingTokens = [
    '--spacing-xs',
    '--spacing-sm',
    '--spacing-md',
    '--spacing-lg',
    '--spacing-xl',
  ];

  spacingTokens.forEach(token => {
    const value = rootStyles.getPropertyValue(token).trim();
    if (value) {
      results.passed.push({ token, value });
    } else {
      results.failed.push({ token, error: 'Token not found or empty' });
    }
  });

  // Test typography tokens
  const typographyTokens = [
    '--font-size-xs',
    '--font-size-sm',
    '--font-size-base',
    '--font-size-lg',
    '--font-size-xl',
    '--font-weight-normal',
    '--font-weight-medium',
    '--font-weight-semibold',
  ];

  typographyTokens.forEach(token => {
    const value = rootStyles.getPropertyValue(token).trim();
    if (value) {
      results.passed.push({ token, value });
    } else {
      results.failed.push({ token, error: 'Token not found or empty' });
    }
  });

  // Test button tokens
  const buttonTokens = [
    '--button-border-radius',
    '--button-padding-sm',
    '--button-padding-md',
    '--button-min-height-sm',
    '--button-min-height-md',
  ];

  buttonTokens.forEach(token => {
    const value = rootStyles.getPropertyValue(token).trim();
    if (value) {
      results.passed.push({ token, value });
    } else {
      results.failed.push({ token, error: 'Token not found or empty' });
    }
  });

  // Log results
  console.log('Design Tokens Test Results:');
  console.log(`✅ Passed: ${results.passed.length}`);
  console.log(`❌ Failed: ${results.failed.length}`);

  if (results.failed.length > 0) {
    console.error('Failed tokens:', results.failed);
  }

  // Return summary
  return {
    success: results.failed.length === 0,
    passed: results.passed.length,
    failed: results.failed.length,
    details: results,
  };
}

// Auto-run test when imported in development mode
if (import.meta.env.DEV) {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        console.log('🎨 Running Design Tokens Test...');
        testDesignTokens();
      }, 1000);
    });
  }
}
