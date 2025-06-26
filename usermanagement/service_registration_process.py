from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from botocore.exceptions import ClientError
import boto3
import logging
from .get_login_data import get_login_response
from .models import Context, Role, UserContextRole, Service, ServiceRequest, PendingUserOTP
from Tara.settings.default import *

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_with_service(request):
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name')
    service_id = request.data.get('service_id')
    otp = request.data.get('otp')
    account_type = request.data.get('account_type', 'business')

    # Step 1: Validate required fields
    if not all([email, password, name, service_id, otp]):
        return Response(
            {"error": "All fields are required: email, password, name, service_id, otp"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 2: Validate account_type
    if account_type not in ['personal', 'business']:
        return Response(
            {"error": "Invalid account_type. Must be 'personal' or 'business'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 3: Validate user doesn't already exist
    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists with this email."}, status=status.HTTP_400_BAD_REQUEST)

    # Step 4: Validate OTP
    try:
        otp_obj = PendingUserOTP.objects.get(email=email)
    except PendingUserOTP.DoesNotExist:
        return Response({"error": "OTP not requested for this email."}, status=status.HTTP_400_BAD_REQUEST)

    if otp_obj.is_expired():
        return Response({"error": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

    if otp_obj.otp_code != otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    # Step 5: Validate service
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({"error": "Invalid service ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Step 6: Validate context name uniqueness
    if Context.objects.filter(name=name, context_type=account_type).exists():
        return Response(
            {"error": f"{account_type.capitalize()} context with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 7: Get system role
    role_name = 'Owner'
    role_qs = Role.objects.filter(name=role_name, context_type=account_type, is_system_role=True)
    if not role_qs.exists():
        return Response(
            {"error": f"System role '{role_name}' for {account_type} context not found."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    system_role = role_qs.first()

    # ✅ All validation passed
    try:
        with transaction.atomic():
            # 1. Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                is_active=True,  # No email activation needed
                registration_flow='service',
                registration_completed=False,
                status='active',
                is_super_admin=False,
            )

            # 2. Create context
            context = Context.objects.create(
                name=name,
                context_type=account_type,
                owner_user=user,
                status='active',
                profile_status='incomplete',
                metadata={'account_type': account_type}
            )

            user.active_context = context
            user.save()

            # 3. Assign role
            UserContextRole.objects.create(
                user=user,
                context=context,
                role=system_role,
                status='active',
                added_by=user
            )

            # 4. Create service request
            ServiceRequest.objects.create(
                user=user,
                context=context,
                service=service,
                status='initiated'
            )

            # 5. Delete OTP after use
            otp_obj.delete()

            login_response_data = get_login_response(user)

            return Response(login_response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Registration failed")
        return Response(
            {"error": f"Registration failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


