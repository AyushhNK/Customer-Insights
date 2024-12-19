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
    


# from django.db import models
# from django.contrib.auth.models import User

# class Customer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's User model
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15, blank=True)
#     signup_date = models.DateTimeField(auto_now_add=True)
#     churn_probability = models.FloatField(default=0.0)  # Churn probability score
#     clv = models.FloatField(default=0.0)  # Customer Lifetime Value

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"

# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.name

# class Transaction(models.Model):
#     customer = models.ForeignKey(Customer, related_name='transactions', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name='transactions', on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_date = models.DateTimeField(auto_now_add=True)

# class Service(models.Model):
#     customer = models.ForeignKey(Customer, related_name='services', on_delete=models.CASCADE)
#     service_type = models.CharField(max_length=50)  # e.g., Mobile Banking, Loans, Deposits
#     active_devices = models.IntegerField(default=0)

# class Loan(models.Model):
#     customer = models.ForeignKey(Customer, related_name='loans', on_delete=models.CASCADE)
#     loan_type = models.CharField(max_length=50)  # e.g., Personal Loan, Home Loan
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     due_date = models.DateTimeField()
    
# class Deposit(models.Model):
#     customer = models.ForeignKey(Customer, related_name='deposits', on_delete=models.CASCADE)
#     deposit_type = models.CharField(max_length=50)  # e.g., Fixed, Current/Savings
#     amount = models.DecimalField(max_digits=10, decimal_places=2)

# class CustomerRisk(models.Model):
#     customer = models.ForeignKey(Customer, related_name='risks', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name='risks', on_delete=models.CASCADE)
#     risk_factor = models.FloatField()

# class CustomerSegment(models.Model):
#     customer = models.OneToOneField(Customer, related_name='segment', on_delete=models.CASCADE)
#     segment_type = models.CharField(max_length=50)  # e.g., High Value, Low Value

# # Optional: For recommended services from an API
# class RecommendedService(models.Model):
#     customer = models.ForeignKey(Customer, related_name='recommended_services', on_delete=models.CASCADE)
#     service_description = models.TextField()
