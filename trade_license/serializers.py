from rest_framework import serializers
from .models import *

class BasicDetailsSerializer(serializers.ModelSerializer):
    trade_license_file = serializers.FileField(required=False)
    upload_photo = serializers.FileField(required=False)
    class Meta:
        model = BasicDetail
        fields = '__all__'

class BasicDetailsSerializerRetrieval(serializers.ModelSerializer):
    address = serializers.JSONField()
    class Meta:
        model = BasicDetail
        fields = '__all__'

class TradeLicenseExistOrNotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLicenseExistOrNot
        fields = '__all__'

class TradeEntitySerializer(serializers.ModelSerializer):
    # address = serializers.JSONField()
    class Meta:
        model = TradeEntity
        fields = '__all__'

class TradeEntitySerializerRetrieval(serializers.ModelSerializer):
    address = serializers.JSONField()
    class Meta:
        model = TradeEntity
        fields = '__all__'

class PartnerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerDetails
        fields = '__all__'

class TradeLicenseServiceRequestSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer that combines all Trade License related data for a service request
    """
    trade_license = TradeLicenseExistOrNotSerializer(many=True, read_only=True)
    trade_license_entity = TradeEntitySerializerRetrieval(many=True, read_only=True)
    trade_license_partner = PartnerDetailsSerializer(many=True, read_only=True)
    address = serializers.JSONField()
    
    class Meta:
        model = BasicDetail
        fields = '__all__'
