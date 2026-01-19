<template>
  <div class="design-system-showcase">
    <div class="showcase-header">
      <h1>Design System Showcase</h1>
      <p class="subtitle">
        A living style guide demonstrating all design tokens, components, and patterns used in the application.
      </p>
    </div>

    <!-- Design Tokens Section -->
    <section class="showcase-section">
      <h2>Design Tokens</h2>
      <p class="section-description">
        CSS custom properties that define the visual foundation of our design system.
      </p>

      <!-- Colors -->
      <div class="subsection">
        <h3>Color Palette</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch primary"></div>
            <div class="color-info">
              <strong>Primary</strong>
              <code>--color-primary</code>
              <span class="color-value">#007bff</span>
            </div>
          </div>
          
          <div class="color-item">
            <div class="color-swatch success"></div>
            <div class="color-info">
              <strong>Success</strong>
              <code>--color-success</code>
              <span class="color-value">#28a745</span>
            </div>
          </div>
          
          <div class="color-item">
            <div class="color-swatch warning"></div>
            <div class="color-info">
              <strong>Warning</strong>
              <code>--color-warning</code>
              <span class="color-value">#ffc107</span>
            </div>
          </div>
          
          <div class="color-item">
            <div class="color-swatch danger"></div>
            <div class="color-info">
              <strong>Danger</strong>
              <code>--color-danger</code>
              <span class="color-value">#dc3545</span>
            </div>
          </div>
          
          <div class="color-item">
            <div class="color-swatch secondary"></div>
            <div class="color-info">
              <strong>Secondary</strong>
              <code>--color-secondary</code>
              <span class="color-value">#6c757d</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Spacing -->
      <div class="subsection">
        <h3>Spacing Scale</h3>
        <div class="spacing-demo">
          <div class="spacing-item">
            <div class="spacing-box xs"></div>
            <div class="spacing-label">
              <strong>XS</strong>
              <code>--spacing-xs</code>
              <span>0.25rem (4px)</span>
            </div>
          </div>
          
          <div class="spacing-item">
            <div class="spacing-box sm"></div>
            <div class="spacing-label">
              <strong>SM</strong>
              <code>--spacing-sm</code>
              <span>0.5rem (8px)</span>
            </div>
          </div>
          
          <div class="spacing-item">
            <div class="spacing-box md"></div>
            <div class="spacing-label">
              <strong>MD</strong>
              <code>--spacing-md</code>
              <span>0.75rem (12px)</span>
            </div>
          </div>
          
          <div class="spacing-item">
            <div class="spacing-box lg"></div>
            <div class="spacing-label">
              <strong>LG</strong>
              <code>--spacing-lg</code>
              <span>1rem (16px)</span>
            </div>
          </div>
          
          <div class="spacing-item">
            <div class="spacing-box xl"></div>
            <div class="spacing-label">
              <strong>XL</strong>
              <code>--spacing-xl</code>
              <span>1.5rem (24px)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Typography -->
      <div class="subsection">
        <h3>Typography Scale</h3>
        <div class="typography-demo">
          <p class="text-xs">
            <strong>Extra Small</strong> - <code>--font-size-xs</code> - 0.75rem (12px)
          </p>
          <p class="text-sm">
            <strong>Small</strong> - <code>--font-size-sm</code> - 0.8125rem (13px)
          </p>
          <p class="text-base">
            <strong>Base</strong> - <code>--font-size-base</code> - 0.875rem (14px)
          </p>
          <p class="text-md">
            <strong>Medium</strong> - <code>--font-size-md</code> - 0.95rem (15.2px)
          </p>
          <p class="text-lg">
            <strong>Large</strong> - <code>--font-size-lg</code> - 1rem (16px)
          </p>
          <p class="text-xl">
            <strong>Extra Large</strong> - <code>--font-size-xl</code> - 1.125rem (18px)
          </p>
          <p class="text-2xl">
            <strong>2X Large</strong> - <code>--font-size-2xl</code> - 1.25rem (20px)
          </p>
          <p class="text-3xl">
            <strong>3X Large</strong> - <code>--font-size-3xl</code> - 1.5rem (24px)
          </p>
        </div>
      </div>

      <!-- Font Weights -->
      <div class="subsection">
        <h3>Font Weights</h3>
        <div class="font-weight-demo">
          <p class="weight-normal">
            <strong>Normal (400)</strong> - <code>--font-weight-normal</code> - The quick brown fox jumps over the lazy dog
          </p>
          <p class="weight-medium">
            <strong>Medium (500)</strong> - <code>--font-weight-medium</code> - The quick brown fox jumps over the lazy dog
          </p>
          <p class="weight-semibold">
            <strong>Semibold (600)</strong> - <code>--font-weight-semibold</code> - The quick brown fox jumps over the lazy dog
          </p>
          <p class="weight-bold">
            <strong>Bold (700)</strong> - <code>--font-weight-bold</code> - The quick brown fox jumps over the lazy dog
          </p>
        </div>
      </div>
    </section>

    <!-- Component Tokens Section -->
    <section class="showcase-section">
      <h2>Component Tokens</h2>
      <p class="section-description">
        Specialized tokens for specific component types.
      </p>

      <!-- Buttons -->
      <div class="subsection">
        <h3>Button Tokens</h3>
        <div class="button-demo">
          <div class="button-group">
            <button class="demo-button small">
              Small Button
            </button>
            <div class="token-info">
              <code>--button-padding-sm</code>
              <code>--button-min-height-sm</code> (36px)
              <code>--button-font-size-sm</code>
            </div>
          </div>
          
          <div class="button-group">
            <button class="demo-button medium">
              Medium Button
            </button>
            <div class="token-info">
              <code>--button-padding-md</code>
              <code>--button-min-height-md</code> (44px)
              <code>--button-font-size-md</code>
            </div>
          </div>
          
          <div class="button-group">
            <button class="demo-button large">
              Large Button
            </button>
            <div class="token-info">
              <code>--button-padding-lg</code>
              <code>--button-min-height-lg</code> (48px)
              <code>--button-font-size-lg</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Badges -->
      <div class="subsection">
        <h3>Status Badge Tokens</h3>
        <div class="badge-demo">
          <div class="badge-item">
            <span class="demo-badge incomplete">Incomplete</span>
            <code>--color-warning</code>
          </div>
          <div class="badge-item">
            <span class="demo-badge complete">Complete</span>
            <code>--color-success</code>
          </div>
          <div class="badge-item">
            <span class="demo-badge paid">Paid</span>
            <code>--color-primary</code>
          </div>
          <div class="badge-item">
            <span class="demo-badge forfait">Forfait</span>
            <code>--color-danger</code>
          </div>
        </div>
        <div class="token-info">
          <code>--badge-border-radius</code> (12px)
          <code>--badge-padding</code> (0.25rem 0.75rem)
          <code>--badge-font-size</code> (0.75rem)
        </div>
      </div>

      <!-- Cards -->
      <div class="subsection">
        <h3>Card Tokens</h3>
        <div class="card-demo">
          <div class="demo-card">
            <h4>Example Card</h4>
            <p>This card demonstrates the card tokens in action.</p>
            <div class="card-actions">
              <button class="demo-button small">Action</button>
            </div>
          </div>
        </div>
        <div class="token-info">
          <code>--card-border-radius</code> (8px)
          <code>--card-padding-mobile</code> (1rem)
          <code>--card-padding-desktop</code> (1.5rem)
          <code>--card-shadow</code>
        </div>
      </div>
    </section>

    <!-- Responsive Breakpoints -->
    <section class="showcase-section">
      <h2>Responsive Breakpoints</h2>
      <p class="section-description">
        Breakpoints used for responsive design across the application.
      </p>
      
      <div class="breakpoint-demo">
        <div class="breakpoint-item">
          <strong>Mobile</strong>
          <code>--breakpoint-mobile</code>
          <span>&lt; 768px</span>
        </div>
        <div class="breakpoint-item">
          <strong>Tablet</strong>
          <code>--breakpoint-tablet</code>
          <span>768px - 1023px</span>
        </div>
        <div class="breakpoint-item">
          <strong>Desktop</strong>
          <code>--breakpoint-desktop</code>
          <span>≥ 1024px</span>
        </div>
      </div>
      
      <div class="current-breakpoint">
        <strong>Current viewport:</strong> 
        <span class="mobile-indicator">📱 Mobile</span>
        <span class="tablet-indicator">📱 Tablet</span>
        <span class="desktop-indicator">🖥️ Desktop</span>
      </div>
    </section>

    <!-- Components Section -->
    <section class="showcase-section">
      <h2>Components</h2>
      <p class="section-description">
        Reusable components built with design tokens.
      </p>

      <!-- BaseButton Component -->
      <div class="subsection">
        <h3>BaseButton Component</h3>
        <p class="component-description">
          Standardized button component with consistent styling and behavior across all variants and sizes.
        </p>

        <!-- Button Variants -->
        <div class="component-demo">
          <h4>Variants</h4>
          <div class="button-variants">
            <BaseButton variant="primary">Primary Button</BaseButton>
            <BaseButton variant="secondary">Secondary Button</BaseButton>
            <BaseButton variant="danger">Danger Button</BaseButton>
            <BaseButton variant="warning">Warning Button</BaseButton>
          </div>
        </div>

        <!-- Button Sizes -->
        <div class="component-demo">
          <h4>Sizes</h4>
          <div class="button-sizes">
            <BaseButton size="small" variant="primary">Small</BaseButton>
            <BaseButton size="medium" variant="primary">Medium</BaseButton>
            <BaseButton size="large" variant="primary">Large</BaseButton>
          </div>
        </div>

        <!-- Button States -->
        <div class="component-demo">
          <h4>States</h4>
          <div class="button-states">
            <BaseButton variant="primary">Normal</BaseButton>
            <BaseButton variant="primary" :disabled="true">Disabled</BaseButton>
            <BaseButton variant="primary" :loading="true">Loading</BaseButton>
          </div>
        </div>

        <!-- Full Width -->
        <div class="component-demo">
          <h4>Full Width</h4>
          <div class="button-full-width">
            <BaseButton variant="primary" :full-width="true">Full Width Button</BaseButton>
          </div>
        </div>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import BaseButton from '@/components/base/BaseButton.vue'

