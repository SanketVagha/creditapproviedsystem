from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse


from creditapi.models import Customer,Loan
from creditapi.serializers import CustomerSerializer, LoanSerializer


# Create your views here.

@csrf_exempt

def register(request):
    if request.method == 'GET':
        # customers = Customer.objects.all()
        # customer_serializer = CustomerSerializer(customers, many = True)
        # return JsonResponse(customer_serializer.data , safe= False)
        return JsonResponse("Register Get API Call", safe= False)
    elif request.method == 'POST':
        customer_data = JSONParser().parse(request)
        customer_serializer = CustomerSerializer(data= customer_data)
        if customer_serializer.is_valid():
            customer_serializer.save()
            return JsonResponse("Added Successfully", safe= False)
        return JsonResponse("Failed to Add", safe= False)