from django.urls import path
from .views import CustomerListView, ProductUsageView, CustomerInsightsView, RevenueTrendsView,CustomerProfileView

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('products/usage/', ProductUsageView.as_view(), name='product-usage'),
    path('customers/insights/', CustomerInsightsView.as_view(), name='customer-insights'),
    path('revenue/trends/', RevenueTrendsView.as_view(), name='revenue-trends'),
    path('customers/<int:customer_id>/', CustomerProfileView.as_view(), name='customer-profile'),
]
