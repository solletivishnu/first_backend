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

from .models import Context, Role, UserContextRole, Service, ServiceRequest
from Tara.settings.default import *

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_with_service(request):
    email = request.data.get('email')
    password = request.data.get('password')
    business_name = request.data.get('business_name')
    service_id = request.data.get('service_id')

    # ✅ Step 1: Validate input presence
    if not all([email, password, business_name, service_id]):
        return Response(
            {"error": "All fields are required: email, password, business_name, service_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Step 2: Validate user does not already exist
    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists with this email."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Step 3: Validate service
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({"error": "Invalid service ID."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Step 4: Validate business name uniqueness
    if Context.objects.filter(name=business_name, context_type='business').exists():
        return Response({"error": "Business context with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Step 5: Validate role exists
    role_qs = Role.objects.filter(name='Owner', context_type='business', is_system_role=True)
    if not role_qs.exists():
        return Response({"error": "System role 'Owner' for business context not found."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ✅ All validation passed — now safely write
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                is_active='no',
                registration_flow='service',
                registration_completed=False,
                status='active'
            )

            context = Context.objects.create(
                name=business_name,
                context_type='business',
                owner_user=user,
                status='active',
                profile_status='incomplete',
                metadata={}
            )

            user.active_context = context
            user.save()

            role = Role.objects.get(name='Owner', context=context)
            UserContextRole.objects.create(user=user, context=context, role=role, status='active', added_by=user)

            ServiceRequest.objects.create(
                user=user,
                context=context,
                service=service,
                status='initiated'
            )

            # ✅ Send activation email (optional)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            activation_link = f"{FRONTEND_URL}activation?uid={uid}&token={token}"

            try:
                ses_client = boto3.client(
                    'ses',
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )
                ses_client.send_email(
                    Source=EMAIL_HOST_USER,
                    Destination={'ToAddresses': [email]},
                    Message={
                        'Subject': {'Data': "Activate your account"},
                        'Body': {
                            'Html': {'Data': f"<p>Click "
                                             f"<a href='{activation_link}'>here</a> to activate your account.</p>"},
                            'Text': {'Data': f"Activate your account: {activation_link}"}
                        },
                    }
                )
            except ClientError as e:
                logger.error(f"SES email error: {e.response['Error']['Message']}")

            return Response({
                "message": "Registration successful. Activation email sent.",
                "user_id": user.id,
                "context_id": context.id,
                "service_id": service.id,
                "activation_link": activation_link
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Registration failed")
        return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

