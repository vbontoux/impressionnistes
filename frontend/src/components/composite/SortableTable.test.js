import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SortableTable from './SortableTable.vue'

describe('SortableTable - Column Width Management', () => {
  const createWrapper = (columns, data = []) => {
    return mount(SortableTable, {
      props: {
        columns,
        data
      }
    })
  }

  it('applies width style to th and td elements when width is specified', () => {
    const columns = [
      { key: 'name', label: 'Name', width: '150px' },
      { key: 'age', label: 'Age', width: '100px' }
    ]
    const data = [
      { id: 1, name: 'John Doe', age: 30 }
    ]

    const wrapper = createWrapper(columns, data)
    
    // Check th elements
    const headers = wrapper.findAll('th')
    expect(headers[0].attributes('style')).toContain('width: 150px')
    expect(headers[1].attributes('style')).toContain('width: 100px')
    
    // Check td elements
    const cells = wrapper.findAll('td')
    expect(cells[0].attributes('style')).toContain('width: 150px')
    expect(cells[1].attributes('style')).toContain('width: 100px')
  })

  it('applies minWidth style to th and td elements when minWidth is specified', () => {
    const columns = [
      { key: 'name', label: 'Name', minWidth: '200px' },
      { key: 'description', label: 'Description', minWidth: '300px' }
    ]
    const data = [
      { id: 1, name: 'Item', description: 'A long description' }
    ]

    const wrapper = createWrapper(columns, data)
    
    // Check th elements
    const headers = wrapper.findAll('th')
    expect(headers[0].attributes('style')).toContain('min-width: 200px')
    expect(headers[1].attributes('style')).toContain('min-width: 300px')
    
    // Check td elements
    const cells = wrapper.findAll('td')
    expect(cells[0].attributes('style')).toContain('min-width: 200px')
    expect(cells[1].attributes('style')).toContain('min-width: 300px')
  })

  it('applies both width and minWidth when both are specified', () => {
    const columns = [
      { key: 'name', label: 'Name', width: '150px', minWidth: '100px' }
    ]
    const data = [
      { id: 1, name: 'John Doe' }
    ]

    const wrapper = createWrapper(columns, data)
    
    const header = wrapper.find('th')
    expect(header.attributes('style')).toContain('width: 150px')
    expect(header.attributes('style')).toContain('min-width: 100px')
    
    const cell = wrapper.find('td')
    expect(cell.attributes('style')).toContain('width: 150px')
    expect(cell.attributes('style')).toContain('min-width: 100px')
  })

  it('supports percentage widths', () => {
    const columns = [
      { key: 'name', label: 'Name', width: '50%' },
      { key: 'age', label: 'Age', width: '25%' }
    ]
    const data = [
      { id: 1, name: 'John Doe', age: 30 }
    ]

    const wrapper = createWrapper(columns, data)
    
    const headers = wrapper.findAll('th')
    expect(headers[0].attributes('style')).toContain('width: 50%')
    expect(headers[1].attributes('style')).toContain('width: 25%')
  })

  it('auto-sizes columns when no width is specified', () => {
    const columns = [
      { key: 'name', label: 'Name' },
      { key: 'age', label: 'Age' }
    ]
    const data = [
      { id: 1, name: 'John Doe', age: 30 }
    ]

    const wrapper = createWrapper(columns, data)
    
    // When no width is specified, style should be empty or not contain width
    const headers = wrapper.findAll('th')
    const header0Style = headers[0].attributes('style') || ''
    const header1Style = headers[1].attributes('style') || ''
    
    expect(header0Style).not.toContain('width:')
    expect(header1Style).not.toContain('width:')
  })

  it('supports mixed width configurations', () => {
    const columns = [
      { key: 'id', label: 'ID', width: '80px' },
      { key: 'name', label: 'Name', minWidth: '150px' },
      { key: 'description', label: 'Description' }, // auto-size
      { key: 'actions', label: 'Actions', width: '200px', minWidth: '180px' }
    ]
    const data = [
      { id: 1, name: 'Item', description: 'Description', actions: 'Edit' }
    ]

    const wrapper = createWrapper(columns, data)
    
    const headers = wrapper.findAll('th')
    
    // ID column: width only
    expect(headers[0].attributes('style')).toContain('width: 80px')
    expect(headers[0].attributes('style')).not.toContain('min-width')
    
    // Name column: minWidth only
    expect(headers[1].attributes('style')).toContain('min-width: 150px')
    // Check that it doesn't have width property (but has min-width)
    const nameStyle = headers[1].attributes('style')
    expect(nameStyle).toMatch(/min-width:\s*150px/)
    expect(nameStyle).not.toMatch(/^width:|;\s*width:/)
    
    // Description column: no width styling
    const descStyle = headers[2].attributes('style') || ''
    expect(descStyle).not.toContain('width')
    
    // Actions column: both width and minWidth
    expect(headers[3].attributes('style')).toContain('width: 200px')
    expect(headers[3].attributes('style')).toContain('min-width: 180px')
  })

  it('supports other CSS units (rem, em, vw)', () => {
    const columns = [
      { key: 'col1', label: 'Col 1', width: '10rem' },
      { key: 'col2', label: 'Col 2', width: '15em' },
      { key: 'col3', label: 'Col 3', width: '20vw' }
    ]
    const data = [
      { id: 1, col1: 'A', col2: 'B', col3: 'C' }
    ]

    const wrapper = createWrapper(columns, data)
    
    const headers = wrapper.findAll('th')
    expect(headers[0].attributes('style')).toContain('width: 10rem')
    expect(headers[1].attributes('style')).toContain('width: 15em')
    expect(headers[2].attributes('style')).toContain('width: 20vw')
  })
})

