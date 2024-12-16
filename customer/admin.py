from django.contrib import admin
from .models import Customer, Product, Transaction, RecommendedService

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(RecommendedService)
