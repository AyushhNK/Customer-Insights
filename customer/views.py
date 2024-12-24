from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Max
from .models import Customer, Product, Transaction
from .serializers import CustomerSerializer
from django.utils import timezone  # Import timezone from Django
from rest_framework import status 
from datetime import datetime, timedelta, date
from django.db.models import Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear



class CustomerListView(APIView):
    def get(self, request):
        # Get query parameters
        segment = request.query_params.get('segment')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        min_spent = request.query_params.get('min_spent')
        has_anomalies = request.query_params.get('has_anomalies')
        period = request.query_params.get('period', 'all')  # Default to 'all'

        # Base queryset with annotations
        customers = Customer.objects.annotate(
            total_transactions=Count('transactions'),
            total_spent=Sum('transactions__amount'),
            last_transaction_date=Max('transactions__transaction_date')
        )

        # Apply filters based on segment
        if segment:
            customers = customers.filter(segment=segment)

        # Apply filters based on the specified period
        if period != 'all':
            today = timezone.now()
            if period == 'day':
                start_date = today - timedelta(days=1)
                end_date = today
            elif period == 'week':
                start_date = today - timedelta(days=today.weekday())  # Start of the week (Monday)
                end_date = start_date + timedelta(days=6)  # End of the week (Sunday)
            elif period == 'month':
                start_date = today.replace(day=1)  # Start of the month
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # End of the month
            else:
                return Response({"error": "Invalid period specified"}, status=status.HTTP_400_BAD_REQUEST)

            customers = customers.filter(signup_date=[start_date, end_date])

        # Apply filters based on transaction dates
        if date_from and date_to:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                customers = customers.filter(transactions__transaction_date__range=[date_from, date_to])
            except ValueError:
                return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        # Apply filters based on minimum spent amount
        if min_spent:
            try:
                customers = customers.filter(total_spent__gte=float(min_spent))
            except ValueError:
                return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter customers with anomalies in transactions
        if has_anomalies is not None:  # Check for presence of the parameter
            customers = customers.filter(transactions__is_anomalous=True).distinct()

        # Serialize customer data
        serializer = CustomerSerializer(customers, many=True)

        # Prepare analytics data
        analytics = {
            'total_customers': customers.count(),
            'segment_distribution': dict(customers.values_list('segment').annotate(count=Count('segment'))),
            'average_customer_value': customers.aggregate(avg=Avg('total_spent'))['avg'],
            'customer_acquisition_trend': dict(
                customers.values('signup_date__month')
                .annotate(count=Count('customer_id'))
                .order_by('signup_date__month')
            )
        }

        return Response({
            'analytics': analytics,
            'customers': serializer.data
        })



class ProductUsageView(APIView):
    def get(self, request, *args, **kwargs):
        product_usage = (
            Transaction.objects.values('product__name')
            .annotate(count=Count('product'))
            .order_by('-count')
        )
        product_aggregation = {item['product__name']: item['count'] for item in product_usage}
        return Response(product_aggregation)