describe('SortableTable - Compact Mode', () => {
  const createWrapper = (compact = false, columns = [], data = []) => {
    return mount(SortableTable, {
      props: {
        columns,
        data,
        compact
      }
    })
  }

  it('does not apply compact-mode class by default', () => {
    const columns = [
      { key: 'name', label: 'Name' }
    ]
    const data = [
      { id: 1, name: 'John Doe' }
    ]

    const wrapper = createWrapper(false, columns, data)
    
    const tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).not.toContain('compact-mode')
  })

  it('applies compact-mode class when compact prop is true', () => {
    const columns = [
      { key: 'name', label: 'Name' }
    ]
    const data = [
      { id: 1, name: 'John Doe' }
    ]

    const wrapper = createWrapper(true, columns, data)
    
    const tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).toContain('compact-mode')
  })

  it('toggles compact-mode class when prop changes', async () => {
    const columns = [
      { key: 'name', label: 'Name' }
    ]
    const data = [
      { id: 1, name: 'John Doe' }
    ]

    const wrapper = createWrapper(false, columns, data)
    
    // Initially not compact
    let tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).not.toContain('compact-mode')
    
    // Toggle to compact
    await wrapper.setProps({ compact: true })
    tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).toContain('compact-mode')
    
    // Toggle back to normal
    await wrapper.setProps({ compact: false })
    tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).not.toContain('compact-mode')
  })

  it('compact prop defaults to false', () => {
    const columns = [
      { key: 'name', label: 'Name' }
    ]
    const data = [
      { id: 1, name: 'John Doe' }
    ]

    // Mount without specifying compact prop
    const wrapper = mount(SortableTable, {
      props: {
        columns,
        data
      }
    })
    
    const tableWrapper = wrapper.find('.sortable-table-wrapper')
    expect(tableWrapper.classes()).not.toContain('compact-mode')
  })
})

