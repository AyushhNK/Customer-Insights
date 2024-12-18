from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Customer, Product, Transaction
from .serializers import CustomerSerializer
from django.utils import timezone  # Import timezone from Django

class CustomerListView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all customers
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)

        # Aggregate product usage
        product_usage = (
            Transaction.objects.values('product__name')
            .annotate(count=Count('product'))
            .order_by('-count')
        )
        product_aggregation = {item['product__name']: item['count'] for item in product_usage}

        # Calculate Basic Insights
        total_customers = Customer.objects.count()

        # Get today's date and calculate current and last week's date ranges
        today = timezone.now()  # Use timezone-aware current date
        
        # Current week range (Monday to Sunday)
        current_week_start = today - timezone.timedelta(days=today.weekday())  # Start of current week (Monday)
        current_week_end = current_week_start + timezone.timedelta(days=6)  # End of current week (Sunday)

        # Last week range (Monday to Sunday)
        last_week_start = current_week_start - timezone.timedelta(days=7)  # Start of last week (Monday)
        last_week_end = last_week_start + timezone.timedelta(days=6)  # End of last week (Sunday)

        print(current_week_start, current_week_end)
        print(last_week_start, last_week_end)

        # Count customers for the current and previous weeks
        current_week_customers = Customer.objects.filter(signup_date__range=(current_week_start, current_week_end)).count()
        last_week_customers = Customer.objects.filter(signup_date__range=(last_week_start, last_week_end)).count()

        print(current_week_customers, last_week_customers)

        # Calculate WoW Change
        if last_week_customers > 0:
            wow_change = ((current_week_customers - last_week_customers) / last_week_customers) * 100
        else:
            wow_change = float('inf')  # Infinite increase if there were no customers last week

        # Calculate average revenue for this week and last week
        avg_revenue_this_week = Transaction.objects.filter(
            transaction_date__range=(current_week_start, current_week_end)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        avg_revenue_last_week = Transaction.objects.filter(
            transaction_date__range=(last_week_start, last_week_end)
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        # Prepare Trends
        customer_count_trend = list(
            Customer.objects.extra({'day': "DATE(signup_date)"})
            .values('day')
            .annotate(count=Count('customer_id'))
            .order_by('day')
        )

        revenue_trend = list(
            Transaction.objects.extra({'day': "DATE(transaction_date)"})
            .values('day')
            .annotate(total_revenue=Avg('amount'))
            .order_by('day')
        )

        # Construct Response
        response_data = {
            "customers": serializer.data,
            "aggregation": {
                "product_usage": product_aggregation,
                "wow_change": wow_change,
                "average_revenue": {
                    "current": avg_revenue_this_week,
                    "last_week": avg_revenue_last_week,
                },
            },
            "trends": {
                "customer_count": customer_count_trend,
                "revenue_trend": revenue_trend,
            },
        }
        
        return Response(response_data)
