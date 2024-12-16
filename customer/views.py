from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Customer, Product, Transaction
from .serializers import CustomerSerializer
from datetime import datetime

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
        last_week_customers = (
            Customer.objects.filter(signup_date__week=(datetime.now().isocalendar()[1] - 1)).count()
        )
        print(last_week_customers)
        wow_change = ((total_customers - last_week_customers) / last_week_customers) * 100 if last_week_customers > 0 else 0

        avg_revenue_this_week = Transaction.objects.filter(
            transaction_date__week=datetime.now().isocalendar()[1]
        ).aggregate(avg_revenue=Avg('amount'))['avg_revenue'] or 0

        avg_revenue_last_week = Transaction.objects.filter(
            transaction_date__week=(datetime.now().isocalendar()[1] - 1)
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

        # Step Construct Response
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
