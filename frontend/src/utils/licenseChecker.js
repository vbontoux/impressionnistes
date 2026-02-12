/**
 * French Rowing Federation License Checker
 * 
 * Checks if rowing licenses are valid by scraping the FFAviron intranet.
 * A license is considered valid if:
 * - The state is "Active"
 * - The license type contains "compétition"
 * 
 * Search Strategy:
 * 1. First searches by name
 * 2. If not found, retries by license number
 * 3. Provides detailed reasons for any validation issues
 */

import apiClient from '@/services/apiClient'

/**
 * Search FFAviron by query (name or license number)
 * @param {string} query - Search query
 * @param {string} cookieString - Cookie string
 * @returns {Promise<{success: boolean, rows: NodeList|null, error: string|null}>}
 */
async function searchByQuery(query, cookieString) {
  const searchQuery = encodeURIComponent(query)
  const url = `https://intranet.ffaviron.fr/licences/recherche?licencies_q=${searchQuery}`

  try {
    const response = await apiClient.post('/admin/html-proxy', {
      url: url,
      cookies: cookieString,
      method: 'GET'
    })

    const html = response.data.data.html
    const finalUrl = response.data.data.final_url || url
    
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // Check if we were redirected to a profile page (302 redirect to /personnes/fiche/...)
    if (finalUrl.includes('/personnes/fiche/')) {
      console.log('[License Search] Redirected to profile page:', finalUrl)
      // Extract data from profile page
      return extractFromProfilePage(doc)
    }
    
    // Otherwise, extract from search results table
    let table = doc.querySelector('table.table-generated')
    if (!table) {
      table = doc.querySelector('table')
    }
    
    if (!table) {
      return { success: false, rows: null, error: 'No results table found' }
    }

    const tbody = table.querySelector('tbody')
    if (!tbody) {
      return { success: false, rows: null, error: 'No results found in table' }
    }

    const rows = tbody.querySelectorAll('tr')
    if (rows.length === 0) {
      return { success: false, rows: null, error: 'No data rows found' }
    }

    return { success: true, rows: rows, error: null }
  } catch (error) {
    return { success: false, rows: null, error: error.message }
  }
}

/**
 * Extract license data from a profile page (when redirected)
 * Profile pages have a different structure - cards instead of table rows
 * @param {Document} doc - Parsed HTML document
 * @returns {{success: boolean, rows: Array|null, error: string|null, personName: string|null}}
 */