&lt;!-- Basic usage --&gt;
&lt;BaseButton variant="primary" @click="handleClick"&gt;
  Save
&lt;/BaseButton&gt;

&lt;!-- With size --&gt;
&lt;BaseButton variant="danger" size="small" @click="handleDelete"&gt;
  Delete
&lt;/BaseButton&gt;

&lt;!-- With loading state --&gt;
&lt;BaseButton variant="primary" :loading="isSubmitting" @click="handleSubmit"&gt;
  Submit
&lt;/BaseButton&gt;

&lt;!-- Disabled --&gt;
&lt;BaseButton variant="secondary" :disabled="!isValid"&gt;
  Continue
&lt;/BaseButton&gt;

&lt;!-- Full width --&gt;
&lt;BaseButton variant="primary" :full-width="true"&gt;
  Sign In
&lt;/BaseButton&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>variant</code></td>
                <td>String</td>
                <td>'primary'</td>
                <td>'primary', 'secondary', 'danger', 'warning'</td>
              </tr>
              <tr>
                <td><code>size</code></td>
                <td>String</td>
                <td>'medium'</td>
                <td>'small', 'medium', 'large'</td>
              </tr>
              <tr>
                <td><code>disabled</code></td>
                <td>Boolean</td>
                <td>false</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>loading</code></td>
                <td>Boolean</td>
                <td>false</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>fullWidth</code></td>
                <td>Boolean</td>
                <td>false</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>type</code></td>
                <td>String</td>
                <td>'button'</td>
                <td>'button', 'submit', 'reset'</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- StatusBadge Component -->
      <div class="subsection">
        <h3>StatusBadge Component</h3>
        <p class="component-description">
          Consistent status indicator component that automatically applies correct colors based on status type.
        </p>

        <!-- Status Variants -->
        <div class="component-demo">
          <h4>Status Variants</h4>
          <div class="badge-variants">
            <StatusBadge status="incomplete" />
            <StatusBadge status="complete" />
            <StatusBadge status="paid" />
            <StatusBadge status="free" />
            <StatusBadge status="forfait" />
          </div>
        </div>

        <!-- Badge Sizes -->
        <div class="component-demo">
          <h4>Sizes</h4>
          <div class="badge-sizes">
            <StatusBadge status="complete" size="small" />
            <StatusBadge status="complete" size="medium" />
          </div>
        </div>

        <!-- Custom Content -->
        <div class="component-demo">
          <h4>Custom Content</h4>
          <div class="badge-custom">
            <StatusBadge status="paid">Payé</StatusBadge>
            <StatusBadge status="complete">Terminé</StatusBadge>
            <StatusBadge status="incomplete">En cours</StatusBadge>
          </div>
        </div>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import StatusBadge from '@/components/base/StatusBadge.vue'

&lt;!-- Basic usage (auto-displays status text) --&gt;
&lt;StatusBadge status="incomplete" /&gt;
&lt;StatusBadge status="complete" /&gt;
&lt;StatusBadge status="paid" /&gt;
&lt;StatusBadge status="forfait" /&gt;

&lt;!-- With size --&gt;
&lt;StatusBadge status="complete" size="small" /&gt;

&lt;!-- Custom content (e.g., translated text) --&gt;
&lt;StatusBadge status="paid"&gt;Payé&lt;/StatusBadge&gt;
&lt;StatusBadge status="complete"&gt;Terminé&lt;/StatusBadge&gt;

&lt;!-- Dynamic status from data --&gt;
&lt;StatusBadge :status="boat.registration_status" /&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>status</code></td>
                <td>String</td>
                <td>required</td>
                <td>'incomplete', 'complete', 'paid', 'free', 'forfait'</td>
              </tr>
              <tr>
                <td><code>size</code></td>
                <td>String</td>
                <td>'medium'</td>
                <td>'small', 'medium'</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Color Mapping -->
        <div class="component-demo">
          <h4>Color Mapping</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Background Color</th>
                <th>Text Color</th>
                <th>Design Token</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>incomplete</code></td>
                <td>#ffc107 (Yellow)</td>
                <td>Black</td>
                <td><code>--color-warning</code></td>
              </tr>
              <tr>
                <td><code>complete</code></td>
                <td>#28a745 (Green)</td>
                <td>White</td>
                <td><code>--color-success</code></td>
              </tr>
              <tr>
                <td><code>paid</code></td>
                <td>#007bff (Blue)</td>
                <td>White</td>
                <td><code>--color-primary</code></td>
              </tr>
              <tr>
                <td><code>free</code></td>
                <td>#007bff (Blue)</td>
                <td>White</td>
                <td><code>--color-primary</code></td>
              </tr>
              <tr>
                <td><code>forfait</code></td>
                <td>#dc3545 (Red)</td>
                <td>White</td>
                <td><code>--color-danger</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- LoadingSpinner Component -->
      <div class="subsection">
        <h3>LoadingSpinner Component</h3>
        <p class="component-description">
          Consistent loading indicator component with optional message text and size variants.
        </p>

        <!-- Sizes -->
        <div class="component-demo">
          <h4>Sizes</h4>
          <div class="spinner-sizes">
            <div class="spinner-demo-item">
              <LoadingSpinner size="small" />
              <span class="demo-label">Small</span>
            </div>
            <div class="spinner-demo-item">
              <LoadingSpinner size="medium" />
              <span class="demo-label">Medium (Default)</span>
            </div>
            <div class="spinner-demo-item">
              <LoadingSpinner size="large" />
              <span class="demo-label">Large</span>
            </div>
          </div>
        </div>

        <!-- With Message -->
        <div class="component-demo">
          <h4>With Message</h4>
          <div class="spinner-message-demo">
            <LoadingSpinner message="Loading boats..." />
            <LoadingSpinner message="Saving changes..." size="small" />
          </div>
        </div>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import LoadingSpinner from '@/components/base/LoadingSpinner.vue'

&lt;!-- Basic usage --&gt;
&lt;LoadingSpinner /&gt;

&lt;!-- With message --&gt;
&lt;LoadingSpinner message="Loading boats..." /&gt;

&lt;!-- With size --&gt;
&lt;LoadingSpinner size="small" message="Saving..." /&gt;
&lt;LoadingSpinner size="large" message="Processing..." /&gt;

