from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse


from creditapi.models import Customer,Loan
from creditapi.serializers import CustomerSerializer, LoanSerializer


import numpy as np

# Create your views here.

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
        customer_data['monthly_salary'] = np.around(customer_data['monthly_salary'])
        customer_data["approved_limit"] = 36 * customer_data['monthly_salary']
        customer_serializer = CustomerSerializer(data = customer_data)
        # return JsonResponse(customer_serializer, safe= False)
        if customer_serializer.is_valid():
            record = customer_serializer.save()
            data['customer_id'] = record.customer_id
            data['name'] = record.first_name + " " + record.last_name
            data['age'] = record.age
            data['monthly_salary'] = record.monthly_salary
            data['approved_limit'] = record.approved_limit
            data['phone_number'] = record.phone_number
            return JsonResponse(data, safe= False)
    data['message'] = 'Record Not Saved'
    return JsonResponse(data, safe= False)