describe('SortableTable - Sorting Functionality', () => {
  const createWrapper = (columns, data, initialSortField = '', initialSortDirection = 'asc') => {
    return mount(SortableTable, {
      props: {
        columns,
        data,
        initialSortField,
        initialSortDirection
      }
    })
  }

  describe('Sortable Column Header Clicks', () => {
    it('emits sort event when clicking a sortable column header', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie', age: 30 },
        { id: 2, name: 'Alice', age: 25 },
        { id: 3, name: 'Bob', age: 35 }
      ]

      const wrapper = createWrapper(columns, data)
      
      // Click name header to sort
      const nameHeader = wrapper.findAll('th')[0]
      await nameHeader.trigger('click')
      
      // Verify sort event was emitted with correct parameters
      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')[0][0]).toEqual({
        field: 'name',
        direction: 'asc'
      })
    })

    it('sorts by initial sort field on mount', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie', age: 30 },
        { id: 2, name: 'Alice', age: 25 },
        { id: 3, name: 'Bob', age: 35 }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'asc')
      
      // Check data is sorted by name ascending on mount
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Alice')
      expect(rows[1].text()).toContain('Bob')
      expect(rows[2].text()).toContain('Charlie')
    })

    it('supports keyboard navigation (Enter key) to sort', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie' },
        { id: 2, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('keydown.enter')
      
      // Verify sort event was emitted
      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')[0][0].field).toBe('name')
    })

    it('supports keyboard navigation (Space key) to sort', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie' },
        { id: 2, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('keydown.space')
      
      // Verify sort event was emitted
      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')[0][0].field).toBe('name')
    })
  })

  describe('Sort Direction Toggle', () => {
    it('emits correct direction when toggling sort', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Charlie' },
        { id: 2, name: 'Alice' },
        { id: 3, name: 'Bob' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      
      // First click - ascending
      await nameHeader.trigger('click')
      expect(wrapper.emitted('sort')[0][0]).toEqual({
        field: 'name',
        direction: 'asc'
      })
      
      // Second click - descending
      await nameHeader.trigger('click')
      expect(wrapper.emitted('sort')[1][0]).toEqual({
        field: 'name',
        direction: 'desc'
      })
    })

    it('resets to ascending when clicking a different column', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 },
        { id: 2, name: 'Bob', age: 25 }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'desc')
      
      const headers = wrapper.findAll('th')
      
      // Sort by age - should reset to ascending
      await headers[1].trigger('click')
      
      const sortEvents = wrapper.emitted('sort')
      const lastEvent = sortEvents[sortEvents.length - 1][0]
      expect(lastEvent).toEqual({
        field: 'age',
        direction: 'asc'
      })
    })

    it('respects initial sort direction', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'desc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Bob')
      expect(rows[1].text()).toContain('Alice')
    })
  })

  describe('Sort Indicator Display', () => {
    it('displays ascending indicator (▲) when sorted ascending', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Bob' },
        { id: 2, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      
      const indicator = wrapper.find('.sort-indicator')
      expect(indicator.text()).toBe('▲')
    })

    it('displays descending indicator (▼) when sorted descending', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      await nameHeader.trigger('click')
      
      const indicator = wrapper.find('.sort-indicator')
      expect(indicator.text()).toBe('▼')
    })

    it('displays no indicator on unsorted columns', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 }
      ]

      const wrapper = createWrapper(columns, data)
      
      // Sort by name
      const nameHeader = wrapper.findAll('th')[0]
      await nameHeader.trigger('click')
      
      // Age column should have empty indicator
      const indicators = wrapper.findAll('.sort-indicator')
      expect(indicators[0].text()).toBe('▲') // name column
      expect(indicators[1].text()).toBe('') // age column
    })

    it('applies sorted class to currently sorted column', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 }
      ]

      const wrapper = createWrapper(columns, data)
      
      const headers = wrapper.findAll('th')
      
      // Sort by name
      await headers[0].trigger('click')
      expect(headers[0].classes()).toContain('sorted')
      expect(headers[1].classes()).not.toContain('sorted')
      
      // Sort by age
      await headers[1].trigger('click')
      expect(headers[0].classes()).not.toContain('sorted')
      expect(headers[1].classes()).toContain('sorted')
    })
  })

  describe('Non-Sortable Columns', () => {
    it('does not sort when clicking non-sortable column', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Bob', age: 30 },
        { id: 2, name: 'Alice', age: 25 }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.findAll('th')[0]
      await nameHeader.trigger('click')
      
      // Data should remain in original order
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Bob')
      expect(rows[1].text()).toContain('Alice')
    })

    it('does not display sort indicator on non-sortable columns', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      expect(nameHeader.find('.sort-indicator').exists()).toBe(false)
    })

    it('does not apply sortable class to non-sortable columns', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 }
      ]

      const wrapper = createWrapper(columns, data)
      
      const headers = wrapper.findAll('th')
      expect(headers[0].classes()).not.toContain('sortable')
      expect(headers[1].classes()).toContain('sortable')
    })

    it('sets tabindex=-1 on non-sortable columns', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 }
      ]

      const wrapper = createWrapper(columns, data)
      
      const headers = wrapper.findAll('th')
      expect(headers[0].attributes('tabindex')).toBe('-1')
      expect(headers[1].attributes('tabindex')).toBe('0')
    })
  })

  describe('Sorting with Different Data Types', () => {
    it('sorts string data alphabetically (case-insensitive)', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'zebra' },
        { id: 2, name: 'Apple' },
        { id: 3, name: 'banana' }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Apple')
      expect(rows[1].text()).toContain('banana')
      expect(rows[2].text()).toContain('zebra')
    })

    it('sorts numeric data numerically', () => {
      const columns = [
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, age: 100 },
        { id: 2, age: 5 },
        { id: 3, age: 25 }
      ]

      const wrapper = createWrapper(columns, data, 'age', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('5')
      expect(rows[1].text()).toContain('25')
      expect(rows[2].text()).toContain('100')
    })

    it('sorts boolean data correctly', async () => {
      const columns = [
        { key: 'active', label: 'Active', sortable: true }
      ]
      const data = [
        { id: 1, active: true },
        { id: 2, active: false },
        { id: 3, active: true }
      ]

      const wrapper = createWrapper(columns, data, 'active', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      // false should come before true in ascending order
      expect(rows[0].findAll('td')[0].text()).toContain('false')
      expect(rows[1].findAll('td')[0].text()).toContain('true')
    })

    it('sorts boat numbers with alphanumeric logic', () => {
      const columns = [
        { key: 'boat_number', label: 'Boat Number', sortable: true }
      ]
      const data = [
        { id: 1, boat_number: 'SM.2.1' },
        { id: 2, boat_number: 'M.1.2' },
        { id: 3, boat_number: 'M.1.1' },
        { id: 4, boat_number: 'VM.3.1' }
      ]

      const wrapper = createWrapper(columns, data, 'boat_number', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('M.1.1')
      expect(rows[1].text()).toContain('M.1.2')
      expect(rows[2].text()).toContain('SM.2.1')
      expect(rows[3].text()).toContain('VM.3.1')
    })
  })

  describe('Null Value Handling in Sorting', () => {
    it('places null values at the end when sorting ascending', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Bob' },
        { id: 2, name: null },
        { id: 3, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Alice')
      expect(rows[1].text()).toContain('Bob')
      // Null should be last
      expect(rows[2].findAll('td')[0].text().trim()).toBe('')
    })

    it('places null values at the beginning when sorting descending', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Bob' },
        { id: 2, name: null },
        { id: 3, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'desc')
      
      const rows = wrapper.findAll('tbody tr')
      // In descending order, null values come first (at the beginning)
      // This is the current implementation behavior
      expect(rows[0].findAll('td')[0].text().trim()).toBe('')
      expect(rows[1].text()).toContain('Bob')
      expect(rows[2].text()).toContain('Alice')
    })

    it('handles undefined values like null values', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Bob' },
        { id: 2 }, // name is undefined
        { id: 3, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'asc')
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].text()).toContain('Alice')
      expect(rows[1].text()).toContain('Bob')
      // Undefined should be last
      expect(rows[2].findAll('td')[0].text().trim()).toBe('')
    })

    it('handles all null values gracefully', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: null },
        { id: 2, name: null },
        { id: 3, name: null }
      ]

      const wrapper = createWrapper(columns, data, 'name', 'asc')
      
      // Should not throw error
      const rows = wrapper.findAll('tbody tr')
      expect(rows).toHaveLength(3)
    })
  })

  describe('Sort Event Emission', () => {
    it('emits sort event when column is clicked', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      
      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')).toHaveLength(1)
      expect(wrapper.emitted('sort')[0][0]).toEqual({
        field: 'name',
        direction: 'asc'
      })
    })

    it('emits sort event with correct direction on toggle', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      
      // First click - ascending
      await nameHeader.trigger('click')
      expect(wrapper.emitted('sort')[0][0]).toEqual({
        field: 'name',
        direction: 'asc'
      })
      
      // Second click - descending
      await nameHeader.trigger('click')
      expect(wrapper.emitted('sort')[1][0]).toEqual({
        field: 'name',
        direction: 'desc'
      })
    })

    it('does not emit sort event for non-sortable columns', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      
      expect(wrapper.emitted('sort')).toBeFalsy()
    })
  })

  describe('ARIA Attributes for Accessibility', () => {
    it('sets aria-sort="none" on sortable columns that are not sorted', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'age', label: 'Age', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice', age: 30 }
      ]

      const wrapper = createWrapper(columns, data)
      
      const headers = wrapper.findAll('th')
      expect(headers[0].attributes('aria-sort')).toBe('none')
      expect(headers[1].attributes('aria-sort')).toBe('none')
    })

    it('sets aria-sort="ascending" on sorted ascending column', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      
      expect(nameHeader.attributes('aria-sort')).toBe('ascending')
    })

    it('sets aria-sort="descending" on sorted descending column', async () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: true }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      await nameHeader.trigger('click')
      await nameHeader.trigger('click')
      
      expect(nameHeader.attributes('aria-sort')).toBe('descending')
    })

    it('does not set aria-sort on non-sortable columns', () => {
      const columns = [
        { key: 'name', label: 'Name', sortable: false }
      ]
      const data = [
        { id: 1, name: 'Alice' }
      ]

      const wrapper = createWrapper(columns, data)
      
      const nameHeader = wrapper.find('th')
      expect(nameHeader.attributes('aria-sort')).toBeUndefined()
    })
  })
})