function extractFromProfilePage(doc) {
  try {
    // Extract person's name from page title
    let personName = null
    const titleElement = doc.querySelector('title')
    if (titleElement) {
      const titleText = titleElement.textContent.trim()
      // Format: "FFA - Mme LAMOUR Fanny" or "FFA - M. DOE John"
      const match = titleText.match(/FFA\s*-\s*(?:M\.|Mme\s+)?(.+)/)
      if (match) {
        personName = match[1].trim()
      }
    }
    
    console.log('[License Search] Profile page person name from title:', personName)
    
    // Extract license number from breadcrumb
    let licenseNumber = null
    const breadcrumbLinks = doc.querySelectorAll('.breadcrumb-item')
    for (const link of breadcrumbLinks) {
      const text = link.textContent.trim()
      // Format: "562066 - Mme LAMOUR Fanny"
      const match = text.match(/^(\d+)\s*-/)
      if (match) {
        licenseNumber = match[1]
        break
      }
    }
    
    // If not found in breadcrumb, try to find badge with license number
    if (!licenseNumber) {
      const badges = doc.querySelectorAll('.badge-primary')
      for (const badge of badges) {
        const text = badge.textContent.trim()
        // Check if it's a number (license numbers are numeric)
        if (/^\d+$/.test(text)) {
          licenseNumber = text
          break
        }
      }
    }
    
    console.log('[License Search] Profile page license number:', licenseNumber)
    
    // Find the most recent active license (card with border-left-success)
    let status = 'Unknown'
    let licenseType = 'Unknown'
    
    // Look for the active license card (green border = success = active)
    const activeCard = doc.querySelector('.card.border-left-success .card-body')
    if (activeCard) {
      status = 'Active'
      
      // Extract license type from h6 in the card
      const h6 = activeCard.querySelector('h6')
      if (h6) {
        const typeText = h6.textContent.trim()
        // Format: "Licence Annuelle compétition" or "Licence Annuelle loisir"
        if (typeText.includes('compétition')) {
          licenseType = 'Annuelle compétition'
        } else if (typeText.includes('loisir')) {
          licenseType = 'Annuelle loisir'
        } else {
          licenseType = typeText
        }
      }
      
      console.log('[License Search] Found active license card')
      console.log('[License Search] License type:', licenseType)
    } else {
      // No active license found, check for any license card
      const anyCard = doc.querySelector('.card-body h6')
      if (anyCard) {
        const typeText = anyCard.textContent.trim()
        if (typeText.includes('compétition')) {
          licenseType = 'Annuelle compétition'
        } else if (typeText.includes('loisir')) {
          licenseType = 'Annuelle loisir'
        } else {
          licenseType = typeText
        }
        status = 'Inactive'
        console.log('[License Search] No active license found, using first license card')
      }
    }
    
    console.log('[License Search] Final status:', status)
    console.log('[License Search] Final license type:', licenseType)
    
    // Create a fake row structure that matches what the rest of the code expects
    // The code expects rows with cells: [license, name, club, ..., status, type]
    if (licenseNumber && personName) {
      const fakeRow = {
        querySelectorAll: (selector) => {
          if (selector === 'td') {
            // Return fake cells that match the expected structure
            return [
              { textContent: licenseNumber },  // cell 0: license number
              { textContent: personName },      // cell 1: name
              { textContent: '' },              // cell 2: club (not available)
              { textContent: '' },              // cell 3: (not used)
              { textContent: status },          // cell 4: status
              { textContent: licenseType }      // cell 5: type
            ]
          }
          return []
        }
      }
      
      console.log('[License Search] Created fake row from profile page data')
      return {
        success: true,
        rows: [fakeRow],  // Return array with single fake row
        error: null,
        personName: personName
      }
    }
    
    console.log('[License Search] Could not extract license data from profile page')
    console.log('[License Search] Missing data - licenseNumber:', licenseNumber, 'personName:', personName)
    return {
      success: false,
      rows: null,
      error: 'Could not extract license data from profile page',
      personName: personName
    }
  } catch (error) {
    console.error('[License Search] Profile page parsing error:', error)
    return {
      success: false,
      rows: null,
      error: `Profile page parsing error: ${error.message}`,
      personName: null
    }
  }
}

/**
 * Check if two names match (ignoring order and case)
 * @param {string} name1 - First name
 * @param {string} name2 - Second name
 * @returns {boolean} True if names match
 */
function namesMatch(name1, name2) {
  if (!name1 || !name2) return false
  
  // List of titles to ignore
  const titlesToIgnore = ['m', 'm.', 'mme', 'mme.', 'mr', 'mr.', 'ms', 'ms.', 'miss', 'dr', 'dr.']
  
  // Normalize: lowercase and split into words
  const words1 = name1.toLowerCase()
    .split(/\s+/)
    .filter(w => w.length > 0 && !titlesToIgnore.includes(w.replace(/\./g, '')))
    .sort()
  
  const words2 = name2.toLowerCase()
    .split(/\s+/)
    .filter(w => w.length > 0 && !titlesToIgnore.includes(w.replace(/\./g, '')))
    .sort()
  
  // Check if all words from one name are in the other
  // This handles different word orders like "Clement GUITET GOUSSIN" vs "GUITET GOUSSIN Clement"
  const allWords1InWords2 = words1.every(w => words2.includes(w))
  const allWords2InWords1 = words2.every(w => words1.includes(w))
  
  return allWords1InWords2 && allWords2InWords1
}

/**
 * Validate a license row and return detailed result
 * @param {string} rowLicense - License number from row
 * @param {string} rowName - Name from row
 * @param {string} rowState - State from row
 * @param {string} rowType - Type from row
 * @param {string} expectedName - Expected name
 * @param {Function} t - i18n translate function
 * @returns {{valid: boolean, details: string}}
 */
