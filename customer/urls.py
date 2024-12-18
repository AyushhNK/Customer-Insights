from django.urls import path
from .views import CustomerListView, ProductUsageView, CustomerInsightsView, RevenueTrendsView

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('products/usage/', ProductUsageView.as_view(), name='product-usage'),
    path('customers/insights/', CustomerInsightsView.as_view(), name='customer-insights'),
    path('revenue/trends/', RevenueTrendsView.as_view(), name='revenue-trends'),
]
