<template>
  <div class="profile-view">
    <div class="header">
      <h1>{{ $t('profile.title') }}</h1>
      <p class="subtitle">{{ $t('profile.subtitle') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <span>{{ error }}</span>
      <button @click="error = null" class="btn-close-error">×</button>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <span>{{ successMessage }}</span>
      <button @click="successMessage = null" class="btn-close-success">×</button>
    </div>

    <!-- Profile Form -->
    <div v-if="!loading && profile" class="profile-form">
      <div class="form-section">
        <h2>{{ $t('profile.personalInfo') }}</h2>
        
        <div class="form-group">
          <label for="firstName">{{ $t('profile.firstName') }}</label>
          <input
            id="firstName"
            v-model="profile.first_name"
            type="text"
            class="form-input"
            :placeholder="$t('profile.firstName')"
          />
        </div>

        <div class="form-group">
          <label for="lastName">{{ $t('profile.lastName') }}</label>
          <input
            id="lastName"
            v-model="profile.last_name"
            type="text"
            class="form-input"
            :placeholder="$t('profile.lastName')"
          />
        </div>

        <div class="form-group">
          <label for="email">{{ $t('profile.email') }}</label>
          <input
            id="email"
            v-model="profile.email"
            type="email"
            class="form-input"
            disabled
            :title="$t('profile.emailReadonly')"
          />
          <p class="field-hint">{{ $t('profile.emailReadonly') }}</p>
        </div>
      </div>

      <div class="form-section">
        <h2>{{ $t('profile.clubInfo') }}</h2>
        
        <div class="form-group">
          <label for="clubAffiliation">{{ $t('profile.clubAffiliation') }}</label>
          
          <!-- Foreign Club Checkbox -->
          <div class="checkbox-group">
            <input
              id="foreignClub"
              v-model="isForeignClub"
              type="checkbox"
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
              class="form-input"
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
            v-model="profile.club_affiliation"
            type="text"
            class="form-input"
            :placeholder="$t('profile.clubAffiliation')"
          />
        </div>

        <div class="form-group">
          <label for="mobileNumber">{{ $t('profile.mobileNumber') }}</label>
          <input
            id="mobileNumber"
            v-model="profile.mobile_number"
            type="tel"
            class="form-input"
            :placeholder="$t('profile.mobileHint')"
          />
          <p class="field-hint">{{ $t('profile.mobileHint') }}</p>
        </div>
      </div>

      <div class="form-actions">
        <button @click="saveProfile" :disabled="saving" class="btn-primary">
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const authStore = useAuthStore()
const { t } = useI18n()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const successMessage = ref(null)
const profile = ref(null)

// Club search state
const clubs = ref([])
const clubSearchQuery = ref('')
const filteredClubs = ref([])
const showClubDropdown = ref(false)
const isForeignClub = ref(false)

// Fetch clubs from API
const fetchClubs = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL.replace(/\/$/, '')
    const response = await axios.get(`${apiUrl}/clubs`)
    clubs.value = response.data.data.clubs || []
    filteredClubs.value = clubs.value.slice(0, 50)
  } catch (err) {
    console.error('Error fetching clubs:', err)
  }
}

// Handle club focus
const handleClubFocus = () => {
  showClubDropdown.value = true
  handleClubSearch()
}

// Handle club search
const handleClubSearch = () => {
  if (!clubSearchQuery.value) {
    filteredClubs.value = clubs.value.slice(0, 50)
    showClubDropdown.value = true
    return
  }
  
  const query = clubSearchQuery.value.toLowerCase()
  filteredClubs.value = clubs.value
    .filter(club => {
      const nameMatch = club.name.toLowerCase().includes(query)
      const urlMatch = club.url && club.url.toLowerCase().includes(query)
      return nameMatch || urlMatch
    })
    .slice(0, 50)
  
  showClubDropdown.value = true
}

// Select a club
const selectClub = (club) => {
  profile.value.club_affiliation = club.name
  clubSearchQuery.value = club.name
  showClubDropdown.value = false
}

// Handle blur
const handleClubBlur = () => {
  setTimeout(() => {
    showClubDropdown.value = false
  }, 200)
}

const loadProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Get profile from auth store
    await authStore.fetchProfile()
    profile.value = { ...authStore.user }
    
    // Initialize club search query with current club
    if (profile.value.club_affiliation) {
      clubSearchQuery.value = profile.value.club_affiliation
    }
  } catch (err) {
    error.value = err.message || t('profile.loadError')
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  error.value = null
  successMessage.value = null
  
  try {
    await authStore.updateProfile({
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      club_affiliation: profile.value.club_affiliation,
      mobile_number: profile.value.mobile_number
    })
    
    successMessage.value = t('profile.saveSuccess')
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err) {
    error.value = err.message || t('profile.saveError')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchClubs()
  await loadProfile()
})
</script>

<style scoped>
.profile-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.subtitle {
  color: #666;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-message,
.success-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.error-message {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
}

.success-message {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.btn-close-error,
.btn-close-success {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  margin-left: 1rem;
  line-height: 1;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-error {
  color: #c33;
}

.btn-close-error:hover {
  color: #a00;
}

.btn-close-success {
  color: #155724;
}

.btn-close-success:hover {
  color: #0c3d1a;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e0e0e0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-input:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.field-hint {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
  color: #666;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.checkbox-label {
  margin: 0;
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
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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

.club-name {
  font-weight: 500;
  color: #333;
}

.autocomplete-no-results {
  padding: 1rem;
  text-align: center;
  color: #999;
  font-style: italic;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  padding: 0.75rem 2rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .profile-view {
    padding: 1rem;
  }

  .form-section {
    padding: 1.5rem;
  }

  .form-actions {
    padding: 1rem;
  }
}
</style>
