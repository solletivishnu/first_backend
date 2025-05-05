from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.db import transaction
from django.utils import timezone
from .models import Module, SubscriptionPlan, Role, UserFeaturePermission
from .serializers import (
    ModuleSerializer, SubscriptionPlanSerializer, RoleSerializer,
    UserFeaturePermissionSerializer, ModuleDetailSerializer,
    SubscriptionPlanSerializer, RoleDetailSerializer,
    UserFeaturePermissionSerializer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from distutils.util import strtobool
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .service_serializers import *


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def service_list_create(request):
    if request.method == 'GET':
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def service_detail(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)

    if request.method == 'GET':
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Service updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        service.delete()
        return Response({'message': 'Service deleted'})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def service_plan_list_create(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)

    if request.method == 'GET':
        plans = service.plans.all()
        serializer = ServicePlanSerializer(plans, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['service'] = service.id
        serializer = ServicePlanSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def service_plan_detail(request, plan_id):
    try:
        plan = ServicePlan.objects.get(id=plan_id)
    except ServicePlan.DoesNotExist:
        return Response({'error': 'Plan not found'}, status=404)

    if request.method == 'GET':
        serializer = ServicePlanSerializer(plan)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ServicePlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Plan updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        plan.delete()
        return Response({'message': 'Plan deleted'})