&lt;!-- Conditional rendering --&gt;
&lt;LoadingSpinner v-if="isLoading" message="Loading data..." /&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>size</code></td>
                <td>String</td>
                <td>'medium'</td>
                <td>'small', 'medium', 'large'</td>
              </tr>
              <tr>
                <td><code>message</code></td>
                <td>String</td>
                <td>''</td>
                <td>Any text string</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--spinner-size</code></td>
                <td>40px</td>
                <td>Default spinner diameter</td>
              </tr>
              <tr>
                <td><code>--spinner-border-width</code></td>
                <td>4px</td>
                <td>Spinner border thickness</td>
              </tr>
              <tr>
                <td><code>--spinner-border-color</code></td>
                <td>#f3f3f3</td>
                <td>Base border color</td>
              </tr>
              <tr>
                <td><code>--spinner-border-top-color</code></td>
                <td>#4CAF50</td>
                <td>Animated border color</td>
              </tr>
              <tr>
                <td><code>--spinner-animation-duration</code></td>
                <td>1s</td>
                <td>Rotation speed</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BaseModal Component -->
      <div class="subsection">
        <h3>BaseModal Component</h3>
        <p class="component-description">
          Consistent modal/dialog component with responsive behavior. Displays as a centered modal on desktop and a bottom sheet on mobile.
        </p>

        <!-- Modal Sizes -->
        <div class="component-demo">
          <h4>Sizes</h4>
          <div class="button-variants">
            <BaseButton variant="primary" @click="showSmallModal = true">Small Modal</BaseButton>
            <BaseButton variant="primary" @click="showMediumModal = true">Medium Modal</BaseButton>
            <BaseButton variant="primary" @click="showLargeModal = true">Large Modal</BaseButton>
          </div>
        </div>

        <!-- Modal Variants -->
        <div class="component-demo">
          <h4>Variants</h4>
          <div class="button-variants">
            <BaseButton variant="secondary" @click="showNoCloseModal = true">No Overlay Close</BaseButton>
            <BaseButton variant="secondary" @click="showWithFooterModal = true">With Footer Actions</BaseButton>
          </div>
        </div>

        <!-- Modal Components -->
        <BaseModal :show="showSmallModal" title="Small Modal" size="small" @close="showSmallModal = false">
          <p>This is a small modal. It's perfect for simple confirmations or brief messages.</p>
        </BaseModal>

        <BaseModal :show="showMediumModal" title="Medium Modal" size="medium" @close="showMediumModal = false">
          <p>This is a medium modal (default size). It's suitable for most use cases like forms or detailed information.</p>
          <p>The modal automatically handles body scroll locking and provides smooth transitions.</p>
        </BaseModal>

        <BaseModal :show="showLargeModal" title="Large Modal" size="large" @close="showLargeModal = false">
          <p>This is a large modal. Use it when you need more space for complex content or multiple sections.</p>
          <div style="margin-top: 1rem; padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <h4 style="margin-top: 0;">Example Content Section</h4>
            <p>Large modals can accommodate more detailed content, multiple form sections, or data tables.</p>
          </div>
        </BaseModal>

        <BaseModal 
          :show="showNoCloseModal" 
          title="No Overlay Close" 
          :close-on-overlay="false" 
          @close="showNoCloseModal = false"
        >
          <p>This modal won't close when clicking the overlay. Users must use the close button or footer actions.</p>
          <p>This is useful for important confirmations or when you want to prevent accidental dismissal.</p>
        </BaseModal>

        <BaseModal 
          :show="showWithFooterModal" 
          title="Modal with Footer" 
          @close="showWithFooterModal = false"
        >
          <template #default>
            <p>This modal demonstrates the footer slot for action buttons.</p>
            <p>The footer automatically stacks buttons vertically on mobile for better touch targets.</p>
          </template>
          <template #footer>
            <BaseButton variant="secondary" @click="showWithFooterModal = false">Cancel</BaseButton>
            <BaseButton variant="primary" @click="showWithFooterModal = false">Confirm</BaseButton>
          </template>
        </BaseModal>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import BaseModal from '@/components/base/BaseModal.vue'
import { ref } from 'vue'

const showModal = ref(false)

&lt;!-- Basic usage --&gt;
&lt;BaseButton @click="showModal = true"&gt;Open Modal&lt;/BaseButton&gt;

&lt;BaseModal :show="showModal" title="My Modal" @close="showModal = false"&gt;
  &lt;p&gt;Modal content goes here&lt;/p&gt;
&lt;/BaseModal&gt;

&lt;!-- With size --&gt;
&lt;BaseModal :show="showModal" title="Large Modal" size="large" @close="showModal = false"&gt;
  &lt;p&gt;More content space&lt;/p&gt;
&lt;/BaseModal&gt;

&lt;!-- With footer actions --&gt;
&lt;BaseModal :show="showModal" title="Confirm Action" @close="showModal = false"&gt;
  &lt;template #default&gt;
    &lt;p&gt;Are you sure you want to proceed?&lt;/p&gt;
  &lt;/template&gt;
  &lt;template #footer&gt;
    &lt;BaseButton variant="secondary" @click="showModal = false"&gt;Cancel&lt;/BaseButton&gt;
    &lt;BaseButton variant="danger" @click="handleDelete"&gt;Delete&lt;/BaseButton&gt;
  &lt;/template&gt;
&lt;/BaseModal&gt;

&lt;!-- Prevent overlay close --&gt;
&lt;BaseModal 
  :show="showModal" 
  title="Important" 
  :close-on-overlay="false"
  @close="showModal = false"
&gt;
  &lt;p&gt;This requires explicit action&lt;/p&gt;
