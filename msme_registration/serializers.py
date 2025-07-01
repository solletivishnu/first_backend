from rest_framework import serializers
from .models import *


class BusinessIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessIdentity
        fields = '__all__'

    def validate(self, attrs):
        if attrs.get('has_business_commenced') is False: # If business not commenced, remove date
            attrs['date_of_commencement'] = None
        return attrs


class BusinessClassificationInputsSerializer(serializers.ModelSerializer):
    nic_codes = serializers.JSONField(required=False, allow_null=True)
    number_of_persons_employed = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = BusinessClassificationInputs
        fields = '__all__'


class TurnoverAndInvestmentDeclarationSerializer(serializers.ModelSerializer):
    turnover_in_inr = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = TurnoverAndInvestmentDeclaration
        fields = '__all__'


class LocationOfPlantOrUnitSerializer(serializers.ModelSerializer):
    unit_details = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = LocationOfPlantOrUnit
        fields = '__all__'


class RegisteredAddressSerializer(serializers.ModelSerializer):
    official_address_of_enterprise = serializers.JSONField(required=False, allow_null=True)
    location_of_plant_or_unit = LocationOfPlantOrUnitSerializer(many=True, read_only=True)

    class Meta:
        model = RegisteredAddress
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MsmeReviewFilingCertificate
        fields = '__all__'


class RegisteredAddressWithLocationPlantSerializer(serializers.ModelSerializer):
    official_address_of_enterprise = serializers.JSONField(required=False, allow_null=True)
    location_of_plant_or_unit = LocationOfPlantOrUnitSerializer(many=True, read_only=True)

    class Meta:
        model = RegisteredAddress
        fields = '__all__'

