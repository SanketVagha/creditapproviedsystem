from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.db.models import Sum
from django.db.models import F

from creditapi.models import Customer,Loan
from creditapi.serializers import CustomerSerializer, LoanSerializer
from datetime import datetime
from dateutil.relativedelta import relativedelta


from asgiref.sync import async_to_sync


import numpy as np

# Create your views here.

def customerid_validation(customerid):
    no_of_customer_id = Customer.objects.filter(customer_id = customerid).count()
    return no_of_customer_id

def loanid_available(loanid):
    no_of_loan = Loan.objects.filter(loan_id = loanid).count()
    return no_of_loan

def pastLoanPaidOnTime(customerid):
    loan_pay_on_time =  Loan.objects.only("emi_paid_on_time").filter(emi_paid_on_time= F("tenure"), customer_id = customerid, end_date__lt = datetime.today().strftime("%Y-%m-%d")).count()
    return loan_pay_on_time

def pastLoanTaken(customerid):
    past_loans = Loan.objects.only("loan_id").filter(customer_id = customerid, end_date__lt = datetime.today().strftime("%Y-%m-%d")).count()
    return past_loans

def loalApproved(customerid):
    loan_approved = Loan.objects.only("loan_id").filter(customer_id= customerid, approval= 1).count()
    return loan_approved


def activeLoan(customerid):
    current_loans = Loan.objects.only("loan_id").filter(customer_id = customerid, end_date__gte = datetime.today().strftime("%Y-%m-%d")).count()
    return current_loans

def loanApproved(customerid):
    loan_approved = Loan.objects.only("loan_id").filter(customer_id = customerid, approval = 1).count()
    return loan_approved

def approved_limit(customerid):
    limit = Customer.objects.only('approved_limit').filter(customer_id= customerid).first()
    if limit:
        return int(limit.approved_limit)
    return 0
def current_loan_amount(customerid):
    customer_count = Loan.objects.filter(customer_id= customerid, end_date__gte = datetime.today().strftime("%Y-%m-%d")).count()
    loan_amount = 0
    if customer_count > 0:
        loan_amount = Loan.objects.filter(customer_id= customerid, end_date__gte = datetime.today().strftime("%Y-%m-%d")).aggregate(Sum("loan_amount"))["loan_amount__sum"]
        # print(loan_amount)
    return loan_amount

def current_loan_emi(customerid):
    loan_emi_amount = 0
    customer_count = Loan.objects.filter(customer_id= customerid, end_date__gte = datetime.today().strftime("%Y-%m-%d")).count()
    if customer_count > 0:
        loan_emi_amount = Loan.objects.filter(customer_id= customerid, end_date__gte = datetime.today().strftime("%Y-%m-%d")).aggregate(Sum("monthly_installment"))['monthly_installment__sum']
    
    return loan_emi_amount

def customer_salary(customerid):
        customer_salary = Customer.objects.only("monthly_salary").filter(customer_id = customerid).first()
        if customer_salary:
            return int(customer_salary.monthly_salary)
        return 0

def get_credit_score(customerid):
        customer_limit = approved_limit(customerid)
        current_loan_amounts = current_loan_amount(customerid)
        paidOnTimeLoan =  pastLoanPaidOnTime(customerid)
        pastloan = pastLoanTaken(customerid)

        credit_score = 0
        if(pastloan == 0):
            credit_score = 30
            # print(type(credit_score))
            return credit_score
        else:
            credit_score = (50 * (paidOnTimeLoan/pastloan)) + (50 * (current_loan_amounts/customer_limit))
        
        return credit_score


def monthly_emi_installment(loan_amount,interest_rate,tenure):

    # Convert annual interest rate to monthly and percentage to decimal
    monthly_interest_rate = (interest_rate / 12) / 100

    # Calculate the monthly installment using the loan amortization formula
    monthly_installment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**tenure) / ((1 + monthly_interest_rate)**tenure - 1)

    return round(monthly_installment, 2)



def loanData(loan_id):
    data = Loan.objects.filter(loan_id = loan_id)
    return data.values()

def customerData(customer_id):
    data = Customer.objects.filter(customer_id = customer_id)
    return data.values()

def customerLoanData(customerid):
    data = Loan.objects.filter(customer_id = customerid)
    return data.values()

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

@csrf_exempt

