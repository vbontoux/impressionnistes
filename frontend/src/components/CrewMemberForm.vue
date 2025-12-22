<template>
  <div class="crew-member-form">
    <h3>{{ isEdit ? $t('crew.form.editTitle') : $t('crew.form.createTitle') }}</h3>

    <form @submit.prevent="handleSubmit">
      <!-- First Name -->
      <div class="form-group">
        <label for="firstName">{{ $t('crew.form.firstName') }} *</label>
        <input
          id="firstName"
          v-model="form.first_name"
          type="text"
          required
          :disabled="loading"
          @blur="validateField('first_name')"
        />
        <span v-if="errors.first_name" class="error">{{ errors.first_name }}</span>
      </div>

      <!-- Last Name -->
      <div class="form-group">
        <label for="lastName">{{ $t('crew.form.lastName') }} *</label>
        <input
          id="lastName"
          v-model="form.last_name"
          type="text"
          required
          :disabled="loading"
          @blur="validateField('last_name')"
        />
        <span v-if="errors.last_name" class="error">{{ errors.last_name }}</span>
      </div>

      <!-- Date of Birth -->
      <div class="form-group">
        <label for="dateOfBirth">{{ $t('crew.form.dateOfBirth') }} *</label>
        <input
          id="dateOfBirth"
          v-model="form.date_of_birth"
          type="date"
          required
          :disabled="loading"
          @blur="validateField('date_of_birth')"
        />
        <span v-if="errors.date_of_birth" class="error">{{ errors.date_of_birth }}</span>
      </div>

      <!-- Gender -->
      <div class="form-group">
        <label for="gender">{{ $t('crew.form.gender') }} *</label>
        <select
          id="gender"
          v-model="form.gender"
          required
          :disabled="loading"
        >
          <option value="">{{ $t('crew.form.selectGender') }}</option>
          <option value="M">{{ $t('crew.form.male') }}</option>
          <option value="F">{{ $t('crew.form.female') }}</option>
        </select>
        <span v-if="errors.gender" class="error">{{ errors.gender }}</span>
      </div>

      <!-- License Number with Warning -->
      <div class="form-group license-with-warning">
        <div class="license-field">
          <label for="licenseNumber">{{ $t('crew.form.licenseNumber') }} *</label>
          <input
            id="licenseNumber"
            v-model="form.license_number"
            type="text"
            required
            :disabled="loading"
            placeholder="ABC123456"
            maxlength="12"
            @blur="validateField('license_number')"
          />
          <small class="hint">{{ $t('crew.form.licenseHint') }}</small>
          <span v-if="errors.license_number" class="error">{{ errors.license_number }}</span>
        </div>
        
        <div class="warning-box" :class="{ 'expanded': warningExpanded }" @click="warningExpanded = !warningExpanded">
          <svg class="warning-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 20h20L12 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="currentColor" fill-opacity="0.1"/>
            <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="17" r="1" fill="currentColor"/>
          </svg>
          <div class="warning-content">
            <strong>{{ $t('crew.form.licenseWarningTitle') }}</strong>
            <p v-show="warningExpanded">{{ $t('crew.form.licenseWarningText') }}</p>
          </div>
          <svg class="expand-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="6 9 12 15 18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <!-- Club Affiliation -->
      <div class="form-group">
        <label for="clubAffiliation">{{ $t('crew.form.clubAffiliation') }}</label>
        
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
            <svg class="ffa-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 811.33 348.36"><path d="M551.5,78.1v16.03c12.64-6.5,26.66-9.89,40.88-9.88,49.48,0,89.6,40.11,89.6,89.6s-40.11,89.6-89.6,89.6c-14.22.01-28.23-3.37-40.88-9.88v51.4c4.8,0,9.53-.28,14.2-.79,9.93-1.08,19.71-3.31,29.12-6.64,15.98-5.66,30.7-14.39,43.32-25.71v40.36c6.7-3.19,13.16-6.87,19.32-11,8.65-5.78,16.7-12.43,24-19.84,23.72-24.14,39.84-56.16,43.23-91.78v100.16c1.02-1.16,2.09-2.36,3.09-3.54,24.3-29.01,39.27-66.07,40.32-106.62v-10.77c-1.05-40.55-16.02-77.61-40.32-106.62-.99-1.19-2.06-2.38-3.09-3.54v100.15c-3.39-35.62-19.51-67.64-43.23-91.78-7.3-7.41-15.34-14.06-24-19.84-6.16-4.14-12.62-7.81-19.32-11v40.36c-12.62-11.31-27.34-20.05-43.32-25.71-9.42-3.33-19.19-5.56-29.12-6.64-4.71-.52-9.45-.78-14.2-.79v34.71M508.18,238.04v37.97c8.29.52,19.76-.56,30.46-2.64,4.33-.84,8.62-1.89,12.85-3.15-17.18-9.66-31.77-20.5-43.31-32.18M508.18,110.32v-37.97c8.29-.52,19.76.56,30.46,2.64,4.33.84,8.62,1.89,12.85,3.15-17.18,9.65-31.77,20.5-43.31,32.18" style="fill: #182765;"></path><path d="M551.5,289.86c-2.19-2.49-4.32-5.04-6.37-7.65-2.25-2.88-4.41-5.82-6.48-8.83-10.7,2.08-22.18,3.15-30.46,2.64h0s0,21.54,0,21.54c13.91,4.92,28.56,7.43,43.31,7.42v-15.11h0ZM594.82,348.36h.05c14.86,0,29.5-1.93,43.26-5.44-15.17-3.93-29.74-9.89-43.32-17.72v23.16h0ZM681.46,281.35c-7.3,7.41-15.34,14.06-24,19.84-6.16,4.14-12.62,7.81-19.32,11v30.72c15.38-3.95,29.9-10,43.32-17.75v-43.81h0ZM768.09,179.57c-1.05,40.55-16.03,77.6-40.32,106.62-.99,1.19-2.07,2.38-3.09,3.54v47.32c16.36-10.96,31.06-24.34,43.41-39.63v-117.85h0ZM490.65,272.02h-25.61c12.59,11.22,27.24,19.89,43.13,25.53-5.24-6.48-10.13-13.32-14.52-20.45-1.03-1.68-2.03-3.37-3.01-5.08M551.5,58.5c-2.19,2.49-4.32,5.04-6.37,7.65-2.25,2.88-4.41,5.82-6.48,8.83-10.7-2.08-22.18-3.15-30.46-2.64v-21.54c13.91-4.92,28.56-7.43,43.31-7.42,0,0,0,15.11,0,15.11Z" style="fill: #bed4e1;"></path><path d="M508.18,50.81v-14.55c1.74-.83,3.5-1.62,5.27-2.38,2.43-1.03,4.89-2,7.37-2.9,2.47-.91,4.97-1.75,7.48-2.53.54-.17,7.59-2.37,8.13-2.53,0,0-14.16,8.97-28.25,24.89M594.82,0h.05c14.86,0,29.5,1.93,43.26,5.44-15.17,3.93-29.74,9.89-43.32,17.72V0ZM681.46,67.01c-7.3-7.41-15.34-14.06-24-19.84-6.16-4.14-12.62-7.81-19.32-11V5.44c15.38,3.95,29.9,10,43.32,17.75v43.81ZM768.09,168.79c-1.05-40.55-16.03-77.6-40.32-106.62-.99-1.19-2.07-2.38-3.09-3.54V11.31c16.36,10.96,31.06,24.34,43.41,39.63h0s0,0,0,0v117.85h0ZM490.65,76.34h-25.61c12.59-11.22,27.24-19.89,43.13-25.53-5.24,6.48-10.13,13.32-14.52,20.45-1.03,1.68-2.03,3.37-3.01,5.08M508.18,297.55v14.5c1.74.83,3.5,1.62,5.27,2.38,2.42,1.04,4.88,1.99,7.37,2.9,2.47.91,4.97,1.75,7.48,2.53.54.17,7.59,2.37,8.13,2.53l-28.25-24.85h0Z" style="fill: #bed4e1;"></path><path d="M573.26,326.75c7.28,0,14.55-.56,21.56-1.55-10.4-6.02-20.23-13.05-29.12-21.02-4.71.52-9.45.78-14.2.79v20.2c7.21,1.05,14.48,1.57,21.76,1.58M638.14,271.83c-12.62,11.31-27.34,20.05-43.32,25.71v27.66c15.01-2.13,29.62-6.51,43.32-13v-40.36h0ZM681.46,281.35v43.81c16.3-9.42,30.84-21.41,43.23-35.43v-106.75c-.11,2.21.21,4.4,0,6.59-3.39,35.62-19.51,67.65-43.23,91.78M573.26,21.61c7.28,0,14.55.56,21.56,1.55-10.4,6.02-20.23,13.05-29.12,21.02-4.71-.52-9.45-.78-14.2-.79v-20.2c7.21-1.04,14.48-1.57,21.76-1.58" style="fill: #00b289;"></path><path d="M638.14,76.53c-12.62-11.32-27.34-20.05-43.32-25.71v-27.66c15.01,2.13,29.62,6.51,43.32,13v40.36ZM681.46,67.01V23.2c16.3,9.42,30.84,21.41,43.23,35.43v106.75c-.11-2.21.21-4.41,0-6.59-3.39-35.62-19.51-67.65-43.23-91.78M811.33,173.34c0-46.36-16.2-88.94-43.23-122.4v246.48c27.03-33.46,43.23-76.03,43.23-122.4,0-.28-.02-.56-.02-.84s.02-.56.02-.84" style="fill: #00b289;"></path><path d="M325.99,202.77h14.95v-57.07h-14.95v57.07ZM187.68,183.08l12.11-17.94,12.11,17.94h-24.22ZM198.19,145.7l-42.3,57.07h18.49l6.64-9.83h37.53l6.64,9.83h18.49l-42.3-57.07h-3.2,0ZM593.56,145.7v34.18l-54.68-34.18h-3.86v57.07h14.95v-34.52l55.06,34.52h3.48v-57.07h-14.95ZM271.32,182.5l-25.4-36.8h-18.49l42.29,57.07h3.2l42.29-57.07h-18.49l-25.4,36.8ZM377.25,157.71h31.75c1.98,0,3.68.69,5.11,2.06,1.42,1.37,2.14,3.16,2.14,5.35s-.71,3.9-2.14,5.27c-1.43,1.37-3.13,2.06-5.11,2.06h-31.75v-14.74ZM415.66,202.77h17.49l-15.26-20.57c2.55-.85,4.84-2.03,6.79-3.62,4.2-3.42,6.3-8.22,6.3-14.41s-2.1-10.46-6.3-13.71c-4.2-3.25-9.78-4.75-16.75-4.75h-45.64v57.07h14.95v-19.07s25.43,0,25.43,0l12.99,19.07h0ZM518.33,161.6c-1.8-3.65-4.38-6.7-7.73-9.16-3.35-2.45-7.41-4.31-12.19-5.56-4.78-1.26-10.14-1.88-16.1-1.88s-11.33.62-16.14,1.88c-4.81,1.25-8.9,3.11-12.28,5.56-.51.37-.87.84-1.34,1.24l10.6,9.46c.19-.2.35-.41.55-.61,1.16-1.12,2.6-2.1,4.32-2.93,1.71-.84,3.75-1.49,6.11-1.97,2.35-.47,5.09-.7,8.18-.7,4.62,0,8.43.51,11.42,1.53,2.99,1.03,5.36,2.36,7.09,4.01,1.73,1.65,2.94,3.5,3.62,5.56.67,2,1.01,4.1,1.01,6.21,0,2.07-.33,4.14-1.01,6.2-.68,2.06-1.89,3.92-3.62,5.56-1.73,1.65-4.1,2.98-7.09,4-2.99,1.03-6.8,1.54-11.42,1.54-3.1,0-5.83-.23-8.18-.7-2.36-.47-4.39-1.12-6.11-1.94-1.71-.82-3.16-1.79-4.32-2.89-1.11-1.04-2.06-2.24-2.79-3.58-.69-1.26-1.18-2.62-1.47-4.02-.29-1.37-.43-2.76-.43-4.16,0-1.35.14-2.72.43-4.1.09-.43.23-.84.36-1.26h-15.99c-.3,1.77-.46,3.56-.47,5.36,0,4.77.91,8.98,2.74,12.64,1.83,3.65,4.43,6.7,7.81,9.15,3.38,2.45,7.47,4.31,12.28,5.56,4.8,1.26,10.18,1.88,16.14,1.88s11.32-.62,16.1-1.88c4.78-1.25,8.84-3.11,12.19-5.56,3.35-2.45,5.93-5.51,7.73-9.15,1.8-3.65,2.7-7.87,2.7-12.64s-.89-8.98-2.7-12.64" style="fill: #182765;"></path><path d="M84.4,202.77h15.21v-22.44h50.25v-12.14h-50.25v-10.76h50.25v-11.73h-65.46v57.07ZM0,202.77h15.21v-22.44h50.25v-12.14H15.21v-10.76h50.25v-11.73H0v57.07Z" style="fill: #00b289;"></path></svg>
          </label>
        </div>

        <!-- Searchable Dropdown for French Clubs -->
        <div v-if="!isForeignClub" class="autocomplete-wrapper">
          <input
            id="clubAffiliation"
            v-model="clubSearchQuery"
            type="text"
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
          :disabled="loading"
          :placeholder="$t('crew.form.clubPlaceholder')"
        />
        
        <small class="hint">{{ $t('crew.form.clubHint') }}</small>
        <span v-if="errors.club_affiliation" class="error">{{ errors.club_affiliation }}</span>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>

      <!-- Action Buttons -->
      <div class="button-group">
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading">{{ $t('common.loading') }}</span>
          <span v-else>{{ isEdit ? $t('crew.form.update') : $t('crew.form.create') }}</span>
        </button>
        <button type="button" class="btn btn-secondary" @click="handleCancel" :disabled="loading">
          {{ $t('common.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCrewStore } from '../stores/crewStore';
import { useAuthStore } from '../stores/authStore';
import axios from 'axios';
import { calculateAge } from '../utils/raceEligibility';

const props = defineProps({
  crewMember: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['success', 'cancel']);

const { t } = useI18n();
const crewStore = useCrewStore();
const authStore = useAuthStore();

const isEdit = computed(() => !!props.crewMember);

// Get the team manager's club as default
const defaultClub = authStore.user?.club_affiliation || '';

const form = reactive({
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: '',
  license_number: '',
  club_affiliation: defaultClub,
});

const errors = reactive({});
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const warningExpanded = ref(false);

// Club search state
const clubs = ref([]);
const clubSearchQuery = ref('');
const filteredClubs = ref([]);
const showClubDropdown = ref(false);
const isForeignClub = ref(false);

// Initialize form with crew member data if editing
onMounted(async () => {
  // Fetch clubs list
  await fetchClubs();
  
  if (props.crewMember) {
    Object.assign(form, {
      first_name: props.crewMember.first_name,
      last_name: props.crewMember.last_name,
      date_of_birth: props.crewMember.date_of_birth,
      gender: props.crewMember.gender,
      license_number: props.crewMember.license_number,
      club_affiliation: props.crewMember.club_affiliation || '',
    });
    
    // Set club search query to the club name if it exists
    if (form.club_affiliation) {
      clubSearchQuery.value = form.club_affiliation;
    }
  } else {
    // For new crew members, set default club
    clubSearchQuery.value = defaultClub;
  }
});

// Fetch clubs from API
const fetchClubs = async () => {
  try {
    const token = authStore.token;
    const apiUrl = import.meta.env.VITE_API_URL.replace(/\/$/, ''); // Remove trailing slash
    console.log('Fetching clubs from:', `${apiUrl}/clubs`);
    const response = await axios.get(`${apiUrl}/clubs`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    console.log('Clubs response:', response.data);
    clubs.value = response.data.data.clubs || [];
    console.log(`Loaded ${clubs.value.length} clubs`);
  } catch (error) {
    console.error('Error fetching clubs:', error);
    console.error('Error details:', error.response?.data);
    // Don't show error to user, just log it
    // They can still use foreign club checkbox
  }
};

// Handle club focus - show dropdown with initial results
const handleClubFocus = () => {
  showClubDropdown.value = true;
  handleClubSearch();
};

// Handle club search input
const handleClubSearch = () => {
  if (!clubSearchQuery.value) {
    filteredClubs.value = clubs.value.slice(0, 50); // Show first 50 clubs
    return;
  }
  
  const query = clubSearchQuery.value.toLowerCase();
  filteredClubs.value = clubs.value
    .filter(club => {
      const nameMatch = club.name.toLowerCase().includes(query);
      const urlMatch = club.url && club.url.toLowerCase().includes(query);
      return nameMatch || urlMatch;
    })
    .slice(0, 50); // Limit to 50 results for performance
};

// Select a club from dropdown
const selectClub = (club) => {
  form.club_affiliation = club.name;
  clubSearchQuery.value = club.name;
  showClubDropdown.value = false;
};

// Handle blur event on club input
const handleClubBlur = () => {
  // Delay hiding dropdown to allow click events to fire
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
    // Switching to foreign club mode - clear club affiliation
    form.club_affiliation = '';
    clubSearchQuery.value = '';
  } else {
    // Switching back to French club mode
    form.club_affiliation = '';
    clubSearchQuery.value = '';
  }
});

// Validation functions
const validateField = (field) => {
  delete errors[field];

  if (field === 'first_name' && form.first_name.length < 1) {
    errors.first_name = t('crew.validation.firstNameRequired');
  }

  if (field === 'last_name' && form.last_name.length < 1) {
    errors.last_name = t('crew.validation.lastNameRequired');
  }

  if (field === 'date_of_birth') {
    if (!form.date_of_birth) {
      errors.date_of_birth = t('crew.validation.dateOfBirthRequired');
    } else {
      const birthDate = new Date(form.date_of_birth);
      const today = new Date();
      
      // Use the centralized calculateAge function
      const ageThisYear = calculateAge(form.date_of_birth);
      
      // Minimum age is J14 (14 years old)
      const minAge = 14;
      
      // Maximum date is today (can't be born in the future)
      if (birthDate > today) {
        errors.date_of_birth = t('crew.validation.dateInFuture');
      } else if (ageThisYear < minAge) {
        // Too young - will not reach minimum age this year
        const minBirthYear = today.getFullYear() - minAge;
        errors.date_of_birth = t('crew.validation.dateTooOld', { year: minBirthYear });
      }
    }
  }

  if (field === 'license_number') {
    const licenseRegex = /^[A-Z0-9]{6,12}$/i;
    if (!licenseRegex.test(form.license_number)) {
      errors.license_number = t('crew.validation.licenseInvalid');
    }
  }
};

const validateForm = () => {
  // Clear all errors first
  Object.keys(errors).forEach(key => delete errors[key]);
  
  // Validate all fields
  Object.keys(form).forEach(validateField);
  
  console.log('Form validation result:', {
    errors: { ...errors },
    hasErrors: Object.keys(errors).length > 0
  });
  
  return Object.keys(errors).length === 0;
};

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!validateForm()) {
    return;
  }

  // Handle club affiliation before submitting
  if (!isForeignClub.value) {
    // If not foreign club, ensure we have a valid club or use default
    if (!form.club_affiliation || form.club_affiliation.trim() === '') {
      // Empty field → use team manager's club
      form.club_affiliation = defaultClub;
    } else {
      // Check if the entered text matches a valid club
      const matchingClub = clubs.value.find(
        club => club.name.toLowerCase() === form.club_affiliation.toLowerCase()
      );
      if (!matchingClub) {
        // Invalid text → use team manager's club
        form.club_affiliation = defaultClub;
      }
    }
  }

  loading.value = true;

  try {
    if (isEdit.value) {
      await crewStore.updateCrewMember(props.crewMember.crew_member_id, form);
      successMessage.value = t('crew.form.updateSuccess');
    } else {
      await crewStore.createCrewMember(form);
      successMessage.value = t('crew.form.createSuccess');
      
      // Reset form after creation
      Object.keys(form).forEach(key => form[key] = '');
    }

    setTimeout(() => {
      emit('success');
    }, 1500);
  } catch (error) {
    console.error('Crew member form error:', error);
    console.error('Error response:', error.response);
    
    // Try to extract detailed error message
    let detailedError = t('crew.form.error');
    
    if (error.response?.data?.error) {
      const errorData = error.response.data.error;
      
      // Check for specific error codes that need translation
      if (errorData.code === 'DUPLICATE_LICENSE') {
        detailedError = t('crew.validation.licenseDuplicate');
      }
      // Check if it's a validation error with field-specific messages
      else if (typeof errorData === 'object' && !errorData.message) {
        // Format validation errors
        const errorMessages = Object.entries(errorData)
          .map(([field, msg]) => `${field}: ${msg}`)
          .join(', ');
        detailedError = errorMessages;
      } else if (errorData.message) {
        detailedError = errorData.message;
      } else if (typeof errorData === 'string') {
        detailedError = errorData;
      }
    } else if (error.message) {
      detailedError = error.message;
    }
    
    errorMessage.value = detailedError;
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  // Clear error messages when cancelling
  errorMessage.value = '';
  successMessage.value = '';
  emit('cancel');
};
</script>

<style scoped>
/* Mobile-first base styles */
.crew-member-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h3 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
}

/* Mobile-optimized inputs: 16px font to prevent iOS zoom, 44px min height for touch targets */
input, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px; /* Prevents iOS zoom on focus */
  min-height: 44px; /* Touch target minimum */
  box-sizing: border-box;
}

