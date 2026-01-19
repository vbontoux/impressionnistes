import { describe, it, expect } from 'vitest'
import { useTableKeyboard } from './useTableKeyboard'

describe('useTableKeyboard', () => {
  it('should export useTableKeyboard function', () => {
    expect(useTableKeyboard).toBeDefined()
    expect(typeof useTableKeyboard).toBe('function')
  })

  it('should accept tableRef and sortByField parameters', () => {
    // This test verifies the function signature
    // Actual functionality is tested through integration tests with SortableTable component
    expect(useTableKeyboard.length).toBe(2)
  })
})
