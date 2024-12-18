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

from django.db.models import Count
from .models import Transaction

class ProductUsageView(APIView):
    def get(self, request, *args, **kwargs):
        product_usage = (
            Transaction.objects.values('product__name')
            .annotate(count=Count('product'))
            .order_by('-count')
        )
        product_aggregation = {item['product__name']: item['count'] for item in product_usage}
        return Response(product_aggregation)
from django.utils import timezone
from django.db.models import Count, Avg
from .models import Customer, Transaction

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