input:focus, select:focus {
  outline: none;
  border-color: #4CAF50;
}

input:disabled, select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.hint {
  display: block;
  color: #666;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.error {
  display: block;
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Mobile: Stack license field and warning vertically */
.license-with-warning {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.license-field {
  display: flex;
  flex-direction: column;
}

.warning-box {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: #fff3e0;
  border: 2px solid #ff9800;
  border-radius: 6px;
  align-items: flex-start;
  height: fit-content;
  cursor: pointer;
  transition: background-color 0.2s;
  min-height: 44px; /* Touch target minimum */
}

.warning-box:hover {
  background-color: #ffe0b2;
}

.warning-icon {
  width: 24px;
  height: 24px;
  color: #ff9800;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.warning-content {
  flex: 1;
}

.warning-content strong {
  display: block;
  color: #e65100;
  font-size: 0.85rem;
  margin-bottom: 0;
  font-weight: 600;
}

.warning-box.expanded .warning-content strong {
  margin-bottom: 0.35rem;
}

.warning-content p {
  color: #e65100;
  font-size: 0.85rem;
  line-height: 1.4;
  margin: 0;
  margin-top: 0.35rem;
}

.expand-icon {
  width: 20px;
  height: 20px;
  color: #ff9800;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.warning-box.expanded .expand-icon {
  transform: rotate(180deg);
}

.alert {
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
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

/* Mobile: Stack buttons vertically */
.button-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 16px; /* Prevents iOS zoom */
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  min-height: 44px; /* Touch target minimum */
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
  min-height: 44px; /* Touch target minimum */
}

.checkbox-group input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.checkbox-label {
  margin-bottom: 0;
  font-weight: normal;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.ffa-logo {
  height: 32px;
  width: auto;
}

.autocomplete-wrapper {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 250px;
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
  min-height: 44px; /* Touch target minimum */
  display: flex;
  align-items: center;
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
  font-size: 0.875rem;
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
  font-size: 0.875rem;
}

/* Tablet and larger: Enhanced layout */
@media (min-width: 768px) {
  .crew-member-form {
    padding: 2rem;
  }

  h3 {
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    font-size: 1rem;
  }

  input, select {
    font-size: 1rem;
  }

  /* Desktop: Side-by-side license and warning */
  .license-with-warning {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    align-items: start;
  }

  .alert {
    padding: 1rem;
    font-size: 1rem;
  }

  /* Desktop: Horizontal button group */
  .button-group {
    flex-direction: row;
    gap: 1rem;
    margin-top: 2rem;
  }

  .btn {
    flex: 1;
    font-size: 1rem;
  }

  .checkbox-label {
    font-size: 1rem;
  }

  .ffa-logo {
    height: 40px;
  }

  .autocomplete-dropdown {
    max-height: 300px;
  }

  .club-name {
    font-size: 1rem;
  }

  .autocomplete-no-results {
    font-size: 1rem;
  }
}
</style>
