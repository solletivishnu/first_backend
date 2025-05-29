from rest_framework import serializers
from .models import *


class BusinessIdentitySerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessIdentity
        fields = '__all__'


    def create(self, validated_data):
        print("VALIDATED DATA:", validated_data)  # Debugging
        return super().create(validated_data)


class ApplicantDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantDetails
        fields = '__all__'


class SignatoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatoryDetails
        fields = '__all__'


class BusinessLocationSerializer(serializers.ModelSerializer):
    address = serializers.JSONField()
    class Meta:
        model = BusinessLocation
        fields = '__all__'


class AdditionalSpaceBusinessSerializer(serializers.ModelSerializer):
    address = serializers.JSONField()
    class Meta:
        model = AdditionalSpaceBusiness
        fields = '__all__'


class TradeLicenseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLicenseDetails
        fields = '__all__'

    def validate(self, data):
        apply_new_license = data.get('apply_new_license', getattr(self.instance, 'apply_new_license', 'yes'))

        if apply_new_license == 'no':
            trade_license_number = data.get('trade_license_number') or getattr(self.instance, 'trade_license_number', None)
            trade_license_file = data.get('trade_license_file') or getattr(self.instance, 'trade_license_file', None)

            if not trade_license_number:
                raise serializers.ValidationError({"trade_license_number": "This field is required when applying for a new license."})
            if not trade_license_file:
                raise serializers.ValidationError({"trade_license_file": "This file is required when applying for a new license."})

        return data


class BusinessDocumentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDocumentDetails
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'
