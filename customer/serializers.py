from rest_framework import serializers
from .models import Customer,Transaction, Product

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'email', 'phone_number', 'segment', 'signup_date','profile_image']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'category', 'risk_factor']

class MobileBankingSerializer(serializers.Serializer):
    since = serializers.DateField()
    expiry_date = serializers.DateField()
    active_devices = serializers.IntegerField()

class LoanSerializer(serializers.Serializer):
    type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    due_date = serializers.DateField()

class DepositSerializer(serializers.Serializer):
    fixed = serializers.DecimalField(max_digits=10, decimal_places=2)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'transaction_date', 'amount', 'is_anomalous']

class CustomerProfileSerializer(serializers.Serializer):
    personal_info = serializers.SerializerMethodField()
    services_used = serializers.SerializerMethodField()
    recommended_service = serializers.CharField()
    churn_probability = serializers.SerializerMethodField()
    clv = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_history = TransactionSerializer(many=True)
    customer_product_risk = serializers.JSONField()
    segmentation = serializers.CharField()

    def get_personal_info(self, obj):
        return {
            "name": obj.name,
            "email": obj.email,
            "phone_number": obj.phone_number,
            "address": obj.address,
        }

    def get_services_used(self, obj):
        # Mocked Data or Fetch from DB/API
        return {
            "mobile_banking": {
                "since": "2020-01-01",
                "expiry_date": "2025-01-01",
                "active_devices": 3,
            },
            "loans": [
                {"type": "Home Loan", "amount": 50000, "due_date": "2024-06-01"}
            ],
            "deposits": {"fixed": 10000, "savings": 5000},
        }

    def get_churn_probability(self, obj):
        return {"value": 0.75, "graph": [0.6, 0.65, 0.75]}
