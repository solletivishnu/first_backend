from rest_framework import serializers
from .models import *

class EntrepreneurDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntrepreneurDetails
        fields = '__all__'

class EntrepreneurDetailsSerializerRetrival(serializers.ModelSerializer):
    address_of_entrepreneur = serializers.JSONField()
    class Meta:
        model = EntrepreneurDetails
        fields = '__all__'

class EstablishmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstablishmentDetails
        fields = '__all__'

class EstablishmentDetailsSerializerRetrival(serializers.ModelSerializer):
    address_of_establishment = serializers.JSONField()
    class Meta:
        model = EstablishmentDetails
        fields = '__all__'

class WorkLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLocation
        fields = '__all__'

class WorkLocationSerializerRetrival(serializers.ModelSerializer):
    work_location = serializers.JSONField()
    class Meta:
        model = WorkLocation
        fields = '__all__'

class EmployerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerDetails
        fields = '__all__'

class EmployerDetailsSerializerRetrival(serializers.ModelSerializer):
    address_of_employer = serializers.JSONField()
    total_employees = serializers.JSONField()
    class Meta:
        model = EmployerDetails
        fields = '__all__'

class filesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = '__all__'

class LabourLicenseServiceRequestSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer that combines all Labour License-related data for a service request
    """
    establishment_details = EstablishmentDetailsSerializerRetrival(source='EstablishmentDetails', read_only=True, many=True)
    work_locations = WorkLocationSerializerRetrival(source='work_location', read_only=True, many=True)
    employer_details = EmployerDetailsSerializerRetrival(source='employer_details', read_only=True, many=True)
    files = filesSerializer(source='files_uploaded', read_only=True, many=True)
    
    class Meta:
        model = EntrepreneurDetails
        fields = '__all__'