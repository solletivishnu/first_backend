from rest_framework import serializers
from .models import ServiceTask, ServiceSubTask
from datetime import date
from usermanagement.models import Users  # Adjust the import path if necessary

class UserDisplaySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.last_name]
        # Filter out None or empty strings, then join with space
        return " ".join(part for part in parts if part).strip()


class ServiceTaskDetailedSerializer(serializers.ModelSerializer):
    client = UserDisplaySerializer(read_only=True)
    assignee = UserDisplaySerializer(read_only=True)
    reviewer = UserDisplaySerializer(read_only=True)
    ageing = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTask
        fields = '__all__'

    def get_ageing(self, obj):
        if obj.created_at:
            return (date.today() - obj.created_at.date()).days
        return None


class ServiceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTask
        fields = '__all__'


class ServiceSubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSubTask
        fields = '__all__'
