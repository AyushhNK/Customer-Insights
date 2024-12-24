from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    signup_date = models.DateTimeField(auto_now_add=True)
    segment = models.CharField(max_length=50, choices=[
        ('High', 'High Value'), 
        ('Low', 'Low Value'), 
        ('Barely', 'Barely Active')
    ])
    profile_image = models.ImageField(upload_to='customer_images/', default='customer_images/default.jpg', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[('Loan', 'Loan'), ('Deposit', 'Deposit'), ('Banking', 'Mobile Banking')])
    risk_factor = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField()
    is_anomalous = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"

class RecommendedService(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='recommended_service')
    service_name = models.CharField(max_length=100)
    recommendation_reason = models.TextField()

    def __str__(self):
        return self.service_name
    
