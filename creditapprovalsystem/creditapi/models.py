from django.db import models
from django.db.models import Model

# Create your models here.

class Customer(Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)
    phone_number = models.IntegerField(max_length = 11)
    age = models.IntegerField(max_length = 1)
    monthly_salary = models.IntegerField(max_length = 200)
    approved_limit = models.IntegerField(max_length = 200)


class Loan(Model):
    loan_id = models.AutoField(primary_key= True)
    customer_id = models.ForeignKey(Customer, on_delete = models.CASCADE)
    loan_amount = models.FloatField(max_length = 50)
    tenure = models.IntegerField(max_length = 50)
    interest_rate = models.FloatField(max_length = 50)
    monthly_installment = models.FloatField(max_length = 50)
    emi_paid_on_time = models.IntegerField(max_length = 50)
    start_date = models.DateField()
    end_date = models.DateField()