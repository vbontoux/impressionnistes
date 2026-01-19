/**
 * PaymentHistory Component Tests
 * 
 * Minimal tests for payment history page
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import PaymentHistory from './PaymentHistory.vue';
import paymentService from '../services/paymentService';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'table'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Mock payment service
vi.mock('../services/paymentService', () => ({
  default: {
    getPaymentHistory: vi.fn()
  }
}));

// Mock composables
vi.mock('../composables/useTableSort', () => ({
  useTableSort: () => ({
    sortField: { value: 'paid_at' },
    sortDirection: { value: 'desc' },
    handleSort: vi.fn(),
    getSortIndicator: vi.fn(() => '')
  })
}));

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      payment: {
        history: {
          title: 'Payment History',
          subtitle: 'View your past payments',
          search: 'Search payments...',
          startDate: 'Start Date',
          endDate: 'End Date',
          date: 'Date',
          amount: 'Amount',
          boats: 'Boats',
          status: 'Status',
          noPayments: 'No payments found',
          viewReceipt: 'View Receipt',
          downloadInvoice: 'Download Invoice',
          errorLoading: 'Failed to load payment history'
        }
      },
      common: {
        loading: 'Loading...',
        actions: 'Actions'
      }
    }
  }
});

describe('PaymentHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders table with payment data', async () => {
    // Mock payment data
    const mockPayments = [
      {
        payment_id: 'pay_123',
        paid_at: '2026-01-15T10:30:00Z',
        amount: 100.00,
        currency: 'EUR',
        status: 'succeeded',
        boat_registration_ids: ['boat_1', 'boat_2'],
        stripe_receipt_url: 'https://stripe.com/receipt'
      }
    ];

    paymentService.getPaymentHistory.mockResolvedValue({
      payments: mockPayments
    });

    const wrapper = mount(PaymentHistory, {
      global: {
        plugins: [i18n],
        stubs: {
          ListHeader: true,
          ListFilters: true,
          LoadingSpinner: true,
          MessageAlert: true,
          EmptyState: true,
          DataCard: true,
          StatusBadge: true,
          BaseButton: true,
          SortableTable: true,
          BaseModal: true
        }
      }
    });

    // Wait for data to load
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Check that payment data is rendered
    expect(wrapper.vm.payments).toHaveLength(1);
    expect(wrapper.vm.payments[0].payment_id).toBe('pay_123');
    expect(wrapper.vm.payments[0].amount).toBe(100.00);
  });

  it('renders empty state when no payments', async () => {
    // Mock empty payment data
    paymentService.getPaymentHistory.mockResolvedValue({
      payments: []
    });

    const wrapper = mount(PaymentHistory, {
      global: {
        plugins: [i18n],
        stubs: {
          ListHeader: true,
          ListFilters: true,
          LoadingSpinner: true,
          MessageAlert: true,
          EmptyState: true,
          DataCard: true,
          StatusBadge: true,
          BaseButton: true,
          SortableTable: true,
          BaseModal: true
        }
      }
    });

    // Wait for data to load
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Check that empty state is shown
    expect(wrapper.vm.payments).toHaveLength(0);
    expect(wrapper.vm.filteredPayments).toHaveLength(0);
  });
});
