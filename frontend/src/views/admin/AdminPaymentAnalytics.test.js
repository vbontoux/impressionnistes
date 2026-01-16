import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import AdminPaymentAnalytics from './AdminPaymentAnalytics.vue';

// Mock payment service with default export
vi.mock('../../services/paymentService', () => ({
  default: {
    getAllPayments: vi.fn(),
    getPaymentAnalytics: vi.fn(),
  },
}));

import paymentService from '../../services/paymentService';

// Create i18n instance with all required keys
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      admin: {
        paymentAnalytics: {
          title: 'Payment Analytics',
          subtitle: 'View payment statistics and trends',
          totalRevenue: 'Total Revenue',
          totalPayments: 'Total Payments',
          outstandingBalance: 'Outstanding Balance',
          boatsPaid: 'Boats Paid',
          topPayers: 'Top Payers',
          rank: 'Rank',
          teamManager: 'Team Manager',
          totalPaid: 'Total Paid',
          payments: 'Payments',
          boats: 'Boats',
          startDate: 'Start Date',
          endDate: 'End Date',
          groupBy: 'Group By',
          day: 'Day',
          week: 'Week',
          month: 'Month',
          exportCSV: 'Export CSV',
          errorLoading: 'Failed to load payment analytics',
        },
        boats: {
          clearFilters: 'Clear Filters',
        },
      },
      common: {
        loading: 'Loading...',
        cardView: 'Card View',
        tableView: 'Table View',
      },
    },
  },
});

describe('AdminPaymentAnalytics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the component', () => {
    paymentService.getPaymentAnalytics.mockResolvedValue({
      total_revenue: 5000,
      total_payments: 10,
      outstanding_balance: 1000,
      total_boats_paid: 8,
      top_team_managers: [],
    });

    const wrapper = mount(AdminPaymentAnalytics, {
      global: {
        plugins: [i18n],
        stubs: {
          ListHeader: true,
          ListFilters: true,
        },
      },
    });

    // Component should render
    expect(wrapper.exists()).toBe(true);
  });

  it('displays summary cards with analytics data', async () => {
    const mockData = {
      total_revenue: 5000,
      total_payments: 10,
      outstanding_balance: 1000,
      total_boats_paid: 8,
      top_team_managers: [],
    };

    paymentService.getPaymentAnalytics.mockResolvedValue(mockData);

    const wrapper = mount(AdminPaymentAnalytics, {
      global: {
        plugins: [i18n],
        stubs: {
          ListHeader: true,
          ListFilters: true,
        },
      },
    });

    // Wait for component to mount and data to load
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 100));

    // Check that summary data is displayed
    const text = wrapper.text();
    expect(text).toContain('5,000');  // Formatted currency
    expect(text).toContain('10');
  });
});