function validateLicenseRow(rowLicense, rowName, rowState, rowType, expectedName, t) {
  const isActive = rowState.includes('Active')
  const isCompetition = rowType.toLowerCase().includes('compétition')
  const nameMatches = expectedName ? namesMatch(rowName, expectedName) : true

  // Name mismatch is INVALID - wrong person!
  if (expectedName && !nameMatches) {
    return {
      valid: false,
      details: t('admin.licenseChecker.messages.nameMismatch', {
        foundName: rowName,
        expectedName: expectedName,
        license: rowLicense,
        state: rowState,
        type: rowType
      })
    }
  }

  // Check license status and type
  if (isActive && isCompetition) {
    return {
      valid: true,
      details: t('admin.licenseChecker.messages.validLicense', {
        name: rowName,
        license: rowLicense,
        state: rowState,
        type: rowType
      })
    }
  } else {
    const reasons = []
    if (!isActive) {
      reasons.push(t('admin.licenseChecker.messages.statusNotActive', { state: rowState }))
    }
    if (!isCompetition) {
      reasons.push(t('admin.licenseChecker.messages.typeNotCompetition', { type: rowType }))
    }
    const reasonText = reasons.join(` ${t('admin.licenseChecker.messages.and')} `)
    return {
      valid: false,
      details: t('admin.licenseChecker.messages.invalidLicense', {
        name: rowName,
        license: rowLicense,
        reason: reasonText
      })
    }
  }
}

/**
 * Check if a license is valid (active and competition type)
 * 
 * Strategy:
 * 1. First, search by name
 * 2. If name search fails or doesn't find the license, retry by license number
 * 3. Provide detailed reasons for any issues found
 * 
 * @param {string} name - Name to search for
 * @param {string} licenseNumber - License number to check
 * @param {string} cookieString - Cookie string from browser
 * @param {Function} t - i18n translate function
 * @returns {Promise<{valid: boolean, details: string}>}
 */
