/**
 * French Rowing Federation License Checker
 * 
 * Checks if rowing licenses are valid by scraping the FFAviron intranet.
 * A license is considered valid if:
 * - The state is "Active"
 * - The license type contains "compétition"
 */

import apiClient from '@/services/apiClient'

/**
 * Check if a license is valid (active and competition type)
 * @param {string} name - Name to search for
 * @param {string} licenseNumber - License number to check
 * @param {string} cookieString - Cookie string from browser
 * @returns {Promise<{valid: boolean, details: string}>}
 */
export async function checkLicense(name, licenseNumber, cookieString) {
  if (!name || !cookieString) {
    throw new Error('Name and cookie string are required')
  }

  // Build FFAviron search URL
  const searchQuery = encodeURIComponent(name)
  const url = `https://intranet.ffaviron.fr/licences/recherche?licencies_q=${searchQuery}`

  try {
    // Use backend proxy to avoid CORS issues
    const response = await apiClient.post('/admin/html-proxy', {
      url: url,
      cookies: cookieString,
      method: 'GET'
    })

    const html = response.data.data.html
    
    // Parse HTML to find license information
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // Find the results table
    let table = doc.querySelector('table.table-generated')
    if (!table) {
      table = doc.querySelector('table')
    }
    
    if (!table) {
      return {
        valid: false,
        details: 'No results table found'
      }
    }

    const tbody = table.querySelector('tbody')
    if (!tbody) {
      return {
        valid: false,
        details: 'No results found in table'
      }
    }

    const rows = tbody.querySelectorAll('tr')
    if (rows.length === 0) {
      return {
        valid: false,
        details: 'No data rows found'
      }
    }

    // Search through rows for matching license
    for (const row of rows) {
      const cells = row.querySelectorAll('td')
      if (cells.length >= 6) {
        const rowLicense = cells[0].textContent.trim()
        const rowName = cells[1].textContent.trim()
        const rowState = cells[4].textContent.trim()
        const rowType = cells[5].textContent.trim()

        // Check if this row matches our criteria
        const matchesLicense = licenseNumber && rowLicense === licenseNumber
        const matchesName = !licenseNumber && rowName.toLowerCase().includes(name.toLowerCase())

        if (matchesLicense || matchesName) {
          const isActive = rowState.includes('Active')
          const isCompetition = rowType.toLowerCase().includes('compétition')

          const details = `${rowName} - ${rowLicense} - ${rowState} - ${rowType}`

          if (isActive && isCompetition) {
            return {
              valid: true,
              details: `Valid: ${details}`
            }
          } else {
            return {
              valid: false,
              details: `Invalid: ${details}`
            }
          }
        }
      }
    }

    return {
      valid: false,
      details: `License ${licenseNumber || 'for ' + name} not found in ${rows.length} results`
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
 * @param {Function} onProgress - Progress callback (current, total)
 * @returns {Promise<Array<{name: string, license: string, valid: boolean, details: string}>>}
 */
export async function checkLicensesBatch(members, cookieString, onProgress = null) {
  const results = []
  
  for (let i = 0; i < members.length; i++) {
    const member = members[i]
    
    try {
      const result = await checkLicense(member.name, member.license, cookieString)
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
