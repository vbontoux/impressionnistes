<template>
  <div class="admin-license-checker">
    <ListHeader
      :title="$t('admin.licenseChecker.title')"
      :subtitle="$t('admin.licenseChecker.subtitle')"
    />

    <!-- Cookie Configuration -->
    <div class="cookie-config-section">
      <h3>{{ $t('admin.licenseChecker.cookieConfig') }}</h3>
      <p class="help-text">{{ $t('admin.licenseChecker.cookieHelp') }}</p>
      
      <!-- Link to FFAviron -->
      <div class="ffaviron-link">
        <a href="https://intranet.ffaviron.fr/licences/recherche" target="_blank" rel="noopener noreferrer" class="external-link">
          🔗 {{ $t('admin.licenseChecker.openFFAviron') }}
        </a>
      </div>
      
      <!-- Cookie Example -->
      <div class="cookie-example">
        <p class="example-label">{{ $t('admin.licenseChecker.cookieExample') }}</p>
        <div class="example-box">
          <code class="cookie-header">Cookie: </code>
          <code class="cookie-value">{{ $t('admin.licenseChecker.cookieExampleValue') }}</code>
        </div>
        <p class="example-hint">
          <strong>→</strong> {{ $t('admin.licenseChecker.cookieHelpText') }}
        </p>
      </div>
      
      <FormGroup
        :label="$t('admin.licenseChecker.cookieLabel')"
        :required="true"
      >
        <textarea
          v-model="cookieString"
          rows="3"
          :placeholder="$t('admin.licenseChecker.cookiePlaceholder')"
          class="cookie-input"
        />
      </FormGroup>
    </div>

    <!-- Filters -->
    <ListFilters
      v-model:searchQuery="searchTerm"
      :searchPlaceholder="$t('admin.licenseChecker.searchPlaceholder')"
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('admin.licenseChecker.filterByTeamManager') }}&nbsp;:</label>
          <select v-model="filterTeamManager" class="filter-select">
            <option value="">{{ $t('admin.crewMembers.allTeamManagers') }}</option>
            <option v-for="tm in teamManagers" :key="tm.id" :value="tm.id">
              {{ tm.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.licenseChecker.filterByStatus') }}&nbsp;:</label>
          <select v-model="statusFilter" class="filter-select">
            <option value="all">{{ $t('admin.licenseChecker.allStatuses') }}</option>
            <option value="unchecked">{{ $t('admin.licenseChecker.unchecked') }}</option>
            <option value="valid">{{ $t('admin.licenseChecker.valid') }}</option>
            <option value="invalid">{{ $t('admin.licenseChecker.invalid') }}</option>
            <option value="error">{{ $t('admin.licenseChecker.error') }}</option>
          </select>
        </div>
      </template>
    </ListFilters>

    <!-- Bulk Actions -->
    <div class="bulk-actions-section">
      <div class="selection-info">
        <label class="checkbox-label">
          <input
            type="checkbox"
            :checked="allFilteredSelected"
            :indeterminate.prop="someFilteredSelected"
            @change="toggleSelectAllFiltered"
          />
          <span>
            {{ selectedCount > 0 
              ? $t('admin.licenseChecker.selectedCount', { count: selectedCount })
              : $t('admin.licenseChecker.selectAll')
            }}
          </span>
        </label>
      </div>

      <div class="action-buttons">
        <BaseButton
          variant="primary"
          size="medium"
          :disabled="selectedCount === 0 || !cookieString || checking"
          :loading="checking"
          @click="checkSelectedLicenses"
        >
          {{ checking 
            ? $t('admin.licenseChecker.checking') 
            : $t('admin.licenseChecker.checkSelected', { count: selectedCount })
          }}
        </BaseButton>

        <BaseButton
          variant="success"
          size="medium"
          :disabled="selectedCount === 0 || checking || saving"
          @click="markSelectedAsValid"
        >
          {{ $t('admin.licenseChecker.markAsValid') }}
        </BaseButton>

        <BaseButton
          variant="danger"
          size="medium"
          :disabled="selectedCount === 0 || checking || saving"
          @click="markSelectedAsInvalid"
        >
          {{ $t('admin.licenseChecker.markAsInvalid') }}
        </BaseButton>

        <BaseButton
          variant="primary"
          size="medium"
          :disabled="!hasUnsavedChanges || checking || saving"
          :loading="saving"
          @click="saveVerificationStatus"
        >
          {{ saving 
            ? $t('common.saving') 
            : $t('common.save')
          }}
        </BaseButton>

        <BaseButton
          variant="secondary"
          size="medium"
          :disabled="selectedCount === 0"
          @click="clearSelection"
        >
          {{ $t('admin.licenseChecker.clearSelection') }}
        </BaseButton>

        <BaseButton
          variant="secondary"
          size="medium"
          :disabled="selectedCount === 0"
          @click="emailSelected"
        >
          {{ $t('admin.licenseChecker.emailSelected') }}
        </BaseButton>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="checking" class="progress-section">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <p class="progress-text">
        {{ $t('admin.licenseChecker.progress', { 
          current: checkProgress.current, 
          total: checkProgress.total 
        }) }}
      </p>
    </div>

    <!-- Messages -->
    <MessageAlert
      v-if="errorMessage"
      type="error"
      :message="errorMessage"
      :dismissible="true"
      @dismiss="errorMessage = ''"
    />

    <MessageAlert
      v-if="successMessage"
      type="success"
      :message="successMessage"
      :dismissible="true"
      :auto-dismiss="true"
      @dismiss="successMessage = ''"
    />

    <!-- Loading state -->
    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <!-- Crew members table -->
    <div v-if="!loading && !error" class="license-table-container">
      <p class="count">
        {{ $t('admin.licenseChecker.totalCount', { count: filteredCrewMembers.length }) }}
      </p>
      
      <table class="license-table">
        <thead>
          <tr>
            <th class="checkbox-column">
              <input
                type="checkbox"
                :checked="allFilteredSelected"
                :indeterminate.prop="someFilteredSelected"
                @change="toggleSelectAllFiltered"
              />
            </th>
            <th @click="sortBy('last_name')" class="sortable">
              {{ $t('crew.form.lastName') }}
              <span v-if="sortField === 'last_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('crew.form.licenseNumber') }}</th>
            <th @click="sortBy('club_affiliation')" class="sortable">
              {{ $t('crew.card.club') }}
              <span v-if="sortField === 'club_affiliation'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('crew.card.assigned') }}</th>
            <th @click="sortBy('team_manager_name')" class="sortable">
              {{ $t('admin.crewMembers.teamManager') }}
              <span v-if="sortField === 'team_manager_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('admin.licenseChecker.status') }}</th>
            <th>{{ $t('admin.licenseChecker.details') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="crew in filteredCrewMembers" 
            :key="crew.crew_member_id"
            :class="{ 
              'checking': crew._checking,
              'valid': crew._licenseStatus === 'valid',
              'invalid': crew._licenseStatus === 'invalid',
              'error': crew._licenseStatus === 'error'
            }"
          >
            <td class="checkbox-column">
              <input
                type="checkbox"
                :checked="selectedMembers.has(crew.crew_member_id)"
                @change="toggleSelection(crew.crew_member_id)"
                :disabled="checking"
              />
            </td>
            <td>
              <div class="name-cell">
                <strong>{{ crew.first_name }} {{ crew.last_name }}</strong>
              </div>
            </td>
            <td>
              <span class="license-number">{{ crew.license_number || '-' }}</span>
            </td>
            <td>
              <span class="club-box">{{ crew.club_affiliation || crew.team_manager_club || '-' }}</span>
            </td>
            <td>
              <span v-if="crew.assigned_boat_id" class="badge badge-assigned">
                {{ $t('crew.card.assigned') }}
              </span>
              <span v-else class="badge badge-unassigned">
                {{ $t('crew.card.unassigned') }}
              </span>
            </td>
            <td>
              <div class="team-manager-info">
                <div>{{ crew.team_manager_name }}</div>
              </div>
            </td>
            <td>
              <!-- Show temporary check status if exists (fresh check takes priority) -->
              <div v-if="crew._licenseStatus" class="verification-status">
                <span v-if="crew._checking" class="status-badge status-checking">
                  {{ $t('admin.licenseChecker.checking') }}...
                </span>
                <span v-else-if="crew._licenseStatus === 'valid'" class="status-badge status-valid">
                  ✓ {{ $t('admin.licenseChecker.valid') }}
                </span>
                <span v-else-if="crew._licenseStatus === 'invalid'" class="status-badge status-invalid">
                  ✗ {{ $t('admin.licenseChecker.invalid') }}
                </span>
                <span v-else-if="crew._licenseStatus === 'error'" class="status-badge status-error">
                  ⚠ {{ $t('admin.licenseChecker.error') }}
                </span>
                <span v-if="unsavedChanges.has(crew.crew_member_id)" class="status-unsaved">
                  {{ $t('admin.licenseChecker.unsaved') }}
                </span>
              </div>
              <!-- Show DB status if no fresh check -->
              <div v-else-if="crew.license_verification_status" class="verification-status">
                <span :class="['status-badge', getVerificationStatusClass(crew.license_verification_status)]">
                  {{ getVerificationStatusLabel(crew.license_verification_status) }}
                </span>
                <span class="verification-method">
                  {{ crew.license_verification_status.startsWith('manually_') 
                    ? $t('admin.licenseChecker.manual') 
                    : $t('admin.licenseChecker.auto') 
                  }}
                </span>
              </div>
              <!-- Show "Not verified" if neither exists -->
              <span v-else class="status-badge status-unchecked">
                {{ $t('admin.licenseChecker.unchecked') }}
              </span>
            </td>
            <td>
              <!-- Show temporary check details if exists (fresh check takes priority) -->
              <div v-if="crew._licenseDetails" class="details-cell">
                {{ crew._licenseDetails }}
              </div>
              <!-- Show DB details if no fresh check -->
              <div v-else-if="crew.license_verification_status" class="details-cell">
                <div>{{ crew.license_verification_details || '-' }}</div>
                <div v-if="crew.license_verification_date" class="verification-meta">
                  {{ formatDate(crew.license_verification_date) }}
                </div>
              </div>
              <!-- Show dash if neither exists -->
              <div v-else class="details-cell">
                -
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination removed - using filters only -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ListHeader from '@/components/shared/ListHeader.vue'
import ListFilters from '@/components/shared/ListFilters.vue'
import FormGroup from '@/components/composite/FormGroup.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import MessageAlert from '@/components/composite/MessageAlert.vue'
import LoadingSpinner from '@/components/base/LoadingSpinner.vue'
import { checkLicense } from '@/utils/licenseChecker'
import adminService from '@/services/adminService'

const { t } = useI18n()

// State
const loading = ref(false)
const checking = ref(false)
const saving = ref(false)
const error = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const cookieString = ref(localStorage.getItem('ffaviron_cookie') || '')

// Watch cookieString and save to localStorage
watch(cookieString, (newValue) => {
  if (newValue) {
    localStorage.setItem('ffaviron_cookie', newValue)
  } else {
    localStorage.removeItem('ffaviron_cookie')
  }
})

const crewMembers = ref([])
const selectedMembers = ref(new Set())
const checkProgress = ref({ current: 0, total: 0 })
const unsavedChanges = ref(new Map()) // Track unsaved verification changes

// Filters
const searchTerm = ref('')
const filterTeamManager = ref('')
const statusFilter = ref('all')

// Sorting
const sortField = ref('last_name')
const sortDirection = ref('asc')

// Pagination removed - using filters only

// Computed
const teamManagers = computed(() => {
  const managers = new Map()
  crewMembers.value.forEach(crew => {
    if (crew.team_manager_id && crew.team_manager_name) {
      managers.set(crew.team_manager_id, {
        id: crew.team_manager_id,
        name: crew.team_manager_name
      })
    }
  })
  return Array.from(managers.values()).sort((a, b) => a.name.localeCompare(b.name))
})

const filteredCrewMembers = computed(() => {
  let filtered = crewMembers.value

  // Search filter
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(crew =>
      crew.first_name?.toLowerCase().includes(search) ||
      crew.last_name?.toLowerCase().includes(search) ||
      crew.license_number?.toLowerCase().includes(search) ||
      crew.team_manager_name?.toLowerCase().includes(search)
    )
  }

  // Team manager filter
  if (filterTeamManager.value) {
    filtered = filtered.filter(crew => crew.team_manager_id === filterTeamManager.value)
  }

  // Status filter
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(crew => {
      if (statusFilter.value === 'unchecked') {
        // Unchecked means no fresh check AND no DB verification
        return !crew._licenseStatus && !crew.license_verification_status
      }
      
      // For valid/invalid/error, check both fresh status and DB status
      if (statusFilter.value === 'valid') {
        return crew._licenseStatus === 'valid' || 
               crew.license_verification_status === 'verified_valid' ||
               crew.license_verification_status === 'manually_verified_valid'
      }
      
      if (statusFilter.value === 'invalid') {
        return crew._licenseStatus === 'invalid' || 
               crew.license_verification_status === 'verified_invalid' ||
               crew.license_verification_status === 'manually_verified_invalid'
      }
      
      if (statusFilter.value === 'error') {
        return crew._licenseStatus === 'error'
      }
      
      return crew._licenseStatus === statusFilter.value
    })
  }

  // Sort
  filtered.sort((a, b) => {
    let aVal = a[sortField.value] || ''
    let bVal = b[sortField.value] || ''
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return filtered
})

// No pagination - show all filtered results

const selectedCount = computed(() => selectedMembers.value.size)

const allSelected = computed(() => {
  return crewMembers.value.length > 0 && selectedMembers.value.size === crewMembers.value.length
})

const someSelected = computed(() => {
  return selectedMembers.value.size > 0 && selectedMembers.value.size < crewMembers.value.length
})

const allFilteredSelected = computed(() => {
  return filteredCrewMembers.value.length > 0 && 
    filteredCrewMembers.value.every(crew => selectedMembers.value.has(crew.crew_member_id))
})

const someFilteredSelected = computed(() => {
  const selectedFiltered = filteredCrewMembers.value.filter(crew => 
    selectedMembers.value.has(crew.crew_member_id)
  )
  return selectedFiltered.length > 0 && selectedFiltered.length < filteredCrewMembers.value.length
})

const progressPercentage = computed(() => {
  if (checkProgress.value.total === 0) return 0
  return Math.round((checkProgress.value.current / checkProgress.value.total) * 100)
})

const hasUnsavedChanges = computed(() => {
  return unsavedChanges.value.size > 0
})

// Methods
const loadCrewMembers = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await adminService.listAllCrewMembers()
    console.log('API Response:', response) // Debug log
    
    if (!response || !response.crew_members) {
      console.error('Invalid response structure:', response)
      error.value = 'Invalid response from server'
      return
    }
    
    crewMembers.value = response.crew_members.map(crew => ({
      ...crew,
      _licenseStatus: null,
      _licenseDetails: null,
      _checking: false
    }))
    
    console.log('Loaded crew members:', crewMembers.value.length) // Debug log
  } catch (err) {
    console.error('Failed to load crew members:', err)
    error.value = err.response?.data?.message || t('admin.licenseChecker.loadError')
  } finally {
    loading.value = false
  }
}

const toggleSelection = (crewMemberId) => {
  if (selectedMembers.value.has(crewMemberId)) {
    selectedMembers.value.delete(crewMemberId)
  } else {
    selectedMembers.value.add(crewMemberId)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedMembers.value.clear()
  } else {
    crewMembers.value.forEach(crew => {
      selectedMembers.value.add(crew.crew_member_id)
    })
  }
}

const toggleSelectAllFiltered = () => {
  if (allFilteredSelected.value) {
    filteredCrewMembers.value.forEach(crew => {
      selectedMembers.value.delete(crew.crew_member_id)
    })
  } else {
    filteredCrewMembers.value.forEach(crew => {
      selectedMembers.value.add(crew.crew_member_id)
    })
  }
}

const clearSelection = () => {
  selectedMembers.value.clear()
}

const emailSelected = () => {
  const selectedCrew = filteredCrewMembers.value.filter(
    c => selectedMembers.value.has(c.crew_member_id)
  )
  
  if (selectedCrew.length === 0) return
  
  // Prevent double-triggering
  if (emailSelected.processing) return
  emailSelected.processing = true
  
  setTimeout(() => {
    emailSelected.processing = false
  }, 1000)
  
  // Group by club (using team_manager_club from backend)
  const crewByClub = {}
  selectedCrew.forEach(crew => {
    const club = crew.team_manager_club || crew.club_affiliation || 'Club non spécifié / Club not specified'
    if (!crewByClub[club]) {
      crewByClub[club] = []
    }
    crewByClub[club].push(crew)
  })
  
  // Sort clubs alphabetically
  const sortedClubs = Object.keys(crewByClub).sort()
  
  // Build French section
  let body = "Bonjour,\n\n"
  body += "Veuillez vérifier les licences FFAviron suivantes pour vos équipiers :\n\n"
  
  sortedClubs.forEach(club => {
    body += `${club}\n`
    crewByClub[club].forEach(crew => {
      body += `- ${crew.first_name} ${crew.last_name} - Licence: ${crew.license_number || 'N/A'}`
      
      // Add verification details if available (check fresh check first, then DB)
      const details = crew._licenseDetails || crew.license_verification_details
      if (details) {
        body += `\n  Détails: ${details}`
      }
      body += "\n"
    })
    body += "\n"
  })
  
  body += "Merci d'ajuster les noms et numéros de licences conformément à ce qui est enregistré sur le site intranet de la fédération.\n\n"
  body += "Vous pouvez vérifier les licences sur :\n"
  body += "https://intranet.ffaviron.fr/licences/recherche\n\n"
  body += "Merci,\nL'équipe d'organisation des Impressionnistes\n\n"
  
  // Build English section
  body += "---\n\nHello,\n\n"
  body += "Please verify the following FFAviron licenses for your crew members:\n\n"
  
  sortedClubs.forEach(club => {
    body += `${club}\n`
    crewByClub[club].forEach(crew => {
      body += `- ${crew.first_name} ${crew.last_name} - License: ${crew.license_number || 'N/A'}`
      
      // Add verification details if available (check fresh check first, then DB)
      const details = crew._licenseDetails || crew.license_verification_details
      if (details) {
        body += `\n  Details: ${details}`
      }
      body += "\n"
    })
    body += "\n"
  })
  
  body += "Please adjust names and license numbers according to what is registered on the federation's intranet site.\n\n"
  body += "You can verify licenses at:\n"
  body += "https://intranet.ffaviron.fr/licences/recherche\n\n"
  body += "Thank you,\nThe Impressionnistes organizing team"
  
  // Get unique emails for BCC
  const emails = [...new Set(
    selectedCrew
      .map(c => c.team_manager_email)
      .filter(e => e)
  )]
  
  if (emails.length === 0) {
    errorMessage.value = t('admin.licenseChecker.noEmailsFound')
    return
  }
  
  const subject = "Vérification des licences FFAviron requise / FFAviron License Verification Required"
  
  window.location.href = `mailto:?bcc=${encodeURIComponent(emails.join(','))}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}

const checkSelectedLicenses = async () => {
  if (!cookieString.value.trim()) {
    errorMessage.value = t('admin.licenseChecker.cookieRequired')
    return
  }

  if (selectedCount.value === 0) {
    errorMessage.value = t('admin.licenseChecker.noSelection')
    return
  }

  checking.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  const selectedCrewMembers = crewMembers.value.filter(crew => 
    selectedMembers.value.has(crew.crew_member_id)
  )

  checkProgress.value = {
    current: 0,
    total: selectedCrewMembers.length
  }

  let validCount = 0
  let invalidCount = 0
  let errorCount = 0

  for (const crew of selectedCrewMembers) {
    crew._checking = true
    
    try {
      const result = await checkLicense(
        `${crew.first_name} ${crew.last_name}`,
        crew.license_number,
        cookieString.value,
        t
      )
      
      crew._licenseStatus = result.valid ? 'valid' : 'invalid'
      crew._licenseDetails = result.details
      
      // Track this as an unsaved change
      unsavedChanges.value.set(crew.crew_member_id, {
        team_manager_id: crew.team_manager_id,
        crew_member_id: crew.crew_member_id,
        status: result.valid ? 'verified_valid' : 'verified_invalid',
        details: result.details
      })
      
      if (result.valid) {
        validCount++
      } else {
        invalidCount++
      }
    } catch (err) {
      crew._licenseStatus = 'error'
      crew._licenseDetails = err.message
      errorCount++
      // Don't add errors to unsaved changes - they need manual review
    } finally {
      crew._checking = false
      checkProgress.value.current++
    }

    // Small delay to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 500))
  }

  checking.value = false
  successMessage.value = t('admin.licenseChecker.checkComplete', {
    valid: validCount,
    invalid: invalidCount,
    error: errorCount
  })
}

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const clearFilters = () => {
  searchTerm.value = ''
  filterTeamManager.value = ''
  statusFilter.value = 'all'
}

const markSelectedAsValid = () => {
  const selectedCrewMembers = crewMembers.value.filter(crew => 
    selectedMembers.value.has(crew.crew_member_id)
  )

  console.log('Marking as valid:', selectedCrewMembers.length, 'members')

  selectedCrewMembers.forEach(crew => {
    crew._licenseStatus = 'valid'
    crew._licenseDetails = t('admin.licenseChecker.manuallyMarkedValid')
    
    // Track this change for saving
    unsavedChanges.value.set(crew.crew_member_id, {
      team_manager_id: crew.team_manager_id,
      crew_member_id: crew.crew_member_id,
      status: 'manually_verified_valid',
      details: t('admin.licenseChecker.manuallyMarkedValid')
    })
  })

  console.log('Unsaved changes size:', unsavedChanges.value.size)
  console.log('Has unsaved changes:', hasUnsavedChanges.value)

  successMessage.value = t('admin.licenseChecker.markedAsValid', { count: selectedCrewMembers.length })
}

const markSelectedAsInvalid = () => {
  const selectedCrewMembers = crewMembers.value.filter(crew => 
    selectedMembers.value.has(crew.crew_member_id)
  )

  selectedCrewMembers.forEach(crew => {
    crew._licenseStatus = 'invalid'
    crew._licenseDetails = t('admin.licenseChecker.manuallyMarkedInvalid')
    
    // Track this change for saving
    unsavedChanges.value.set(crew.crew_member_id, {
      team_manager_id: crew.team_manager_id,
      crew_member_id: crew.crew_member_id,
      status: 'manually_verified_invalid',
      details: t('admin.licenseChecker.manuallyMarkedInvalid')
    })
  })

  successMessage.value = t('admin.licenseChecker.markedAsInvalid', { count: selectedCrewMembers.length })
}

const saveVerificationStatus = async () => {
  if (unsavedChanges.value.size === 0) {
    return
  }

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // Convert unsaved changes to array
    const verifications = Array.from(unsavedChanges.value.values())

    // Call bulk update API
    const response = await adminService.bulkUpdateLicenseVerification(verifications)

    // Clear unsaved changes
    unsavedChanges.value.clear()

    // Show success message
    successMessage.value = t('admin.licenseChecker.saveSuccess', {
      success: response.success_count,
      total: verifications.length
    })

    // If there were failures, show them
    if (response.failure_count > 0) {
      errorMessage.value = t('admin.licenseChecker.savePartialFailure', {
        failed: response.failure_count
      })
    }
  } catch (err) {
    console.error('Failed to save verification status:', err)
    errorMessage.value = err.response?.data?.message || t('admin.licenseChecker.saveError')
    
    // Keep status as "not verified" on error (don't update UI)
    // The unsaved changes remain so user can retry
  } finally {
    saving.value = false
  }
}

// Helper methods for verification status display
const getVerificationStatusClass = (status) => {
  if (!status) return 'status-unchecked'
  
  if (status === 'verified_valid' || status === 'manually_verified_valid') {
    return 'status-valid'
  }
  if (status === 'verified_invalid' || status === 'manually_verified_invalid') {
    return 'status-invalid'
  }
  
  return 'status-unchecked'
}

const getVerificationStatusLabel = (status) => {
  if (!status) return t('admin.licenseChecker.unchecked')
  
  if (status === 'verified_valid' || status === 'manually_verified_valid') {
    return '✓ ' + t('admin.licenseChecker.valid')
  }
  if (status === 'verified_invalid' || status === 'manually_verified_invalid') {
    return '✗ ' + t('admin.licenseChecker.invalid')
  }
  
  return t('admin.licenseChecker.unchecked')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (err) {
    return dateString
  }
}

// Lifecycle
onMounted(() => {
  loadCrewMembers()
})
</script>

<style scoped>
.admin-license-checker {
  padding: var(--spacing-lg);
  max-width: 100%;
  margin: 0 auto;
}

.cookie-config-section {
  background: var(--color-light);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.cookie-config-section h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
}

.help-text {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.ffaviron-link {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: #e3f2fd;
  border: 1px solid #2196f3;
  border-radius: 6px;
}

.external-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
}

.external-link:hover {
  text-decoration: underline;
}

.cookie-example {
  background: #f8f9fa;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.example-label {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
}

.example-box {
  background: white;
  border: 2px solid var(--color-primary);
  border-radius: 4px;
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  font-family: monospace;
  font-size: var(--font-size-sm);
  overflow-x: auto;
  white-space: nowrap;
}

.cookie-header {
  color: var(--color-muted);
  font-weight: var(--font-weight-normal);
}

.cookie-value {
  background: #fff3cd;
  padding: 2px 4px;
  border-radius: 3px;
  color: var(--color-dark);
  font-weight: var(--font-weight-semibold);
}

.example-hint {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-muted);
  font-style: italic;
}

.example-hint strong {
  color: var(--color-primary);
  font-style: normal;
}

.cookie-input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-family: monospace;
  font-size: var(--font-size-sm);
  resize: vertical;
}

.bulk-actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--color-light);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
}

.selection-info {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-weight: var(--font-weight-medium);
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
}

.progress-section {
  margin-bottom: var(--spacing-lg);
}

.progress-bar {
  width: 100%;
  height: 24px;
  background: var(--color-light);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  margin: 0;
}

.count {
  margin-bottom: var(--spacing-md);
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.license-table-container {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--spacing-lg);
  overflow-x: auto;
}

.license-table {
  width: 100%;
  border-collapse: collapse;
}

.license-table th {
  text-align: left;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 2px solid var(--color-border);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  white-space: nowrap;
}

.license-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.license-table th.sortable:hover {
  background: var(--color-light);
}

.license-table th.checkbox-column {
  width: 40px;
  text-align: center;
}

.license-table td {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.license-table td.checkbox-column {
  text-align: center;
}

.license-table tbody tr {
  transition: background-color 0.2s;
}

.license-table tbody tr:hover {
  background: var(--color-light);
}

.license-table tbody tr.checking {
  background: #fff9e6;
}

.license-table tbody tr.valid {
  background: #f0f9f4;
}

.license-table tbody tr.invalid {
  background: #fef2f2;
}

.license-table tbody tr.error {
  background: #fff4e6;
}

.name-cell strong {
  color: var(--color-dark);
}

.license-number {
  font-family: monospace;
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.club-box {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: var(--color-light);
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.team-manager-info {
  font-size: var(--font-size-sm);
}

.status-badge {
  display: inline-block;
  padding: var(--badge-padding);
  border-radius: var(--badge-border-radius);
  font-size: var(--badge-font-size);
  font-weight: var(--font-weight-medium);
  width: fit-content;
}

.status-unchecked {
  background: var(--color-light);
  color: var(--color-muted);
}

.status-checking {
  background: #fff9e6;
  color: #856404;
}

.status-valid {
  background: #d4edda;
  color: #155724;
}

.status-invalid {
  background: #f8d7da;
  color: #721c24;
}

.status-error {
  background: #fff3cd;
  color: #856404;
}

.verification-status {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.verification-method {
  font-size: var(--font-size-xs);
  color: var(--color-muted);
  font-style: italic;
}

.status-unsaved {
  font-size: var(--font-size-xs);
  color: var(--color-warning);
  font-weight: var(--font-weight-semibold);
}

.verification-meta {
  font-size: var(--font-size-xs);
  color: var(--color-muted);
  margin-top: var(--spacing-xs);
}

.details-cell {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Assigned/Unassigned Badge Styles */
.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  width: fit-content;
}

.badge-assigned {
  background-color: #d4edda;
  color: #155724;
}

.badge-unassigned {
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

/* Pagination styles removed - using filters only */

@media (max-width: 768px) {
  .admin-license-checker {
    padding: var(--spacing-md);
  }

  .bulk-actions-section {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    flex-direction: column;
  }

  .license-table-container {
    padding: var(--spacing-md);
  }

  .license-table {
    font-size: var(--font-size-sm);
  }

  .license-table th,
  .license-table td {
    padding: var(--spacing-xs) var(--spacing-sm);
  }
}
</style>
