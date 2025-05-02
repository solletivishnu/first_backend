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
# Module Management APIs


@api_view(['POST'])
def create_module(request):
    """
    API endpoint for creating a new module
    Expected JSON payload:
    {
        "name": "Payroll",
        "description": "Payroll management system",
        "context_type": "business",
        "is_active": true
    }
    """
    serializer = ModuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Module created successfully',
            'module': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_modules(request):
    """
    API endpoint for listing all modules
    Optional query parameters:
    - context_type: Filter by context type (personal/business)
    - is_active: Filter by active status (true/false)
    """
    try:
        context_type = request.query_params.get('context_type')
        is_active_param = request.query_params.get('is_active')
        category = request.query_params.get('category')

        filters = {}
        if context_type:
            filters['context_type'] = context_type

        if is_active_param is not None:
            filters['is_active'] = is_active_param
        if category:
            filters['category'] = category

        # Fetch modules with or without filters
        modules = Module.objects.filter(**filters)
        serializer = ModuleSerializer(modules, many=True)

        return Response({
            'success': True,
            'modules': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET', 'PUT'])
def update_module(request, module_id):
    """
    API endpoint for updating a module
    Expected JSON payload:
    {
        "name": "Updated Payroll",
        "description": "Updated description",
        "is_active": false
    }
    """
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Module with ID {module_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ModuleDetailSerializer(module)
        return Response({
            'success': True,
            'module': serializer.data
        })

    serializer = ModuleSerializer(module, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Module updated successfully',
            'module': serializer.data
        })
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_module(request, module_id):
    """
    API endpoint for deleting a module
    """
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Module with ID {module_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    module.delete()
    return Response({
        'success': True,
        'message': 'Module deleted successfully'
    })


# Subscription Plan Management APIs


# Role Management APIs

@api_view(['POST'])
def create_role(request):
    """
    API endpoint for creating a new role
    Expected JSON payload:
    {
        "name": "Manager",
        "description": "Manager role with limited permissions",
        "context_type": "business",
        "is_active": true
    }
    """
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Role created successfully',
            'role': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_roles(request):
    """
    API endpoint for listing all roles
    Optional query parameters:
    - context_type: Filter by context type (personal/business)
    - is_active: Filter by active status (true/false)
    """
    context_type = request.query_params.get('context_type')
    is_active = request.query_params.get('is_active')

    # Build query
    query = {}
    if context_type:
        query['context_type'] = context_type
    if is_active is not None:
        query['is_active'] = is_active.lower() == 'true'

    # Get roles
    roles = Role.objects.filter(**query)
    serializer = RoleSerializer(roles, many=True)

    return Response({
        'success': True,
        'roles': serializer.data
    })


@api_view(['GET', 'PUT'])
def update_role(request, role_id):
    """
    API endpoint for updating a role
    Expected JSON payload:
    {
        "name": "Updated Manager",
        "description": "Updated description",
        "is_active": false
    }
    """
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Role with ID {role_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoleDetailSerializer(role)
        return Response({
            'success': True,
            'role': serializer.data
        })

    serializer = RoleSerializer(role, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Role updated successfully',
            'role': serializer.data
        })
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_role(request, role_id):
    """
    API endpoint for deleting a role
    """
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Role with ID {role_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    role.delete()
    return Response({
        'success': True,
        'message': 'Role deleted successfully'
    })


# Module Permission Management APIs

@api_view(['POST'])
def create_module_permission(request):
    """
    API endpoint for creating module permissions for a role
    Expected JSON payload:
    {
        "role_id": 1,
        "module_id": 1,
        "permissions": ["create", "read", "update", "delete"]
    }
    """
    serializer = UserFeaturePermissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Module permission created successfully',
            'permission': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_module_permissions(request):
    """
    API endpoint for listing module permissions
    Optional query parameters:
    - role_id: Filter by role ID
    - module_id: Filter by module ID
    """
    role_id = request.query_params.get('role_id')
    module_id = request.query_params.get('module_id')

    # Build query
    query = {}
    if role_id:
        query['role_id'] = role_id
    if module_id:
        query['module_id'] = module_id

    # Get permissions
    permissions = UserFeaturePermission.objects.filter(**query)
    serializer = UserFeaturePermissionSerializer(permissions, many=True)

    return Response({
        'success': True,
        'permissions': serializer.data
    })


@api_view(['GET', 'PUT'])
def update_module_permission(request, permission_id):
    """
    API endpoint for updating module permissions
    Expected JSON payload:
    {
        "permissions": ["read", "update"]
    }
    """
    try:
        permission = UserFeaturePermission.objects.get(id=permission_id)
    except UserFeaturePermission.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Permission with ID {permission_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserFeaturePermissionSerializer(permission)
        return Response({
            'success': True,
            'permission': serializer.data
        })

    serializer = UserFeaturePermissionSerializer(permission, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Module permission updated successfully',
            'permission': serializer.data
        })
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_module_permission(request, permission_id):
    """
    API endpoint for deleting module permissions
    """
    try:
        permission = UserFeaturePermission.objects.get(id=permission_id)
    except UserFeaturePermission.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Permission with ID {permission_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)

    permission.delete()
    return Response({
        'success': True,
        'message': 'Module permission deleted successfully'
    })
