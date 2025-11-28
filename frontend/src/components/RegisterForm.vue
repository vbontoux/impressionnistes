<template>
  <div class="register-form">
    <div class="form-header">
      <img src="../assets/rcpm-logo.png" alt="RCPM Logo" class="form-logo" />
      <h2>{{ $t('auth.register.title') }}</h2>
      <p class="subtitle">{{ $t('auth.register.subtitle') }}</p>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Email -->
      <div class="form-group">
        <label for="email">{{ $t('auth.register.email') }} *</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          :disabled="loading"
          @blur="validateEmail"
        />
        <span v-if="errors.email" class="error">{{ errors.email }}</span>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label for="password">{{ $t('auth.register.password') }} *</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          :disabled="loading"
          @input="validatePassword"
        />
        <div class="password-requirements">
          <div class="requirement" :class="{ valid: passwordChecks.minLength }">
            <span class="icon">{{ passwordChecks.minLength ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordMinLength') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasUppercase }">
            <span class="icon">{{ passwordChecks.hasUppercase ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasUppercase') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasLowercase }">
            <span class="icon">{{ passwordChecks.hasLowercase ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasLowercase') }}</span>
          </div>
          <div class="requirement" :class="{ valid: passwordChecks.hasNumber }">
            <span class="icon">{{ passwordChecks.hasNumber ? '✓' : '○' }}</span>
            <span>{{ $t('auth.validation.passwordHasNumber') }}</span>
          </div>
        </div>
      </div>

      <!-- First Name -->
      <div class="form-group">
        <label for="firstName">{{ $t('auth.register.firstName') }} *</label>
        <input
          id="firstName"
          v-model="form.first_name"
          type="text"
          required
          :disabled="loading"
        />
        <span v-if="errors.first_name" class="error">{{ errors.first_name }}</span>
      </div>

      <!-- Last Name -->
      <div class="form-group">
        <label for="lastName">{{ $t('auth.register.lastName') }} *</label>
        <input
          id="lastName"
          v-model="form.last_name"
          type="text"
          required
          :disabled="loading"
        />
        <span v-if="errors.last_name" class="error">{{ errors.last_name }}</span>
      </div>

      <!-- Club Affiliation -->
      <div class="form-group">
        <label for="clubAffiliation">{{ $t('auth.register.clubAffiliation') }} *</label>
        
        <!-- Foreign Club Checkbox -->
        <div class="checkbox-group">
          <input
            id="foreignClub"
            v-model="isForeignClub"
            type="checkbox"
            :disabled="loading"
          />
          <label for="foreignClub" class="checkbox-label">
            {{ $t('crew.form.foreignClub') }}
          </label>
        </div>

        <!-- Searchable Dropdown for French Clubs -->
        <div v-if="!isForeignClub" class="autocomplete-wrapper">
          <input
            id="clubAffiliation"
            v-model="clubSearchQuery"
            type="text"
            required
            :disabled="loading"
            :placeholder="$t('crew.form.clubSearchPlaceholder')"
            @input="handleClubSearch"
            @focus="handleClubFocus"
            @blur="handleClubBlur"
            autocomplete="off"
          />
          <div v-if="showClubDropdown && filteredClubs.length > 0" class="autocomplete-dropdown">
            <div
              v-for="club in filteredClubs"
              :key="club.club_id"
              class="autocomplete-item"
              @mousedown.prevent="selectClub(club)"
            >
              <div class="club-name">{{ club.name }}</div>
            </div>
          </div>
          <div v-if="showClubDropdown && clubSearchQuery && filteredClubs.length === 0" class="autocomplete-no-results">
            {{ $t('crew.form.noClubsFound') }}
          </div>
        </div>

        <!-- Free Text Input for Foreign Clubs -->
        <input
          v-else
          id="clubAffiliationForeign"
          v-model="form.club_affiliation"
          type="text"
          required
          :disabled="loading"
          :placeholder="$t('auth.register.clubAffiliation')"
        />
        
        <span v-if="errors.club_affiliation" class="error">{{ errors.club_affiliation }}</span>
      </div>

      <!-- Mobile Number -->
      <div class="form-group">
        <label for="mobileNumber">{{ $t('auth.register.mobileNumber') }} *</label>
        <input
          id="mobileNumber"
          v-model="form.mobile_number"
          type="tel"
          required
          :disabled="loading"
          placeholder="+33612345678"
        />
        <span v-if="errors.mobile_number" class="error">{{ errors.mobile_number }}</span>
        <small class="hint">{{ $t('auth.register.mobileHint') }}</small>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>

      <!-- Submit Button -->
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading">{{ $t('common.loading') }}</span>
        <span v-else>{{ $t('auth.register.submit') }}</span>
      </button>

      <!-- Login Link -->
      <p class="text-center">
        {{ $t('auth.register.haveAccount') }}
        <router-link to="/login">{{ $t('auth.register.loginLink') }}</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { useI18n } from 'vue-i18n';
import axios from 'axios';

const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();

const form = reactive({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  club_affiliation: '',
  mobile_number: '',
});

const errors = reactive({});
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Password validation checks
const passwordChecks = reactive({
  minLength: false,
  hasUppercase: false,
  hasLowercase: false,
  hasNumber: false
});

// Club search state
const clubs = ref([]);
const clubSearchQuery = ref('');
const filteredClubs = ref([]);
const showClubDropdown = ref(false);
const isForeignClub = ref(false);

// Fetch clubs on mount
onMounted(async () => {
  await fetchClubs();
});

// Fetch clubs from API
const fetchClubs = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL.replace(/\/$/, ''); // Remove trailing slash
    console.log('Fetching clubs from:', `${apiUrl}/clubs`);
    const response = await axios.get(`${apiUrl}/clubs`);
    console.log('Clubs response:', response.data);
    clubs.value = response.data.data.clubs || [];
    console.log(`Loaded ${clubs.value.length} clubs`);
    // Initialize filtered clubs with first 50
    filteredClubs.value = clubs.value.slice(0, 50);
  } catch (error) {
    console.error('Error fetching clubs:', error);
    console.error('Error details:', error.response?.data);
    // Don't show error to user, they can still use foreign club checkbox
  }
};

// Handle club focus - show dropdown with initial results
const handleClubFocus = () => {
  console.log('Club focus - clubs:', clubs.value.length, 'filtered:', filteredClubs.value.length);
  showClubDropdown.value = true;
  handleClubSearch();
  console.log('After search - showDropdown:', showClubDropdown.value, 'filtered:', filteredClubs.value.length);
};

// Handle club search input
const handleClubSearch = () => {
  if (!clubSearchQuery.value) {
    filteredClubs.value = clubs.value.slice(0, 50);
    showClubDropdown.value = true;
    return;
  }
  
  const query = clubSearchQuery.value.toLowerCase();
  filteredClubs.value = clubs.value
    .filter(club => {
      const nameMatch = club.name.toLowerCase().includes(query);
      const urlMatch = club.url && club.url.toLowerCase().includes(query);
      return nameMatch || urlMatch;
    })
    .slice(0, 50);
  
  showClubDropdown.value = true;
};

// Select a club from dropdown
const selectClub = (club) => {
  form.club_affiliation = club.name;
  clubSearchQuery.value = club.name;
  showClubDropdown.value = false;
};

// Handle blur event on club input
const handleClubBlur = () => {
  setTimeout(() => {
    showClubDropdown.value = false;
    
    // If not foreign club, validate that the entered text matches a club name
    if (!isForeignClub.value && clubSearchQuery.value) {
      const matchingClub = clubs.value.find(
        club => club.name.toLowerCase() === clubSearchQuery.value.toLowerCase()
      );
      
      if (!matchingClub) {
        // Reset to empty if no match found
        clubSearchQuery.value = '';
        form.club_affiliation = '';
      } else {
        // Ensure exact match
        form.club_affiliation = matchingClub.name;
        clubSearchQuery.value = matchingClub.name;
      }
    }
  }, 200);
};

// Watch for foreign club checkbox changes
watch(isForeignClub, (newValue) => {
  if (newValue) {
    form.club_affiliation = '';
    clubSearchQuery.value = '';
  } else {
    form.club_affiliation = '';
    clubSearchQuery.value = '';
  }
});

// Validation functions
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errors.email = t('auth.validation.invalidEmail');
  } else {
    delete errors.email;
  }
};

const validatePassword = () => {
  // Update individual checks
  passwordChecks.minLength = form.password.length >= 8;
  passwordChecks.hasUppercase = /[A-Z]/.test(form.password);
  passwordChecks.hasLowercase = /[a-z]/.test(form.password);
  passwordChecks.hasNumber = /[0-9]/.test(form.password);
  
  // Set error if any check fails
  const allValid = passwordChecks.minLength && 
                   passwordChecks.hasUppercase && 
                   passwordChecks.hasLowercase && 
                   passwordChecks.hasNumber;
  
  if (!allValid) {
    errors.password = t('auth.validation.passwordRequirements');
  } else {
    delete errors.password;
  }
};

const handleSubmit = async () => {
  // Clear messages
  errorMessage.value = '';
  successMessage.value = '';

  // Validate all fields
  validateEmail();
  validatePassword();

  if (Object.keys(errors).length > 0) {
    return;
  }

  loading.value = true;

  try {
    await authStore.register(form);
    
    successMessage.value = t('auth.register.success');
    
    // Redirect to verify email page after 2 seconds
    setTimeout(() => {
      router.push({ 
        path: '/verify-email',
        query: { email: form.email }
      });
    }, 2000);
  } catch (error) {
    console.error('Registration error:', error);
    console.error('Error response:', error.response);
    
    // Show detailed error message
    if (error.response?.data?.error?.message) {
      errorMessage.value = error.response.data.error.message;
    } else if (error.response?.data?.error) {
      errorMessage.value = JSON.stringify(error.response.data.error);
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = t('auth.register.error');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-form {
  max-width: 500px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-logo {
  height: 80px;
  width: auto;
  margin-bottom: 1rem;
}

h2 {
  margin-bottom: 0.5rem;
  color: #333;
}

.subtitle {
  color: #666;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error {
  display: block;
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.hint {
  display: block;
  color: #666;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #66bb6a;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.text-center {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

a {
  color: #4CAF50;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.password-requirements {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 0.875rem;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  color: #666;
  transition: color 0.3s;
}

.requirement.valid {
  color: #4CAF50;
  font-weight: 500;
}

.requirement .icon {
  font-weight: bold;
  font-size: 1rem;
  min-width: 1.2rem;
}

.requirement.valid .icon {
  color: #4CAF50;
}

.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.checkbox-label {
  margin-bottom: 0;
  font-weight: normal;
  cursor: pointer;
}

.autocomplete-wrapper {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 1000;
}

.autocomplete-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-item:hover {
  background-color: #f5f5f5;
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.club-name {
  font-weight: 500;
  color: #333;
}

.club-url {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.autocomplete-no-results {
  padding: 0.75rem;
  color: #666;
  font-style: italic;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
}
</style>
