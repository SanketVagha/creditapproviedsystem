from rest_framework import serializers
from creditapi.models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    # customer_id = serializers.ReadOnlyField()
    class Meta:
        model = Customer
        fields = "__all__"
    
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"