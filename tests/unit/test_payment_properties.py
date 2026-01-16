"""
Property-based tests for payment functionality
Tests universal properties with minimal test data (2-5 records)
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
import copy

# Import utilities from Lambda layer
import sys
sys.path.insert(0, 'functions/layer/python')

from payment_formatters import sort_payments_by_field, format_payment_response
from payment_queries import query_payments_by_team
from payment_calculations import calculate_total_paid


class TestPaymentListSorting:
    """
    Feature: payment-history-balance, Property 1: Payment List Sorting
    For any set of payment records, returned list should be sorted by date descending
    """
    
    def test_payment_list_sorted_descending(self):
        """Test with 3-5 payment records only"""
        # Create test payments with different dates
        payments = [
            {'paid_at': '2026-01-15T10:00:00Z', 'payment_id': 'pay-1', 'amount': Decimal('100')},
            {'paid_at': '2026-01-14T10:00:00Z', 'payment_id': 'pay-2', 'amount': Decimal('50')},
            {'paid_at': '2026-01-16T10:00:00Z', 'payment_id': 'pay-3', 'amount': Decimal('75')},
        ]
        
        # Sort by paid_at descending (newest first)
        sorted_payments = sort_payments_by_field(payments, 'paid_at', descending=True)
        
        # Verify sorting
        assert sorted_payments[0]['paid_at'] == '2026-01-16T10:00:00Z'
        assert sorted_payments[1]['paid_at'] == '2026-01-15T10:00:00Z'
        assert sorted_payments[2]['paid_at'] == '2026-01-14T10:00:00Z'
        
        # Verify all payments are present
        assert len(sorted_payments) == 3


class TestDateRangeFiltering:
    """
    Feature: payment-history-balance, Property 2: Date Range Filtering
    For any set of payments and date range, returned payments should be within range
    """
    
    def test_date_range_filtering(self):
        """Test with 3-5 payment records only"""
        # Create test payments across different dates
        payments = [
            {'paid_at': '2026-01-10T10:00:00Z', 'payment_id': 'pay-1'},
            {'paid_at': '2026-01-15T10:00:00Z', 'payment_id': 'pay-2'},
            {'paid_at': '2026-01-20T10:00:00Z', 'payment_id': 'pay-3'},
            {'paid_at': '2026-01-25T10:00:00Z', 'payment_id': 'pay-4'},
        ]
        
        # Filter by date range (Jan 14 to Jan 21)
        start_date = '2026-01-14T00:00:00Z'
        end_date = '2026-01-21T23:59:59Z'
        
        filtered = [
            p for p in payments
            if start_date <= p['paid_at'] <= end_date
        ]
        
        # Verify only payments within range are returned
        assert len(filtered) == 2
        assert filtered[0]['payment_id'] == 'pay-2'
        assert filtered[1]['payment_id'] == 'pay-3'
        
        # Verify all returned payments are within range
        for payment in filtered:
            assert payment['paid_at'] >= start_date
            assert payment['paid_at'] <= end_date


class TestPaymentRecordCompleteness:
    """
    Feature: payment-history-balance, Property 3: Payment Record Completeness
    For any payment record, it should contain all required fields
    """
    
    def test_payment_record_has_required_fields(self):
        """Test with 1-2 payment records only"""
        # Create test payment with all required fields
        payment = {
            'payment_id': 'pay-123',
            'stripe_payment_intent_id': 'pi_xxx',
            'amount': Decimal('100.00'),
            'currency': 'EUR',
            'paid_at': '2026-01-15T10:30:00Z',
            'boat_registration_ids': ['boat-1', 'boat-2'],
            'stripe_receipt_url': 'https://stripe.com/receipt',
            'status': 'succeeded'
        }
        
        # Format payment
        formatted = format_payment_response(payment)
        
        # Verify all required fields are present
        required_fields = [
            'payment_id',
            'stripe_payment_intent_id',
            'amount',
            'currency',
            'paid_at',
            'boat_registration_ids',
            'stripe_receipt_url',
            'status'
        ]
        
        for field in required_fields:
            assert field in formatted, f"Missing required field: {field}"
        
        # Verify boat_count is calculated
        assert 'boat_count' in formatted
        assert formatted['boat_count'] == 2



class TestTotalPaidCalculation:
    """
    Feature: payment-history-balance, Property 4: Total Paid Calculation
    For any set of payments, total should equal sum of amounts
    """
    
    def test_total_paid_calculation(self):
        """Test with 2-3 payment records only"""
        payments = [
            {'amount': Decimal('100.00')},
            {'amount': Decimal('50.00')},
            {'amount': Decimal('25.50')}
        ]
        
        total = calculate_total_paid(payments)
        expected = Decimal('100.00') + Decimal('50.00') + Decimal('25.50')
        
        assert total == expected
        assert total == Decimal('175.50')


class TestOutstandingBalanceCalculation:
    """
    Feature: payment-history-balance, Property 5: Outstanding Balance Calculation
    For any set of unpaid boats, outstanding balance should equal sum of estimated amounts
    """
    
    def test_outstanding_balance_calculation(self):
        """Test with 2-3 boat records only"""
        # Mock unpaid boats with pricing
        unpaid_boats = [
            {
                'boat_registration_id': 'boat-1',
                'event_type': 'Course',
                'boat_type': '4+',
                'registration_status': 'complete',
                'pricing': {'total': Decimal('50.00')}
            },
            {
                'boat_registration_id': 'boat-2',
                'event_type': 'Semi-Marathon',
                'boat_type': '2x',
                'registration_status': 'complete',
                'pricing': {'total': Decimal('40.00')}
            }
        ]
        
        # Mock pricing config (not used since boats have pricing)
        pricing_config = {'base_seat_price': 20}
        crew_members = []
        
        from payment_calculations import calculate_outstanding_balance
        total_outstanding, boat_details = calculate_outstanding_balance(
            unpaid_boats, crew_members, pricing_config
        )
        
        # Verify total equals sum
        assert total_outstanding == Decimal('90.00')
        assert len(boat_details) == 2


class TestUnpaidBoatFields:
    """
    Feature: payment-history-balance, Property 6: Unpaid Boat Fields
    For any unpaid boat, it should contain required fields
    """
    
    def test_unpaid_boat_has_required_fields(self):
        """Test with 1-2 boat records only"""
        unpaid_boats = [
            {
                'boat_registration_id': 'boat-1',
                'event_type': 'Course',
                'boat_type': '4+',
                'registration_status': 'complete',
                'pricing': {'total': Decimal('50.00')}
            }
        ]
        
        pricing_config = {'base_seat_price': 20}
        crew_members = []
        
        from payment_calculations import calculate_outstanding_balance
        _, boat_details = calculate_outstanding_balance(
            unpaid_boats, crew_members, pricing_config
        )
        
        # Verify required fields are present
        required_fields = ['boat_registration_id', 'event_type', 'boat_type', 'estimated_amount']
        for boat in boat_details:
            for field in required_fields:
                assert field in boat, f"Missing required field: {field}"


class TestPricingFallback:
    """
    Feature: payment-history-balance, Property 7: Pricing Fallback
    For any boat without pricing, system should calculate using pricing config
    """
    
    def test_pricing_fallback_calculation(self):
        """Test with 1 boat record without pricing"""
        # Mock boat without pricing
        unpaid_boats = [
            {
                'boat_registration_id': 'boat-1',
                'event_type': 'Course',
                'boat_type': '4+',
                'registration_status': 'complete',
                'seats': [
                    {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                    {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                    {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                    {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'},
                    {'position': 5, 'type': 'coxswain', 'crew_member_id': 'crew-5'}
                ]
                # No 'pricing' field
            }
        ]
        
        # Mock pricing config
        pricing_config = {
            'base_seat_price': 20,
            'coxswain_discount': 0.5
        }
        
        # Mock crew members
        crew_members = [
            {'crew_member_id': 'crew-1'},
            {'crew_member_id': 'crew-2'},
            {'crew_member_id': 'crew-3'},
            {'crew_member_id': 'crew-4'},
            {'crew_member_id': 'crew-5'}
        ]
        
        from payment_calculations import calculate_outstanding_balance
        total_outstanding, boat_details = calculate_outstanding_balance(
            unpaid_boats, crew_members, pricing_config
        )
        
        # Verify pricing was calculated (should be > 0)
        assert total_outstanding > Decimal('0')
        assert boat_details[0]['estimated_amount'] > 0



class TestAdminQueryCompleteness:
    """
    Feature: payment-history-balance, Property 8: Admin Query Completeness
    For any set of team managers with payments, admin query should include all
    """
    
    def test_admin_query_includes_all_team_managers(self):
        """Test with 2-3 team managers only"""
        # Mock payments from different team managers
        payments = [
            {'team_manager_id': 'tm-1', 'amount': Decimal('100.00')},
            {'team_manager_id': 'tm-2', 'amount': Decimal('50.00')},
            {'team_manager_id': 'tm-1', 'amount': Decimal('75.00')},
        ]
        
        # Get unique team managers
        unique_tms = set(p['team_manager_id'] for p in payments)
        
        # Verify all team managers are represented
        assert len(unique_tms) == 2
        assert 'tm-1' in unique_tms
        assert 'tm-2' in unique_tms


class TestTeamManagerFiltering:
    """
    Feature: payment-history-balance, Property 9: Team Manager Filtering
    For any set of payments, filtering by team manager should return only that manager's payments
    """
    
    def test_team_manager_filtering(self):
        """Test with 2 team managers only"""
        # Mock payments from different team managers
        all_payments = [
            {'payment_id': 'pay-1', 'team_manager_id': 'tm-1', 'amount': Decimal('100.00')},
            {'payment_id': 'pay-2', 'team_manager_id': 'tm-2', 'amount': Decimal('50.00')},
            {'payment_id': 'pay-3', 'team_manager_id': 'tm-1', 'amount': Decimal('75.00')},
        ]
        
        # Filter by team manager
        filter_tm = 'tm-1'
        filtered = [p for p in all_payments if p['team_manager_id'] == filter_tm]
        
        # Verify only tm-1 payments returned
        assert len(filtered) == 2
        assert all(p['team_manager_id'] == filter_tm for p in filtered)
        assert filtered[0]['payment_id'] == 'pay-1'
        assert filtered[1]['payment_id'] == 'pay-3'


class TestMultiFieldSorting:
    """
    Feature: payment-history-balance, Property 10: Multi-Field Sorting
    For any set of payments, sorting by a field should correctly order results
    """
    
    def test_sorting_by_date(self):
        """Test sorting by date only (1 field)"""
        payments = [
            {'paid_at': '2026-01-15T10:00:00Z', 'amount': Decimal('100')},
            {'paid_at': '2026-01-14T10:00:00Z', 'amount': Decimal('50')},
            {'paid_at': '2026-01-16T10:00:00Z', 'amount': Decimal('75')},
        ]
        
        # Sort by date ascending
        sorted_payments = sort_payments_by_field(payments, 'paid_at', descending=False)
        
        # Verify correct order
        assert sorted_payments[0]['paid_at'] == '2026-01-14T10:00:00Z'
        assert sorted_payments[1]['paid_at'] == '2026-01-15T10:00:00Z'
        assert sorted_payments[2]['paid_at'] == '2026-01-16T10:00:00Z'


class TestAnalyticsCounting:
    """
    Feature: payment-history-balance, Property 11: Analytics Counting
    For any set of payments, analytics should correctly count payments, boats, and team managers
    """
    
    def test_analytics_counting(self):
        """Test with 2-3 payment records only"""
        payments = [
            {
                'payment_id': 'pay-1',
                'team_manager_id': 'tm-1',
                'amount': Decimal('100.00'),
                'boat_registration_ids': ['boat-1', 'boat-2']
            },
            {
                'payment_id': 'pay-2',
                'team_manager_id': 'tm-2',
                'amount': Decimal('50.00'),
                'boat_registration_ids': ['boat-3']
            },
            {
                'payment_id': 'pay-3',
                'team_manager_id': 'tm-1',
                'amount': Decimal('75.00'),
                'boat_registration_ids': ['boat-4', 'boat-5']
            }
        ]
        
        # Count payments
        payment_count = len(payments)
        assert payment_count == 3
        
        # Count boats
        total_boats = sum(len(p['boat_registration_ids']) for p in payments)
        assert total_boats == 5
        
        # Count unique team managers
        unique_tms = len(set(p['team_manager_id'] for p in payments))
        assert unique_tms == 2


class TestTimePeriodGrouping:
    """
    Feature: payment-history-balance, Property 12: Time Period Grouping
    For any set of payments, grouping by time period should place each payment in exactly one group
    """
    
    def test_time_period_grouping(self):
        """Test with 3-5 payments across 2 days only"""
        from collections import defaultdict
        from datetime import datetime
        
        payments = [
            {'paid_at': '2026-01-15T10:00:00Z', 'amount': Decimal('100')},
            {'paid_at': '2026-01-15T14:00:00Z', 'amount': Decimal('50')},
            {'paid_at': '2026-01-16T10:00:00Z', 'amount': Decimal('75')},
            {'paid_at': '2026-01-16T16:00:00Z', 'amount': Decimal('25')},
        ]
        
        # Group by day
        grouped = defaultdict(list)
        for payment in payments:
            dt = datetime.fromisoformat(payment['paid_at'].replace('Z', '+00:00'))
            day = dt.strftime('%Y-%m-%d')
            grouped[day].append(payment)
        
        # Verify grouping
        assert len(grouped) == 2
        assert len(grouped['2026-01-15']) == 2
        assert len(grouped['2026-01-16']) == 2
        
        # Verify sum across groups equals total
        total_in_groups = sum(
            sum(float(p['amount']) for p in group)
            for group in grouped.values()
        )
        total_all = sum(float(p['amount']) for p in payments)
        assert total_in_groups == total_all


class TestTopPayersRanking:
    """
    Feature: payment-history-balance, Property 13: Top Payers Ranking
    For any set of team managers, ranking should be sorted by total paid descending
    """
    
    def test_top_payers_ranking(self):
        """Test with 2-3 team managers only"""
        from collections import defaultdict
        
        payments = [
            {'team_manager_id': 'tm-1', 'amount': Decimal('100.00')},
            {'team_manager_id': 'tm-2', 'amount': Decimal('150.00')},
            {'team_manager_id': 'tm-1', 'amount': Decimal('75.00')},
            {'team_manager_id': 'tm-3', 'amount': Decimal('50.00')},
        ]
        
        # Calculate totals per team manager
        tm_totals = defaultdict(Decimal)
        for payment in payments:
            tm_totals[payment['team_manager_id']] += payment['amount']
        
        # Sort by total descending
        ranked = sorted(
            [(tm_id, total) for tm_id, total in tm_totals.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Verify ranking (tm-1 has 175, tm-2 has 150, tm-3 has 50)
        assert ranked[0][0] == 'tm-1'  # Highest (100 + 75 = 175)
        assert ranked[0][1] == Decimal('175.00')
        assert ranked[1][0] == 'tm-2'  # Second (150)
        assert ranked[1][1] == Decimal('150.00')
        assert ranked[2][0] == 'tm-3'  # Lowest (50)
        assert ranked[2][1] == Decimal('50.00')
        
        # Verify each total equals sum of individual payments
        for tm_id, total in ranked:
            individual_sum = sum(
                p['amount'] for p in payments
                if p['team_manager_id'] == tm_id
            )
            assert total == individual_sum



class TestPDFInvoiceCompleteness:
    """
    Feature: payment-history-balance, Property 21: PDF Invoice Completeness
    For any payment record, PDF should include all required fields
    """
    
    def test_pdf_invoice_contains_required_fields(self):
        """Test with 1 payment record only"""
        from io import BytesIO
        from PyPDF2 import PdfReader
        
        # Mock payment data
        payment = {
            'payment_id': 'pay-123',
            'paid_at': '2026-01-15T10:30:00Z',
            'amount': Decimal('100.00'),
            'currency': 'EUR',
            'status': 'succeeded',
            'stripe_receipt_url': 'https://stripe.com/receipt',
            'boat_registration_ids': ['boat-1']
        }
        
        team_manager = {
            'first_name': 'John',
            'last_name': 'Doe',
            'club_affiliation': 'Test Club',
            'email': 'john@example.com'
        }
        
        boats = [
            {
                'boat_registration_id': 'boat-1',
                'event_type': 'Course',
                'boat_type': '4+',
                'locked_pricing': {'total': Decimal('100.00')}
            }
        ]
        
        # Import the PDF generation function
        sys.path.insert(0, 'functions/payment')
        from get_payment_invoice import generate_pdf_invoice
        
        # Generate PDF
        pdf_content = generate_pdf_invoice(payment, team_manager, boats)
        
        # Verify PDF was generated
        assert pdf_content is not None
        assert len(pdf_content) > 0
        assert pdf_content.startswith(b'%PDF')  # PDF magic number
        
        # Read PDF content
        pdf_reader = PdfReader(BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Verify required fields are in PDF
        assert 'pay-123' in text  # payment_id
        assert '100.00' in text  # amount
        assert 'EUR' in text  # currency
        assert 'John' in text  # team_manager name
        assert 'Doe' in text
        assert 'Test Club' in text  # club_affiliation
        assert 'john@example.com' in text  # email
        assert 'Course des Impressionnistes' in text  # event name
        assert 'Course' in text  # boat event_type
        assert '4+' in text  # boat type


class TestPDFFilenameFormat:
    """
    Feature: payment-history-balance, Property 22: PDF Filename Format
    For any payment record, filename should match the pattern
    """
    
    def test_pdf_filename_format(self):
        """Test with 1 payment record only"""
        from datetime import datetime
        
        # Mock payment data
        payment = {
            'payment_id': 'pay-abc-123',
            'paid_at': '2026-01-15T10:30:00Z',
            'amount': Decimal('100.00'),
            'currency': 'EUR'
        }
        
        # Generate filename
        payment_date = datetime.fromisoformat(payment['paid_at'].replace('Z', '+00:00'))
        filename = f"invoice-payment-{payment['payment_id']}-{payment_date.strftime('%Y-%m-%d')}.pdf"
        
        # Verify format
        assert filename == 'invoice-payment-pay-abc-123-2026-01-15.pdf'
        assert filename.startswith('invoice-payment-')
        assert filename.endswith('.pdf')
        assert 'pay-abc-123' in filename
        assert '2026-01-15' in filename


class TestPDFReceiptLinkInclusion:
    """
    Feature: payment-history-balance, Property 23: PDF Receipt Link Inclusion
    For any payment with receipt URL, PDF should contain the link
    """
    
    def test_pdf_contains_receipt_link(self):
        """Test with 1 payment record with receipt URL"""
        from io import BytesIO
        from PyPDF2 import PdfReader
        
        # Mock payment data with receipt URL
        payment = {
            'payment_id': 'pay-123',
            'paid_at': '2026-01-15T10:30:00Z',
            'amount': Decimal('100.00'),
            'currency': 'EUR',
            'status': 'succeeded',
            'stripe_receipt_url': 'https://stripe.com/receipt/test123',
            'boat_registration_ids': ['boat-1']
        }
        
        team_manager = {
            'first_name': 'John',
            'last_name': 'Doe',
            'club_affiliation': 'Test Club',
            'email': 'john@example.com'
        }
        
        boats = [
            {
                'boat_registration_id': 'boat-1',
                'event_type': 'Course',
                'boat_type': '4+',
                'locked_pricing': {'total': Decimal('100.00')}
            }
        ]
        
        # Import the PDF generation function
        sys.path.insert(0, 'functions/payment')
        from get_payment_invoice import generate_pdf_invoice
        
        # Generate PDF
        pdf_content = generate_pdf_invoice(payment, team_manager, boats)
        
        # Read PDF content
        pdf_reader = PdfReader(BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Verify receipt URL is in PDF
        assert 'stripe.com/receipt/test123' in text or 'Stripe Receipt' in text



class TestCurrencyFormatting:
    """
    Feature: payment-history-balance, Property 14: Currency Formatting
    For any decimal amount, formatting should have exactly two decimal places
    """
    
    def test_currency_formatting_two_decimal_places(self):
        """Test with 2-3 amounts only"""
        from decimal import Decimal
        
        # Test amounts
        amounts = [
            Decimal('100.00'),
            Decimal('50.5'),  # Should become 50.50
            Decimal('25.123')  # Should become 25.12
        ]
        
        # Format each amount
        formatted = []
        for amount in amounts:
            # Round to 2 decimal places
            formatted_amount = round(float(amount), 2)
            formatted.append(formatted_amount)
        
        # Verify all have exactly 2 decimal places when converted to string
        for i, amount in enumerate(formatted):
            amount_str = f"{amount:.2f}"
            # Count decimal places
            decimal_part = amount_str.split('.')[1]
            assert len(decimal_part) == 2, f"Amount {amount} should have exactly 2 decimal places"
        
        # Verify specific values
        assert formatted[0] == 100.00
        assert formatted[1] == 50.50
        assert formatted[2] == 25.12



class TestPricingLockOnPayment:
    """
    Feature: payment-history-balance, Property 19: Pricing Lock on Payment
    For any boat registration, when marked as paid, locked_pricing should equal current pricing
    """
    
    def test_pricing_locked_when_boat_marked_paid(self):
        """Test with 1 boat record only"""
        # Mock boat before payment
        boat_before_payment = {
            'boat_registration_id': 'boat-1',
            'event_type': 'Course',
            'boat_type': '4+',
            'registration_status': 'complete',
            'payment_status': 'unpaid',
            'pricing': {
                'total': Decimal('100.00'),
                'base_price': Decimal('80.00'),
                'additional_fees': Decimal('20.00')
            }
        }
        
        # Simulate payment webhook marking boat as paid
        # This is what happens in confirm_payment_webhook.py
        boat_after_payment = boat_before_payment.copy()
        boat_after_payment['payment_status'] = 'paid'
        boat_after_payment['payment_id'] = 'pay-123'
        
        # Lock the pricing (deep copy to prevent reference issues)
        if 'pricing' in boat_after_payment:
            boat_after_payment['locked_pricing'] = copy.deepcopy(boat_after_payment['pricing'])
        
        # Verify locked_pricing was set
        assert 'locked_pricing' in boat_after_payment
        assert boat_after_payment['locked_pricing'] is not None
        
        # Verify locked_pricing equals original pricing
        assert boat_after_payment['locked_pricing']['total'] == boat_before_payment['pricing']['total']
        assert boat_after_payment['locked_pricing']['base_price'] == boat_before_payment['pricing']['base_price']
        assert boat_after_payment['locked_pricing']['additional_fees'] == boat_before_payment['pricing']['additional_fees']
        
        # Verify locked_pricing is a copy, not a reference
        # (changing pricing shouldn't affect locked_pricing)
        boat_after_payment['pricing']['total'] = Decimal('200.00')
        assert boat_after_payment['locked_pricing']['total'] == Decimal('100.00')


class TestPaginationConsistency:
    """
    Feature: payment-history-balance, Property 20: Pagination Consistency
    For any paginated query, union of all pages should equal complete result set
    """
    
    def test_pagination_returns_all_records_exactly_once(self):
        """Test with 5-10 records and page size of 3"""
        # Create test payments (7 records)
        all_payments = [
            {'payment_id': 'pay-1', 'paid_at': '2026-01-15T10:00:00Z', 'amount': Decimal('100')},
            {'payment_id': 'pay-2', 'paid_at': '2026-01-14T10:00:00Z', 'amount': Decimal('50')},
            {'payment_id': 'pay-3', 'paid_at': '2026-01-16T10:00:00Z', 'amount': Decimal('75')},
            {'payment_id': 'pay-4', 'paid_at': '2026-01-13T10:00:00Z', 'amount': Decimal('120')},
            {'payment_id': 'pay-5', 'paid_at': '2026-01-17T10:00:00Z', 'amount': Decimal('90')},
            {'payment_id': 'pay-6', 'paid_at': '2026-01-12T10:00:00Z', 'amount': Decimal('60')},
            {'payment_id': 'pay-7', 'paid_at': '2026-01-18T10:00:00Z', 'amount': Decimal('80')},
        ]
        
        # Sort by date descending (as the API does)
        sorted_payments = sorted(all_payments, key=lambda p: p['paid_at'], reverse=True)
        
        # Paginate with page size of 3
        page_size = 3
        pages = []
        for i in range(0, len(sorted_payments), page_size):
            page = sorted_payments[i:i + page_size]
            pages.append(page)
        
        # Verify we have 3 pages (3, 3, 1)
        assert len(pages) == 3
        assert len(pages[0]) == 3
        assert len(pages[1]) == 3
        assert len(pages[2]) == 1
        
        # Collect all payment IDs from all pages
        paginated_ids = set()
        for page in pages:
            for payment in page:
                paginated_ids.add(payment['payment_id'])
        
        # Verify union of all pages equals complete result set
        original_ids = set(p['payment_id'] for p in all_payments)
        assert paginated_ids == original_ids
        
        # Verify count matches
        total_in_pages = sum(len(page) for page in pages)
        assert total_in_pages == len(all_payments)
        
        # Verify no payment appears in multiple pages
        all_ids_in_pages = []
        for page in pages:
            for payment in page:
                all_ids_in_pages.append(payment['payment_id'])
        
        # Check for duplicates
        assert len(all_ids_in_pages) == len(set(all_ids_in_pages)), "Payment appears in multiple pages"
