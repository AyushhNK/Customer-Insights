from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Customer, Product, Transaction
from .serializers import CustomerSerializer
from django.utils import timezone  # Import timezone from Django

class CustomerListView(APIView):
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


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
        
        # Current week range (Monday to Sunday)
        current_week_start = today - timezone.timedelta(days=today.weekday())
        current_week_end = current_week_start + timezone.timedelta(days=6)

        # Last week range (Monday to Sunday)
        last_week_start = current_week_start - timezone.timedelta(days=7)
        last_week_end = last_week_start + timezone.timedelta(days=6)

        # Count customers for the current and previous weeks
        current_week_customers = Customer.objects.filter(signup_date__range=(current_week_start, current_week_end)).count()
        last_week_customers = Customer.objects.filter(signup_date__range=(last_week_start, last_week_end)).count()

        # Calculate WoW Change for customers
        if last_week_customers > 0:
            wow_change = ((current_week_customers - last_week_customers) / last_week_customers) * 100
        else:
            wow_change = float('inf')

        # Calculate average revenue for this week and last week
        avg_revenue_this_week = Transaction.objects.filter(
            transaction_date__range=(current_week_start, current_week_end)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        avg_revenue_last_week = Transaction.objects.filter(
            transaction_date__range=(last_week_start, last_week_end)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        # Calculate percentage change in revenue
        if avg_revenue_last_week > 0:
            revenue_change_percentage = ((avg_revenue_this_week - avg_revenue_last_week) / avg_revenue_last_week) * 100
        else:
            revenue_change_percentage = float('inf')  # Handle case where last week's revenue is zero

        response_data = {
            "wow_change": wow_change,
            "average_revenue": {
                "current": avg_revenue_this_week,
                "last_week": avg_revenue_last_week,
                "revenue_change_percentage": revenue_change_percentage,
            },
            "current_week_customers": current_week_customers,
            "last_week_customers": last_week_customers,
        }
        
        return Response(response_data)
    

class RevenueTrendsView(APIView):
    def get(self, request, *args, **kwargs):
        # Trends for customer count
        customer_count_trend = list(
            Customer.objects.extra({'day': "DATE(signup_date)"})
            .values('day')
            .annotate(count=Count('customer_id'))
            .order_by('day')
        )

        # Trends for revenue
        revenue_trend = list(
            Transaction.objects.extra({'day': "DATE(transaction_date)"})
            .values('day')
            .annotate(total_revenue=Avg('amount'))
            .order_by('day')
        )

        response_data = {
            "customer_count_trend": customer_count_trend,
            "revenue_trend": revenue_trend,
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
            customer = Customer.objects.get(customer_id=customer_id)
            transactions = Transaction.objects.filter(customer=customer)
            transaction_data = [
                {
                    "transaction_id": t.transaction_id,
                    "transaction_date": t.transaction_date,
                    "amount": t.amount,
                    "is_anomalous": t.is_anomalous,
                }
                for t in transactions
            ]
            return Response(transaction_data)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)


class CustomerProductRiskView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        # Mocked data; replace with actual calculations or database/API calls as needed
        customer_product_risk = {
            "Mobile Banking": 0.2,
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

