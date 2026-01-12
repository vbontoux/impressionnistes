import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useTableSort } from './useTableSort'

describe('useTableSort', () => {
  it('should sort strings alphabetically', () => {
    const data = ref([
      { id: 1, name: 'Charlie' },
      { id: 2, name: 'Alice' },
      { id: 3, name: 'Bob' }
    ])

    const { sortedData, sortBy } = useTableSort(data, 'name', 'asc')

    expect(sortedData.value[0].name).toBe('Alice')
    expect(sortedData.value[1].name).toBe('Bob')
    expect(sortedData.value[2].name).toBe('Charlie')
  })

  it('should sort numbers correctly', () => {
    const data = ref([
      { id: 1, age: 30 },
      { id: 2, age: 20 },
      { id: 3, age: 25 }
    ])

    const { sortedData } = useTableSort(data, 'age', 'asc')

    expect(sortedData.value[0].age).toBe(20)
    expect(sortedData.value[1].age).toBe(25)
    expect(sortedData.value[2].age).toBe(30)
  })

  it('should toggle sort direction', () => {
    const data = ref([
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' }
    ])

    const { sortedData, sortBy, sortDirection } = useTableSort(data, 'name', 'asc')

    expect(sortedData.value[0].name).toBe('Alice')
    expect(sortDirection.value).toBe('asc')

    sortBy('name')
    expect(sortDirection.value).toBe('desc')
    expect(sortedData.value[0].name).toBe('Bob')
  })

  it('should handle boat number sorting correctly', () => {
    const data = ref([
      { id: 1, boat_number: 'SM.2.3' },
      { id: 2, boat_number: 'M.1.1' },
      { id: 3, boat_number: 'SM.2.1' },
      { id: 4, boat_number: 'M.1.5' }
    ])

    const { sortedData } = useTableSort(data, 'boat_number', 'asc')

    // M comes before SM, then sorted by order and sequence
    expect(sortedData.value[0].boat_number).toBe('M.1.1')
    expect(sortedData.value[1].boat_number).toBe('M.1.5')
    expect(sortedData.value[2].boat_number).toBe('SM.2.1')
    expect(sortedData.value[3].boat_number).toBe('SM.2.3')
  })

  it('should handle null values', () => {
    const data = ref([
      { id: 1, name: 'Alice' },
      { id: 2, name: null },
      { id: 3, name: 'Bob' }
    ])

    const { sortedData } = useTableSort(data, 'name', 'asc')

    // Null values should be sorted to the end
    expect(sortedData.value[0].name).toBe('Alice')
    expect(sortedData.value[1].name).toBe('Bob')
    expect(sortedData.value[2].name).toBe(null)
  })

  it('should return unsorted data when no sort field is set', () => {
    const data = ref([
      { id: 1, name: 'Charlie' },
      { id: 2, name: 'Alice' },
      { id: 3, name: 'Bob' }
    ])

    const { sortedData } = useTableSort(data, '', 'asc')

    expect(sortedData.value[0].name).toBe('Charlie')
    expect(sortedData.value[1].name).toBe('Alice')
    expect(sortedData.value[2].name).toBe('Bob')
  })

  it('should provide sort indicator', () => {
    const data = ref([{ id: 1, name: 'Alice' }])
    const { getSortIndicator, sortBy } = useTableSort(data, 'name', 'asc')

    expect(getSortIndicator('name')).toBe('▲')
    expect(getSortIndicator('other')).toBe('')

    sortBy('name')
    expect(getSortIndicator('name')).toBe('▼')
  })

  it('should check if field is sorted', () => {
    const data = ref([{ id: 1, name: 'Alice' }])
    const { isSortedBy } = useTableSort(data, 'name', 'asc')

    expect(isSortedBy('name')).toBe(true)
    expect(isSortedBy('other')).toBe(false)
  })
})
