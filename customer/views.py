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

        # Calculate WoW Change
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

        response_data = {
            "wow_change": wow_change,
            "average_revenue": {
                "current": avg_revenue_this_week,
                "last_week": avg_revenue_last_week,
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


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer, Transaction
from .serializers import CustomerProfileSerializer

class CustomerProfileView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        try:
            # Fetch Customer Data
            customer = Customer.objects.get(customer_id=customer_id)

            # Personal Info (from model directly)
            personal_info = {
                "name": customer.name,
                "email": customer.email,
                "phone_number": customer.phone_number,
                "address": customer.address,
            }

            # Fetch Services Used (mocked or from database/API)
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

            # Fetch Recommended Service (mocked or call an API)
            recommended_service = "Loan Against Fixed Deposit"

            # Fetch Churn Probability (mocked or call an API)
            churn_probability = {"value": 0.7, "graph": [0.6, 0.65, 0.7]}

            # Fetch CLV (mocked or call an API)
            clv = 1500.00

            # Fetch Transaction History
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

            # Fetch Customer Product Risk (mocked or call an API)
            customer_product_risk = {
                "Mobile Banking": 0.2,
                "Loans": 0.8,
                "Deposits": 0.1,
            }

            # Fetch Customer Segmentation
            segmentation = customer.segment

            # Response Data
            response_data = {
                "personal_info": personal_info,
                "services_used": services_used,
                "recommended_service": recommended_service,
                "churn_probability": churn_probability,
                "clv": clv,
                "transaction_history": transaction_data,
                "customer_product_risk": customer_product_risk,
                "segmentation": segmentation,
            }

            return Response(response_data)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)
