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
