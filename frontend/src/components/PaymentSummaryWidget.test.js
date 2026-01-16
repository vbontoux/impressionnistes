/**
 * PaymentSummaryWidget Component Tests
 * 
 * Minimal tests for payment summary widget
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import PaymentSummaryWidget from './PaymentSummaryWidget.vue';
import paymentService from '../services/paymentService';

// Mock payment service
vi.mock('../services/paymentService', () => ({
  default: {
    getPaymentSummary: vi.fn()
  }
}));

// Mock router
const mockPush = vi.fn();
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}));

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      payment: {
        summary: {
          title: 'Payment Summary',
          viewAll: 'View All',
          totalPaid: 'Total Paid',
          paymentCount: 'Payments',
          boatsPaid: 'Boats Paid',
          outstanding: 'Outstanding Balance',
          unpaidBoats: 'Unpaid Boats',
          makePayment: 'Make Payment',
          errorLoading: 'Failed to load payment summary'
        }
      },
      common: {
        loading: 'Loading...'
      }
    }
  }
});

describe('PaymentSummaryWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays summary data correctly', async () => {
    // Mock summary data
    const mockSummary = {
      paid: {
        total_amount: 500.00,
        currency: 'EUR',
        payment_count: 5,
        boat_count: 10
      },
      outstanding: {
        total_amount: 100.00,
        currency: 'EUR',
        boat_count: 2
      }
    };

    paymentService.getPaymentSummary.mockResolvedValue(mockSummary);

    const wrapper = mount(PaymentSummaryWidget, {
      global: {
        plugins: [i18n],
        stubs: {
          LoadingSpinner: true,
          MessageAlert: true,
          BaseButton: true
        }
      }
    });

    // Wait for data to load
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Check that summary data is displayed
    expect(wrapper.vm.summary.paid.total_amount).toBe(500.00);
    expect(wrapper.vm.summary.paid.payment_count).toBe(5);
    expect(wrapper.vm.summary.outstanding.total_amount).toBe(100.00);
  });

  it('highlights outstanding balance when greater than zero', async () => {
    // Mock summary with outstanding balance
    const mockSummary = {
      paid: {
        total_amount: 500.00,
        currency: 'EUR',
        payment_count: 5,
        boat_count: 10
      },
      outstanding: {
        total_amount: 100.00,
        currency: 'EUR',
        boat_count: 2
      }
    };

    paymentService.getPaymentSummary.mockResolvedValue(mockSummary);

    const wrapper = mount(PaymentSummaryWidget, {
      global: {
        plugins: [i18n],
        stubs: {
          LoadingSpinner: true,
          MessageAlert: true,
          BaseButton: true
        }
      }
    });

    // Wait for data to load
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Check that outstanding balance is highlighted
    expect(wrapper.vm.hasOutstanding).toBe(true);
  });
});
