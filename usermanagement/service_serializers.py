from rest_framework import serializers
from .models import Service, ServicePlan, Users, Context, ServiceRequest


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ServicePlanSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = ServicePlan
        fields = '__all__'


class ServiceRequestCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    plan_id = serializers.IntegerField(required=False, allow_null=True)
    context_id = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        user = Users.objects.get(id=validated_data['user_id'])
        service = Service.objects.get(id=validated_data['service_id'])
        plan = ServicePlan.objects.get(id=validated_data['plan_id']) if validated_data.get('plan_id') else None
        context = Context.objects.get(id=validated_data['context_id']) if validated_data.get('context_id') else None

        return ServiceRequest.objects.create(
            user=user,
            service=service,
            plan=plan,
            context=context,
            status='initiated'
        )