&lt;/BaseModal&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>show</code></td>
                <td>Boolean</td>
                <td>required</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>title</code></td>
                <td>String</td>
                <td>''</td>
                <td>Any text string</td>
              </tr>
              <tr>
                <td><code>size</code></td>
                <td>String</td>
                <td>'medium'</td>
                <td>'small', 'medium', 'large'</td>
              </tr>
              <tr>
                <td><code>closeOnOverlay</code></td>
                <td>Boolean</td>
                <td>true</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>showCloseButton</code></td>
                <td>Boolean</td>
                <td>true</td>
                <td>true, false</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Slots Reference -->
        <div class="props-reference">
          <h4>Slots</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Slot</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>header</code></td>
                <td>Custom header content (replaces title)</td>
              </tr>
              <tr>
                <td><code>default</code></td>
                <td>Modal body content</td>
              </tr>
              <tr>
                <td><code>footer</code></td>
                <td>Footer with action buttons</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Events Reference -->
        <div class="props-reference">
          <h4>Events</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>@close</code></td>
                <td>Emitted when modal should close (overlay click or close button)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--modal-overlay-bg</code></td>
                <td>rgba(0, 0, 0, 0.5)</td>
                <td>Overlay background</td>
              </tr>
              <tr>
                <td><code>--modal-border-radius-desktop</code></td>
                <td>8px</td>
                <td>Border radius on desktop</td>
              </tr>
              <tr>
                <td><code>--modal-border-radius-mobile</code></td>
                <td>12px 12px 0 0</td>
                <td>Border radius on mobile (bottom sheet)</td>
              </tr>
              <tr>
                <td><code>--modal-max-width</code></td>
                <td>600px</td>
                <td>Maximum width (medium size)</td>
              </tr>
              <tr>
                <td><code>--modal-padding</code></td>
                <td>1rem 1.5rem</td>
                <td>Header, body, and footer padding</td>
              </tr>
              <tr>
                <td><code>--modal-shadow</code></td>
                <td>0 4px 8px rgba(0, 0, 0, 0.1)</td>
                <td>Box shadow</td>
              </tr>
              <tr>
                <td><code>--z-index-modal</code></td>
                <td>1000</td>
                <td>Z-index for modal content</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Responsive Behavior -->
        <div class="component-demo">
          <h4>Responsive Behavior</h4>
          <div style="padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <p><strong>Desktop (≥ 768px):</strong></p>
            <ul>
              <li>Centered on screen</li>
              <li>Fade and scale animation</li>
              <li>Fixed max-width based on size prop</li>
              <li>Rounded corners (8px)</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Mobile (&lt; 768px):</strong></p>
            <ul>
              <li>Bottom sheet pattern</li>
              <li>Slide up animation</li>
              <li>Full width</li>
              <li>Rounded top corners only (12px)</li>
              <li>Max height 90vh with scrollable content</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- DataCard Component -->
      <div class="subsection">
        <h3>DataCard Component</h3>
        <p class="component-description">
          Reusable card component for displaying entity data with consistent styling, status-based border colors, and responsive padding.
        </p>

        <!-- Component Demos -->
        <div class="component-demo">
          <h4>Basic Card with Title and Status</h4>
          <div class="card-demo-grid">
            <DataCard 
              title="4x+ Homme Senior - 21km" 
              status="incomplete"
            >
              <div class="detail-row">
                <span class="label">Boat Number:</span>
                <span class="value">B-042</span>
              </div>
              <div class="detail-row">
                <span class="label">Club:</span>
                <span class="value">Aviron Club de Paris</span>
              </div>
              <div class="detail-row">
                <span class="label">Crew Members:</span>
                <span class="value">4/5</span>
              </div>
              <template #actions>
                <BaseButton variant="secondary" size="small">View</BaseButton>
                <BaseButton variant="danger" size="small">Delete</BaseButton>
              </template>
            </DataCard>

            <DataCard 
              title="2x Femme Vétéran - 21km" 
              status="complete"
            >
              <div class="detail-row">
                <span class="label">Boat Number:</span>
                <span class="value">B-015</span>
              </div>
              <div class="detail-row">
                <span class="label">Club:</span>
                <span class="value">Société Nautique de la Marne</span>
              </div>
              <div class="detail-row">
                <span class="label">Crew Members:</span>
                <span class="value">2/2</span>
              </div>
              <template #actions>
                <BaseButton variant="secondary" size="small">View</BaseButton>
                <BaseButton variant="primary" size="small">Pay</BaseButton>
              </template>
            </DataCard>

            <DataCard 
              title="8+ Mixte Senior - 21km" 
              status="paid"
            >
              <div class="detail-row">
                <span class="label">Boat Number:</span>
                <span class="value">B-128</span>
              </div>
              <div class="detail-row">
                <span class="label">Club:</span>
                <span class="value">Rowing Club de France</span>
              </div>
              <div class="detail-row">
                <span class="label">Crew Members:</span>
                <span class="value">9/9</span>
              </div>
              <template #actions>
                <BaseButton variant="secondary" size="small">View Details</BaseButton>
              </template>
            </DataCard>

            <DataCard 
              title="1x Homme Senior - 21km" 
              status="forfait"
            >
              <div class="detail-row">
                <span class="label">Boat Number:</span>
                <span class="value">B-087</span>
              </div>
              <div class="detail-row">
                <span class="label">Club:</span>
                <span class="value">Cercle de l'Aviron de Paris</span>
              </div>
              <div class="detail-row">
                <span class="label">Reason:</span>
                <span class="value">Injury</span>
              </div>
              <template #actions>
                <BaseButton variant="secondary" size="small">View</BaseButton>
              </template>
            </DataCard>
          </div>
        </div>

        <div class="component-demo">
          <h4>Card without Status Badge</h4>
          <DataCard 
            title="Crew Member Information" 
            :statusBadge="false"
          >
            <div class="detail-row">
              <span class="label">Name:</span>
              <span class="value">Jean Dupont</span>
            </div>
            <div class="detail-row">
              <span class="label">Email:</span>
              <span class="value">jean.dupont@example.com</span>
            </div>
            <div class="detail-row">
              <span class="label">Age:</span>
              <span class="value">32</span>
            </div>
            <template #actions>
              <BaseButton variant="secondary" size="small">Edit</BaseButton>
              <BaseButton variant="danger" size="small">Remove</BaseButton>
            </template>
          </DataCard>
        </div>

        <div class="component-demo">
          <h4>Card with Custom Header Slot</h4>
          <DataCard>
            <template #header>
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <h3 style="margin: 0;">Custom Header Content</h3>
                <StatusBadge status="complete" />
              </div>
            </template>
            <p>This card uses a custom header slot instead of the default title prop.</p>
            <p>You have full control over the header layout and content.</p>
            <template #actions>
              <BaseButton variant="primary" size="small">Action</BaseButton>
            </template>
          </DataCard>
        </div>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import DataCard from '@/components/composite/DataCard.vue'

&lt;!-- Basic usage with title and status --&gt;
&lt;DataCard 
  title="4x+ Homme Senior - 21km" 
  status="incomplete"
&gt;
  &lt;div class="detail-row"&gt;
    &lt;span class="label"&gt;Boat Number:&lt;/span&gt;
    &lt;span class="value"&gt;B-042&lt;/span&gt;
  &lt;/div&gt;
  &lt;template #actions&gt;
    &lt;BaseButton variant="secondary" size="small"&gt;View&lt;/BaseButton&gt;
    &lt;BaseButton variant="danger" size="small"&gt;Delete&lt;/BaseButton&gt;
  &lt;/template&gt;
&lt;/DataCard&gt;

&lt;!-- Without status badge --&gt;
&lt;DataCard 
  title="Crew Member" 
  :statusBadge="false"
&gt;
  &lt;p&gt;Card content without status badge&lt;/p&gt;
&lt;/DataCard&gt;

&lt;!-- Custom header slot --&gt;
&lt;DataCard&gt;
  &lt;template #header&gt;
    &lt;div class="custom-header"&gt;
      &lt;h3&gt;Custom Header&lt;/h3&gt;
      &lt;StatusBadge status="paid" /&gt;
    &lt;/div&gt;
  &lt;/template&gt;
  &lt;p&gt;Card content&lt;/p&gt;
&lt;/DataCard&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>title</code></td>
                <td>String</td>
                <td>''</td>
                <td>Any text string</td>
              </tr>
              <tr>
                <td><code>status</code></td>
                <td>String</td>
                <td>''</td>
                <td>'incomplete', 'complete', 'paid', 'forfait', 'free'</td>
              </tr>
              <tr>
                <td><code>statusBadge</code></td>
                <td>Boolean</td>
                <td>true</td>
                <td>true, false</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Slots Reference -->
        <div class="props-reference">
          <h4>Slots</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Slot</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>header</code></td>
                <td>Custom header content (replaces title and status badge)</td>
              </tr>
              <tr>
                <td><code>default</code></td>
                <td>Card body content</td>
              </tr>
              <tr>
                <td><code>actions</code></td>
                <td>Action buttons (displayed at bottom of card)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--card-padding-mobile</code></td>
                <td>1rem</td>
                <td>Card padding on mobile</td>
              </tr>
              <tr>
                <td><code>--card-padding-desktop</code></td>
                <td>1.5rem</td>
                <td>Card padding on desktop</td>
              </tr>
              <tr>
                <td><code>--card-border-radius</code></td>
                <td>8px</td>
                <td>Border radius</td>
              </tr>
              <tr>
                <td><code>--card-shadow</code></td>
                <td>0 2px 4px rgba(0, 0, 0, 0.1)</td>
                <td>Default box shadow</td>
              </tr>
              <tr>
                <td><code>--card-shadow-hover</code></td>
                <td>0 4px 8px rgba(0, 0, 0, 0.15)</td>
                <td>Hover box shadow (desktop)</td>
              </tr>
              <tr>
                <td><code>--color-warning</code></td>
                <td>#ffc107</td>
                <td>Incomplete status border</td>
              </tr>
              <tr>
                <td><code>--color-success</code></td>
                <td>#28a745</td>
                <td>Complete status border</td>
              </tr>
              <tr>
                <td><code>--color-primary</code></td>
                <td>#007bff</td>
                <td>Paid/Free status border</td>
              </tr>
              <tr>
                <td><code>--color-danger</code></td>
                <td>#dc3545</td>
                <td>Forfait status border</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Features -->
        <div class="component-demo">
          <h4>Features</h4>
          <div style="padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <ul>
              <li><strong>Status-based border colors:</strong> Left border color automatically matches status</li>
              <li><strong>Responsive padding:</strong> 1rem on mobile, 1.5rem on desktop</li>
              <li><strong>Hover effect:</strong> Enhanced shadow on desktop hover</li>
              <li><strong>Flexible slots:</strong> Customize header, body, and actions</li>
              <li><strong>Detail row styling:</strong> Built-in styles for label-value pairs</li>
              <li><strong>Action button layout:</strong> Vertical on mobile, horizontal on desktop</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- SortableTable Component -->
      <div class="subsection">
        <h3>SortableTable Component</h3>
        <p class="component-description">
          Reusable table component with built-in sorting functionality, consistent styling with design tokens, and responsive behavior with horizontal scroll on mobile.
        </p>

        <!-- Basic Table Demo -->
        <div class="component-demo">
          <h4>Basic Sortable Table</h4>
          <SortableTable
            :columns="sampleTableColumns"
            :data="sampleTableData"
            :hoverable="true"
          />
        </div>

        <!-- Table with Custom Cell Slots -->
        <div class="component-demo">
          <h4>Table with Custom Cell Slots</h4>
          <SortableTable
            :columns="boatTableColumns"
            :data="boatTableData"
            :hoverable="true"
          >
            <template #cell-status="{ value }">
              <StatusBadge :status="value" />
            </template>
            <template #cell-actions="{ row }">
              <div style="display: flex; gap: 0.5rem; flex-direction: column;">
                <BaseButton variant="secondary" size="small">View</BaseButton>
                <BaseButton variant="danger" size="small">Delete</BaseButton>
              </div>
            </template>
          </SortableTable>
        </div>

        <!-- Column Width Management Demo -->
        <div class="component-demo">
          <h4>Column Width Management</h4>
          <p class="demo-description">
            Columns support <code>width</code> and <code>minWidth</code> properties with any CSS units (px, %, rem, etc.).
          </p>
          <SortableTable
            :columns="widthDemoColumns"
            :data="widthDemoData"
            :hoverable="true"
          />
          <p class="demo-note">
            <strong>Note:</strong> ID has fixed width (80px), Name has minWidth (150px), Description auto-sizes, Actions has both width and minWidth.
          </p>
        </div>

        <!-- Code Example -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import SortableTable from '@/components/composite/SortableTable.vue'

