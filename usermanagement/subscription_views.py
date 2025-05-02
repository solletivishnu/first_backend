from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import SubscriptionPlan, Module
from .serializers import SubscriptionPlanSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from distutils.util import strtobool

@api_view(['POST'])
@permission_classes([AllowAny])
def create_subscription_plan(request):
    """
    Create a new subscription plan for a module
    Required fields: module_id, name, plan_type, base_price
    Optional fields: description, usage_unit, free_tier_limit, price_per_unit, billing_cycle_days
    """
    try:
        # Validate module exists
        module_id = request.data.get('module_id')
        if not module_id:
            return Response({
                'success': False,
                'error': 'module_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Module with id {module_id} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        # Add module to request data
        data = request.data.copy()
        data['module'] = module_id

        serializer = SubscriptionPlanSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Subscription plan created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError as e:
        return Response({
            'success': False,
            'error': 'A subscription plan with this name already exists for this module'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_subscription_plans(request):
#     try:
#         module_id = request.query_params.get('module_id')
#         plan_type = request.query_params.get('plan_type')
#
#         query = {}
#         if module_id:
#             query['module_id'] = module_id
#         if plan_type:
#             query['plan_type'] = str(plan_type)  # fix: ensure it's not a tuple
#
#         plans = SubscriptionPlan.objects.filter(is_active=True)
#         serializer = SubscriptionPlanSerializer(plans, many=True)
#
#         return Response({
#             'success': True,
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({
#             'success': False,
#             'error': 'An unexpected error occurred',
#             'details': str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_subscription_plans(request):
    """
    List all subscription plans
    Optional filters: module_id, plan_type, is_active
    """
    try:
        module_id = request.query_params.get('module_id')
        plan_type = request.query_params.get('plan_type')
        is_active = request.query_params.get('is_active')

        query = {}
        if module_id:
            query['module_id'] = module_id
        if plan_type:
            query['plan_type'] = plan_type
        if is_active:
            query['is_active'] = is_active

        plans = SubscriptionPlan.objects.filter(**query)
        serializer = SubscriptionPlanSerializer(plans, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_subscription_plan(request, plan_id):
    """
    Get details of a specific subscription plan
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        serializer = SubscriptionPlanSerializer(plan)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except SubscriptionPlan.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Subscription plan with id {plan_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_subscription_plan(request, plan_id):
    """
    Update a subscription plan
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Subscription plan updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except SubscriptionPlan.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Subscription plan with id {plan_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subscription_plan(request, plan_id):
    """
    Delete a subscription plan
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Check if plan is being used by any active subscriptions
        if plan.module_subscriptions.filter(status__in=['trial', 'active', 'pending_renewal']).exists():
            return Response({
                'success': False,
                'error': 'Cannot delete plan with active subscriptions'
            }, status=status.HTTP_400_BAD_REQUEST)

        plan.delete()
        return Response({
            'success': True,
            'message': 'Subscription plan deleted successfully'
        }, status=status.HTTP_200_OK)

    except SubscriptionPlan.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Subscription plan with id {plan_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)