class CustomerInsightsView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now()
        period = request.query_params.get('period', 'week')  # Default to 'week'

        if period == 'day':
            start_date = today - timedelta(days=1)
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            return Response({"error": "Invalid period specified"}, status=400)

        # Last period range
        if period == 'day':
            last_period_start = start_date - timedelta(days=1)
            last_period_end = start_date
        elif period == 'week':
            last_period_start = start_date - timedelta(days=7)
            last_period_end = last_period_start + timedelta(days=6)
        elif period == 'month':
            last_period_start = (start_date - timedelta(days=1)).replace(day=1)
            last_period_end = start_date - timedelta(days=1)

        # Count customers for the current and previous periods
        current_period_customers = Customer.objects.filter(signup_date__range=(start_date, end_date)).count()
        last_period_customers = Customer.objects.filter(signup_date__range=(last_period_start, last_period_end)).count()

        # Calculate WoW Change for customers
        if last_period_customers > 0:
            wow_change = ((current_period_customers - last_period_customers) / last_period_customers) * 100
        else:
            wow_change = None  # Use None instead of float('inf')

        # Calculate average revenue for this period and last period
        avg_revenue_this_period = Transaction.objects.filter(
            transaction_date__range=(start_date, end_date)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        avg_revenue_last_period = Transaction.objects.filter(
            transaction_date__range=(last_period_start, last_period_end)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        # Calculate percentage change in revenue
        if avg_revenue_last_period > 0:
            revenue_change_percentage = ((avg_revenue_this_period - avg_revenue_last_period) / avg_revenue_last_period) * 100
        else:
            revenue_change_percentage = None  # Use None instead of float('inf')

        response_data = {
            "wow_change": wow_change,
            "average_revenue": {
                "current": avg_revenue_this_period,
                "last_period": avg_revenue_last_period,
                "revenue_change_percentage": revenue_change_percentage,
            },
            "current_period_customers": current_period_customers,
            "last_period_customers": last_period_customers,
        }

        return Response(response_data)
    
class RevenueTrendsView(APIView):
    def get(self, request, *args, **kwargs):
        # Get parameters
        period = request.query_params.get('period', 'day')  # Default to daily
        custom_start = request.query_params.get('start_date')
        custom_end = request.query_params.get('end_date')
        
        # Initialize base querysets
        customer_qs = Customer.objects.all()
        transaction_qs = Transaction.objects.all()
        
        # Set up date trunc mapping
        date_trunc_mapping = {
            'day': TruncDate('signup_date'),
            'week': TruncWeek('signup_date'),
            'month': TruncMonth('signup_date'),
            'year': TruncYear('signup_date')
        }
        
        transaction_trunc_mapping = {
            'day': TruncDate('transaction_date'),
            'week': TruncWeek('transaction_date'),
            'month': TruncMonth('transaction_date'),
            'year': TruncYear('transaction_date')
        }
        
        # Apply date filtering
        if period == 'custom' and custom_start and custom_end:
            try:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                
                customer_qs = customer_qs.filter(
                    signup_date__range=[start_date, end_date + timedelta(days=1)]
                )
                transaction_qs = transaction_qs.filter(
                    transaction_date__range=[start_date, end_date + timedelta(days=1)]
                )
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=400
                )
        else:
            now = timezone.now()
            if period == 'week':
                start_date = now - timedelta(days=now.weekday())
            elif period == 'month':
                start_date = now.replace(day=1)
            elif period == 'year':
                start_date = now.replace(month=1, day=1)
            else:  # day
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            customer_qs = customer_qs.filter(signup_date__gte=start_date)
            transaction_qs = transaction_qs.filter(transaction_date__gte=start_date)
        
        # Get trends based on period
        trunc_date = date_trunc_mapping.get(period, TruncDate('signup_date'))
        trunc_transaction = transaction_trunc_mapping.get(period, TruncDate('transaction_date'))
        
        # Customer trends with cumulative calculation
        customer_count_trend = (
            customer_qs
            .annotate(period=trunc_date)
            .values('period')
            .annotate(new_customers=Count('customer_id'))
            .order_by('period')
        )
        
        # Calculate cumulative customers manually
        cumulative_customers = []
        running_total = 0
        for item in customer_count_trend:
            running_total += item['new_customers']
            cumulative_customers.append({
                'period': item['period'],
                'new_customers': item['new_customers'],
                'cumulative_customers': running_total
            })
        
        # Revenue trends
        revenue_trend = (
            transaction_qs
            .annotate(period=trunc_transaction)
            .values('period')
            .annotate(
                total_revenue=Sum('amount'),
                average_transaction=Avg('amount'),
                transaction_count=Count('transaction_id'),
                anomaly_count=Count('transaction_id', filter=Q(is_anomalous=True))
            )
            .order_by('period')
        )
        
        # Calculate segment distribution over time
        segment_trend = (
            customer_qs
            .annotate(period=trunc_date)
            .values('period', 'segment')
            .annotate(count=Count('customer_id'))
            .order_by('period', 'segment')
        )
        
        # Calculate product category performance
        product_trend = (
            transaction_qs
            .annotate(period=trunc_transaction)
            .values('period', 'product__category')
            .annotate(
                revenue=Sum('amount'),
                transaction_count=Count('transaction_id')
            )
            .order_by('period', 'product__category')
        )
        
        # Calculate summary metrics
        summary = {
            'total_customers': customer_qs.count(),
            'total_revenue': transaction_qs.aggregate(total=Sum('amount'))['total'] or 0,
            'average_transaction': transaction_qs.aggregate(avg=Avg('amount'))['avg'] or 0,
            'anomaly_rate': (
                transaction_qs.filter(is_anomalous=True).count() /
                float(transaction_qs.count()) if transaction_qs.exists() else 0
            ) * 100  # Convert to percentage
        }
        
        # Add revenue growth metrics
        if revenue_trend:
            first_revenue = next(iter(revenue_trend))['total_revenue']
            last_revenue = list(revenue_trend)[-1]['total_revenue']
            revenue_growth = ((last_revenue - first_revenue) / first_revenue * 100) if first_revenue else 0
            summary['revenue_growth'] = revenue_growth
        
        response_data = {
            'period': period,
            'summary': summary,
            'customer_trends': {
                'count_trend': cumulative_customers,
                'segment_distribution': list(segment_trend)
            },
            'revenue_trends': {
                'revenue_by_period': list(revenue_trend),
                'product_performance': list(product_trend)
            }
        }
        
        return Response(response_data)

class CustomerPersonalInfoView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            personal_info = {
                "name": customer.name,
                "email": customer.email,
                "phone_number": customer.phone_number,
                "address": customer.address,
            }
            return Response(personal_info)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)
        
