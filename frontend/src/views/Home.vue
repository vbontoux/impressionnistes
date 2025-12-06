<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="container">
        <h1>{{ $t('home.hero.title') }}</h1>
        <p class="hero-subtitle">{{ $t('home.hero.subtitle') }}</p>
        <div v-if="!authStore.isAuthenticated" class="hero-actions">
          <router-link to="/register" class="btn btn-primary">
            {{ $t('home.hero.register') }}
          </router-link>
          <router-link to="/login" class="btn btn-secondary">
            {{ $t('home.hero.login') }}
          </router-link>
          <a :href="eventWebsite" target="_blank" rel="noopener noreferrer" class="btn btn-outline">
            {{ $t('home.hero.eventWebsite') }}
          </a>
        </div>
        <div v-else class="hero-actions">
          <router-link to="/dashboard" class="btn btn-primary">
            {{ $t('nav.dashboard') }}
          </router-link>
          <a :href="eventWebsite" target="_blank" rel="noopener noreferrer" class="btn btn-outline">
            {{ $t('home.hero.eventWebsite') }}
          </a>
        </div>
      </div>
    </section>

    <!-- Important Dates -->
    <section class="dates-section">
      <div class="container">
        <h2>{{ $t('home.dates.title') }}</h2>
        <div class="dates-grid">
          <div class="date-card">
            <div class="date-icon">📅</div>
            <h3>{{ $t('home.dates.registrationOpen') }}</h3>
            <p class="date-value">{{ $t('home.dates.registrationOpenDate') }}</p>
            <div class="date-rules">
              <p class="rule-text">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase1.rule1') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase1.rule2') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase1.rule3') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon warning" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase1.rule4') }}
              </p>
            </div>
          </div>
          <div class="date-card">
            <div class="date-icon">🔒</div>
            <h3>{{ $t('home.dates.registrationClose') }}</h3>
            <p class="date-value">{{ $t('home.dates.registrationCloseDate') }}</p>
            <div class="date-rules">
              <p class="rule-text">
                <svg class="rule-icon cross" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase2.rule1') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase2.rule2') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase2.rule3') }}
              </p>
              <p class="rule-text refund-possible">
                <svg class="rule-icon check" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase2.rule5') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon warning" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase2.rule4') }}
              </p>
            </div>
          </div>
          <div class="date-card">
            <div class="date-icon">💳</div>
            <h3>{{ $t('home.dates.paymentDeadline') }}</h3>
            <p class="date-value">{{ $t('home.dates.paymentDeadlineDate') }}</p>
            <div class="date-rules">
              <p class="rule-text">
                <svg class="rule-icon cross" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase3.rule1') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon cross" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase3.rule2') }}
              </p>
              <p class="rule-text">
                <svg class="rule-icon warning" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ $t('home.timeline.phase3.rule5') }}
              </p>
            </div>
          </div>
          <div class="date-card highlight">
            <div class="date-icon">🏁</div>
            <h3>{{ $t('home.dates.competitionDate') }}</h3>
            <p class="date-value">{{ $t('home.dates.competitionDateValue') }}</p>
            <div class="date-rules">
              <p class="rule-text">
                <svg class="rule-icon warning" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <strong>{{ $t('home.timeline.phase3.rule3') }}</strong>
              </p>
              <p class="rule-text">
                <svg class="rule-icon warning" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <strong>{{ $t('home.timeline.phase3.rule4') }}</strong>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Events Overview -->
    <section class="events-section">
      <div class="container">
        <h2>{{ $t('home.events.title') }}</h2>
        <div class="events-grid">
          <!-- Semi-Marathon -->
          <div class="event-card">
            <div class="event-header">
              <h3>{{ $t('home.events.semiMarathon.title') }}</h3>
              <span class="event-distance">21 km</span>
            </div>
            <p class="event-description">{{ $t('home.events.semiMarathon.description') }}</p>
            <ul class="event-features">
              <li>{{ $t('home.events.semiMarathon.boats') }}</li>
              <li>{{ $t('home.events.semiMarathon.categories') }}</li>
              <li>{{ $t('home.events.semiMarathon.oars') }}</li>
              <li>{{ $t('home.events.semiMarathon.crews') }}</li>
            </ul>
            <div class="event-races">
              <strong>{{ $t('home.events.semiMarathon.racesCount') }}</strong>
            </div>
          </div>

          <!-- Marathon -->
          <div class="event-card">
            <div class="event-header">
              <h3>{{ $t('home.events.marathon.title') }}</h3>
              <span class="event-distance">42 km</span>
            </div>
            <p class="event-description">{{ $t('home.events.marathon.description') }}</p>
            <ul class="event-features">
              <li>{{ $t('home.events.marathon.boats') }}</li>
              <li>{{ $t('home.events.marathon.categories') }}</li>
              <li>{{ $t('home.events.marathon.format') }}</li>
            </ul>
            <div class="event-races">
              <strong>{{ $t('home.events.marathon.racesCount') }}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Registration Process -->
    <section class="process-section">
      <div class="container">
        <h2>{{ $t('home.process.title') }}</h2>
        <p class="section-intro">{{ $t('home.process.intro') }}</p>
        <div class="process-steps">
          <div class="step">
            <div class="step-number">1</div>
            <h3>{{ $t('home.process.step1.title') }}</h3>
            <p>{{ $t('home.process.step1.description') }}</p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3>{{ $t('home.process.step2.title') }}</h3>
            <p>{{ $t('home.process.step2.description') }}</p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3>{{ $t('home.process.step3.title') }}</h3>
            <p>{{ $t('home.process.step3.description') }}</p>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <h3>{{ $t('home.process.step4.title') }}</h3>
            <p>{{ $t('home.process.step4.description') }}</p>
          </div>
          <div class="step">
            <div class="step-number">5</div>
            <h3>{{ $t('home.process.step5.title') }}</h3>
            <p>{{ $t('home.process.step5.description') }}</p>
          </div>
          <div class="step">
            <div class="step-number">6</div>
            <h3>{{ $t('home.process.step6.title') }}</h3>
            <p>{{ $t('home.process.step6.description') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section class="pricing-section">
      <div class="container">
        <h2>{{ $t('home.pricing.title') }}</h2>
        
        <!-- Seat Registration Fees -->
        <div class="pricing-category">
          <h3 class="category-title">{{ $t('home.pricing.seatFees.title') }}</h3>
          <p class="category-description">{{ $t('home.pricing.seatFees.description') }}</p>
          <div class="pricing-grid">
            <div class="pricing-card">
              <div class="pricing-icon">🚣</div>
              <h4>{{ $t('home.pricing.seatFees.crew.title') }}</h4>
              <div class="price">€20<span class="price-unit">/{{ $t('home.pricing.seat') }}</span></div>
              <p>{{ $t('home.pricing.seatFees.crew.description') }}</p>
            </div>
            <div class="pricing-card">
              <div class="pricing-icon">🛶</div>
              <h4>{{ $t('home.pricing.seatFees.skiff.title') }}</h4>
              <div class="price">€50</div>
              <p>{{ $t('home.pricing.seatFees.skiff.description') }}</p>
            </div>
          </div>
        </div>

        <!-- Boat Rental Fees -->
        <div class="pricing-category">
          <h3 class="category-title">{{ $t('home.pricing.boatRental.title') }}</h3>
          <p class="category-description">{{ $t('home.pricing.boatRental.description') }}</p>
          <div class="pricing-grid">
            <div class="pricing-card">
              <div class="pricing-icon">🛶</div>
              <h4>{{ $t('home.pricing.boatRental.skiff.title') }}</h4>
              <div class="price">€50</div>
              <p>{{ $t('home.pricing.boatRental.skiff.description') }}</p>
            </div>
            <div class="pricing-card">
              <div class="pricing-icon">🚣‍♂️</div>
              <h4>{{ $t('home.pricing.boatRental.crew.title') }}</h4>
              <div class="price">€20<span class="price-unit">/{{ $t('home.pricing.seat') }}</span></div>
              <p>{{ $t('home.pricing.boatRental.crew.description') }}</p>
            </div>
          </div>
        </div>

        <!-- Examples -->
        <div class="pricing-examples">
          <h3>{{ $t('home.pricing.examples.title') }}</h3>
          
          <!-- Registration Only Examples -->
          <div class="example-section">
            <h4 class="example-section-title">{{ $t('home.pricing.examples.registrationOnly') }}</h4>
            <div class="examples-grid">
              <div class="example-card">
                <div class="example-icon">🚣‍♀️</div>
                <h5>{{ $t('home.pricing.examples.eight.title') }}</h5>
                <p class="example-calc">{{ $t('home.pricing.examples.eight.calc') }}</p>
                <div class="example-total">{{ $t('home.pricing.examples.eight.total') }}</div>
              </div>
              <div class="example-card">
                <div class="example-icon">🚣</div>
                <h5>{{ $t('home.pricing.examples.four.title') }}</h5>
                <p class="example-calc">{{ $t('home.pricing.examples.four.calc') }}</p>
                <div class="example-total">{{ $t('home.pricing.examples.four.total') }}</div>
              </div>
              <div class="example-card">
                <div class="example-icon">🛶</div>
                <h5>{{ $t('home.pricing.examples.skiff.title') }}</h5>
                <p class="example-calc">{{ $t('home.pricing.examples.skiff.calc') }}</p>
                <div class="example-total">{{ $t('home.pricing.examples.skiff.total') }}</div>
              </div>
            </div>
          </div>

          <!-- Registration + Rental Examples -->
          <div class="example-section">
            <h4 class="example-section-title">{{ $t('home.pricing.examples.withRental') }}</h4>
            <div class="examples-grid">
              <div class="example-card rental">
                <div class="example-icon">🚣‍♂️</div>
                <h5>{{ $t('home.pricing.examples.fourWithRental.title') }}</h5>
                <p class="example-calc">{{ $t('home.pricing.examples.fourWithRental.calc') }}</p>
                <div class="example-total">{{ $t('home.pricing.examples.fourWithRental.total') }}</div>
              </div>
              <div class="example-card rental">
                <div class="example-icon">🛶</div>
                <h5>{{ $t('home.pricing.examples.skiffWithRental.title') }}</h5>
                <p class="example-calc">{{ $t('home.pricing.examples.skiffWithRental.calc') }}</p>
                <div class="example-total">{{ $t('home.pricing.examples.skiffWithRental.total') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact -->
    <section class="contact-section">
      <div class="container">
        <h2>{{ $t('home.contact.title') }}</h2>
        <p>{{ $t('home.contact.description') }}</p>
        <a :href="`mailto:${contactEmail}`" class="contact-email">
          {{ contactEmail }}
        </a>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <h2>{{ $t('home.cta.title') }}</h2>
        <p>{{ $t('home.cta.description') }}</p>
        <router-link to="/register" class="btn btn-primary btn-large">
          {{ $t('home.cta.button') }}
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/authStore';

const authStore = useAuthStore();
const contactEmail = import.meta.env.VITE_CONTACT_EMAIL || 'impressionnistes@rcpm-aviron.fr';
const eventWebsite = import.meta.env.VITE_EVENT_WEBSITE || 'https://rcpm-aviron.fr/';
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 0;
  text-align: center;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Buttons */
.btn {
  padding: 0.875rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-block;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-secondary {
  background-color: white;
  color: #667eea;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: transparent;
  color: white;
}

.btn-outline {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-outline:hover {
  background-color: white;
  color: #667eea;
}

.btn-large {
  padding: 1.125rem 3rem;
  font-size: 1.125rem;
}

/* Sections */
section {
  padding: 5rem 0;
}

section h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-align: center;
  color: #333;
}

.section-intro {
  text-align: center;
  font-size: 1.125rem;
  color: #666;
  max-width: 800px;
  margin: 0 auto 3rem;
}

/* Dates Section */
.dates-section {
  background-color: #f8f9fa;
}

.dates-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-top: 3rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.date-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.date-card:hover {
  transform: translateY(-4px);
}

.date-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.date-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.date-card h3 {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
  color: inherit;
  font-weight: 600;
}

.date-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: inherit;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
}

.date-card.highlight .date-value {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.date-rules {
  text-align: left;
  margin-top: 1rem;
}

.rule-text {
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0.75rem 0;
  color: inherit;
  opacity: 0.95;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.rule-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.rule-icon.check {
  color: #4CAF50;
}

.rule-icon.cross {
  color: #f44336;
}

.rule-icon.warning {
  color: #ff9800;
}

.license-warning {
  background-color: rgba(255, 107, 107, 0.25);
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 4px solid #ff6b6b;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
}

.license-warning strong {
  color: #ffe0e0;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Events Section */
.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.event-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 2rem;
  transition: all 0.3s;
}

.event-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.event-header h3 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.event-distance {
  background: #667eea;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 700;
}

.event-description {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.event-features {
  list-style: none;
  padding: 0;
  margin-bottom: 1.5rem;
}

.event-features li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.event-features li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #4CAF50;
  font-weight: 700;
}

.event-races {
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  color: #667eea;
}

/* Process Section */
.process-section {
  background-color: #f8f9fa;
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.step {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.step-number {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.step h3 {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: #333;
}

.step p {
  color: #666;
  line-height: 1.6;
}

/* Pricing Section */
.pricing-category {
  margin-bottom: 3rem;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.category-title {
  font-size: 1.75rem;
  color: #333;
  margin-bottom: 0.5rem;
  text-align: center;
}

.category-description {
  text-align: center;
  color: #666;
  font-size: 1.125rem;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.pricing-card {
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
}

.pricing-card:hover {
  border-color: #4CAF50;
  box-shadow: 0 4px 16px rgba(76, 175, 80, 0.2);
  transform: translateY(-4px);
  background: white;
}

.pricing-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.pricing-card h4 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #333;
}

.price {
  font-size: 3rem;
  font-weight: 700;
  color: #4CAF50;
  margin-bottom: 1rem;
  line-height: 1;
}

.price-unit {
  font-size: 1.25rem;
  color: #666;
  font-weight: 400;
}

.pricing-card p {
  color: #666;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Examples */
.pricing-examples {
  margin-top: 3rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pricing-examples h3 {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  color: #333;
  text-align: center;
}

.example-section {
  margin-bottom: 2.5rem;
}

.example-section:last-child {
  margin-bottom: 0;
}

.example-section-title {
  font-size: 1.25rem;
  color: #667eea;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 600;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.example-card {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.example-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.example-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.example-card h5 {
  font-size: 1.125rem;
  color: #333;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.example-calc {
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.example-total {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4CAF50;
}

/* Contact Section */
.contact-section {
  background-color: #f8f9fa;
  text-align: center;
}

.contact-section p {
  font-size: 1.125rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.contact-email {
  display: inline-block;
  font-size: 1.5rem;
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  padding: 1rem 2rem;
  border: 2px solid #667eea;
  border-radius: 8px;
  transition: all 0.3s;
}

.contact-email:hover {
  background-color: #667eea;
  color: white;
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.cta-section h2 {
  color: white;
  margin-bottom: 1rem;
}

.cta-section p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

/* Responsive */
@media (max-width: 1024px) and (min-width: 769px) {
  .dates-grid {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1.125rem;
  }

  section h2 {
    font-size: 2rem;
  }

  .dates-grid,
  .events-grid,
  .process-steps,
  .pricing-grid {
    grid-template-columns: 1fr;
  }

  .date-card {
    min-height: auto;
  }

  .container {
    padding: 0 1rem;
  }
}
</style>