&lt;!-- Define columns --&gt;
const columns = [
  { key: 'boat_number', label: 'Boat #', sortable: true, width: '120px' },
  { key: 'event_type', label: 'Event', sortable: true, minWidth: '150px' },
  { key: 'team_manager', label: 'Manager', sortable: true },
  { key: 'status', label: 'Status', sortable: true, align: 'center' },
  { key: 'actions', label: 'Actions', sortable: false, align: 'right', width: '200px', minWidth: '180px' }
]

&lt;!-- Basic usage --&gt;
&lt;SortableTable
  :columns="columns"
  :data="boats"
  :hoverable="true"
  @sort="handleSort"
/&gt;

&lt;!-- With custom cell slots --&gt;
&lt;SortableTable :columns="columns" :data="boats"&gt;
  &lt;template #cell-status="{ value }"&gt;
    &lt;StatusBadge :status="value" /&gt;
  &lt;/template&gt;
  &lt;template #cell-actions="{ row }"&gt;
    &lt;BaseButton @click="editBoat(row)"&gt;Edit&lt;/BaseButton&gt;
  &lt;/template&gt;
&lt;/SortableTable&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>columns</code></td>
                <td>Array</td>
                <td>required</td>
                <td>Column definitions with key, label, sortable, width, align</td>
              </tr>
              <tr>
                <td><code>data</code></td>
                <td>Array</td>
                <td>required</td>
                <td>Data array to display</td>
              </tr>
              <tr>
                <td><code>initialSortField</code></td>
                <td>String</td>
                <td>''</td>
                <td>Initial field to sort by</td>
              </tr>
              <tr>
                <td><code>initialSortDirection</code></td>
                <td>String</td>
                <td>'asc'</td>
                <td>Initial sort direction ('asc' or 'desc')</td>
              </tr>
              <tr>
                <td><code>hoverable</code></td>
                <td>Boolean</td>
                <td>true</td>
                <td>Enable hover effect on rows</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Column Definition -->
        <div class="props-reference">
          <h4>Column Definition</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Property</th>
                <th>Type</th>
                <th>Required</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>key</code></td>
                <td>String</td>
                <td>Yes</td>
                <td>Data property key</td>
              </tr>
              <tr>
                <td><code>label</code></td>
                <td>String</td>
                <td>Yes</td>
                <td>Column header label</td>
              </tr>
              <tr>
                <td><code>sortable</code></td>
                <td>Boolean</td>
                <td>No</td>
                <td>Enable sorting (default: true)</td>
              </tr>
              <tr>
                <td><code>width</code></td>
                <td>String</td>
                <td>No</td>
                <td>Column width (e.g., '120px', '20%')</td>
              </tr>
              <tr>
                <td><code>align</code></td>
                <td>String</td>
                <td>No</td>
                <td>'left', 'center', or 'right' (default: 'left')</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Events -->
        <div class="props-reference">
          <h4>Events</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Payload</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>sort</code></td>
                <td>{ field: string, direction: string }</td>
                <td>Emitted when sort changes</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Slots -->
        <div class="props-reference">
          <h4>Slots</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Slot</th>
                <th>Props</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>cell-{key}</code></td>
                <td>{ row, value, column }</td>
                <td>Custom cell content for specific column</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--table-header-bg</code></td>
                <td>#f8f9fa</td>
                <td>Header background color</td>
              </tr>
              <tr>
                <td><code>--table-header-font-weight</code></td>
                <td>600</td>
                <td>Header font weight</td>
              </tr>
              <tr>
                <td><code>--table-cell-padding-mobile</code></td>
                <td>0.75rem</td>
                <td>Cell padding on mobile</td>
              </tr>
              <tr>
                <td><code>--table-cell-padding-desktop</code></td>
                <td>1rem</td>
                <td>Cell padding on desktop</td>
              </tr>
              <tr>
                <td><code>--table-border-color</code></td>
                <td>#dee2e6</td>
                <td>Border color</td>
              </tr>
              <tr>
                <td><code>--table-hover-bg</code></td>
                <td>#f8f9fa</td>
                <td>Row hover background</td>
              </tr>
              <tr>
                <td><code>--color-primary</code></td>
                <td>#007bff</td>
                <td>Sort indicator color</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Features -->
        <div class="component-demo">
          <h4>Features</h4>
          <div style="padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <ul>
              <li><strong>Click-to-sort headers:</strong> Click column headers to toggle sort direction</li>
              <li><strong>Sort indicators:</strong> Visual indicators (▲ ▼) show current sort state</li>
              <li><strong>Alphanumeric sorting:</strong> Special handling for boat numbers (e.g., M.1.1, SM.2.3)</li>
              <li><strong>Type-aware sorting:</strong> Handles strings, numbers, booleans correctly</li>
              <li><strong>Responsive design:</strong> Horizontal scroll on mobile with visual indicators</li>
              <li><strong>Status-based styling:</strong> Row border colors match status</li>
              <li><strong>Custom cell slots:</strong> Full control over cell rendering</li>
              <li><strong>Hover effects:</strong> Row highlighting on desktop</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- FormGroup Component -->
      <div class="subsection">
        <h3>FormGroup Component</h3>
        <p class="component-description">
          Consistent form field wrapper with label, required indicator, error messages, and help text. Provides standardized styling for all form inputs.
        </p>

        <!-- Basic Form Group -->
        <div class="component-demo">
          <h4>Basic Form Group</h4>
          <FormGroup label="Email Address" :required="true" inputId="demo-email">
            <input id="demo-email" type="email" placeholder="Enter your email" />
          </FormGroup>

          <FormGroup label="Full Name" inputId="demo-name">
            <input id="demo-name" type="text" placeholder="Enter your name" />
          </FormGroup>

          <FormGroup label="Country" inputId="demo-country">
            <select id="demo-country">
              <option value="">Select a country</option>
              <option value="fr">France</option>
              <option value="us">United States</option>
              <option value="uk">United Kingdom</option>
            </select>
          </FormGroup>
        </div>

        <!-- Form Group with Error -->
        <div class="component-demo">
          <h4>Form Group with Error</h4>
          <FormGroup 
            label="Password" 
            :required="true" 
            error="Password must be at least 8 characters"
            inputId="demo-password-error"
          >
            <input id="demo-password-error" type="password" value="short" />
          </FormGroup>

          <FormGroup 
            label="Email" 
            :required="true" 
            error="Please enter a valid email address"
            inputId="demo-email-error"
          >
            <input id="demo-email-error" type="email" value="invalid-email" />
          </FormGroup>
        </div>

        <!-- Form Group with Help Text -->
        <div class="component-demo">
          <h4>Form Group with Help Text</h4>
          <FormGroup 
            label="Username" 
            :required="true" 
            helpText="Choose a unique username between 3-20 characters"
            inputId="demo-username"
          >
            <input id="demo-username" type="text" placeholder="username" />
          </FormGroup>

          <FormGroup 
            label="Bio" 
            helpText="Tell us a bit about yourself (optional)"
            inputId="demo-bio"
          >
            <textarea id="demo-bio" placeholder="Write your bio here..."></textarea>
          </FormGroup>
        </div>

        <!-- Form Group States -->
        <div class="component-demo">
          <h4>Form Group States</h4>
          <FormGroup label="Disabled Input" inputId="demo-disabled">
            <input id="demo-disabled" type="text" value="Cannot edit" disabled />
          </FormGroup>

          <FormGroup 
            label="Required Field" 
            :required="true" 
            helpText="This field is required"
            inputId="demo-required"
          >
            <input id="demo-required" type="text" placeholder="Required field" />
          </FormGroup>
        </div>

        <!-- Code Example -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import FormGroup from '@/components/composite/FormGroup.vue'

