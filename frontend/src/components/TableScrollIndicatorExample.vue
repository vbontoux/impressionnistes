<!--
  TableScrollIndicator Example Component
  
  This is a test/example component to demonstrate the TableScrollIndicator
  in action. It can be used for testing and as a reference implementation.
  
  To test this component:
  1. Import it in a view or route
  2. View on mobile device or browser mobile emulation
  3. Scroll the table horizontally to see indicators
  
  This file can be deleted after testing is complete.
-->

<template>
  <div class="example-container">
    <h2>TableScrollIndicator Example</h2>
    
    <p class="example-description">
      This example demonstrates the TableScrollIndicator component.
      On mobile devices, scroll the table horizontally to see gradient indicators.
    </p>
    
    <!-- Example 1: Simple table with scroll indicators -->
    <section class="example-section">
      <h3>Example 1: Simple Data Table</h3>
      <TableScrollIndicator aria-label="Sample crew members table">
        <table class="sample-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Age</th>
              <th>License</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in sampleData" :key="member.id">
              <td>{{ member.name }}</td>
              <td>{{ member.email }}</td>
              <td>{{ member.role }}</td>
              <td>{{ member.age }}</td>
              <td>{{ member.license }}</td>
              <td>
                <span :class="['status-badge', member.status]">
                  {{ member.status }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-sm">Edit</button>
                  <button class="btn-sm">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </TableScrollIndicator>
    </section>
    
    <!-- Example 2: Custom styled indicators -->
    <section class="example-section">
      <h3>Example 2: Custom Indicator Color</h3>
      <TableScrollIndicator
        indicator-color="rgba(74, 144, 226, 0.2)"
        :indicator-width="30"
        aria-label="Custom styled table"
      >
        <table class="sample-table custom-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Supplier</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in productData" :key="product.id">
              <td>{{ product.name }}</td>
              <td>{{ product.category }}</td>
              <td>{{ product.price }}</td>
              <td>{{ product.stock }}</td>
              <td>{{ product.supplier }}</td>
              <td>{{ product.updated }}</td>
            </tr>
          </tbody>
        </table>
      </TableScrollIndicator>
    </section>
    
    <!-- Example 3: Disabled indicators -->
    <section class="example-section">
      <h3>Example 3: Indicators Disabled</h3>
      <p class="note">This table has indicators disabled for comparison.</p>
      <TableScrollIndicator :disabled="true">
        <table class="sample-table">
          <thead>
            <tr>
              <th>Column 1</th>
              <th>Column 2</th>
              <th>Column 3</th>
              <th>Column 4</th>
              <th>Column 5</th>
              <th>Column 6</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in 3" :key="i">
              <td>Data {{ i }}-1</td>
              <td>Data {{ i }}-2</td>
              <td>Data {{ i }}-3</td>
              <td>Data {{ i }}-4</td>
              <td>Data {{ i }}-5</td>
              <td>Data {{ i }}-6</td>
            </tr>
          </tbody>
        </table>
      </TableScrollIndicator>
    </section>
    
    <div class="testing-notes">
      <h3>Testing Notes</h3>
      <ul>
        <li>Resize browser to mobile width (&lt; 768px) to see indicators</li>
        <li>Scroll tables horizontally to see indicators appear/disappear</li>
        <li>On tablet/desktop (≥ 768px), indicators are hidden</li>
        <li>Test on actual mobile devices for best results</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TableScrollIndicator from './TableScrollIndicator.vue'

// Sample data for examples
const sampleData = ref([
  {
    id: 1,
    name: 'Jean Dupont',
    email: 'jean.dupont@example.com',
    role: 'Rameur',
    age: 28,
    license: 'FR-12345',
    status: 'active'
  },
  {
    id: 2,
    name: 'Marie Martin',
    email: 'marie.martin@example.com',
    role: 'Barreur',
    age: 32,
    license: 'FR-67890',
    status: 'active'
  },
  {
    id: 3,
    name: 'Pierre Bernard',
    email: 'pierre.bernard@example.com',
    role: 'Rameur',
    age: 45,
    license: 'FR-11223',
    status: 'inactive'
  },
  {
    id: 4,
    name: 'Sophie Dubois',
    email: 'sophie.dubois@example.com',
    role: 'Rameur',
    age: 26,
    license: 'FR-44556',
    status: 'active'
  }
])

const productData = ref([
  {
    id: 1,
    name: 'Rowing Shell',
    category: 'Equipment',
    price: '€5,000',
    stock: 12,
    supplier: 'Marine Sports Inc.',
    updated: '2024-12-15'
  },
  {
    id: 2,
    name: 'Oars Set',
    category: 'Equipment',
    price: '€450',
    stock: 25,
    supplier: 'Rowing Gear Co.',
    updated: '2024-12-18'
  },
  {
    id: 3,
    name: 'Life Jacket',
    category: 'Safety',
    price: '€85',
    stock: 50,
    supplier: 'Safety First Ltd.',
    updated: '2024-12-20'
  }
])
</script>

<style scoped>
.example-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 767px) {
  .example-container {
    padding: 1rem;
  }
}

h2 {
  margin-bottom: 1rem;
  color: #333;
}

.example-description {
  margin-bottom: 2rem;
  color: #666;
  line-height: 1.6;
}

.example-section {
  margin-bottom: 3rem;
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (max-width: 767px) {
  .example-section {
    padding: 1rem;
  }
}

.example-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.25rem;
}

.note {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  color: #856404;
  font-size: 0.875rem;
}

/* Sample table styles */
.sample-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 700px; /* Forces horizontal scroll on mobile */
}

.sample-table th,
.sample-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
}

.sample-table th {
  font-weight: 600;
  background: #f5f5f5;
  color: #333;
}

.sample-table tbody tr:hover {
  background: #f9f9f9;
}

/* Custom table variant */
.custom-table th {
  background: #e3f2fd;
  color: #1976d2;
}

/* Status badge */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

/* Action buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  min-height: 32px;
  white-space: nowrap;
}

.btn-sm:hover {
  background: #f5f5f5;
}

/* Testing notes */
.testing-notes {
  margin-top: 3rem;
  padding: 1.5rem;
  background: #e8f4f8;
  border-radius: 8px;
  border-left: 4px solid #4A90E2;
}

.testing-notes h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #1976d2;
}

.testing-notes ul {
  margin: 0;
  padding-left: 1.5rem;
  color: #333;
}

.testing-notes li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

@media (min-width: 768px) {
  .sample-table {
    min-width: auto; /* Remove minimum width on larger screens */
  }
  
  .sample-table th,
  .sample-table td {
    white-space: normal; /* Allow text wrapping */
  }
}
</style>
