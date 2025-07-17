from rest_framework import serializers
from .models import (
    BusinessIdentityStructure, SignatoryDetails, signatoryDetailsInfo, BusinessLocationProofs,
    AdditionalSpaceBusiness, BusinessRegistrationDocuments, ReviewFilingCertificate
)


class BusinessIdentityStructureSerializer(serializers.ModelSerializer):
    number_of_employees = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = BusinessIdentityStructure
        fields = '__all__'


class signatoryDetailsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = signatoryDetailsInfo
        fields = '__all__'


class SignatoryDetailsSerializer(serializers.ModelSerializer):
    signatory_details_info = signatoryDetailsInfoSerializer(many=True, required=False)
    class Meta:
        model = SignatoryDetails
        fields = '__all__'


class AdditionalSpaceBusinessSerializer(serializers.ModelSerializer):
    address = serializers.JSONField()

    class Meta:
        model = AdditionalSpaceBusiness
        fields = '__all__'


class BusinessLocationProofsSerializer(serializers.ModelSerializer):
    principal_place_of_business = serializers.JSONField()
    additional_space_business = AdditionalSpaceBusinessSerializer(required=False)
    class Meta:
        model = BusinessLocationProofs
        fields = '__all__'


class BusinessRegistrationDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRegistrationDocuments
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'