&lt;!-- Basic usage --&gt;
&lt;FormGroup label="Email" :required="true" inputId="email"&gt;
  &lt;input id="email" v-model="form.email" type="email" /&gt;
&lt;/FormGroup&gt;

&lt;!-- With error message --&gt;
&lt;FormGroup 
  label="Password" 
  :required="true" 
  :error="errors.password"
  inputId="password"
&gt;
  &lt;input id="password" v-model="form.password" type="password" /&gt;
&lt;/FormGroup&gt;

&lt;!-- With help text --&gt;
&lt;FormGroup 
  label="Username" 
  helpText="Choose a unique username"
  inputId="username"
&gt;
  &lt;input id="username" v-model="form.username" type="text" /&gt;
&lt;/FormGroup&gt;

&lt;!-- With textarea --&gt;
&lt;FormGroup label="Description" inputId="description"&gt;
  &lt;textarea id="description" v-model="form.description"&gt;&lt;/textarea&gt;
&lt;/FormGroup&gt;

&lt;!-- With select --&gt;
&lt;FormGroup label="Country" :required="true" inputId="country"&gt;
  &lt;select id="country" v-model="form.country"&gt;
    &lt;option value=""&gt;Select...&lt;/option&gt;
    &lt;option value="fr"&gt;France&lt;/option&gt;
  &lt;/select&gt;
&lt;/FormGroup&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>label</code></td>
                <td>String</td>
                <td>''</td>
                <td>Label text for the form field</td>
              </tr>
              <tr>
                <td><code>required</code></td>
                <td>Boolean</td>
                <td>false</td>
                <td>Show required indicator (*)</td>
              </tr>
              <tr>
                <td><code>error</code></td>
                <td>String</td>
                <td>''</td>
                <td>Error message to display</td>
              </tr>
              <tr>
                <td><code>helpText</code></td>
                <td>String</td>
                <td>''</td>
                <td>Help text to display (hidden when error is shown)</td>
              </tr>
              <tr>
                <td><code>inputId</code></td>
                <td>String</td>
                <td>''</td>
                <td>ID for the input element (for label association)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Slots -->
        <div class="props-reference">
          <h4>Slots</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Slot</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>default</code></td>
                <td>Input element (input, select, textarea, etc.)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--form-label-gap</code></td>
                <td>0.5rem</td>
                <td>Gap between label and input</td>
              </tr>
              <tr>
                <td><code>--form-group-gap</code></td>
                <td>1rem</td>
                <td>Gap between form groups</td>
              </tr>
              <tr>
                <td><code>--form-input-padding</code></td>
                <td>0.5rem</td>
                <td>Input padding</td>
              </tr>
              <tr>
                <td><code>--form-input-border-color</code></td>
                <td>#ddd</td>
                <td>Input border color</td>
              </tr>
              <tr>
                <td><code>--form-input-border-radius</code></td>
                <td>4px</td>
                <td>Input border radius</td>
              </tr>
              <tr>
                <td><code>--form-input-min-height</code></td>
                <td>44px</td>
                <td>Minimum input height (touch-friendly)</td>
              </tr>
              <tr>
                <td><code>--color-danger</code></td>
                <td>#dc3545</td>
                <td>Error message and border color</td>
              </tr>
              <tr>
                <td><code>--color-muted</code></td>
                <td>#666</td>
                <td>Label and help text color</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Features -->
        <div class="component-demo">
          <h4>Features</h4>
          <div style="padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <ul>
              <li><strong>Consistent label styling:</strong> Standardized font size, weight, and color</li>
              <li><strong>Required indicator:</strong> Red asterisk (*) for required fields</li>
              <li><strong>Error display:</strong> Red border and error message with warning icon</li>
              <li><strong>Help text:</strong> Italic gray text for additional guidance</li>
              <li><strong>Automatic input styling:</strong> Consistent padding, borders, and focus states</li>
              <li><strong>Touch-friendly:</strong> 44px minimum height on mobile devices</li>
              <li><strong>Accessible:</strong> Proper label-input association via inputId</li>
              <li><strong>Flexible:</strong> Works with input, select, textarea, and custom elements</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- MessageAlert Component -->
      <div class="subsection">
        <h3>MessageAlert Component</h3>
        <p class="component-description">
          Consistent message alert component for displaying error, success, warning, and info messages with auto-dismiss and dismissible options.
        </p>

        <!-- Alert Types -->
        <div class="component-demo">
          <h4>Alert Types</h4>
          <div class="alert-types-demo">
            <MessageAlert type="error" message="This is an error message. Something went wrong!" />
            <MessageAlert type="success" message="Success! Your changes have been saved." />
            <MessageAlert type="warning" message="Warning: This action cannot be undone." />
            <MessageAlert type="info" message="Info: New features are available in this release." />
          </div>
        </div>

        <!-- Non-dismissible Alert -->
        <div class="component-demo">
          <h4>Non-dismissible Alert</h4>
          <MessageAlert 
            type="warning" 
            message="This alert cannot be dismissed by the user." 
            :dismissible="false"
          />
        </div>

        <!-- Auto-dismiss Alert -->
        <div class="component-demo">
          <h4>Auto-dismiss Alert</h4>
          <p style="margin-bottom: var(--spacing-md); color: var(--color-muted); font-size: var(--font-size-sm);">
            This alert will automatically dismiss after 5 seconds.
          </p>
          <MessageAlert 
            type="success" 
            message="This message will disappear in 5 seconds!" 
            :auto-dismiss="5000"
          />
        </div>

        <!-- Code Examples -->
        <div class="code-example">
          <h4>Usage</h4>
          <pre><code>&lt;!-- Import the component --&gt;
import MessageAlert from '@/components/composite/MessageAlert.vue'

&lt;!-- Error message --&gt;
&lt;MessageAlert 
  type="error" 
  message="Failed to save changes. Please try again." 
/&gt;

&lt;!-- Success message --&gt;
&lt;MessageAlert 
  type="success" 
  message="Your boat registration has been saved!" 
/&gt;

&lt;!-- Warning message --&gt;
&lt;MessageAlert 
  type="warning" 
  message="You have unsaved changes." 
/&gt;

&lt;!-- Info message --&gt;
&lt;MessageAlert 
  type="info" 
  message="Registration opens on January 15th." 
/&gt;

&lt;!-- Non-dismissible --&gt;
&lt;MessageAlert 
  type="error" 
  message="Critical error occurred." 
  :dismissible="false"
/&gt;

&lt;!-- Auto-dismiss after 3 seconds --&gt;
&lt;MessageAlert 
  type="success" 
  message="Changes saved!" 
  :auto-dismiss="3000"
/&gt;

&lt;!-- With dismiss event handler --&gt;
&lt;MessageAlert 
  type="info" 
  message="Welcome back!" 
  @dismiss="handleDismiss"
