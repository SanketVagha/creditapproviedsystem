from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.db.models import Sum

from creditapi.models import Customer,Loan
from creditapi.serializers import CustomerSerializer, LoanSerializer
from datetime import datetime


import numpy as np

# Create your views here.

def customerid_validation(customerid):
    no_of_customer_id = Customer.objects.filter(customer_id = customerid).count()
    return no_of_customer_id

def pastLoanPaidOnTime(customerid):
    loan_pay_on_time =  Loan.objects.filter(emi_paid_on_time= Loan.tenure, customer_id = customerid, end_date__lt = (datetime.now().date)).count()
    return loan_pay_on_time

def pastLoanTaken(customerid):
    past_loans = Loan.objects.filter(customer_id = customerid, end_date__lt = (datetime.now().date)).count()
    return past_loans

def loalApproved(customerid):
    loan_approved = Loan.objects.filter(customer_id= customerid, approval= 1).count()
    return loan_approved


def activeLoan(customerid):
    current_loans = Loan.objects.filter(customer_id = customerid, end_date__gte = (datetime.now().date)).count()
    return current_loans

def loanApproved(customerid):
    loan_approved = Loan.objects.filter(customer_id = customerid, approval = 1).count()
    return loan_approved

def approved_limit(customerid):
    limit = Customer.objects.only('customerid').filter(customer_id= customerid)
    return limit

def current_loan_amount(customerid):
    loan_amount = Loan.objects.only("loan_amount").filter(customer_id= customerid, end_date__gte = (datetime.now().date)).aggregate(Sum('loan_amount'))
    return loan_amount

def current_loan_emi(customerid):
    loan_emi_amount = Loan.objects.only("monthly_installment").filter(customer_id= customerid, end_date__gte = (datetime.now().date)).aggregate(Sum('monthly_installment'))
    return loan_emi_amount

def customer_salary(customerid):
        customer_salary = Customer.objects.only("monthly_salary").filter(customer_id = customerid)
        return customer_salary


def get_credit_score(customerid, loan_request):
        customer_limit = approved_limit(customerid)
        current_loan_amounts = current_loan_amount(customerid)
        salary = customer_salary(customerid)
        loan_emi = current_loan_emi(customerid)
        paidOnTimeLoan =  pastLoanPaidOnTime(customerid)
        pastloan = pastLoanTaken(customerid)

        data = {}
        credit_score = 0

        if (current_loan_amounts + loan_request ) > customer_limit:
            data['message'] = "Loan Limit Not Available"
            return JsonResponse(data, safe= False)


        if((salary/2) < loan_emi):
            data['message'] = "EMI Amount Greater Then Salary Not Approved"
            return JsonResponse(data= data, safe= False)

        credit_score = (50 * (paidOnTimeLoan/pastloan)) + (50 * (current_loan_amounts/customer_limit))
        
        return credit_score


def monthly_emi_installment(loan_amount,interest_rate,tenure):
    
        interest_rate = interest_rate / (12*100)
        monthly_installment = (loan_amount * interest_rate * ((1+interest_rate)**tenure)) / (interest_rate ** interest_rate)
        return monthly_installment
@csrf_exempt


def register(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        data = {}
        if not customer_data['first_name']:
            data['message'] = 'Customer First Name Empty'
            return JsonResponse(data, safe= False)

        if not (customer_data['first_name']).isalpha()  :
            data['message'] = 'Customer First Name Invalid'
            return JsonResponse(data, safe= False)

        if not customer_data['last_name']:
            data['message'] = 'Customer Last Name Empty'
            return JsonResponse(data, safe= False)

        if not (customer_data['last_name']).isalpha():
            data['message'] = 'Customer Last Name Invalid'
            return JsonResponse(data, safe= False)

        if not customer_data['phone_number']:
            data['message'] = 'Customer Phone Number Empty'
            return JsonResponse(data, safe= False)
        
        if not customer_data['age']:
            data['message'] = 'Customer Age Empty'
            return JsonResponse(data, safe= False)
        
        if customer_data['age'] > 120 :
            data['message'] = 'Customer Age Out of Range'
            return JsonResponse(data, safe= False)
        
        if not customer_data['monthly_salary']:
            data['message'] = 'Cunstomer Monthly Salary Empty'
            return JsonResponse(data, safe=False)
        
        if customer_data['monthly_salary'] < 0:
            data['message'] = 'Customer Salary Less Then 0 Not Allow'
            return JsonResponse(data, safe= False)





        # print(customer_data)
        customer_data['monthly_salary'] = np.round(customer_data['monthly_salary'])
        customer_data["approved_limit"] = np.round((36 * customer_data['monthly_salary'])/100000) * 100000
        customer_serializer = CustomerSerializer(data = customer_data)
        # return JsonResponse(customer_serializer, safe= False)
        if customer_serializer.is_valid():
            record = customer_serializer.save()
            data['customer_id'] = record.customer_id
            data['name'] = record.first_name + " " + record.last_name
            data['phone_number'] = record.phone_number
            data['age'] = record.age
            data['monthly_salary'] = record.monthly_salary
            data['approved_limit'] = record.approved_limit
            return JsonResponse(data, safe= False)
    data['message'] = 'Record Not Saved'
    return JsonResponse(data, safe= False)


def checkeligibility(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        data = {}
        if not customer_data['customer_id']:
            data['message'] = "Customer Id Empty"
            return JsonResponse(data, safe= False)
        
        if customerid_validation(customer_data['customer_id']) != 0:
            data['message'] = "Customer Id Invalid"
            return JsonResponse(data, safe= False)

        if not customer_data['loan_amount']:
            data['message'] = "Loan Amount Empty"
            return JsonResponse(data, safe= False)
        
        if customer_data['loan_amount'] <= 0:
            data['message'] = "Loan Amount Invalid"
            return JsonResponse(data, safe= False)

        if not customer_data['interest_rate']:
            data['message'] = "Interest Rate Empty"
            return JsonResponse(data, safe= False)
        
        if customer_data['interest_rate'] < 0:
            data['message'] = "Interest Rate Invalid"
            return JsonResponse(data, safe= False)

        if not customer_data['tenure']:
            data['message'] = "Tenure Empty"
            return JsonResponse(data, safe= False)

        if customer_data['tenure'] <= 0 :
            data['message'] = "Tenure Invalid"
            return JsonResponse(data, safe= False)
        

        score = get_credit_score(customer_data['customer_id'], customer_data['loan_amount'])

        if score < 10:
            data['message'] = "Credit Score Less Not Approved"
            return JsonResponse(data= data, safe= False)
        
        if  30 > score and score >= 10:
            if customer_data['interest_rate'] < 16:
                data['message'] = "Interest Rate At List 16% Required"
                return JsonResponse(data= data, safe= False)
        if 50 > score and score >= 30:
            if customer_data['interest_rate'] < 12:
                data['message'] = "Interest Rate At List 12% Required"
                return JsonResponse(data= data, safe= False)
        
        monthly_installment =  monthly_emi_installment(customer_data['loan_amount'], customer_data['interest_rate'], customer_data['tenure'])


        customer_data['monthly_installment'] = monthly_installment
        customer_data['approval'] = 1
        customer_data['start_date'] = (datetime.now().date)

        #   Data Insert in database and all New keys arange acording to table attribute in database



