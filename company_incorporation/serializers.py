from rest_framework import serializers
from .models import *


class CompanyIncorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyIncorporation
        fields = '__all__'

    def create(self, validated_data):
        return CompanyIncorporation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CompanyIncorporationSerializerRetrieval(serializers.ModelSerializer):
    address = serializers.JSONField()

    class Meta:
        model = CompanyIncorporation
        fields = '__all__'


class DirectorsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectorsDetails
        fields = '__all__'

        def create(self, validated_data):
            return ShareHoldersInformation.objects.create(**validated_data)

        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance



class DirectorsDetailsSerializerRetrieval(serializers.ModelSerializer):
    address = serializers.JSONField()
    shareholder_details = serializers.JSONField()

    class Meta:
        model = DirectorsDetails
        fields = '__all__'


class AuthorizedAndPaidUpCapitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedAndPaidupCapital
        fields = '__all__'

    def create(self, validated_data):
        return AuthorizedAndPaidupCapital.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ShareHoldersInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareHoldersInformation
        fields = '__all__'

    def create(self, validated_data):
        return ShareHoldersInformation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ShareHoldersInformationSerializerRetrieval(serializers.ModelSerializer):
    address = serializers.JSONField()

    class Meta:
        model = ShareHoldersInformation
        fields = '__all__'


class DetailsOfExistingDirectorshipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailsOfExistingDirectorships
        fields = '__all__'

    def create(self, validated_data):
        return DetailsOfExistingDirectorships.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance