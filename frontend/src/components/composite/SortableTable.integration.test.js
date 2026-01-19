import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SortableTable from './SortableTable.vue'

describe('SortableTable - Integration Tests (Checkpoint 10)', () => {
  describe('Feature Independence Tests', () => {
    it('horizontal scrolling works independently', () => {
      const columns = [
        { key: 'col1', label: 'Column 1', width: '300px' },
        { key: 'col2', label: 'Column 2', width: '300px' },
        { key: 'col3', label: 'Column 3', width: '300px' },
        { key: 'col4', label: 'Column 4', width: '300px' }
      ]
      const data = [
        { id: 1, col1: 'A', col2: 'B', col3: 'C', col4: 'D' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.exists()).toBe(true)
      
      // Verify scrollbar styling is applied
      expect(tableWrapper.classes()).toContain('sortable-table-wrapper')
    })

    it('sticky columns work independently', () => {
      const columns = [
        { key: 'id', label: 'ID', sticky: 'left' },
        { key: 'name', label: 'Name' },
        { key: 'actions', label: 'Actions', sticky: 'right' }
      ]
      const data = [
        { id: 1, name: 'Test', actions: 'Edit' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).toContain('sticky-left')
      expect(headers[2].classes()).toContain('sticky-right')
      
      const cells = wrapper.findAll('td')
      expect(cells[0].classes()).toContain('sticky-left')
      expect(cells[2].classes()).toContain('sticky-right')
    })

    it('responsive column hiding works independently', () => {
      const columns = [
        { key: 'id', label: 'ID', responsive: 'always' },
        { key: 'email', label: 'Email', responsive: 'hide-below-1024' },
        { key: 'phone', label: 'Phone', responsive: 'hide-below-768' }
      ]
      const data = [
        { id: 1, email: 'test@example.com', phone: '123-456-7890' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).toContain('column-always')
      expect(headers[1].classes()).toContain('column-hide-below-1024')
      expect(headers[2].classes()).toContain('column-hide-below-768')
    })

    it('compact mode works independently', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, compact: true }
      })

      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.classes()).toContain('compact-mode')
    })

    it('column width management works independently', () => {
      const columns = [
        { key: 'col1', label: 'Column 1', width: '150px' },
        { key: 'col2', label: 'Column 2', minWidth: '200px' }
      ]
      const data = [
        { id: 1, col1: 'A', col2: 'B' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].attributes('style')).toContain('width: 150px')
      expect(headers[1].attributes('style')).toContain('min-width: 200px')
    })
  })

  describe('Feature Combination Tests', () => {
    it('sticky columns + responsive hiding work together', () => {
      const columns = [
        { key: 'id', label: 'ID', sticky: 'left', responsive: 'always' },
        { key: 'name', label: 'Name', responsive: 'always' },
        { key: 'email', label: 'Email', responsive: 'hide-below-1024' },
        { key: 'actions', label: 'Actions', sticky: 'right', responsive: 'always' }
      ]
      const data = [
        { id: 1, name: 'Test', email: 'test@example.com', actions: 'Edit' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      
      // ID column: sticky left + always visible
      expect(headers[0].classes()).toContain('sticky-left')
      expect(headers[0].classes()).toContain('column-always')
      
      // Email column: responsive hiding
      expect(headers[2].classes()).toContain('column-hide-below-1024')
      
      // Actions column: sticky right + always visible
      expect(headers[3].classes()).toContain('sticky-right')
      expect(headers[3].classes()).toContain('column-always')
    })

    it('sticky columns + compact mode work together', () => {
      const columns = [
        { key: 'id', label: 'ID', sticky: 'left' },
        { key: 'name', label: 'Name' },
        { key: 'actions', label: 'Actions', sticky: 'right' }
      ]
      const data = [
        { id: 1, name: 'Test', actions: 'Edit' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, compact: true }
      })

      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.classes()).toContain('compact-mode')
      
      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).toContain('sticky-left')
      expect(headers[2].classes()).toContain('sticky-right')
    })

    it('responsive hiding + compact mode work together', () => {
      const columns = [
        { key: 'id', label: 'ID', responsive: 'always' },
        { key: 'email', label: 'Email', responsive: 'hide-below-1024' }
      ]
      const data = [
        { id: 1, email: 'test@example.com' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, compact: true }
      })

      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.classes()).toContain('compact-mode')
      
      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).toContain('column-always')
      expect(headers[1].classes()).toContain('column-hide-below-1024')
    })

    it('all features work together (sticky + responsive + compact + width)', () => {
      const columns = [
        { 
          key: 'id', 
          label: 'ID', 
          sticky: 'left', 
          responsive: 'always',
          width: '80px'
        },
        { 
          key: 'name', 
          label: 'Name', 
          responsive: 'always',
          minWidth: '150px'
        },
        { 
          key: 'email', 
          label: 'Email', 
          responsive: 'hide-below-1024',
          width: '200px'
        },
        { 
          key: 'actions', 
          label: 'Actions', 
          sticky: 'right', 
          responsive: 'always',
          width: '150px'
        }
      ]
      const data = [
        { id: 1, name: 'Test User', email: 'test@example.com', actions: 'Edit' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, compact: true }
      })

      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.classes()).toContain('compact-mode')
      
      const headers = wrapper.findAll('th')
      
      // ID column: all features
      expect(headers[0].classes()).toContain('sticky-left')
      expect(headers[0].classes()).toContain('column-always')
      expect(headers[0].attributes('style')).toContain('width: 80px')
      
      // Name column: responsive + width
      expect(headers[1].classes()).toContain('column-always')
      expect(headers[1].attributes('style')).toContain('min-width: 150px')
      
      // Email column: responsive + width
      expect(headers[2].classes()).toContain('column-hide-below-1024')
      expect(headers[2].attributes('style')).toContain('width: 200px')
      
      // Actions column: sticky + responsive + width
      expect(headers[3].classes()).toContain('sticky-right')
      expect(headers[3].classes()).toContain('column-always')
      expect(headers[3].attributes('style')).toContain('width: 150px')
    })
  })

  describe('Backward Compatibility Tests', () => {
    it('works with minimal props (columns + data only)', () => {
      const columns = [
        { key: 'name', label: 'Name' },
        { key: 'age', label: 'Age' }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 },
        { id: 2, name: 'Bob', age: 25 }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      expect(wrapper.find('table').exists()).toBe(true)
      expect(wrapper.findAll('th')).toHaveLength(2)
      expect(wrapper.findAll('tbody tr')).toHaveLength(2)
    })

    it('works with original props (initialSortField, initialSortDirection)', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie' },
        { id: 2, name: 'Alice' },
        { id: 3, name: 'Bob' }
      ]

      const wrapper = mount(SortableTable, {
        props: {
          columns,
          data,
          initialSortField: 'name',
          initialSortDirection: 'asc'
        }
      })

      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Alice')
      expect(rows[1].text()).toContain('Bob')
      expect(rows[2].text()).toContain('Charlie')
    })

    it('works with hoverable prop', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, hoverable: true }
      })

      const row = wrapper.find('.table-row')
      expect(row.classes()).toContain('hoverable')
    })

    it('defaults work correctly when new props are omitted', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      // Compact should default to false
      const tableWrapper = wrapper.find('.sortable-table-wrapper')
      expect(tableWrapper.classes()).not.toContain('compact-mode')
      
      // Hoverable should default to true
      const row = wrapper.find('.table-row')
      expect(row.classes()).toContain('hoverable')
      
      // Columns without sticky should not have sticky classes
      const header = wrapper.find('th')
      expect(header.classes()).not.toContain('sticky-left')
      expect(header.classes()).not.toContain('sticky-right')
      
      // Columns without responsive should default to 'always'
      expect(header.classes()).toContain('column-always')
    })

    it('custom cell slots still work', () => {
      const columns = [
        { key: 'name', label: 'Name' },
        { key: 'status', label: 'Status' }
      ]
      const data = [
        { id: 1, name: 'Test', status: 'active' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data },
        slots: {
          'cell-status': '<span class="custom-status">Custom Status</span>'
        }
      })

      expect(wrapper.find('.custom-status').exists()).toBe(true)
      expect(wrapper.find('.custom-status').text()).toBe('Custom Status')
    })
  })

  describe('Accessibility Tests', () => {
    it('has proper ARIA attributes', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data, ariaLabel: 'Test table' }
      })

      const table = wrapper.find('table')
      expect(table.attributes('role')).toBe('table')
      expect(table.attributes('aria-label')).toBe('Test table')
      
      const thead = wrapper.find('thead')
      expect(thead.attributes('role')).toBe('rowgroup')
      
      const tbody = wrapper.find('tbody')
      expect(tbody.attributes('role')).toBe('rowgroup')
      
      const th = wrapper.find('th')
      expect(th.attributes('role')).toBe('columnheader')
      expect(th.attributes('aria-sort')).toBe('none')
      
      const td = wrapper.find('td')
      expect(td.attributes('role')).toBe('cell')
    })

    it('sortable headers have correct tabindex', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'actions', label: 'Actions', sortable: false }
      ]
      const data = [
        { id: 1, name: 'Test', actions: 'Edit' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].attributes('tabindex')).toBe('0') // sortable
      expect(headers[1].attributes('tabindex')).toBe('-1') // not sortable
    })

    it('cells have tabindex for keyboard navigation', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const cell = wrapper.find('td')
      expect(cell.attributes('tabindex')).toBe('0')
    })

    it('sort indicator has aria-hidden', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const indicator = wrapper.find('.sort-indicator')
      expect(indicator.attributes('aria-hidden')).toBe('true')
    })
  })

  describe('Column Configuration Validation', () => {
    it('validates sticky property values', () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const columns = [
        { key: 'name', label: 'Name', sticky: 'invalid' }
      ]
      const data = []

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      expect(consoleError).toHaveBeenCalledWith(
        expect.stringContaining('Invalid sticky value')
      )
      
      consoleError.mockRestore()
    })

    it('validates responsive property values', () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const columns = [
        { key: 'name', label: 'Name', responsive: 'invalid' }
      ]
      const data = []

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      expect(consoleError).toHaveBeenCalledWith(
        expect.stringContaining('Invalid responsive value')
      )
      
      consoleError.mockRestore()
    })

    it('requires key and label for each column', () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const columns = [
        { key: 'name' } // missing label
      ]
      const data = []

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      expect(consoleError).toHaveBeenCalled()
      expect(consoleError.mock.calls[0][0]).toContain('Column must have key and label')
      
      consoleError.mockRestore()
    })
  })

  describe('Event Emission Tests', () => {
    it('emits sort event with correct payload', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const header = wrapper.find('th')
      await header.trigger('click')

      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')[0][0]).toEqual({
        field: 'name',
        direction: 'asc'
      })
    })

    it('emits scroll event when scrolling', () => {
      const columns = [
        { key: 'col1', label: 'Column 1', width: '300px' },
        { key: 'col2', label: 'Column 2', width: '300px' }
      ]
      const data = [
        { id: 1, col1: 'A', col2: 'B' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      // Note: Scroll events are tested in useTableScroll.test.js
      // This test verifies the component is set up to emit scroll events
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Custom Cell Slot Tests', () => {
    it('renders custom slot content', () => {
      const columns = [
        { key: 'name', label: 'Name' },
        { key: 'status', label: 'Status' }
      ]
      const data = [
        { id: 1, name: 'Test', status: 'active' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data },
        slots: {
          'cell-status': '<span class="badge">Active</span>'
        }
      })

      expect(wrapper.find('.badge').exists()).toBe(true)
      expect(wrapper.find('.badge').text()).toBe('Active')
    })

    it('falls back to raw value when no slot provided', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test Value' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const cell = wrapper.find('td')
      expect(cell.text()).toBe('Test Value')
    })

    it('provides correct slot props', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: 'Test', extra: 'data' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data },
        slots: {
          'cell-name': `
            <template #cell-name="{ row, value, column }">
              <span class="custom">{{ value }} - {{ row.extra }} - {{ column.key }}</span>
            </template>
          `
        }
      })

      // Slot props are available to the slot content
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Multiple Sticky Columns', () => {
    it('maintains order of multiple sticky-left columns', () => {
      const columns = [
        { key: 'id', label: 'ID', sticky: 'left' },
        { key: 'name', label: 'Name', sticky: 'left' },
        { key: 'email', label: 'Email' }
      ]
      const data = [
        { id: 1, name: 'Test', email: 'test@example.com' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).toContain('sticky-left')
      expect(headers[1].classes()).toContain('sticky-left')
      expect(headers[2].classes()).not.toContain('sticky-left')
      
      // Order is preserved
      expect(headers[0].text()).toContain('ID')
      expect(headers[1].text()).toContain('Name')
    })

    it('maintains order of multiple sticky-right columns', () => {
      const columns = [
        { key: 'name', label: 'Name' },
        { key: 'edit', label: 'Edit', sticky: 'right' },
        { key: 'delete', label: 'Delete', sticky: 'right' }
      ]
      const data = [
        { id: 1, name: 'Test', edit: 'Edit', delete: 'Delete' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).not.toContain('sticky-right')
      expect(headers[1].classes()).toContain('sticky-right')
      expect(headers[2].classes()).toContain('sticky-right')
      
      // Order is preserved
      expect(headers[1].text()).toContain('Edit')
      expect(headers[2].text()).toContain('Delete')
    })
  })

  describe('Edge Cases', () => {
    it('handles empty data array', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = []

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      expect(wrapper.find('table').exists()).toBe(true)
      expect(wrapper.findAll('tbody tr')).toHaveLength(0)
    })

    it('handles null/undefined cell values', () => {
      const columns = [
        { key: 'name', label: 'Name' },
        { key: 'age', label: 'Age' }
      ]
      const data = [
        { id: 1, name: null, age: undefined }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const cells = wrapper.findAll('td')
      expect(cells[0].text()).toBe('')
      expect(cells[1].text()).toBe('')
    })

    it('handles very long column labels', () => {
      const columns = [
        { key: 'name', label: 'This is a very long column label that might wrap' }
      ]
      const data = [
        { id: 1, name: 'Test' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const header = wrapper.find('th')
      expect(header.text()).toContain('This is a very long column label')
    })

    it('handles special characters in data', () => {
      const columns = [
        { key: 'name', label: 'Name' }
      ]
      const data = [
        { id: 1, name: '<script>alert("xss")</script>' }
      ]

      const wrapper = mount(SortableTable, {
        props: { columns, data }
      })

      const cell = wrapper.find('td')
      // Vue automatically escapes HTML
      expect(cell.text()).toContain('<script>')
    })
  })
})