export async function checkLicense(name, licenseNumber, cookieString, t) {
  if (!cookieString) {
    throw new Error('Cookie string is required')
  }

  let foundInNameSearch = false

  try {
    // Strategy 1: Search by name
    if (name) {
      const nameResult = await searchByQuery(name, cookieString)
      
      if (nameResult.success && nameResult.rows) {
        for (const row of nameResult.rows) {
          const cells = row.querySelectorAll('td')
          if (cells.length >= 6) {
            const rowLicense = cells[0].textContent.trim()
            const rowName = cells[1].textContent.trim()
            const rowState = cells[4].textContent.trim()
            const rowType = cells[5].textContent.trim()

            // If we have a license number, match exactly (normalize for comparison)
            if (licenseNumber) {
              const normalizedRowLicense = rowLicense.replace(/\s+/g, '')
              const normalizedSearchLicense = licenseNumber.replace(/\s+/g, '')
              
              if (normalizedRowLicense === normalizedSearchLicense) {
                foundInNameSearch = true
                return validateLicenseRow(rowLicense, rowName, rowState, rowType, name, t)
              }
            }

            // If no license number provided, match by name
            if (!licenseNumber && namesMatch(rowName, name)) {
              foundInNameSearch = true
              return validateLicenseRow(rowLicense, rowName, rowState, rowType, name, t)
            }
          }
        }
      }
    }

    // Strategy 2: If name search didn't find the license, try searching by license number
    if (licenseNumber && !foundInNameSearch) {
      const licenseResult = await searchByQuery(licenseNumber, cookieString)
      
      if (licenseResult.success && licenseResult.rows) {
        // Check if we found any rows
        if (licenseResult.rows.length === 0) {
          return {
            valid: false,
            details: t('admin.licenseChecker.messages.notFoundByLicense', { license: licenseNumber })
          }
        }

        console.log(`[License Search] Found ${licenseResult.rows.length} rows for license ${licenseNumber}`)

        // Process each row found
        for (let i = 0; i < licenseResult.rows.length; i++) {
          const row = licenseResult.rows[i]
          const cells = row.querySelectorAll('td')
          
          console.log(`[License Search] Row ${i}: Found ${cells.length} cells`)
          
          if (cells.length >= 6) {
            const rowLicense = cells[0].textContent.trim()
            const rowName = cells[1].textContent.trim()
            const rowState = cells[4].textContent.trim()
            const rowType = cells[5].textContent.trim()

            console.log(`[License Search] Row ${i} data:`, {
              rowLicense,
              rowName,
              rowState,
              rowType,
              searchingFor: licenseNumber
            })

            // Compare license numbers (normalize both to handle any formatting)
            const normalizedRowLicense = rowLicense.replace(/\s+/g, '')
            const normalizedSearchLicense = licenseNumber.replace(/\s+/g, '')

            console.log(`[License Search] Normalized comparison:`, {
              normalizedRowLicense,
              normalizedSearchLicense,
              match: normalizedRowLicense === normalizedSearchLicense
            })

            if (normalizedRowLicense === normalizedSearchLicense) {
              console.log(`[License Search] Match found! Checking name...`, {
                expectedName: name,
                foundName: rowName,
                nameProvided: !!name
              })
              
              const result = validateLicenseRow(rowLicense, rowName, rowState, rowType, name, t)
              
              console.log(`[License Search] validateLicenseRow result:`, result)
              
              // Check for name mismatch
              if (name && !namesMatch(rowName, name)) {
                console.log(`[License Search] NAME MISMATCH DETECTED!`)
                return {
                  valid: result.valid,
                  details: t('admin.licenseChecker.messages.nameMismatch', {
                    foundName: rowName,
                    expectedName: name,
                    license: rowLicense,
                    state: rowState,
                    type: rowType
                  })
                }
              }
              
              console.log(`[License Search] Name matches or no name check needed, returning result`)
              return {
                valid: result.valid,
                details: t('admin.licenseChecker.messages.foundByNumber', { details: result.details })
              }
            }
          } else {
            console.log(`[License Search] Row ${i}: Not enough cells (${cells.length})`)
          }
        }

        // If we get here, we found rows but none matched the license number
        console.log(`[License Search] No matching license found in ${licenseResult.rows.length} rows`)
        return {
          valid: false,
          details: t('admin.licenseChecker.messages.notFoundInResults', {
            license: licenseNumber,
            count: licenseResult.rows.length
          })
        }
      } else {
        return {
          valid: false,
          details: t('admin.licenseChecker.messages.searchFailed', {
            license: licenseNumber,
            error: licenseResult.error || 'No results returned'
          })
        }
      }
    }

    // Both strategies failed
    if (name && licenseNumber) {
      return {
        valid: false,
        details: t('admin.licenseChecker.messages.notFoundByName', { name, license: licenseNumber })
      }
    } else if (name) {
      return {
        valid: false,
        details: t('admin.licenseChecker.messages.notFoundByName', { name, license: '' })
      }
    } else {
      return {
        valid: false,
        details: t('admin.licenseChecker.messages.noNameOrLicense')
      }
    }

  } catch (error) {
    console.error('License check error:', error)
    throw new Error(`Request error: ${error.message}`)
  }
}

/**
 * Check multiple licenses in batch
 * @param {Array<{name: string, license: string}>} members - Array of members to check
 * @param {string} cookieString - Cookie string from browser
 * @param {Function} t - i18n translate function
 * @param {Function} onProgress - Progress callback (current, total)
 * @returns {Promise<Array<{name: string, license: string, valid: boolean, details: string}>>}
 */
export async function checkLicensesBatch(members, cookieString, t, onProgress = null) {
  const results = []
  
  for (let i = 0; i < members.length; i++) {
    const member = members[i]
    
    try {
      const result = await checkLicense(member.name, member.license, cookieString, t)
      results.push({
        ...member,
        valid: result.valid,
        details: result.details
      })
    } catch (error) {
      results.push({
        ...member,
        valid: false,
        details: `Error: ${error.message}`
      })
    }

    if (onProgress) {
      onProgress(i + 1, members.length)
    }

    // Small delay to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 500))
  }

  return results
}

/**
 * Export results to CSV format
 * @param {Array} results - Array of check results
 * @returns {string} CSV string
 */
export function exportToCSV(results) {
  const headers = ['name', 'license', 'valid', 'details']
  const rows = results.map(r => [
    r.name,
    r.license || '',
    r.valid ? 'Yes' : 'No',
    r.details || ''
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')

  return csvContent
}

/**
 * Download CSV file
 * @param {string} csvContent - CSV content
 * @param {string} filename - Filename for download
 */
export function downloadCSV(csvContent, filename = 'license_check_results.csv') {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