def checkeligibility(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        data = {}
        if not customer_data['customer_id']:
            data['message'] = "Customer Id Empty"
            return JsonResponse(data, safe= False)
        
        if customerid_validation(customer_data['customer_id']) == 0:
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
        
        current_loan_amounts = current_loan_amount(data['customer_id'])
        salary = customer_salary(data['customer_id'])
        customer_limit = approved_limit(data['customer_id'])
        loan_emi = current_loan_emi(data['customer_id'])

        if(current_loan_amounts + customer_data['loan_amount']) > customer_limit :
            data['message'] = "Loan Limit Not Available"
            return JsonResponse(data, safe= False)
    
        if((salary/2) < loan_emi):
            data['message'] = "EMI Amount Greater Then Salary Not Approved"
            return JsonResponse(data= data, safe= False)
        

        credit_score = get_credit_score(customer_data['customer_id'])

        if credit_score < 10:
            data['message'] = "Credit Score Less Not Approved"
            return JsonResponse(data= data, safe= False)
        
        if  30 > credit_score and credit_score >= 10:
            if customer_data['interest_rate'] < 16:
                data['message'] = "Interest Rate At List 16% Required"
                return JsonResponse(data= data, safe= False)
        if 50 > credit_score and credit_score >= 30:
            if customer_data['interest_rate'] < 12:
                data['message'] = "Interest Rate At List 12% Required"
                return JsonResponse(data= data, safe= False)
        
        monthly_installment =  monthly_emi_installment(customer_data['loan_amount'], customer_data['interest_rate'], customer_data['tenure'])


        customer_data['monthly_installment'] = round(monthly_installment,2)
        customer_data['approval'] = 1

        
        customer_data['start_date'] = datetime.today().strftime("%Y-%m-%d")
        customer_data['end_date'] = (datetime.today() + relativedelta(months=customer_data['tenure'])).strftime("%Y-%m-%d")
        customer_data['credit_score'] = credit_score


        return JsonResponse(data= customer_data, safe= False)

        #   Data Insert in database and all New keys arange acording to table attribute in database

@csrf_exempt
def createloan(request):
    if request.method == 'POST':
        customer_data = JSONParser().parse(request)
        data = {}
        if not customer_data['customer_id']:
            data['message'] = "Customer Id Empty"
            return JsonResponse(data, safe= False)
        
        if customerid_validation(customer_data['customer_id']) == 0:
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
        
        
        current_loan_amounts = current_loan_amount(customer_data['customer_id'])
        salary = customer_salary(customer_data['customer_id'])
        customer_limit = approved_limit(customer_data['customer_id'])
        loan_emi = current_loan_emi(customer_data['customer_id'])

        if(current_loan_amounts + customer_data['loan_amount']) > customer_limit :
            data['message'] = "Loan Limit Not Available"
            return JsonResponse(data, safe= False)
    
        if((salary/2) < loan_emi):
            data['message'] = "EMI Amount Greater Then Salary Not Approved"
            return JsonResponse(data= data, safe= False)
        

        credit_score = get_credit_score(customer_data['customer_id'])
        
        if credit_score < 10:
            data['message'] = "Credit Score Less Not Approved"
            return JsonResponse(data= data, safe= False)
        
        if  30 > credit_score and credit_score >= 10:
            if customer_data['interest_rate'] < 16:
                data['message'] = "Interest Rate At List 16% Required"
                return JsonResponse(data= data, safe= False)
        if 50 > credit_score and credit_score >= 30:
            if customer_data['interest_rate'] < 12:
                data['message'] = "Interest Rate At List 12% Required"
                return JsonResponse(data= data, safe= False)
        
        monthly_installment =  monthly_emi_installment(customer_data['loan_amount'], customer_data['interest_rate'], customer_data['tenure'])


        customer_data['monthly_installment'] = monthly_installment
        customer_data['approval'] = 1

        
        customer_data['start_date'] = datetime.today().strftime("%Y-%m-%d")
        customer_data['end_date'] = (datetime.today() + relativedelta(months=customer_data['tenure'])).strftime("%Y-%m-%d")
        # customer_data['credit_score'] = credit_score
        # customer_data['approval'] = 1
        customer_data['emi_paid_on_time'] = 0


        loan_serializer = LoanSerializer(data= customer_data)

        if(loan_serializer.is_valid()):
            record = loan_serializer.save()
            data['loan_id'] = record.loan_id
            data['customer_id'] = record.customer_id_id
            data['approval'] = record.approval
            if data['approval']:
                data['message'] = "Loan Approved"
            else:
                data['message'] = "Loan Not Approved"
            data['monthly_installment']= record.monthly_installment

            return JsonResponse(data= data, safe= False)
        data['message'] = 'Record Not Saved'
        return JsonResponse(data, safe= False)

        #   Data Insert in database and all New keys arange acording to table attribute in database
    

@csrf_exempt

def loanDetails(request, loan_id):
    # print(request.method)
    if request.method == "GET":
        no_loan = loanid_available(loan_id)
        data = {}
        if no_loan == 0:
            data['message'] = "Loan Id Invalid"
            return JsonResponse(data= data, safe= False)
        loanResult =  loanData(loan_id)
        print(loanResult)
        customerResult = customerData(loanResult[0]['customer_id_id'])
        
        print(customerResult)

        data['loan_id'] = loanResult[0]['loan_id']
        data['customer'] = {
            "customer_id" : customerResult[0]['customer_id'],
            "first_name" : customerResult[0]['first_name'],
            "last_name" : customerResult[0]['last_name'],
            "phone_number" : customerResult[0]['phone_number'],
            "age" : customerResult[0]['age']
        }
        data['loan_amount'] = loanResult[0]['loan_amount']
        data['interest_rate'] = loanResult[0]['interest_rate']
        data['monthly_installment'] = loanResult[0]['monthly_installment']
        data['tenure'] = loanResult[0]['tenure']
        return JsonResponse(data= data, safe= False)



@csrf_exempt

def customerLoanDetails(request, customer_id):
    
    if request.method == "GET":
        data = {}
        no_of_customer = customerid_validation(customer_id)
        # print(no_of_customer)
        if no_of_customer == 0:
            data['message'] = "Customer Id Invalid"
            return JsonResponse(data= data, safe= False)

        customerLoanResult = customerLoanData(customer_id)
        dataList = []
        for i in range(len(customerLoanResult)):
            datas = {
                "loan_id" : customerLoanResult[i]['loan_id'],
                "loan_amount" : customerLoanResult[i]['loan_amount'],
                "interest_rate" : customerLoanResult[i]['interest_rate'],
                "monthly_installment" : customerLoanResult[i]['monthly_installment'],
                "repayments_left" : customerLoanResult[i]['tenure'] - customerLoanResult[i]['emi_paid_on_time']
            }
            dataList.append(datas)
        data = dataList
        return JsonResponse(data= data, safe= False)