class ServicesUsedView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        # Mocked data; replace with actual database/API calls as needed
        services_used = {
            "mobile_banking": {
                "since": "2020-01-01",
                "expiry_date": "2025-01-01",
                "active_devices": 2,
            },
            "loans": [
                {"type": "Home Loan", "amount": 50000, "due_date": "2024-06-01"}
            ],
            "deposits": {"fixed": 10000, "savings": 5000},
        }
        return Response(services_used)

class RecommendedServiceView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        recommended_service = "Loan Against Fixed Deposit"  # Mocked data
        return Response({"recommended_service": recommended_service})

class ChurnProbabilityView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        churn_probability = {"value": 0.7, "graph": [0.6, 0.65, 0.7]}  # Mocked data
        return Response(churn_probability)

class CLVView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        clv = 1500.00  # Mocked data
        return Response({"clv": clv})


class TransactionHistoryView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        try:
            # Get time period from query parameters
            period = request.query_params.get('period', 'all')  # Default to all
            custom_start = request.query_params.get('start_date')
            custom_end = request.query_params.get('end_date')
            
            # Get customer
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Base query
            transactions = Transaction.objects.filter(customer=customer)
            
            # Get current datetime
            now = timezone.now()
            
            # Apply time period filter
            if period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                transactions = transactions.filter(transaction_date__gte=start_date)
            
            elif period == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                transactions = transactions.filter(transaction_date__gte=start_date)
            
            elif period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                transactions = transactions.filter(transaction_date__gte=start_date)
            
            elif period == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                transactions = transactions.filter(transaction_date__gte=start_date)
            
            elif period == 'custom' and custom_start and custom_end:
                try:
                    start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                    end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                    transactions = transactions.filter(
                        transaction_date__gte=start_date,
                        transaction_date__lte=end_date + timedelta(days=1)
                    )
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD"},
                        status=400
                    )
            
            # Calculate summary statistics
            summary = {
                'total_transactions': transactions.count(),
                'total_amount': transactions.aggregate(Sum('amount'))['amount__sum'] or 0,
                'anomalous_transactions': transactions.filter(is_anomalous=True).count(),
                'period': period,
            }
            
            # Get transaction details
            transaction_data = [
                {
                    "transaction_id": t.transaction_id,
                    "transaction_date": t.transaction_date,
                    "amount": t.amount,
                    "is_anomalous": t.is_anomalous,
                    "product_name": t.product.name if t.product else None,
                    "product_category": t.product.category if t.product else None,
                }
                for t in transactions.order_by('-transaction_date')
            ]
            
            return Response({
                'summary': summary,
                'transactions': transaction_data
            })
            
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)


class CustomerProductRiskView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        # Mocked data; replace with actual calculations or database/API calls as needed
        customer_product_risk = {
            "MobileBanking": 0.2,
            "Loans": 0.8,
            "Deposits": 0.1,
        }
        return Response(customer_product_risk)


class CustomerSegmentationView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            segmentation = customer.segment
            return Response({"segmentation": segmentation})
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