/&gt;</code></pre>
        </div>

        <!-- Props Reference -->
        <div class="props-reference">
          <h4>Props</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Prop</th>
                <th>Type</th>
                <th>Default</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>type</code></td>
                <td>String</td>
                <td>'info'</td>
                <td>'error', 'success', 'warning', 'info'</td>
              </tr>
              <tr>
                <td><code>message</code></td>
                <td>String</td>
                <td>required</td>
                <td>Any text string</td>
              </tr>
              <tr>
                <td><code>dismissible</code></td>
                <td>Boolean</td>
                <td>true</td>
                <td>true, false</td>
              </tr>
              <tr>
                <td><code>autoDismiss</code></td>
                <td>Number</td>
                <td>0</td>
                <td>Milliseconds (0 = no auto-dismiss)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Events Reference -->
        <div class="props-reference">
          <h4>Events</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>@dismiss</code></td>
                <td>Emitted when alert is dismissed (by user or auto-dismiss)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Design Tokens -->
        <div class="component-demo">
          <h4>Design Tokens Used</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Value</th>
                <th>Usage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>--color-danger-light</code></td>
                <td>#fee</td>
                <td>Error background</td>
              </tr>
              <tr>
                <td><code>--color-danger-border</code></td>
                <td>#fcc</td>
                <td>Error border</td>
              </tr>
              <tr>
                <td><code>--color-danger-text</code></td>
                <td>#c33</td>
                <td>Error text</td>
              </tr>
              <tr>
                <td><code>--color-success-light</code></td>
                <td>#e7f5ec</td>
                <td>Success background</td>
              </tr>
              <tr>
                <td><code>--color-success-border</code></td>
                <td>#c3e6cb</td>
                <td>Success border</td>
              </tr>
              <tr>
                <td><code>--color-success-text</code></td>
                <td>#155724</td>
                <td>Success text</td>
              </tr>
              <tr>
                <td><code>--color-warning-light</code></td>
                <td>#fff9e6</td>
                <td>Warning background</td>
              </tr>
              <tr>
                <td><code>--color-warning-border</code></td>
                <td>#ffc107</td>
                <td>Warning border</td>
              </tr>
              <tr>
                <td><code>--color-warning-text</code></td>
                <td>#856404</td>
                <td>Warning text</td>
              </tr>
              <tr>
                <td><code>--color-info-light</code></td>
                <td>#e7f3ff</td>
                <td>Info background</td>
              </tr>
              <tr>
                <td><code>--color-info-border</code></td>
                <td>#b3d9ff</td>
                <td>Info border</td>
              </tr>
              <tr>
                <td><code>--color-info-text</code></td>
                <td>#004085</td>
                <td>Info text</td>
              </tr>
              <tr>
                <td><code>--spacing-lg</code></td>
                <td>1rem</td>
                <td>Alert padding</td>
              </tr>
              <tr>
                <td><code>--button-border-radius</code></td>
                <td>4px</td>
                <td>Border radius</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Color Mapping -->
        <div class="component-demo">
          <h4>Type Color Mapping</h4>
          <table class="props-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Background</th>
                <th>Border</th>
                <th>Text</th>
                <th>Icon</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>error</code></td>
                <td>#fee (Light Red)</td>
                <td>#fcc (Red)</td>
                <td>#c33 (Dark Red)</td>
                <td>✕</td>
              </tr>
              <tr>
                <td><code>success</code></td>
                <td>#e7f5ec (Light Green)</td>
                <td>#c3e6cb (Green)</td>
                <td>#155724 (Dark Green)</td>
                <td>✓</td>
              </tr>
              <tr>
                <td><code>warning</code></td>
                <td>#fff9e6 (Light Yellow)</td>
                <td>#ffc107 (Yellow)</td>
                <td>#856404 (Dark Yellow)</td>
                <td>⚠</td>
              </tr>
              <tr>
                <td><code>info</code></td>
                <td>#e7f3ff (Light Blue)</td>
                <td>#b3d9ff (Blue)</td>
                <td>#004085 (Dark Blue)</td>
                <td>ℹ</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Features -->
        <div class="component-demo">
          <h4>Features</h4>
          <div style="padding: 1rem; background: var(--color-light); border-radius: 4px;">
            <ul>
              <li><strong>Type-based styling:</strong> Automatic colors based on message type</li>
              <li><strong>Icon indicators:</strong> Visual icons for each message type</li>
              <li><strong>Dismissible:</strong> Optional close button for user dismissal</li>
              <li><strong>Auto-dismiss:</strong> Automatic dismissal after specified time</li>
              <li><strong>Smooth transitions:</strong> Fade and slide animations</li>
              <li><strong>Accessible:</strong> Proper ARIA attributes for screen readers</li>
              <li><strong>Keyboard accessible:</strong> Close button is keyboard navigable</li>
              <li><strong>Responsive:</strong> Adapts to mobile and desktop layouts</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Usage Examples -->
    <section class="showcase-section">
      <h2>Usage Examples</h2>
      <p class="section-description">
        How to use design tokens in your components.
      </p>

      <div class="code-example">
        <h4>Using Color Tokens</h4>
        <pre><code>.my-button {
  background-color: var(--color-primary);
  color: white;
}

.my-button:hover {
  background-color: var(--color-primary-hover);
}</code></pre>
      </div>

      <div class="code-example">
        <h4>Using Spacing Tokens</h4>
        <pre><code>.my-card {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  gap: var(--spacing-md);
}</code></pre>
      </div>

      <div class="code-example">
        <h4>Using Typography Tokens</h4>
        <pre><code>.my-heading {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}</code></pre>
      </div>
    </section>

    <!-- Footer -->
    <div class="showcase-footer">
      <p>
        This showcase is a living document. As new components and patterns are added to the design system,
        they should be documented here.
      </p>
      <p>
        <strong>Documentation:</strong> See <code>docs/design-system.md</code> for complete guidelines.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/base/BaseButton.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import LoadingSpinner from '@/components/base/LoadingSpinner.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import DataCard from '@/components/composite/DataCard.vue'
import SortableTable from '@/components/composite/SortableTable.vue'
import FormGroup from '@/components/composite/FormGroup.vue'
import MessageAlert from '@/components/composite/MessageAlert.vue'

// Modal demo state
const showSmallModal = ref(false)
const showMediumModal = ref(false)
const showLargeModal = ref(false)
const showNoCloseModal = ref(false)
const showWithFooterModal = ref(false)

// SortableTable demo data
const sampleTableColumns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'age', label: 'Age', sortable: true, width: '100px', align: 'center' },
  { key: 'club', label: 'Club', sortable: true },
  { key: 'role', label: 'Role', sortable: true }
]

const sampleTableData = ref([
  { id: 1, name: 'Jean Dupont', age: 28, club: 'Aviron Bayonnais', role: 'Rameur' },
  { id: 2, name: 'Marie Martin', age: 32, club: 'Société Nautique de Bayonne', role: 'Barreur' },
  { id: 3, name: 'Pierre Durand', age: 45, club: 'Aviron Bayonnais', role: 'Rameur' },
  { id: 4, name: 'Sophie Bernard', age: 29, club: 'Biarritz Olympique', role: 'Rameur' },
  { id: 5, name: 'Luc Petit', age: 56, club: 'Société Nautique de Bayonne', role: 'Rameur' }
])

const boatTableColumns = [
  { key: 'boat_number', label: 'Boat #', sortable: true, width: '120px' },
  { key: 'event_type', label: 'Event', sortable: true },
  { key: 'team_manager', label: 'Manager', sortable: true },
  { key: 'status', label: 'Status', sortable: true, align: 'center' },
  { key: 'actions', label: 'Actions', sortable: false, align: 'right', width: '150px' }
]

const boatTableData = ref([
  { id: 1, boat_number: 'M.1.1', event_type: '4x+ Homme - 21km', team_manager: 'Jean Dupont', status: 'incomplete', registration_status: 'incomplete' },
  { id: 2, boat_number: 'SM.2.3', event_type: '2x Femme - 21km', team_manager: 'Marie Martin', status: 'complete', registration_status: 'complete' },
  { id: 3, boat_number: 'M.1.5', event_type: '8+ Mixte - 21km', team_manager: 'Pierre Durand', status: 'paid', registration_status: 'paid' },
  { id: 4, boat_number: 'SM.3.2', event_type: '1x Homme - 21km', team_manager: 'Sophie Bernard', status: 'forfait', registration_status: 'forfait' }
])

// Width management demo data
const widthDemoColumns = [
  { key: 'id', label: 'ID', sortable: true, width: '80px', align: 'center' },
  { key: 'name', label: 'Name', sortable: true, minWidth: '150px' },
  { key: 'description', label: 'Description', sortable: false }, // auto-size
  { key: 'actions', label: 'Actions', sortable: false, width: '200px', minWidth: '180px', align: 'right' }
]

const widthDemoData = ref([
  { id: 1, name: 'Short', description: 'This is a short description', actions: 'Edit' },
  { id: 2, name: 'Medium Length Name', description: 'This is a medium length description with more text', actions: 'Edit' },
  { id: 3, name: 'Very Long Name That Tests MinWidth', description: 'This is a very long description that demonstrates how the table handles content that exceeds the container width and triggers horizontal scrolling', actions: 'Edit' }
])
</script>

<style scoped>
.design-system-showcase {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.showcase-header {
  margin-bottom: var(--spacing-3xl);
  text-align: center;
}

.showcase-header h1 {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-md);
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-muted);
  max-width: 600px;
  margin: 0 auto;
}

.showcase-section {
  margin-bottom: var(--spacing-3xl);
  padding: var(--spacing-xl);
  background: var(--color-bg-white);
  border-radius: var(--card-border-radius);
  box-shadow: var(--card-shadow);
}

