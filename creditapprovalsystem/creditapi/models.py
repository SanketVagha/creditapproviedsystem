from django.db import models
from django.db.models import Model

# Create your models here.

class Customer(Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)
    phone_number = models.PositiveBigIntegerField(unique = True, null = False, blank = False)
    age = models.IntegerField()
    monthly_salary = models.PositiveBigIntegerField()
    approved_limit = models.PositiveBigIntegerField()


class Loan(Model):
    loan_id = models.AutoField(primary_key= True)
    customer_id = models.ForeignKey(Customer, on_delete = models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    emi_paid_on_time = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    approval = models.BooleanField(default = False)
