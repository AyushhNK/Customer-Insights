from django.urls import path
from .views import (
    CustomerListView, 
    ProductUsageView, 
    CustomerInsightsView, 
    RevenueTrendsView,
    CustomerPersonalInfoView,
    ServicesUsedView,
    RecommendedServiceView,
    ChurnProbabilityView,
    TransactionHistoryView,
    CustomerProductRiskView,
    CustomerSegmentationView,
    CustomerByProductView,
    ProductListView
)

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:customer_id>/products/', ProductListView.as_view(), name='customer-products'),
    path('products/usage/', ProductUsageView.as_view(), name='product-usage'),
    path('products/<str:product_name>/customers/', CustomerByProductView.as_view(), name='customers-by-product'),
    path('customers/insights/', CustomerInsightsView.as_view(), name='customer-insights'),
    path('revenue/trends/', RevenueTrendsView.as_view(), name='revenue-trends'),
    path('customer/<int:customer_id>/personal_info/', CustomerPersonalInfoView.as_view(), name='customer_personal_info'),
    path('customer/<int:customer_id>/services_used/', ServicesUsedView.as_view(), name='services_used'),
    path('customer/<int:customer_id>/recommended_service/', RecommendedServiceView.as_view(), name='recommended_service'),
    path('customer/<int:customer_id>/churn_probability/', ChurnProbabilityView.as_view(), name='churn_probability'),
    path('customer/<int:customer_id>/transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('customer/<int:customer_id>/product_risk/', CustomerProductRiskView.as_view(), name='product_risk'),
    path('customer/<int:customer_id>/segmentation/', CustomerSegmentationView.as_view(), name='segmentation'),
]