.showcase-section h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
}

.section-description {
  color: var(--color-muted);
  margin-bottom: var(--spacing-xl);
}

.subsection {
  margin-bottom: var(--spacing-xl);
}

.subsection:last-child {
  margin-bottom: 0;
}

.subsection h3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-lg);
}

/* Color Grid */
.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.color-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.color-swatch {
  height: 80px;
  border-radius: var(--button-border-radius);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.color-swatch.primary { background-color: var(--color-primary); }
.color-swatch.success { background-color: var(--color-success); }
.color-swatch.warning { background-color: var(--color-warning); }
.color-swatch.danger { background-color: var(--color-danger); }
.color-swatch.secondary { background-color: var(--color-secondary); }

.color-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.color-info strong {
  font-size: var(--font-size-base);
  color: var(--color-dark);
}

.color-info code {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  background: var(--color-light);
  padding: 0.125rem 0.25rem;
  border-radius: 2px;
}

.color-value {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

/* Spacing Demo */
.spacing-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.spacing-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.spacing-box {
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  min-width: 60px;
  min-height: 40px;
}

.spacing-box.xs { padding: var(--spacing-xs); }
.spacing-box.sm { padding: var(--spacing-sm); }
.spacing-box.md { padding: var(--spacing-md); }
.spacing-box.lg { padding: var(--spacing-lg); }
.spacing-box.xl { padding: var(--spacing-xl); }

.spacing-label {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.spacing-label strong {
  font-size: var(--font-size-base);
}

.spacing-label code {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  background: var(--color-light);
  padding: 0.125rem 0.25rem;
  border-radius: 2px;
}

.spacing-label span {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

/* Typography Demo */
.typography-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.typography-demo p {
  margin: 0;
}

.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-md { font-size: var(--font-size-md); }
.text-lg { font-size: var(--font-size-lg); }
.text-xl { font-size: var(--font-size-xl); }
.text-2xl { font-size: var(--font-size-2xl); }
.text-3xl { font-size: var(--font-size-3xl); }

.typography-demo code {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  background: var(--color-light);
  padding: 0.125rem 0.25rem;
  border-radius: 2px;
}

/* Font Weight Demo */
.font-weight-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.weight-normal { font-weight: var(--font-weight-normal); }
.weight-medium { font-weight: var(--font-weight-medium); }
.weight-semibold { font-weight: var(--font-weight-semibold); }
.weight-bold { font-weight: var(--font-weight-bold); }

/* Button Demo */
.button-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.demo-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--button-border-radius);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: var(--button-transition);
  align-self: flex-start;
}

.demo-button:hover {
  background-color: var(--color-primary-hover);
}

.demo-button.small {
  padding: var(--button-padding-sm);
  min-height: var(--button-min-height-sm);
  font-size: var(--button-font-size-sm);
}

.demo-button.medium {
  padding: var(--button-padding-md);
  min-height: var(--button-min-height-md);
  font-size: var(--button-font-size-md);
}

.demo-button.large {
  padding: var(--button-padding-lg);
  min-height: var(--button-min-height-lg);
  font-size: var(--button-font-size-lg);
}

.token-info {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.token-info code {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  background: var(--color-light);
  padding: 0.25rem 0.5rem;
  border-radius: 2px;
}

/* Badge Demo */
.badge-demo {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

.badge-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  align-items: flex-start;
}

.demo-badge {
  padding: var(--badge-padding);
  border-radius: var(--badge-border-radius);
  font-size: var(--badge-font-size);
  font-weight: var(--badge-font-weight);
  white-space: nowrap;
}

.demo-badge.incomplete {
  background-color: var(--color-warning);
  color: var(--color-dark);
}

.demo-badge.complete {
  background-color: var(--color-success);
  color: white;
}

.demo-badge.paid {
  background-color: var(--color-primary);
  color: white;
}

.demo-badge.forfait {
  background-color: var(--color-danger);
  color: white;
}

/* Card Demo */
.card-demo {
  margin-bottom: var(--spacing-md);
}

.demo-card {
  padding: var(--card-padding-desktop);
  border: var(--card-border-width) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  box-shadow: var(--card-shadow);
}

.demo-card h4 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
}

.demo-card p {
  margin-bottom: var(--spacing-lg);
  color: var(--color-muted);
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* Breakpoint Demo */
.breakpoint-demo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.breakpoint-item {
  padding: var(--spacing-lg);
  background: var(--color-light);
  border-radius: var(--button-border-radius);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.breakpoint-item strong {
  font-size: var(--font-size-lg);
  color: var(--color-dark);
}

.breakpoint-item code {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

.breakpoint-item span {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

.current-breakpoint {
  padding: var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border-radius: var(--button-border-radius);
  text-align: center;
  font-size: var(--font-size-lg);
}

.current-breakpoint span {
  display: none;
}

@media (max-width: 767px) {
  .current-breakpoint .mobile-indicator {
    display: inline;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .current-breakpoint .tablet-indicator {
    display: inline;
  }
}

@media (min-width: 1024px) {
  .current-breakpoint .desktop-indicator {
    display: inline;
  }
}

/* Code Examples */
.code-example {
  margin-bottom: var(--spacing-xl);
}

.code-example h4 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-md);
}

.code-example pre {
  background: var(--color-dark);
  color: #f8f8f2;
  padding: var(--spacing-lg);
  border-radius: var(--button-border-radius);
  overflow-x: auto;
  margin: 0;
}

.code-example code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
}

/* Footer */
.showcase-footer {
  margin-top: var(--spacing-3xl);
  padding: var(--spacing-xl);
  background: var(--color-light);
  border-radius: var(--card-border-radius);
  text-align: center;
}

.showcase-footer p {
  margin-bottom: var(--spacing-md);
  color: var(--color-muted);
}

.showcase-footer p:last-child {
  margin-bottom: 0;
}

.showcase-footer code {
  background: white;
  padding: 0.125rem 0.25rem;
  border-radius: 2px;
  font-size: var(--font-size-sm);
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .design-system-showcase {
    padding: var(--spacing-lg);
  }

  .showcase-section {
    padding: var(--spacing-lg);
  }

  .demo-card {
    padding: var(--card-padding-mobile);
  }
}

/* Component Demo Styles */
.component-description {
  color: var(--color-muted);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-base);
}

.component-demo {
  margin-bottom: var(--spacing-xl);
}

.component-demo h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  color: var(--color-dark);
}

.button-variants,
.button-sizes,
.button-states {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: center;
}

.button-full-width {
  max-width: 400px;
}

/* Props Reference Table */
.props-reference {
  margin-top: var(--spacing-xl);
}

.props-reference h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  color: var(--color-dark);
}

.props-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
  background: white;
  border-radius: var(--button-border-radius);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.props-table thead {
  background: var(--table-header-bg);
}

.props-table th {
  text-align: left;
  padding: var(--spacing-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  border-bottom: 2px solid var(--color-border);
}

.props-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-dark);
}

.props-table tbody tr:last-child td {
  border-bottom: none;
}

.props-table code {
  background: var(--color-light);
  padding: 0.125rem 0.375rem;
  border-radius: 2px;
  font-size: var(--font-size-xs);
  color: var(--color-primary);
}

@media (max-width: 767px) {
  .props-table {
    font-size: var(--font-size-xs);
  }

  .props-table th,
  .props-table td {
    padding: var(--spacing-sm);
  }

  .button-variants,
  .button-sizes,
  .button-states {
    flex-direction: column;
    align-items: stretch;
  }
}

/* StatusBadge Component Demo Styles */
.badge-variants,
.badge-sizes,
.badge-custom {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: center;
}

/* LoadingSpinner Component Demo Styles */
.spinner-sizes {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-3xl);
  align-items: flex-start;
  padding: var(--spacing-xl);
  background: var(--color-light);
  border-radius: var(--button-border-radius);
}

.spinner-demo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.demo-label {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  font-weight: var(--font-weight-medium);
}

.spinner-message-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3xl);
  padding: var(--spacing-xl);
  background: var(--color-light);
  border-radius: var(--button-border-radius);
}

/* DataCard Component Demo Styles */
.card-demo-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

@media (min-width: 768px) {
  .card-demo-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-xl);
  }
}

/* Detail row styles for card demos */
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-light);
  gap: var(--spacing-md);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
  flex-shrink: 0;
}

.detail-row .value {
  text-align: right;
  word-break: break-word;
}

/* MessageAlert Component Demo Styles */
.alert-types-demo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
</style>
