# from django.shortcuts import render
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .serializers import (UserRegistrationSerializer, UsersKYCSerializer, UserActivationSerializer,
#                           FirmKYCSerializer,CustomPermissionSerializer, CustomGroupSerializer)
# from django.db.models import Count
# from .serializers import *
# from password_generator import PasswordGenerator
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from rest_framework.views import APIView
# import traceback
# from django.db import DatabaseError, IntegrityError
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django.core.mail import send_mail
# from django.contrib.auth import get_user_model
# from django.conf import settings
# from .models import User, UserKYC, FirmKYC, CustomPermission, CustomGroup, UserAffiliatedRole, GSTDetails
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.exceptions import ValidationError
# from rest_framework_simplejwt.tokens import RefreshToken
# import logging
# import random
# import requests
# import json
# from Tara.settings.default import *
# import boto3
# from botocore.exceptions import ClientError, BotoCoreError
# from datetime import datetime
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import NotFound
# from django.contrib.auth.password_validation import validate_password
# from django.http import Http404
# from .permissions import GroupPermission, has_group_permission
# from django.contrib.auth.decorators import permission_required
# from django.db.models.functions import Coalesce
# from django.db.models import Count, F, Value
# from collections import defaultdict
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import JsonResponse
# from urllib.parse import urlparse, unquote
# from django.db.models.functions import TruncDate
# # Create loggers for general and error logs
# logger = logging.getLogger(__name__)
#
#
# class Constants:
#     SMS_API_POST_URL = 'https://www.fast2sms.com/dev/bulkV2'
#
# def auto_generate_password():
#     pwo = PasswordGenerator()
#     return pwo.shuffle_password('abcdefghijklmnopqrstuvwxyz', 8)  # Generates an 8-character password
#
#
# def generate_otp():
#     return random.randint(100000, 999999)
#
# def send_otp_helper(phone_number, otp):
#     try:
#         payload = f"variables_values={otp}&route=otp&numbers={phone_number}"
#         headers = {
#             'authorization': "8Vt5jZpbP2KwMDOLlIeSGN9g7qn6kBi4FHuy1dvhoYEaARJQfsHlpLvoyPKxfN2jIbSkrXG3CdhRVQ1E",
#             'Content-Type': "application/x-www-form-urlencoded",
#             'Cache-Control': "no-cache",
#         }
#         response = requests.request("POST", Constants.SMS_API_POST_URL, data=payload, headers=headers)
#         returned_msg = json.loads(response.text)
#         return returned_msg
#     except Exception as e:
#         logger.error(e, exc_info=1)
#         raise ValueError(f'Request failed: {str(e)}')
#
# def authenticate():
#     url = "https://api.sandbox.co.in/authenticate"
#     payload = {}
#     headers = {
#         'x-api-key': SANDBOX_API_KEY,
#         'x-api-secret': SANDBOX_API_SECRET,
#         'x-api-version': '3.4.0'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     return response.json()['access_token']
#
#
# @api_view(['GET', 'POST'])
# def custom_permission_list_create(request):
#     if request.method == 'GET':
#         permissions = CustomPermission.objects.all()
#         serializer = CustomPermissionSerializer(permissions, many=True)
#
#         # Use a defaultdict to group permissions by name
#         grouped_permissions = defaultdict(list)
#
#         for perm in serializer.data:
#             action = {
#                 "id": perm['id'],
#                 "key": perm['action_name'],
#                 "label": perm['action_name'].replace('_', ' ').title(),  # Generate label from codename
#                 "description": perm['description']
#             }
#             grouped_permissions[perm['module_name']].append(action)
#
#         return Response(grouped_permissions)
#
#     elif request.method == 'POST':
#         serializer = CustomPermissionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"data": serializer.data, "detail": "Custom Permission Created."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def custom_permission_retrieve_update_destroy(request, pk):
#     try:
#         permission = CustomPermission.objects.get(pk=pk)
#     except CustomPermission.DoesNotExist:
#         return Response({"error": "Permission not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = CustomPermissionSerializer(permission)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = CustomPermissionSerializer(permission, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         permission.delete()
#         return Response({"message": "Permission deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#
#
# # CRUD for CustomGroup
#
# @api_view(['GET', 'POST'])
# def custom_group_list_create(request):
#     if request.method == 'GET':
#         try:
#             groups = CustomGroup.objects.all()
#             serializer = CustomGroupSerializer(groups, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     elif request.method == 'POST':
#         serializer = CustomGroupSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"data": serializer.data, "detail": "User details saved successfully."},
#                             status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def custom_group_retrieve_update_destroy(request, pk):
#     try:
#         group = CustomGroup.objects.get(pk=pk)
#     except CustomGroup.DoesNotExist:
#         return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = CustomGroupSerializer(group)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = CustomGroupSerializer(group, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         group.delete()
#         return Response({"message": "Group deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['POST'])
# def assign_permissions_to_group(request, group_id):
#     """
#     Assign permissions to a group.
#     """
#     try:
#         group = CustomGroup.objects.get(id=group_id)
#     except CustomGroup.DoesNotExist:
#         return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'POST':
#         permission_ids = request.data.get('permissions', [])
#         if not isinstance(permission_ids, list):
#             return Response({"error": "'permissions' must be a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Add permissions to the group
#         try:
#             permissions = CustomPermission.objects.filter(id__in=permission_ids)
#             group.permissions.set(permissions)  # Replaces existing permissions with the new ones
#             return Response(
#                 {"message": f"Permissions successfully assigned to group '{group.name}'."},
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['POST'])
# def assign_group_with_permissions(request):
#     """
#     Assign a single group to a user with optional customization of permissions.
#     """
#     user_id = request.data.get('user')
#     group_id = request.data.get('group')  # Expecting only one group now
#     custom_permissions_ids = request.data.get('custom_permissions', [])
#
#     # Validate User
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     # Validate Group
#     try:
#         group = CustomGroup.objects.get(id=group_id)
#     except CustomGroup.DoesNotExist:
#         return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     # Get or Create UserGroup (Ensure one user has only one UserGroup entry)
#     user_group, created = UserAffiliatedRole.objects.get_or_create(user=user)
#     user_group.group = group  # Assigning a single group
#
#     # Assign permissions
#     if custom_permissions_ids:
#         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
#         if not custom_permissions.exists():
#             return Response({"error": "Invalid custom permissions provided"}, status=status.HTTP_400_BAD_REQUEST)
#         user_group.custom_permissions.set(custom_permissions)
#     else:
#         # Default to the group's permissions if no custom permissions are provided
#         default_permissions = group.permissions.all()  # Fetch default permissions from the assigned group
#         user_group.custom_permissions.set(default_permissions)
#
#     user_group.save()
#
#     return Response({
#         "user_group": UserGroupSerializer(user_group).data,
#         "message": "Group assigned successfully with custom permissions."
#     }, status=status.HTTP_201_CREATED)
#
#
# def assign_permissions(data):
#     """
#     Assign a single group to a user with optional customization of permissions.
#     Raises ValueError for missing users or groups instead of returning a Response.
#     """
#     created_by = data.get('created_by')
#     user_id = data.get('id')
#
#     if not created_by:
#         user_type = data.get('user_type')
#
#         group_id_mapping = {
#             "Individual": 10,
#             "Business": 11,
#             "ServiceProvider": 1,
#             "CA": 24
#         }
#
#         if user_type not in group_id_mapping:
#             raise ValueError("Invalid user type provided.")
#
#         try:
#             group = CustomGroup.objects.get(id=group_id_mapping[user_type])
#         except ObjectDoesNotExist:
#             raise ValueError(f"Group with ID {group_id_mapping[user_type]} not found.")
#
#         try:
#             user = User.objects.get(id=user_id)
#         except ObjectDoesNotExist:
#             raise ValueError(f"User with ID {user_id} not found.")
#
#         # Get or Create UserGroup (Ensure one user has only one UserGroup entry)
#         user_group = UserAffiliatedRole.objects.create(user=user, affiliated=user, flag=False)
#         user_group.group = group  # Assigning a single group
#         user_group.custom_permissions.set(group.permissions.all())  # Default permissions
#         user_group.save()
#         return UserGroupSerializer(user_group).data
#
#
# @api_view(['GET'])
# def get_user_group_permissions(request):
#     """
#     Retrieve the group and custom permissions associated with a User based on the user_id and/or permission name.
#     """
#     user_id = request.query_params.get('user_id')
#     affiliated_id = request.query_params.get('affiliated_id')
#     permission_name = request.query_params.get('name')
#
#     # Ensure mandatory parameters are provided
#     if not user_id or not affiliated_id:
#         return Response(
#             {"error": "Both 'user_id' and 'affiliated_id' are required."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     # Ensure the user is authenticated
#     if not request.user.is_authenticated:
#         return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
#
#     # If user_id is provided, fetch the UserGroup entry
#     if user_id and affiliated_id:
#         try:
#             user_group = UserAffiliatedRole.objects.get(user_id=user_id, affiliated_id=affiliated_id)
#         except UserAffiliatedRole.DoesNotExist:
#             return Response({"error": "No UserGroup found for the given user."}, status=status.HTTP_404_NOT_FOUND)
#
#         # If permission_name is provided, filter custom permissions
#         if permission_name:
#             filtered_permissions = user_group.custom_permissions.filter(module_name=permission_name)
#         else:
#             filtered_permissions = user_group.custom_permissions.all()
#
#         # Organize permissions by their 'name' field
#         permissions_by_group = {}
#         for perm in filtered_permissions:
#             group_name = perm.module_name  # Group by the 'module_name' of the permission
#             permission_data = {
#                 "id": perm.id,
#                 "key": perm.action_name,
#                 "label": perm.action_name.replace("_", " ").title(),
#                 "description": perm.description
#             }
#             if group_name not in permissions_by_group:
#                 permissions_by_group[group_name] = []
#             permissions_by_group[group_name].append(permission_data)
#
#         # Prepare the final response
#         data = {
#             "id": user_group.id,
#             "user": user_group.user.id,
#             "group": user_group.group.name if user_group.group else None,
#             "custom_permissions": permissions_by_group,
#             "added_on": user_group.added_on
#         }
#
#         return Response(data, status=status.HTTP_200_OK)
#
#     # If neither parameter is provided, return an error
#     return Response({
#         "error": "The 'user_id' parameter is required."
#     }, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['PUT'])
# def update_group_permissions(request, user_group_id):
#     """
#     Update the group or custom permissions associated with a UserGroup.
#     This allows updating the group and custom permissions.
#     """
#     try:
#         user_group = UserAffiliatedRole.objects.get(id=user_group_id)
#     except UserAffiliatedRole.DoesNotExist:
#         return Response({"error": "UserGroup not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     group_id = request.data.get('group')  # Expecting a single group ID
#     custom_permissions_ids = request.data.get('custom_permissions', [])  # List of permission IDs
#
#     # Handle group update
#     if group_id:
#         try:
#             group = CustomGroup.objects.get(id=group_id)
#         except CustomGroup.DoesNotExist:
#             return Response({"error": "Group not found"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user_group.group = group  # Assign new group
#
#     # Handle custom permissions update
#     if custom_permissions_ids is not None:
#         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
#         if custom_permissions.count() != len(custom_permissions_ids):
#             return Response({"error": "Invalid custom permissions provided"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user_group.custom_permissions.set(custom_permissions)
#
#     # Save changes
#     user_group.save()
#
#     return Response({
#         "user_group": UserGroupSerializer(user_group).data,
#         "message": "UserGroup updated successfully."
#     }, status=status.HTTP_200_OK)
#
# # User Registration
# @swagger_auto_schema(
#     method='post',
#     request_body=UserRegistrationSerializer,
#     responses={
#         201: openapi.Response("User registered successfully"),
#         400: openapi.Response("Bad Request"),
#         500: openapi.Response("Internal Server Error"),
#     },
#     operation_description="Handle user registration with email or mobile number verification."
# )
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def user_registration(request):
#     """
#     Handle user registration with autogenerated password if not provided,
#     and verify email or mobile number.
#     """
#     logger.info("Received a user registration request.")
#     print("*********************")
#
#     if request.method == 'POST':
#         try:
#             request_data = request.data
#             email = request_data.get('email', '').lower()
#             mobile_number = request_data.get('mobile_number', '')
#
#             logger.debug(f"Request data: email={email}, mobile_number={mobile_number}")
#
#             # Ensure at least one of email or mobile_number is provided
#             if not email and not mobile_number:
#                 logger.warning("Registration failed: Missing both email and mobile number.")
#                 return Response(
#                     {"error": "Either email or mobile number must be provided."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             serializer = UserRegistrationSerializer(data=request_data)
#             if serializer.is_valid():
#                 user = serializer.save()
#                 user_data = serializer.data
#                 logger.info(f"User created successfully: {user.pk}")
#                 useraffiliated_role = assign_permissions(user_data)
#
#                 # Handle Email Verification
#                 if email:
#                     token = default_token_generator.make_token(user)
#                     uid = urlsafe_base64_encode(str(user.pk).encode())
#                     activation_link = f"{FRONTEND_URL}activation?uid={uid}&token={token}"
#                     ses_client = boto3.client(
#                         'ses',
#                         region_name=AWS_REGION,
#                         aws_access_key_id=AWS_ACCESS_KEY_ID,
#                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#                     )
#
#                     subject = "Activate your account"
#                     body_html = f"""
#                                         <html>
#                                         <body>
#                                             <h1>Activate Your Account</h1>
#                                             <p>Click the link below to activate your account:</p>
#                                             <a href="{activation_link}">Activate Account</a>
#                                         </body>
#                                         </html>
#                                         """
#
#                     try:
#                         response = ses_client.send_email(
#                             Source=EMAIL_HOST_USER,
#                             Destination={'ToAddresses': [email]},
#                             Message={
#                                 'Subject': {'Data': subject},
#                                 'Body': {
#                                     'Html': {'Data': body_html},
#                                     'Text': {'Data': f"Activate your account using the link: {activation_link}"}
#                                 },
#                             }
#                         )
#                         logger.info(f"Activation email sent to: {email}")
#                         return Response(
#                             {"message": "User registered. Check your email for activation link."},
#                             status=status.HTTP_201_CREATED,
#                         )
#                     except ClientError as e:
#                         logger.error(f"Failed to send email via SES: {e.response['Error']['Message']}")
#                         return Response(
#                             {"error": "Failed to send activation email. Please try again later."},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                         )
#
#                 # Handle Mobile Number Verification
#                 if mobile_number:
#                     otp = generate_otp()
#                     response = send_otp_helper(mobile_number, otp)  # Changed function name to avoid conflict
#                     if response['return']:
#                         query = User.objects.filter(mobileNumber=mobile_number)
#                         if query.exists():
#                             obj = query.first()
#                             obj.otp = int(otp)
#                             obj.save()
#                             logger.info(f"OTP sent to mobile number: {mobile_number}")
#                             return Response(
#                                 {"message": "User registered. Check your mobile for activation code."},
#                                 status=status.HTTP_201_CREATED,
#                             )
#
#             logger.warning("Registration failed: Validation errors.")
#             logger.debug(f"Validation errors: {serializer.errors}")
#             print("************************************")
#             print("########################")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except IntegrityError as e:
#             logger.error(f"Integrity error during registration: {str(e)}")
#             return Response({"error": "A user with this email or mobile number already exists."},
#                             status=status.HTTP_400_BAD_REQUEST)
#         except DatabaseError as e:
#             logger.error(f"Database error during registration: {str(e)}")
#             return Response({"error": "Database error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error during registration: {str(e)}")
#             return Response({"error": "An unexpected error occurred.", "details": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# def assign_group_with_user_affiliated_permissions(user_group_permission_data):
#     """
#     Assign a single group to a user with optional customization of permissions.
#     Raises ValueError for missing users, groups, or invalid custom permissions.
#     """
#     user_id = user_group_permission_data.get('id')
#     group_id = user_group_permission_data.get('group')  # Expecting only one group now
#     custom_permissions_ids = user_group_permission_data.get('custom_permissions', [])
#     created_by = user_group_permission_data.get('created_by')
#
#     # Validate User
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         raise ValueError(f"User with ID {user_id} not found.")
#
#     # Validate Created By User
#     try:
#         created_by_user = User.objects.get(id=created_by)
#     except ObjectDoesNotExist:
#         raise ValueError(f"Created By User with ID {created_by} not found.")
#
#     if user.created_by.user_type == "Individual":
#         if user.user_type == "Business":
#             user_group, created = UserAffiliatedRole.objects.get_or_create(user=created_by_user, affiliated=user)
#             group = CustomGroup.objects.get(id=11)
#             user_group.custom_permissions.set(group.permissions.all())
#             user_group.save()
#         elif user.user_type == "CA":
#             user_group, created = UserAffiliatedRole.objects.get_or_create(user=created_by_user, affiliated=user)
#             group = CustomGroup.objects.get(id=25)
#             user_group.custom_permissions.set(group.permissions.all())
#             user_group.save()
#         elif user.user_type == "ServiceProvider":
#             user_group, created = UserAffiliatedRole.objects.get_or_create(user=created_by_user, affiliated=user)
#             group = CustomGroup.objects.get(id=1)
#             user_group.custom_permissions.set(group.permissions.all())
#             user_group.save()
#     if user.created_by.user_type == "Business":
#         if user.user_type == "Individual":
#             user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=created_by_user)
#             group = CustomGroup.objects.get(id=11)
#             user_group.custom_permissions.set(group.permissions.all())
#             user_group.save()
#         elif user.user_type == "CA":
#             user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=created_by_user)
#             group = CustomGroup.objects.get(id=11)
#             user_group.custom_permissions.set(group.permissions.all())
#             user_group.save()
#
#     if group_id:
#         # Validate Group
#         try:
#             group = CustomGroup.objects.get(id=group_id)
#         except ObjectDoesNotExist:
#             raise ValueError(f"Group with ID {group_id} not found.")
#
#     else:
#         user_type = user_group_permission_data.get('user_type')
#
#         group_id_mapping = {
#             "Individual": 10,
#             "Business": 11,
#             "ServiceProvider": 1,
#             "CA": 24
#         }
#
#         if user_type not in group_id_mapping:
#             raise ValueError("Invalid user type provided.")
#
#         try:
#             group = CustomGroup.objects.get(id=group_id_mapping[user_type])
#         except ObjectDoesNotExist:
#             raise ValueError(f"Group with ID {group_id_mapping[user_type]} not found.")
#
#     # Get or Create UserGroup (Ensure one user has only one UserGroup entry)
#
#     self_account, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=user)
#     self_account.group = group
#
#     # Assign permissions
#     if custom_permissions_ids:
#         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
#         if not custom_permissions.exists():
#             raise ValueError("Invalid custom permissions provided.")
#         self_account.custom_permissions.set(custom_permissions)
#
#     else:
#         # Default to the group's permissions if no custom permissions are provided
#         self_account.custom_permissions.set(group.permissions.all())
#     self_account.save()
#
#     return UserGroupSerializer(user_group).data
#
#
# def assign_group_with_affiliated_permissions(user_group_permission_data):
#     """
#     Assign a single group to a user with optional customization of permissions.
#     Raises ValueError for missing users, groups, or invalid custom permissions.
#     """
#     user_id = user_group_permission_data.get('id')
#     group_id = user_group_permission_data.get('group')  # Expecting only one group now
#     custom_permissions_ids = user_group_permission_data.get('custom_permissions', [])
#     created_by = user_group_permission_data.get('created_by')
#
#     # Validate User
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         raise ValueError(f"User with ID {user_id} not found.")
#
#     # Validate Created By User
#     try:
#         created_by_user = User.objects.get(id=created_by)
#     except ObjectDoesNotExist:
#         raise ValueError(f"Created By User with ID {created_by} not found.")
#
#     if group_id:
#         # Validate Group
#         try:
#             group = CustomGroup.objects.get(id=group_id)
#         except ObjectDoesNotExist:
#             raise ValueError(f"Group with ID {group_id} not found.")
#
#     else:
#         user_type = user_group_permission_data.get('user_type')
#
#         group_id_mapping = {
#             "Individual": 10,
#             "Business": 11,
#             "ServiceProvider": 1,
#             "CA": 24
#         }
#
#         if user_type not in group_id_mapping:
#             raise ValueError("Invalid user type provided.")
#
#         try:
#             group = CustomGroup.objects.get(id=group_id_mapping[user_type])
#         except ObjectDoesNotExist:
#             raise ValueError(f"Group with ID {group_id_mapping[user_type]} not found.")
#
#     # Get or Create UserGroup (Ensure one user has only one UserGroup entry)
#
#     user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=created_by_user)
#     user_group.group = group  # Assigning a single group
#
#     self_account, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=user)
#     self_account.group = group
#
#     affiliated_account, created = UserAffiliatedRole.objects.get_or_create(user=created_by_user, affiliated=user)
#     affiliated_account.group = group
#
#     # Assign permissions
#     if custom_permissions_ids:
#         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
#         if not custom_permissions.exists():
#             raise ValueError("Invalid custom permissions provided.")
#         user_group.custom_permissions.set(custom_permissions)
#         self_account.custom_permissions.set(custom_permissions)
#         affiliated_account.custom_permissions.set(custom_permissions)
#
#     else:
#         # Default to the group's permissions if no custom permissions are provided
#         user_group.custom_permissions.set(group.permissions.all())  # Fetch default permissions
#         self_account.custom_permissions.set(group.permissions.all())
#         affiliated_account.custom_permissions.set(group.permissions.all())
#
#     user_group.save()
#     self_account.save()
#     affiliated_account.save()
#
#     return UserGroupSerializer(user_group).data
#
# # def assign_group_with_affiliated_permissions(user_group_permission_data):
# #     """
# #     Assign a single group to a user with optional customization of permissions.
# #     Raises ValueError for missing users, groups, or invalid custom permissions.
# #     """
# #     user_id = user_group_permission_data.get('id')
# #     group_id = user_group_permission_data.get('group')  # Expecting only one group now
# #     custom_permissions_ids = user_group_permission_data.get('custom_permissions', [])
# #     created_by = user_group_permission_data.get('created_by')
# #
# #     # Validate User and Created By User
# #     user = get_object_or_404(User, id=user_id)
# #     created_by_user = get_object_or_404(User, id=created_by)
# #
# #     # Validate Group
# #     group = get_group_for_user(user_group_permission_data, group_id)
# #
# #     # Assign User to Group with Permissions
# #     user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=created_by_user)
# #     self_account, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=user)
# #     affiliated_account, created = UserAffiliatedRole.objects.get_or_create(user=created_by_user, affiliated=user)
# #
# #     # Set permissions for all related accounts
# #     set_permissions(user_group, custom_permissions_ids, group)
# #     set_permissions(self_account, custom_permissions_ids, group)
# #     set_permissions(affiliated_account, custom_permissions_ids, group)
# #
# #     # Save updated roles
# #     UserAffiliatedRole.objects.bulk_update([user_group, self_account, affiliated_account], ['group', 'custom_permissions'])
# #
# #     return UserGroupSerializer(user_group).data
# #
# # def get_group_for_user(user_group_permission_data, group_id):
# #     """
# #     Returns the appropriate group for a user based on provided data.
# #     """
# #     if group_id:
# #         return get_object_or_404(CustomGroup, id=group_id)
# #
# #     # Default to a group mapping if no group ID is provided
# #     user_type = user_group_permission_data.get('user_type')
# #     group_id_mapping = {
# #         "Individual": 10,
# #         "Business": 11,
# #         "ServiceProvider": 1,
# #         "CA": 25
# #     }
# #     group_id = group_id_mapping.get(user_type)
# #     if not group_id:
# #         raise ValueError("Invalid user type provided.")
# #
# #     return get_object_or_404(CustomGroup, id=group_id)
# #
# # def set_permissions(user_group, custom_permissions_ids, group):
# #     """
# #     Assign custom permissions to a user group. Default to group permissions if no custom ones are provided.
# #     """
# #     if custom_permissions_ids:
# #         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
# #         user_group.custom_permissions.set(custom_permissions)
# #     else:
# #         user_group.custom_permissions.set(group.permissions.all())
#
#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def user_registration_by_admin(request):
#     """
#     Handle user registration by superadmin without activation link,
#     and send username and password to the user via email.
#     """
#     logger.info("Received a superadmin user registration request.")
#     print("*********************")
#
#     if request.method == 'POST':
#         try:
#             request_data = request.data.copy()
#
#             group = request_data.pop('group', None)
#             custom_permissions = request_data.pop('custom_permissions', [])
#
#             email = request_data.get('email', '').lower()
#             mobile_number = request_data.get('mobile_number', '')
#
#             logger.debug(f"Request data: email={email}, mobile_number={mobile_number}")
#
#             # Ensure at least one of email or mobile_number is provided
#             if not email and not mobile_number:
#                 logger.warning("Registration failed: Missing both email and mobile number.")
#                 return Response(
#                     {"error": "Either email or mobile number must be provided."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             # Prepare request data for serializer
#             password = request_data['password']
#             # request_data['created_by'] = request.user.id
#             serializer = UserRegistrationSerializer(data=request_data)
#
#             if serializer.is_valid():
#                 user = serializer.save()
#                 user_data = serializer.data
#                 logger.info(f"User created successfully by superadmin: {user.pk}")
#                 user_data['group'] = group
#                 user_data['custom_permissions'] = custom_permissions
#                 # user_affiliated_role = assign_group_with_affiliated_permissions(user_data)
#                 user_affiliated_role =  assign_group_with_user_affiliated_permissions(user_data)
#
#                 # Send email with the username and password
#                 if email:
#                     subject = "Your Account Details"
#                     body_html = f"""
#                                     <html>
#                                     <body>
#                                         <h1>Welcome to Our Platform</h1>
#                                         <p>Your account has been created by the superadmin.</p>
#                                         <p><strong>Username:</strong> {user.user_name}</p>
#                                         <p><strong>Password:</strong> {password}</p>
#                                     </body>
#                                     </html>
#                                     """
#                     ses_client = boto3.client(
#                         'ses',
#                         region_name=AWS_REGION,
#                         aws_access_key_id=AWS_ACCESS_KEY_ID,
#                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#                     )
#
#                     try:
#                         response = ses_client.send_email(
#                             Source=EMAIL_HOST_USER,
#                             Destination={'ToAddresses': [email]},
#                             Message={
#                                 'Subject': {'Data': subject},
#                                 'Body': {
#                                     'Html': {'Data': body_html},
#                                     'Text': {'Data': f"Your username is: {user.email}\nYour password is: {password}"}
#                                 },
#                             }
#                         )
#                         logger.info(f"Account details email sent to: {email}")
#                         return Response(
#                             {"message": "User created successfully. Check your email for the username and password."},
#                             status=status.HTTP_201_CREATED,
#                         )
#
#                     except ClientError as e:
#                         logger.error(f"Failed to send email via SES: {e.response['Error']['Message']}")
#                         return Response(
#                             {"error": "Failed to send account details email. Please try again later."},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                         )
#
#             logger.warning("Registration failed: Validation errors.")
#             logger.debug(f"Validation errors: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         except IntegrityError as e:
#             logger.error(f"Integrity error during registration: {str(e)}")
#             return Response({"error": "A user with this email or mobile number already exists."},
#                             status=status.HTTP_400_BAD_REQUEST)
#         except DatabaseError as e:
#             logger.error(f"Database error during registration: {str(e)}")
#             return Response({"error": "Database error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error during registration: {str(e)}")
#             return Response({"error": "An unexpected error occurred.", "details": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def business_affiliation(request):
#     """
#     Handle user registration by superadmin without activation link,
#     and send username and password to the user via email.
#     """
#     logger.info("Received a superadmin user registration request.")
#     print("*********************")
#
#     if request.method == 'POST':
#         try:
#             request_data = request.data.copy()
#             group = request_data.pop('group', None)
#             custom_permissions = request_data.pop('custom_permissions', [])
#             affiliated_id = request.data.get('affiliated_id')
#             user_id = request.data.get('user_id')
#
#
#         except IntegrityError as e:
#             logger.error(f"Integrity error during registration: {str(e)}")
#             return Response({"error": "A user with this email or mobile number already exists."},
#                             status=status.HTTP_400_BAD_REQUEST)
#         except DatabaseError as e:
#             logger.error(f"Database error during registration: {str(e)}")
#             return Response({"error": "Database error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error during registration: {str(e)}")
#             return Response({"error": "An unexpected error occurred.", "details": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# # Define the conditional schema
# def get_conditional_schema(user_type):
#     """
#     Return the schema based on the user type.
#     """
#     if user_type == 'ServiceProvider_Admin':
#         # Add visa-related fields for ServiceProvider_Admin
#         return openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email Address'),
#                 'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile Number'),
#                 'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
#                 'created_by': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the admin who created the user'),
#                 'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
#                 'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
#                 'passport_number': openapi.Schema(type=openapi.TYPE_STRING, description='Passport Number'),
#                 'purpose': openapi.Schema(type=openapi.TYPE_STRING, description='Purpose of the Visa'),
#                 'visa_type': openapi.Schema(type=openapi.TYPE_STRING, description='Visa Type'),
#                 'destination_country': openapi.Schema(type=openapi.TYPE_STRING, description='Destination Country'),
#             },
#             required=['email', 'mobile_number', 'password', 'created_by']
#         )
#     else:
#         # Return default schema for non-ServiceProvider_Admin
#         return openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email Address'),
#                 'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile Number'),
#                 'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
#                 'created_by': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the admin who created the user'),
#             },
#             required=['email', 'mobile_number', 'password', 'created_by']
#         )
#
#
# def assign_group_with_affiliated_permissions_team_management(user_group_permission_data):
#     user_id = user_group_permission_data.get('id')
#     group_id = user_group_permission_data.get('group')  # Expecting only one group now
#     custom_permissions_ids = user_group_permission_data.get('custom_permissions', [])
#     created_by = user_group_permission_data.get('created_by')
#
#     # Validate User
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         raise ValueError(f"User with ID {user_id} not found.")
#
#     # Validate Created By User
#     try:
#         created_by_user = User.objects.get(id=created_by)
#     except ObjectDoesNotExist:
#         raise ValueError(f"Created By User with ID {created_by} not found.")
#
#     user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=created_by_user)
#     group = CustomGroup.objects.get(id=group_id)
#     user_group.group = group
#     if custom_permissions_ids:
#         custom_permissions = CustomPermission.objects.filter(id__in=custom_permissions_ids)
#         if not custom_permissions.exists():
#             raise ValueError("Invalid custom permissions provided.")
#         user_group.custom_permissions.set(custom_permissions)
#     else:
#         # Default to the group's permissions if no custom permissions are provided
#         user_group.custom_permissions.set(group.permissions.all())
#     user_group.save()
#
#     return UserGroupSerializer(user_group).data
#
#
# # Swagger schema dynamically based on user type
# @swagger_auto_schema(
#     method='post',
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
#             'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description="User's mobile number"),
#         },
#         required=['email', 'mobile_number'],
#     ),
#     responses={
#         201: openapi.Response("User registered successfully. Check your email or mobile for credentials."),
#         400: openapi.Response("Bad Request. Missing required fields or validation error."),
#         500: openapi.Response("Internal Server Error. Database or email sending failed."),
#     },
#     operation_description="Admin can register users, send autogenerated credentials, and trigger email or OTP verification. Provide only `email` or `mobile_number` in the payload.",
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#         ),
#     ],
#    tags=["User Management - UsersCreation"]
# )
# @permission_classes([IsAuthenticated])
# @api_view(['POST'])
# def AdminOwnerUserCreation(request):
#     """
#     Handle user registration by superadmin without activation link,
#     and send username and password to the user via email.
#     """
#     logger.info("Received a superadmin user registration request.")
#     print("*********************")
#
#     if request.method == 'POST':
#         try:
#             request_data = request.data.copy()
#
#             group = request_data.pop('group', None)
#             custom_permissions = request_data.pop('custom_permissions', [])
#
#             email = request_data.get('email', '').lower()
#             mobile_number = request_data.get('mobile_number', '')
#
#             logger.debug(f"Request data: email={email}, mobile_number={mobile_number}")
#
#             # Ensure at least one of email or mobile_number is provided
#             if not email and not mobile_number:
#                 logger.warning("Registration failed: Missing both email and mobile number.")
#                 return Response(
#                     {"error": "Either email or mobile number must be provided."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             request_data['password'] = auto_generate_password()
#
#             # Prepare request data for serializer
#             password = request_data['password']
#             # request_data['created_by'] = request.user.id
#             serializer = UserRegistrationSerializer(data=request_data)
#
#             if serializer.is_valid():
#                 user = serializer.save()
#                 user_data = serializer.data
#                 logger.info(f"User created successfully by superadmin: {user.pk}")
#                 user_data['group'] = group
#                 user_data['custom_permissions'] = custom_permissions
#                 # user_affiliated_role = assign_group_with_affiliated_permissions(user_data)
#                 user_affiliated_role = assign_group_with_affiliated_permissions_team_management(user_data)
#
#                 # Send email with the username and password
#                 if email:
#                     subject = "Your Account Details"
#                     body_html = f"""
#                                     <html>
#                                     <body>
#                                         <h1>Welcome to Our Platform</h1>
#                                         <p>Your account has been created by the superadmin.</p>
#                                         <p><strong>Username:</strong> {user.user_name}</p>
#                                         <p><strong>Password:</strong> {password}</p>
#                                     </body>
#                                     </html>
#                                     """
#                     ses_client = boto3.client(
#                         'ses',
#                         region_name=AWS_REGION,
#                         aws_access_key_id=AWS_ACCESS_KEY_ID,
#                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#                     )
#
#                     try:
#                         response = ses_client.send_email(
#                             Source=EMAIL_HOST_USER,
#                             Destination={'ToAddresses': [email]},
#                             Message={
#                                 'Subject': {'Data': subject},
#                                 'Body': {
#                                     'Html': {'Data': body_html},
#                                     'Text': {'Data': f"Your username is: {user.email}\nYour password is: {password}"}
#                                 },
#                             }
#                         )
#                         logger.info(f"Account details email sent to: {email}")
#                         return Response(
#                             {"message": "User created successfully. Check your email for the username and password."},
#                             status=status.HTTP_201_CREATED,
#                         )
#
#                     except ClientError as e:
#                         logger.error(f"Failed to send email via SES: {e.response['Error']['Message']}")
#                         return Response(
#                             {"error": "Failed to send account details email. Please try again later."},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                         )
#
#             logger.warning("Registration failed: Validation errors.")
#             logger.debug(f"Validation errors: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         except IntegrityError as e:
#             logger.error(f"Integrity error during registration: {str(e)}")
#             return Response({"error": "A user with this email or mobile number already exists."},
#                             status=status.HTTP_400_BAD_REQUEST)
#         except DatabaseError as e:
#             logger.error(f"Database error during registration: {str(e)}")
#             return Response({"error": "Database error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error during registration: {str(e)}")
#             return Response({"error": "An unexpected error occurred.", "details": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @swagger_auto_schema(
#     method='post',
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
#             'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
#             'passport_number': openapi.Schema(type=openapi.TYPE_STRING, description='Passport number of the user'),
#             'purpose': openapi.Schema(type=openapi.TYPE_STRING, description='Purpose of travel'),
#             'visa_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of visa'),
#             'destination_country': openapi.Schema(type=openapi.TYPE_STRING, description='Destination country'),
#             'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user'),
#             'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile number of the user'),
#         },
#         required=['first_name', 'last_name', 'passport_number', 'visa_type', 'destination_country'],
#     ),
#     responses={
#         201: openapi.Response("Visa user registered successfully."),
#         400: openapi.Response("Bad Request. Missing required fields or validation error."),
#         500: openapi.Response("Internal Server Error. Database error occurred."),
#     },
#     operation_description="ServiceProviderAdmin can register visa users with additional details.",
#     tags=["User Management - VisaUsersCreation"],
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#         ),
#     ],
# )
# @permission_classes([IsAuthenticated])
# @api_view(['POST'])
# def visa_users_creation(request):
#     """
#     Handles the creation of a visa user by ServiceProvider_Admin.
#     Creates a user first and associates visa application details with them.
#     """
#     if request.method != 'POST':
#         return Response({"error": "Invalid HTTP method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     service_provider_admin_roles = [
#         'ServiceProvider_Owner', 'ServiceProvider_Admin',
#         'Tara_SuperAdmin', 'Tara_Admin'
#     ]
#
#     if request.user.user_role not in service_provider_admin_roles:
#         return Response(
#             {'error_message': 'Unauthorized Access. Only ServiceProviderAdmin can create visa users.', 'status_cd': 1},
#             status=status.HTTP_401_UNAUTHORIZED
#         )
#
#     try:
#         # Step 1: Create the user
#         email = request.data.get('email', '').lower()
#         mobile_number = request.data.get('mobile_number', '')
#         if not email and not mobile_number:
#             return Response(
#                 {"error": "Either email or mobile number must be provided."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         user_data = {
#             'email': email,
#             'mobile_number': mobile_number,
#             'password': auto_generate_password(),
#             'created_by': request.user.id,
#             'user_type': 'ServiceProvider',
#             'user_role': 'Individual_User',
#             'first_name': request.data.get('first_name'),
#             'last_name': request.data.get('last_name'),
#         }
#
#         with transaction.atomic():
#             # Validate and save user
#             user_serializer = UserRegistrationSerializer(data=user_data)
#             if user_serializer.is_valid():
#                 user_instance = user_serializer.save()
#             else:
#                 return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # Step 2: Create visa application details
#             visa_applications_data = {
#                 'passport_number': request.data.get('passport_number', ''),
#                 'purpose': request.data.get('purpose'),
#                 'visa_type': request.data.get('visa_type'),
#                 'destination_country': request.data.get('destination_country'),
#                 'user': user_instance.id,
#             }
#
#             visa_serializer = VisaApplicationsSerializer(data=visa_applications_data)
#             if visa_serializer.is_valid():
#                 visa_serializer.save()
#             else:
#                 return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # Send email or OTP for the created user
#             if email:
#                 send_user_email(email, user_data['password'])
#             elif mobile_number:
#                 if not send_user_otp(mobile_number):
#                     raise Exception("Failed to send OTP to mobile number.")
#
#         return Response(
#             {"message": "Visa user registered successfully."},
#             status=status.HTTP_201_CREATED,
#         )
#     except IntegrityError as e:
#         logger.error(f"Integrity error: {str(e)}")
#         return Response(
#             {"error": "User with this email or mobile already exists."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         return Response(
#             {"error": "An unexpected error occurred.", "details": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#
# @permission_classes([IsAuthenticated])
# @api_view(['POST'])
# def serviceproviders_user_creation(request):
#     """
#     Handles the creation of a visa user by ServiceProvider_Admin.
#     Creates a user first and associates visa application details with them.
#     """
#     if request.method != 'POST':
#         return Response({"error": "Invalid HTTP method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     service_provider_admin_roles = [
#         'ServiceProvider_Owner', 'ServiceProvider_Admin',
#         'Tara_SuperAdmin', 'Tara_Admin'
#     ]
#
#     if request.user.user_role not in service_provider_admin_roles:
#         return Response(
#             {'error_message': 'Unauthorized Access. Only ServiceProviderAdmin can create visa users.', 'status_cd': 1},
#             status=status.HTTP_401_UNAUTHORIZED
#         )
#
#     try:
#         # Step 1: Create the user
#         email = request.data.get('email', '').lower()
#         mobile_number = request.data.get('mobile_number', '')
#         user_name = request.data.get('user_name')
#         group = request.data.pop('group', None)
#         custom_permissions = request.data.pop('custom_permissions', [])
#         if not email and not mobile_number and not user_name:
#             return Response(
#                 {"error": "Either email or mobile number must be provided."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         user_data = {
#             'email': email,
#             'mobile_number': mobile_number,
#             'password': auto_generate_password(),
#             'created_by': request.data.get('created_by'),
#             'user_type': 'ServiceProvider',
#             'first_name': request.data.get('first_name'),
#             'last_name': request.data.get('last_name'),
#             'user_name': request.data.get('user_name')
#         }
#
#         with transaction.atomic():
#             # Validate and save user
#             user_serializer = UserRegistrationSerializer(data=user_data)
#             if user_serializer.is_valid():
#                 user_instance = user_serializer.save()
#                 user_data = user_serializer.data
#                 user_data['group'] = group
#                 user_data['custom_permissions'] = custom_permissions
#                 user_affiliated_role = assign_group_with_affiliated_permissions(user_data)
#             else:
#                 return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # Step 2: Create visa application details
#             visa_applications_data = {
#                 'passport_number': request.data.get('passport_number', ''),
#                 'purpose': request.data.get('purpose'),
#                 'visa_type': request.data.get('visa_type'),
#                 'destination_country': request.data.get('destination_country'),
#                 'user': user_instance.id,
#             }
#
#             visa_serializer = VisaApplicationsSerializer(data=visa_applications_data)
#             if visa_serializer.is_valid():
#                 visa_serializer.save()
#             else:
#                 return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # Send email or OTP for the created user
#             if email:
#                 send_user_email(email, user_data['password'])
#             elif mobile_number:
#                 if not send_user_otp(mobile_number):
#                     raise Exception("Failed to send OTP to mobile number.")
#
#         return Response(
#             {"message": "Visa user registered successfully."},
#             status=status.HTTP_201_CREATED,
#         )
#     except IntegrityError as e:
#         logger.error(f"Integrity error: {str(e)}")
#         return Response(
#             {"error": "User with this email or mobile already exists."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         return Response(
#             {"error": "An unexpected error occurred.", "details": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#
# class DynamicUserStatsAPIView(APIView):
#     """
#     API View to fetch dynamic user statistics grouped by user_type.
#     Ignores users with user_type='SuperAdmin'.
#     """
#     permission_classes = [AllowAny]
#
#     def get(self, request, *args, **kwargs):
#         # Exclude 'SuperAdmin'
#         users = User.objects.exclude(user_type="SuperAdmin")
#
#         # Get the stats for user types, including those with None values
#         user_stats = users.values("user_type").annotate(count=Count("id"))
#
#         # Initialize stats dictionary with "Individual" for None user_type
#         stats = {"Individual": 0}
#
#         # Loop through each user type count and add to stats
#         for stat in user_stats:
#             user_type = stat["user_type"]
#             if user_type is None:
#                 stats["Individual"] += stat["count"]
#             else:
#                 stats[user_type] = stat["count"]
#
#         return Response(stats, status=status.HTTP_200_OK)
#
#
# class UsersByDynamicTypeAPIView(APIView):
#     """
#     API View to retrieve users based on user_type dynamically.
#     Ignores users with user_type='SuperAdmin'.
#     """
#     permission_classes = [AllowAny]  # Adjust permissions as needed
#
#     def get(self, request, *args, **kwargs):
#         # Get user_type from query parameters
#         user_type = request.query_params.get("user_type")
#
#         if not user_type:
#             return Response({"error": "user_type parameter is required."}, status=400)
#
#         # Filter users dynamically based on user_type
#         if user_type == "Individual":
#             users = User.objects.filter(user_type__isnull=True)
#         else:
#             users = User.objects.filter(user_type=user_type)
#
#         # Exclude 'SuperAdmin' in all cases
#         users = users.exclude(user_type="SuperAdmin")
#
#         # Serialize and return data
#         user_data = UserSerializer(users, many=True).data
#
#         return Response({
#             "users": user_data
#         },  status=status.HTTP_200_OK)
#
# class UserListByTypeAPIView(APIView):
#     """
#     API View to list all users grouped by user_type.
#     Users with user_type = None are categorized under 'Individual'.
#     """
#     permission_classes = [AllowAny]  # Adjust permissions as needed
#
#     def get(self, request, *args, **kwargs):
#         user_groups = {
#             "CA": [],
#             "Business": [],
#             "ServiceProvider": [],
#             "Individual": []
#         }
#
#         # Fetch all users
#         users = User.objects.exclude(user_type="SuperAdmin")
#
#         # Serialize users and group them by user_type
#         for user in users:
#             user_type = user.user_type or "Individual"
#             user_groups[user_type].append(UserSerializer(user).data)
#
#         return Response(user_groups)
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def get_user_details(request):
#     user_id = request.query_params.get("user_id")
#
#     if not user_id:
#         return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         return Response({"error": "No user found with the provided details."}, status=status.HTTP_404_NOT_FOUND)
#
#     # Generate JWT tokens
#     refresh = RefreshToken.for_user(user)
#
#     # Extract user details
#     user_kyc = hasattr(user, "userkyc")
#     user_name = user.userkyc.name if user_kyc else None
#     created_on_date = user.date_joined.date()
#
#     try:
#         user_affiliation_summary = UserAffiliationSummary.objects.get(user=user)
#     except UserAffiliationSummary.DoesNotExist:
#         return Response({"error": "User affiliation data not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     data = {
#         "id": user.id,
#         "email": user.email,
#         "mobile_number": user.mobile_number,
#         "user_name": user.user_name,
#         "name": f"{user.first_name} {user.last_name}",
#         "created_on": created_on_date,
#         "user_type": user.user_type,
#         "user_kyc": user_kyc,
#         "individual_affiliated": list(user_affiliation_summary.individual_affiliated),
#         "ca_firm_affiliated": list(user_affiliation_summary.ca_firm_affiliated),
#         "service_provider_affiliated": list(user_affiliation_summary.service_provider_affiliated),
#         "business_affiliated": list(user_affiliation_summary.business_affiliated),
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#     }
#     if user.user_type == "Business":
#         business_exists = Business.objects.filter(client=user).exists()
#         data['business_exists'] = business_exists
#
#     return Response(data, status=status.HTTP_200_OK)
#
# def send_user_email(email, password):
#     """Sends autogenerated credentials to user's email."""
#     ses_client = boto3.client(
#         'ses',
#         region_name=AWS_REGION,
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     )
#     subject = "Welcome to TaraFirst! Your Account Has Been Created"
#     body_html = f"""
#         <html>
#         <body>
#             <h1>Welcome to TaraFirst!</h1>
#             <p>Your account has been created.</p>
#             <p><strong>Username:</strong> {email}</p>
#             <p><strong>Password:</strong> {password}</p>
#             <footer style="margin-top: 30px;">TaraFirst Team</footer>
#         </body>
#         </html>
#     """
#     ses_client.send_email(
#         Source=EMAIL_HOST_USER,
#         Destination={'ToAddresses': [email]},
#         Message={
#             'Subject': {'Data': subject},
#             'Body': {'Html': {'Data': body_html}},
#         },
#     )
#
#
# def send_user_otp(mobile_number):
#     """Generates and sends OTP to user's mobile number."""
#     otp = generate_otp()
#     response = send_otp_helper(mobile_number, otp)
#     if response['return']:
#         query = User.objects.filter(mobile_number=mobile_number)
#         if query.exists():
#             user = query.first()
#             user.otp = otp
#             user.save()
#         return True
#     return False
#
#
# # Activate User
#
# class ActivateUserView(APIView):
#     """
#     View for activating user accounts using UID and token.
#     """
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('uid', openapi.IN_QUERY, description="User ID (Base64 encoded)", type=openapi.TYPE_STRING),
#             openapi.Parameter('token', openapi.IN_QUERY, description="Activation token", type=openapi.TYPE_STRING)
#         ],
#         responses={
#             200: openapi.Response("Account activated successfully"),
#             400: openapi.Response("Invalid or expired activation link"),
#         },
#         operation_description="Activate user account using UID and token."
#     )
#     def get(self, request, *args, **kwargs):
#         """
#         Handle user account activation using query parameters (uid and token).
#         """
#         logger.info("Starting user account activation process.")
#
#         # Get 'uid' and 'token' from query parameters
#         uid = request.query_params.get('uid')
#         token = request.query_params.get('token')
#
#         if not uid or not token:
#             raise Http404("UID or token is missing from the request.")
#
#         try:
#             uid = urlsafe_base64_decode(uid).decode()
#             user = User.objects.get(pk=uid)
#             logger.info(f"User with UID {uid} found.")
#         except (ValueError, TypeError, User.DoesNotExist) as e:
#             logger.error(f"Error during activation process: {e}")
#             return Response({"message": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)
#
#         if default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             logger.info(f"User account with UID {uid} successfully activated.")
#             return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
#
#         logger.warning(f"Activation token for user with UID {uid} is invalid or expired.")
#         return Response({"message": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'old_password': openapi.Schema(type=openapi.TYPE_STRING, description="Current password"),
#                 'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
#             },
#             required=['old_password', 'new_password']
#         ),
#         responses={
#             200: openapi.Response("Password changed successfully"),
#             400: openapi.Response("Invalid input or validation failed"),
#             401: openapi.Response("Authentication required")
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING
#             ),
#         ],
#         operation_description="Change the password for the authenticated user."
#     )
#     def put(self, request, *args, **kwargs):
#         """
#         Allow the authenticated user to change their password.
#         """
#         user = request.user
#         old_password = request.data.get("old_password")
#         new_password = request.data.get("new_password")
#
#         if not old_password or not new_password:
#             raise ValidationError({"detail": "Both 'old_password' and 'new_password' are required."})
#
#         # Check if the old password is correct
#         if not user.check_password(old_password):
#             raise ValidationError({"old_password": "Old password is incorrect."})
#
#         # Validate the new password
#         try:
#             validate_password(new_password, user=user)
#         except ValidationError as e:
#             # Catch the ValidationError and return a 400 Bad Request with the error message
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Set the new password
#         user.set_password(new_password)
#         user.save()
#
#         return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
#
#
# # Test Protected API
#
# class TestProtectedAPIView(APIView):
#
#     @swagger_auto_schema(
#         operation_description="Test protected endpoint",
#         responses={
#             200: openapi.Response("Success", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
#                 "message": openapi.Schema(type=openapi.TYPE_STRING)
#             })),
#             403: openapi.Response("Forbidden")
#         }
#     )
#     def get(self, request):
#         """
#         Protected endpoint for authenticated users.
#         """
#         return Response({
#             'message': 'You have access to this protected view!',
#             'user_id': request.user.id,
#             'email': request.user.email
#         })
#
#
# # Forgot Password
# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
#             }
#         ),
#         responses={
#             200: openapi.Response("Reset link sent if the email exists"),
#             400: openapi.Response("Bad Request")
#         },
#         operation_description="Send a password reset link to the user's email."
#     )
#     def post(self, request, *args, **kwargs):
#         """
#         Handle forgot password functionality with Amazon SES.
#         """
#         email = request.data.get("email")
#         if not email:
#             logger.warning("Email not provided in the request.")
#             print("**********************")
#             raise ValidationError("Email is required.")
#
#         try:
#             user = User.objects.get(email=email.lower())
#             logger.info(f"User found for email: {email}")
#         except User.DoesNotExist:
#             logger.info(f"Attempt to reset password for non-existent email: {email}")
#             # Send a generic response even if the email does not exist
#             return Response({"message": "If an account exists with this email, you will receive a reset link."},
#                             status=status.HTTP_200_OK)
#
#         # Generate reset token and link
#         token = default_token_generator.make_token(user)
#         uid = urlsafe_base64_encode(str(user.pk).encode())
#         reset_link = f"{Reference_link}/reset-password/{uid}/{token}/"
#
#         # Send the email via Amazon SES
#         try:
#             ses_client = boto3.client(
#                 'ses',
#                 region_name=settings.AWS_REGION,
#                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
#             )
#
#             subject = "Reset Your Password"
#             body = f"""
#             Hello Sir/Madam,
#
#             You requested to reset your password. Click the link below to reset it:
#             {reset_link}
#
#             If you did not request this, please ignore this email.
#
#             Thanks,
#             TaraFirst
#             """
#
#             response = ses_client.send_email(
#                 Source=settings.EMAIL_HOST_USER,
#                 Destination={'ToAddresses': [email]},
#                 Message={
#                     'Subject': {'Data': subject},
#                     'Body': {'Text': {'Data': body}}
#                 }
#             )
#             logger.info(f"Password reset email sent to {email} successfully.")
#             return Response({"message": "If an account exists with this email, you will receive a reset link."},
#                             status=status.HTTP_200_OK)
#
#         except (BotoCoreError, ClientError) as e:
#             # Log SES-related errors
#             logger.error(f"SES Error: {str(e)}")
#             return Response({"message": "Unable to send reset email. Please try again later."},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# # Reset Password
# class ResetPasswordView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
#             }
#         ),
#         manual_parameters=[
#             openapi.Parameter('uid', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING),
#             openapi.Parameter('token', openapi.IN_PATH, description="Reset Token", type=openapi.TYPE_STRING)
#         ],
#         responses={
#             200: openapi.Response("Password has been successfully reset"),
#             400: openapi.Response("Invalid reset link or expired token"),
#         },
#         operation_description="Reset user's password using token and UID."
#     )
#     def post(self, request, uid, token, *args, **kwargs):
#         """
#         Reset user password.
#         """
#         password = request.data.get("password")
#         if not password:
#             logger.warning("Password not provided in the request.")
#             raise ValidationError("Password is required.")
#
#         try:
#             uid = urlsafe_base64_decode(uid).decode()
#             user = User.objects.get(pk=uid)
#             logger.info(f"User found for UID: {uid}")
#         except (User.DoesNotExist, ValueError, TypeError) as e:
#             logger.error(f"Error decoding UID or finding user: {str(e)}")
#             return Response({"message": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)
#
#         if default_token_generator.check_token(user, token):
#             user.set_password(password)
#             user.save()
#             logger.info(f"Password successfully reset for user: {user.email}")
#             return Response({"message": "Password has been successfully reset."}, status=status.HTTP_200_OK)
#
#         logger.warning(f"Invalid or expired token for user: {user.email}")
#         return Response({"message": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# # Refresh Token
# class RefreshTokenView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'refresh': openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description='Refresh token obtained during login'
#                 ),
#             },
#             required=['refresh'],  # Indicate that 'refresh' is required
#         ),
#         responses={
#             200: openapi.Response(
#                 description="New access token generated",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'access': openapi.Schema(
#                             type=openapi.TYPE_STRING,
#                             description='Newly generated access token'
#                         ),
#                     }
#                 )
#             ),
#             400: openapi.Response("Invalid or missing refresh token"),
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING
#             ),
#         ],
#         operation_description="Generate a new access token using a valid refresh token."
#     )
#     def post(self, request, *args, **kwargs):
#         """
#         Refresh the access token using the provided refresh token.
#         """
#         refresh_token = request.data.get("refresh")
#
#         # Ensure the refresh token is provided
#         if not refresh_token:
#             logger.warning("Refresh token is missing from the request.")
#             return Response(
#                 {"detail": "Refresh token is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             # Validate and create a new access token
#             token = RefreshToken(refresh_token)
#             new_access_token = str(token.access_token)
#             logger.info(f"New access token generated for refresh token: {refresh_token}")
#             return Response(
#                 {"access": new_access_token},
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             # Handle invalid or expired refresh tokens
#             logger.error(f"Error generating new access token: {str(e)}. Refresh token: {refresh_token}")
#             return Response(
#                 {"detail": "Invalid refresh token.", "error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class UsersKYCListView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="List all user details.",
#         tags=["UsersKYC"],
#         responses={200: UsersKYCSerializer(many=True)},  # Specify many=True for list
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING
#             ),
#         ]
#     )
#     def get(self, request):
#         user_details = UserKYC.objects.all()
#         serializer = UsersKYCSerializer(user_details, many=True)
#         return Response(serializer.data)
#
#     @swagger_auto_schema(
#         operation_description="Register user details (PAN, Aadhaar, ICAI number, etc.) based on user type.",
#         tags=["UsersKYC"],
#         request_body=UsersKYCSerializer,
#         responses={
#             201: "User details saved successfully.",
#             400: "Invalid data",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING
#             ),
#         ]
#     )
#     def post(self, request):
#         try:
#             if hasattr(request.user, 'userdetails'):
#                 return Response({"detail": "User details already exist."}, status=status.HTTP_400_BAD_REQUEST)
#
#             request_data = request.data
#             # authorizing access token from the sandbox
#             # access_token = authenticate()
#             # url = f"{SANDBOX_API_URL}/kyc/pan/verify"
#             # headers = {
#             #     'Authorization': access_token,
#             #     'x-api-key': SANDBOX_API_KEY,
#             #     'x-api-version': SANDBOX_API_VERSION
#             # }
#             # date_field = datetime.strptime(request_data['date'], "%Y-%m-%d")
#             # dob = date_field.strftime("%d/%m/%Y")
#             # payload = {
#             #     "@entity": "in.co.sandbox.kyc.pan_verification.request",
#             #     "reason": "For onboarding customers",
#             #     "pan": request_data['pan_number'],
#             #     "name_as_per_pan": request_data['name'],
#             #     "date_of_birth": dob,
#             #     "consent": "Y"
#             # }
#             # pan_verification_request = requests.post(url, json=payload, headers=headers)
#             # pan_verification_data = pan_verification_request.json()
#             # category = None
#             # if pan_verification_data['code'] == 200 and pan_verification_data['data']['status'] == 'valid':
#             serializer = UsersKYCSerializer(data=request_data,
#                                             context={'request': request})  # Pass request in the context
#             if serializer.is_valid():
#                 serializer.save(user=request.user)  # Ensure the user is passed when saving
#                 return Response({"data":serializer.data, "detail": "User details saved successfully."},
#                                 status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # elif pan_verification_data['code'] != 200:
#             #     return Response({'error_message': 'Invalid pan details, Please cross check the DOB, Pan number or Name'},
#             #                     status=status.HTTP_400_BAD_REQUEST)
#             # else:
#             #     return Response({'error_message': pan_verification_data['data']['remarks']},
#             #                     status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             logger.error(e, exc_info=1)
#             return Response({'error_message': str(e), 'status_cd': 1},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class UsersKYCDetailView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Retrieve user details by ID.",
#         tags=["UsersKYC"],
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ],
#         responses={
#             200: UsersKYCSerializer,
#             404: openapi.Response(description="User details not found.")
#         }
#     )
#     def get(self, request, pk=None):
#         """
#         Retrieve user details by ID.
#         """
#         try:
#             user_details = UserKYC.objects.get(pk=pk, user=request.user)
#             serializer = UsersKYCSerializer(user_details)
#             return Response(serializer.data)
#         except UserKYC.DoesNotExist:
#             raise NotFound("User details not found.")
#
#     @swagger_auto_schema(
#         operation_description="Update user details by ID.",
#         tags=["UsersKYC"],
#         request_body=UsersKYCSerializer,
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ],
#         responses={
#             200: openapi.Response(description="User details updated successfully."),
#             400: openapi.Response(description="Invalid data."),
#             404: openapi.Response(description="User details not found.")
#         }
#     )
#     def put(self, request, pk=None):
#         """
#         Update user details by ID.
#         """
#         try:
#             user_details = UserKYC.objects.get(pk=pk, user=request.user)
#             serializer = UsersKYCSerializer(user_details, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({"detail": "User details updated successfully."}, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except UserKYC.DoesNotExist:
#             raise NotFound("User details not found.")
#
#     @swagger_auto_schema(
#         operation_description="Delete user details by ID.",
#         tags=["UsersKYC"],
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ],
#         responses={
#             204: openapi.Response(description="User details deleted successfully."),
#             404: openapi.Response(description="User details not found.")
#         }
#     )
#     def delete(self, request, pk=None):
#         """
#         Delete user details by ID.
#         """
#         try:
#             user_details = UserKYC.objects.get(pk=pk, user=request.user)
#             user_details.delete()
#             return Response({"detail": "User details deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#         except UserKYC.DoesNotExist:
#             raise NotFound("User details not found.")
#
#
# class FirmKYCView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Retrieve the FirmKYC details of the authenticated user.",
#         tags=["FirmKYC"],
#         responses={
#             200: FirmKYCSerializer,
#             404: "FirmKYC details not found."
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ]
#     )
#     def get(self, request):
#         """
#         Retrieve FirmKYC details for the authenticated user.
#         """
#         try:
#             firm_kyc = request.user.firmkyc
#             serializer = FirmKYCSerializer(firm_kyc)
#             return Response({"data": serializer.data, "detail": "FIRM KYC saved successfully."},
#                             status=status.HTTP_200_OK)
#         except FirmKYC.DoesNotExist:
#             return Response({"detail": "FirmKYC details not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     @swagger_auto_schema(
#         operation_description="Create FirmKYC details for the authenticated user.",
#         tags=["FirmKYC"],
#         request_body=FirmKYCSerializer,
#         responses={
#             201: "FirmKYC details created successfully.",
#             400: "Invalid data."
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ]
#     )
#     def post(self, request):
#         """
#         Create FirmKYC details for the authenticated user.
#         """
#         serializer = FirmKYCSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @swagger_auto_schema(
#         operation_description="Update FirmKYC details for the authenticated user.",
#         tags=["FirmKYC"],
#         request_body=FirmKYCSerializer,
#         responses={
#             200: "FirmKYC details updated successfully.",
#             400: "Invalid data.",
#             404: "FirmKYC details not found."
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ]
#     )
#     def put(self, request):
#         """
#         Update FirmKYC details for the authenticated user.
#         """
#         try:
#             firm_kyc = request.user.firmkyc
#             serializer = FirmKYCSerializer(firm_kyc, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except FirmKYC.DoesNotExist:
#             return Response({"detail": "FirmKYC details not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     @swagger_auto_schema(
#         operation_description="Delete FirmKYC details for the authenticated user.",
#         tags=["FirmKYC"],
#         responses={
#             204: "FirmKYC details deleted successfully.",
#             404: "FirmKYC details not found."
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ]
#     )
#     def delete(self, request):
#         """
#         Delete FirmKYC details for the authenticated user.
#         """
#         try:
#             firm_kyc = request.user.firmkyc
#             firm_kyc.delete()
#             return Response({"detail": "FirmKYC details deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#         except FirmKYC.DoesNotExist:
#             return Response({"detail": "FirmKYC details not found."}, status=status.HTTP_404_NOT_FOUND)
#
# @swagger_auto_schema(
#     method='patch',
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'id': openapi.Schema(
#                 type=openapi.TYPE_INTEGER,
#                 description='ID of the user to update. If not provided, the currently authenticated user will be updated.',
#                 example=1
#             ),
#             'user_name': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='Email or Mobile Number of the user (optional).',
#                 example='example@example.com'
#             ),
#             'email': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='Email address of the user (optional).',
#                 example='example@example.com'
#             ),
#             'mobile_number': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='Mobile number of the user (optional).',
#                 example='+1234567890'
#             ),
#             'user_type': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='User type to be updated. Choices are: "Individual", "CA", "Business", "ServiceProvider". (optional)',
#                 example='Individual'
#             ),
#             'first_name': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='First name of the user (optional).',
#                 example='John'
#             ),
#             'last_name': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description='Last name of the user (optional).',
#                 example='Doe'
#             ),
#             'is_active': openapi.Schema(
#                 type=openapi.TYPE_BOOLEAN,
#                 description='Indicates if the user is active (optional).',
#                 example=True
#             ),
#         },
#         required=[],  # No required fields because any field from the serializer can be passed.
#     ),
#     responses={
#         200: openapi.Response(
#             description="User updated successfully",
#             schema=openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'message': openapi.Schema(
#                         type=openapi.TYPE_STRING,
#                         description='Success message'
#                     ),
#                     'data': openapi.Schema(
#                         type=openapi.TYPE_OBJECT,
#                         description="Updated user data",
#                     ),
#                 }
#             ),
#         ),
#         400: openapi.Response("Invalid data provided."),
#         404: openapi.Response("User not found."),
#         500: openapi.Response("Unexpected error occurred."),
#     },
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#             required=True  # Make Authorization header required
#         ),
#     ],
#     operation_description="Updates the user fields like email, mobile number, or user type of the currently authenticated user. Only the fields provided will be updated. If `id` is passed, updates the user with that ID."
# )
# @permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this endpoint
# @api_view(['PATCH'])
# def partial_update_user(request):
#     """
#     Handle partial update of user profile. If `id` is passed, update that user;
#     otherwise, update the currently authenticated user.
#     """
#     try:
#         user_id = request.data.get('id', None)  # Get the 'id' from request data
#
#         if user_id:
#             # If `id` is passed, fetch the user with the provided `id`
#             try:
#                 user = User.objects.get(id=user_id)
#             except User.DoesNotExist:
#                 return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             # If no `id` is passed, update the currently authenticated user
#             user = request.user  # Get the currently authenticated user
#
#         # Create a serializer instance with partial update flag
#         serializer = UserUpdateSerializer(user, data=request.data, partial=True)
#
#         if serializer.is_valid():
#             serializer.save()  # Save the updated user data
#             return Response({
#                 "message": "User updated successfully.",
#                 "data": serializer.data  # Include the updated user data in the response
#             }, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         logger.error(f"Error updating user info: {str(e)}")
#         return Response({"error": "An unexpected error occurred while updating user info."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def corporate_details(request):
#     """
#     API to retrieve business users created by the authenticated user.
#     Ignores users with user_type='SuperAdmin'.
#     """
#     try:
#         user_id = request.query_params.get('user_id')
#
#         if not user_id:
#             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Log the user_id to debug
#         print(f"Received user_id: {user_id}")
#
#         try:
#             # Check if the user exists
#             created_by_user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Fetch business users created by the user
#         users = User.objects.filter(created_by=user_id, user_type="Business")
#
#         if not users.exists():
#             return Response({"message": "No business users found."}, status=status.HTTP_404_NOT_FOUND)
#
#         return Response({"users": UserSerializer(users, many=True).data}, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def affiliated_summary_details(request):
# #     """
# #     API to retrieve business users created by the authenticated user.
# #     Ignores users with user_type='SuperAdmin'.
# #     """
# #     try:
# #         user_id = request.query_params.get('user_id')
# #         user_type = request.query_params.get('type')
# #
# #         if not user_id:
# #             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
# #
# #         if not user_type:
# #             return Response({"error": "User type is required."}, status=status.HTTP_400_BAD_REQUEST)
# #
# #         print(f"Received user_id: {user_id}, user_type: {user_type}")
# #
# #         try:
# #             user_affiliated_details = UserAffiliationSummary.objects.get(user_id=user_id)
# #         except ObjectDoesNotExist:
# #             return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)
# #
# #         # Mapping user_type to the appropriate field in UserAffiliatedRole
# #         affiliated_mapping = {
# #             "Business": user_affiliated_details.business_affiliated,
# #             "Individual": user_affiliated_details.individual_affiliated,
# #             "CA": user_affiliated_details.ca_firm_affiliated,
# #             "ServiceProvider": user_affiliated_details.service_provider_affiliated
# #         }
# #
# #         if user_type not in affiliated_mapping:
# #             return Response({"error": "Invalid user type provided."}, status=status.HTTP_400_BAD_REQUEST)
# #
# #         affiliated_users = affiliated_mapping[user_type] or []
# #
# #         # Fetch all user objects in one query
# #         user_ids = [user['id'] for user in affiliated_users if 'id' in user]
# #         users = User.objects.filter(id__in=user_ids, user_type=user_type)
# #
# #         serialized_data = UserSerializer(users, many=True).data
# #
# #         return Response({"users": serialized_data}, status=status.HTTP_200_OK)
# #
# #     except Exception as e:
# #         return Response({"error": f"An unexpected error occurred: {str(e)}"},
# #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def affiliated_summary_details(request):
#     """
#     API to retrieve business users created by the authenticated user.
#     Ignores users with user_type='SuperAdmin'.
#     """
#     try:
#         user_id = request.query_params.get('user_id')
#         user_type = request.query_params.get('type')
#
#         if not user_id:
#             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         if not user_type:
#             return Response({"error": "User type is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         print(f"Received user_id: {user_id}, user_type: {user_type}")
#
#         # Get affiliated details
#         user_affiliated_details = UserAffiliatedRole.objects.filter(user_id=user_id)
#
#         if user_affiliated_details.exists():
#             # Extract affiliated IDs
#             affiliated_data = [affiliated.affiliated.id for affiliated in user_affiliated_details]
#
#             if user_type == "Business":
#                 users = User.objects.filter(id__in=affiliated_data, user_type=user_type)
#                 serialized_data = UserBusinessSerializer(users, many=True).data
#                 return Response({"users": serialized_data}, status=status.HTTP_200_OK)
#             else:
#                 users = User.objects.filter(id__in=affiliated_data, user_type=user_type)
#                 serialized_data = UserSerializer(users, many=True).data
#                 return Response({"users": serialized_data}, status=status.HTTP_200_OK)
#
#         return Response({"error": "No affiliated data found."}, status=status.HTTP_404_NOT_FOUND)
#
#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def user_search(request):
#     """
#     API to search for users by email.
#     Returns a single object if only one user is found, otherwise returns a list.
#     """
#     try:
#         email = request.query_params.get('email')
#
#         if not email:
#             return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         users = User.objects.filter(email=email)
#
#         if not users.exists():
#             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# # class PermissionListView(APIView):
# #     permission_classes = [AllowAny]
# #     def get(self, request):
# #         """
# #         List all available permissions.
# #         """
# #         permissions = Permission.objects.all()
# #         serializer = PermissionSerializer(permissions, many=True)
# #         return Response(serializer.data)
# #
# #
# # class GroupListCreateView(APIView):
# #     """
# #     Create a new group or list all groups.
# #     """
# #
# #     def get(self, request):
# #         groups = Group.objects.all()
# #         serializer = GroupSerializer(groups, many=True)
# #         return Response(serializer.data)
# #
# #     def post(self, request):
# #         """
# #         Create a new group.
# #         """
# #         serializer = GroupSerializer(data=request.data)
# #         if serializer.is_valid():
# #             group = serializer.save()
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def business_list_by_client(request):
#     """
#     API to retrieve a business by client ID.
#     """
#     try:
#         client_id = request.query_params.get('user_id')
#
#         if not client_id:
#             return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             business = Business.objects.get(client=client_id)  # Using get() instead of filter()
#         except Business.DoesNotExist:
#             return Response({'error': 'No business found for this client.'}, status=status.HTTP_404_NOT_FOUND)
#
#         # Serialize and return the business data
#         serializer = BusinessUserSerializer(business)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({'error': f'An unexpected error occurred: {str(e)}'},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def manage_corporate_entity(request):
#     """
#     API to retrieve business users created by the authenticated user.
#     Ignores users with user_type='SuperAdmin'.
#     """
#     try:
#         user_id = request.query_params.get('user_id')
#
#         if not user_id:
#             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Log the user_id to debug
#         print(f"Received user_id: {user_id}")
#
#         try:
#             # Check if the user exists
#             created_by_user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         # Fetch business users created by the user
#         users = User.objects.filter(created_by=user_id, user_type="Business")
#
#         if not users.exists():
#             return Response({"message": "No business users found."}, status=status.HTTP_404_NOT_FOUND)
#
#         return Response({"users": UserSerializer(users, many=True).data}, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# def validate_user(user_id):
#     try:
#         return User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         raise ValueError(f"User with ID {user_id} not found.")
#
#
# def get_or_create_affiliated_role(user, affiliated, group, permissions):
#     user_group, created = UserAffiliatedRole.objects.get_or_create(user=user, affiliated=affiliated)
#     user_group.group = group
#     user_group.custom_permissions.set(permissions)
#     user_group.save()
#     return user_group
#
#
# def business_corporation_affiliation(user_group_permission_data):
#     created_objects = []
#     user_id = user_group_permission_data.get('id')
#     group_id = user_group_permission_data.get('group')
#     custom_permissions_ids = user_group_permission_data.get('custom_permissions', [])
#     created_by = user_group_permission_data.get('created_by')
#
#     user = validate_user(user_id)
#     created_by_user = validate_user(created_by)
#
#     if user.created_by.user_type == "Individual" and user.user_type == "Business":
#         group = CustomGroup.objects.get(id=11)
#         affiliation = get_or_create_affiliated_role(created_by_user, user, group, group.permissions.all())
#         created_objects.append(affiliation)
#
#     if group_id:
#         group = CustomGroup.objects.get(id=group_id)
#     else:
#         user_type = user_group_permission_data.get('user_type')
#         group_id_mapping = {
#             "Individual": 10,
#             "Business": 11,
#             "ServiceProvider": 1,
#             "CA": 24
#         }
#         group = CustomGroup.objects.get(id=group_id_mapping[user_type])
#
#     custom_permissions = CustomPermission.objects.filter(
#         id__in=custom_permissions_ids) if custom_permissions_ids else group.permissions.all()
#     affiliation = get_or_create_affiliated_role(user, user, group, custom_permissions)
#     created_objects.append(affiliation)
#
#     return created_objects
#
#
# def check_business_existence(business_data):
#     """
#     Check if the business or PAN already exists in the database.
#     """
#     if business_data.get('entityType') != 'individual':
#         if Business.objects.filter(nameOfBusiness__iexact=business_data['nameOfBusiness']).exists():
#             return "Business already exists"
#         if Business.objects.filter(pan=business_data['pan']).exists():
#             return "Business with PAN already exists"
#     return None
#
#
# def send_account_email(user, email, password):
#     """
#     Send account details to the user's email.
#     """
#     subject = "Your Account Details"
#     body_html = f"""
#         <html>
#         <body>
#             <h1>Welcome to Our Platform</h1>
#             <p>Your account has been created by the superadmin.</p>
#             <p><strong>Username:</strong> {user.user_name}</p>
#             <p><strong>Password:</strong> {password}</p>
#         </body>
#         </html>
#     """
#
#     # ses_client = boto3.client(
#     #     'ses',
#     #     region_name=AWS_REGION,
#     #     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#     # )
#     ses_client = boto3.client(
#         'ses',
#         region_name=AWS_REGION,
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#     )
#
#     try:
#         # ses_client.send_email(
#         #     Source=EMAIL_HOST_USER,
#         #     Destination={'ToAddresses': [email]},
#         #     Message={
#         #         'Subject': {'Data': subject},
#         #         'Body': {
#         #             'Html': {'Data': body_html},
#         #             'Text': {'Data': f"Your username is: {user.user_name}\nYour password is: {password}"}
#         #         },
#         #     }
#         # )
#         response = ses_client.send_email(
#             Source="admin@tarafirst.com",
#             Destination={'ToAddresses': [email]},
#             Message={
#                 'Subject': {'Data': subject},
#                 'Body': {
#                     'Html': {'Data': body_html},
#                     'Text': {'Data': f"Your username is: {user.email}\nYour password is: {password}"}
#                 },
#             }
#         )
#         logger.info(f"Account details email sent to: {email}")
#         return Response(
#             {"message": "User created successfully. Check your email for the username and password."},
#             status=status.HTTP_201_CREATED,
#         )
#
#
#     except ClientError as e:
#         logger.error(f"Failed to send email via SES: {e.response['Error']['Message']}")
#         return Response(
#             {"error": "Failed to send account details email. Please try again later."},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#
#
# def business_set_up(business_data):
#     """
#     Handle business registration.
#     Returns the instance and serialized data.
#     """
#     serializer = BusinessSerializer(data=business_data)
#     if serializer.is_valid():
#         business_instance = serializer.save()
#         return business_instance, serializer.data  # Returning both
#     raise ValueError(f"Invalid business data provided: {serializer.errors}")
#
#
#
# def object_remove(created_objects):
#     # Reverse the list to delete the last created object first
#     for obj in reversed(created_objects):
#         try:
#             obj.delete()
#             logger.info(f"Successfully deleted: {obj}")
#         except Exception as e:
#             logger.error(f"Failed to delete {obj}: {str(e)}")
#     return
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def businessEntityRegistration(request):
#     """
#     Handle user registration by superadmin without activation link,
#     and send username and password to the user via email.
#     """
#     logger.info("Received a superadmin user registration request.")
#
#     if request.method == 'POST':
#         created_objects = []
#         resultant_data = []
#         try:
#             request_data = request.data.copy()
#             user_creation = request_data.get('user_creation', {})
#             group = request_data.pop('group', None)
#             custom_permissions = request_data.pop('custom_permissions', [])
#             email = user_creation.get('email', '').lower()
#             mobile_number = user_creation.get('mobile_number', '')
#
#             # Ensure at least one of email or mobile_number is provided
#             if not email and not mobile_number:
#                 logger.warning("Registration failed: Missing both email and mobile number.")
#                 return Response(
#                     {"error": "Either email or mobile number must be provided."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             # Check business existence
#             business_data = request_data.get('business', {})
#             business_data['nameOfBusiness'] = business_data.get('nameOfBusiness', '').title()
#             error_message = check_business_existence(business_data)
#             if error_message:
#                 return Response({'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Serialize and validate user data
#             password = user_creation['password']
#             serializer = UserRegistrationSerializer(data=user_creation)
#
#             if serializer.is_valid():
#                 user = serializer.save()
#                 user_data = serializer.data
#                 created_objects.append(user)
#                 resultant_data.append(user_data)
#                 logger.info(f"User created successfully by superadmin: {user.pk}")
#                 user_data['group'] = group
#                 user_data['custom_permissions'] = custom_permissions
#
#                 # Assign roles and create business entity
#                 affiliation_result = business_corporation_affiliation(user_data)
#                 if affiliation_result:
#                     created_objects.extend(affiliation_result)  # Track created affiliations
#
#                 business_data['client'] = user_data['id']
#                 setup_result, serialized_data = business_set_up(business_data)
#                 if setup_result:
#                     created_objects.append(setup_result)  # Append instance
#                     resultant_data.append(serialized_data)  # Append serialized data
#
#                 # Send email with the username and password
#                 if email:
#                     send_account_email(user, email, password)
#
#                 return Response(
#                     {"data": resultant_data, "message": "User created successfully."
#                                                          " Check your email for the username and password."},
#                     status=status.HTTP_201_CREATED,
#                 )
#
#             # Return validation errors
#             logger.warning("Registration failed: Validation errors.")
#             logger.debug(f"Validation errors: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         except IntegrityError as e:
#             logger.error(f"Integrity error during registration: {str(e)}")
#             object_remove(created_objects)
#             return Response(
#                 {"error": "A user with this email or mobile number already exists."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except DatabaseError as e:
#             logger.error(f"Database error during registration: {str(e)}")
#             object_remove(created_objects)
#             return Response(
#                 {"error": "Database error occurred"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#         except ClientError as e:
#             logger.error(f"Failed to send email: {str(e)}")
#             object_remove(created_objects)
#
#             return Response(
#                 {"error": "Failed to send account details email. Please try again later."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#         except Exception as e:
#             logger.error(f"Unexpected error during registration: {str(e)}")
#             object_remove(created_objects)
#             return Response(
#                 {"error": "An unexpected error occurred.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def business_list(request):
#     if request.method == 'GET':
#         businesses = Business.objects.all()
#         serializer = BusinessSerializer(businesses, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#
#         request_data = request.data.copy()  # Create a mutable copy of request data
#
#         request_data['nameOfBusiness'] = request_data.get('nameOfBusiness', '').strip().title()
#
#         entity_type = request_data.get('entityType', '').strip().lower()
#
#         business_name = request_data.get('nameOfBusiness')
#
#         pan = request_data.get('pan', '').strip()
#
#         # Check if a non-individual business with the same name exists
#
#         if entity_type and entity_type != 'individual':
#
#             if Business.objects.filter(nameOfBusiness__iexact=business_name).exists():
#                 return Response({'error_message': 'Business already exists'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check if a business with the same PAN exists
#
#         if pan and Business.objects.filter(pan=pan).exists():
#             return Response({'error_message': 'Business with PAN already exists'}, status=status.HTTP_400_BAD_REQUEST)
#
#         serializer = BusinessSerializer(data=request_data)
#
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def business_detail(request, pk):
#     business = get_object_or_404(Business, pk=pk)
#
#     if request.method == 'GET':
#         serializer = BusinessUserSerializer(business)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = BusinessSerializer(business, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         business.delete()
#         return Response({'message': 'Business deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['GET', 'POST'])
# def gst_details_list_create(request):
#     """
#     List all GST details or create a new GST detail.
#     """
#     if request.method == 'GET':
#         gst_details = GSTDetails.objects.all()
#         serializer = GSTDetailsSerializer(gst_details, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'POST':
#
#         serializer = GSTDetailsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def gst_details_detail(request, pk):
#     """
#     Retrieve, update or delete a GST detail by ID.
#     """
#     try:
#         gst_detail = GSTDetails.objects.get(pk=pk)
#     except GSTDetails.DoesNotExist:
#         return Response({"error": "GST Detail not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = GSTDetailsSerializer(gst_detail)
#         return Response(serializer.data)
#
#     elif request.method in ['PUT', 'PATCH']:
#         serializer = GSTDetailsSerializer(gst_detail, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         gst_detail.delete()
#         return Response({"message": "GST Detail deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
#
#
# def documents_view(request):
#     # Get the URL from the query parameters
#     document_url = request.GET.get('url', None)
#
#     if not document_url:
#         return JsonResponse({'error': 'URL parameter is required'}, status=400)
#
#     try:
#         # Parse the URL to extract the file name (Key)
#         parsed_url = urlparse(document_url)
#         file_key = unquote(parsed_url.path.lstrip('/'))  # Remove leading '/' and decode URL
#
#         # Initialize S3 client
#         s3_client = boto3.client(
#             's3',
#             region_name=AWS_REGION,
#             aws_access_key_id=AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#         )
#
#         # Generate a pre-signed URL
#         file_url = s3_client.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': S3_BUCKET_NAME,
#                 'Key': file_key
#             },
#             ExpiresIn=3600  # URL expires in 1 hour
#         )
#
#         # Return the pre-signed URL
#         return JsonResponse({'url': file_url}, status=200)
#
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#
# @api_view(['GET'])
# def business_with_gst_details(request, business_id):
#     """
#     Retrieve a Business along with all its associated GST details using serializers.
#     """
#     try:
#         business = Business.objects.prefetch_related('gst_details').get(id=business_id)
#     except Business.DoesNotExist:
#         return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     serializer = BusinessWithGSTSerializer(business)
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
# class ServicesMasterDataListAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         operation_description="Retrieve a list of all services.",
#         tags=["ServicesMasterData"],
#         responses={
#             200: ServicesMasterDataSerializer(many=True),
#             404: "No services found."
#         }
#     )
#     def get(self, request):
#         services = ServicesMasterData.objects.all()
#         if not services.exists():
#             return Response({"error": "No services found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = ServicesMasterDataSerializer(services, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @swagger_auto_schema(
#         operation_description="Bulk create or add multiple services.",
#         tags=["ServicesMasterData"],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 "services": openapi.Schema(
#                     type=openapi.TYPE_ARRAY,
#                     items=openapi.Schema(type=openapi.TYPE_STRING),
#                     description="List of service names to add"
#                 )
#             }
#         ),
#         responses={
#             201: "Services created successfully.",
#             400: "Invalid data."
#         }
#     )
#     def post(self, request):
#         services = request.data.get("services", [])
#         if not services or not isinstance(services, list):
#             return Response({"error": "Please provide a list of service names."}, status=status.HTTP_400_BAD_REQUEST)
#
#         created_services = []
#         for service_name in services:
#             service, created = ServicesMasterData.objects.get_or_create(service_name=service_name)
#             if created:
#                 created_services.append(service_name)
#
#         return Response(
#             {
#                 "message": "Services created successfully.",
#                 "created_services": created_services
#             },
#             status=status.HTTP_201_CREATED
#         )
#
#
# class ServicesMasterDataDetailAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         operation_description="Retrieve details of a specific service by ID.",
#         tags=["ServicesMasterData"],
#         responses={
#             200: ServicesMasterDataSerializer,
#             404: "Service not found."
#         }
#     )
#     def get(self, request, pk):
#         try:
#             service = ServicesMasterData.objects.get(pk=pk)
#             serializer = ServicesMasterDataSerializer(service)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except ServicesMasterData.DoesNotExist:
#             return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     @swagger_auto_schema(
#         operation_description="Update an existing service by ID.",
#         tags=["ServicesMasterData"],
#         request_body=ServicesMasterDataSerializer,
#         responses={
#             200: "Service updated successfully.",
#             400: "Invalid data.",
#             404: "Service not found."
#         }
#     )
#     def put(self, request, pk):
#         try:
#             service = ServicesMasterData.objects.get(pk=pk)
#         except ServicesMasterData.DoesNotExist:
#             return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = ServicesMasterDataSerializer(service, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @swagger_auto_schema(
#         operation_description="Delete a service by ID.",
#         tags=["ServicesMasterData"],
#         responses={
#             204: "Service deleted successfully.",
#             404: "Service not found."
#         }
#     )
#     def delete(self, request, pk):
#         try:
#             service = ServicesMasterData.objects.get(pk=pk)
#             service.delete()
#             return Response({"message": "Service deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
#         except ServicesMasterData.DoesNotExist:
#             return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
#
#
# # class VisaApplicationsAPIView(APIView):
# #     permission_classes = [IsAuthenticated]
# #
# #     @swagger_auto_schema(
# #         operation_description="Retrieve a list of all visa applications.",
# #         responses={
# #             200: openapi.Response(description="List of visa applications retrieved successfully."),
# #             403: openapi.Response(description="Unauthorized access. Only ServiceProviderAdmins can view this data."),
# #         },
# #         manual_parameters=[
# #             openapi.Parameter(
# #                 'Authorization',
# #                 openapi.IN_HEADER,
# #                 description="Bearer <JWT Token>",
# #                 type=openapi.TYPE_STRING,
# #                 required=True,
# #             ),
# #         ],
# #     )
# #     def get(self, request):
# #         if request.user.user_type == "ServiceProviderAdmin":
# #             # Retrieve the ID of the user who created the current user
# #             created_by_id = request.user.id
# #             print(created_by_id)
# #
# #             # Filter visa applications for the user created by the current user
# #             visa_applications = VisaApplications.objects.filter(user_id=created_by_id)
# #             serializer = VisaApplicationsSerializer(visa_applications, many=True)
# #             return Response(serializer.data, status=status.HTTP_200_OK)
# #         else:
# #             # If the user is not a ServiceProviderAdmin, return an unauthorized response
# #             return Response(
# #                 {"error": "Unauthorized access. Only ServiceProviderAdmins can view this data."},
# #                 status=status.HTTP_403_FORBIDDEN
# #             )
#
#
# class VisaApplicationDetailAPIView(APIView):
#     permission_classes = [GroupPermission]
#     permission_required = "VS_Task_View"
#
#     @swagger_auto_schema(
#         operation_description="Retrieve details of a specific visa application by ID.",
#         tags=["VisaApplication"],
#         responses={
#             200: "Visa application details retrieved successfully.",
#             404: "Visa application not found."
#         },
#         manual_parameters=[
#                     openapi.Parameter(
#                         'Authorization',
#                         openapi.IN_HEADER,
#                         description="Bearer <JWT Token>",
#                         type=openapi.TYPE_STRING,
#                         required=True,
#                     ),
#                 ]
#     )
#     def get(self, request, pk):
#         try:
#             # visa_application = VisaApplications.objects.get(user_id=pk)
#             # serializer = VisaApplicationsGetSerializer(visa_application)
#             visa_applications = VisaApplications.objects.filter(user_id=pk)
#             serializer = VisaClientUserListSerializer(visa_applications, many=True)
#             response_data = []
#             user_data_map = {}
#
#             for visa_app in serializer.data:  # Use serializer.data to get the serialized data
#                 user = visa_app['email']
#
#                 if user not in user_data_map:
#                     # Add user data to the map if not already added
#                     user_data_map[user] = {
#                         "email": visa_app['email'],
#                         "mobile_number": visa_app['mobile_number'],
#                         "first_name": visa_app['first_name'],
#                         "last_name": visa_app['last_name'],
#                         "services": [],
#                         "user": visa_app['user'],
#                     }
#
#                 # Check if services list is empty
#                 services = visa_app['services']
#                 if len(services) > 0:
#                     for service in services:
#                         user_data_map[user]["services"].append({
#                             "id": service['id'],
#                             "service_type": service['service_type'],
#                             "service_name": service['service_name'],
#                             "date": service['date'],
#                             "status": service['status'],
#                             "comments": service['comments'],
#                             "quantity": service['quantity'],
#                             "visa_application": visa_app['id'],
#                             "last_updated_date": service['last_updated_date'],
#                             "passport_number": visa_app['passport_number'],
#                             "purpose": visa_app['purpose'],
#                             "visa_type": visa_app['visa_type'],
#                             "destination_country": visa_app['destination_country'],
#                             'user_id': visa_app['user']
#                         })
#                 else:
#                     # If no services, add specific fields directly to user data
#                     user_data_map[user].update({
#                         "passport_number": visa_app['passport_number'],
#                         "purpose": visa_app['purpose'],
#                         "visa_type": visa_app['visa_type'],
#                         "destination_country": visa_app['destination_country'],
#                         'user_id': visa_app['user']
#                     })
#
#             # Convert the user data map to a list
#             response_data = user_data_map[user]
#
#             return Response(response_data, status=status.HTTP_200_OK)
#
#         except User.DoesNotExist:
#             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except VisaApplications.DoesNotExist:
#             return Response({"error": "Visa application not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     permission_required = "VS_Task_Edit"
#
#     @swagger_auto_schema(
#         operation_description="Update an existing visa application by ID.",
#         tags=["VisaApplication"],
#         request_body=VisaApplicationsSerializer,
#         responses={
#             200: "Visa application updated successfully.",
#             400: "Invalid data.",
#             404: "Visa application not found."
#         }
#     )
#     def put(self, request, pk):
#         try:
#             visa_application = VisaApplications.objects.get(pk=pk)
#         except VisaApplications.DoesNotExist:
#             return Response({"error": "Visa application not found"}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = VisaApplicationsSerializer(visa_application, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # For DELETE
#     permission_required = "VS_Task_Delete"  # Define the required permission for DELETE method
#
#     @swagger_auto_schema(
#         operation_description="Delete a visa application by ID.",
#         tags=["VisaApplication"],
#         responses={
#             204: "Visa application deleted successfully.",
#             404: "Visa application not found."
#         }
#      )
#     def delete(self, request, pk):
#         try:
#             visa_application = VisaApplications.objects.get(pk=pk)
#             visa_application.delete()
#             return Response({"message": "Visa application deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
#         except VisaApplications.DoesNotExist:
#             return Response({"error": "Visa application not found"}, status=status.HTTP_404_NOT_FOUND)
#
#
# @swagger_auto_schema(
#     method='post',
#     operation_description="Create a new visa application or add multiple services to an existing visa application.",
#     tags=["VisaApplication"],
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#             required=True,  # Mark as required
#         ),
#     ],
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'user_id': openapi.Schema(
#                 type=openapi.TYPE_INTEGER,
#                 description="ID of the user creating the visa application (required for creating a new visa application)."
#             ),
#             'passport_number': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description="Passport number of the applicant (required for creating a new visa application)."
#             ),
#             'purpose': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description="Purpose of the visa application (required for creating a new visa application)."
#             ),
#             'visa_type': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description="Type of visa (required for creating a new visa application)."
#             ),
#             'destination_country': openapi.Schema(
#                 type=openapi.TYPE_STRING,
#                 description="Destination country for the visa application "
#                             "(required for creating a new visa application)."
#             ),
#             'services': openapi.Schema(
#                 type=openapi.TYPE_ARRAY,
#                 items=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'service_type': openapi.Schema(
#                             type=openapi.TYPE_STRING,
#                             description="Type of the service (e.g., Visa Stamping, Processing)."
#                         ),
#                         'comments': openapi.Schema(
#                             type=openapi.TYPE_STRING,
#                             description="Comments or additional information about the service."
#                         ),
#                         'quantity': openapi.Schema(
#                             type=openapi.TYPE_INTEGER,
#                             description="Quantity of the service."
#                         )
#                     },
#                     required=['service_type', 'quantity']  # Required properties for each service
#                 ),
#                 description="List of services to add to the visa application (optional)."
#             )
#         },
#         required=['user_id', 'passport_number', 'purpose', 'visa_type', 'destination_country'],  # Mandatory fields for new visa application
#     ),
#     responses={
#         201: openapi.Response(
#             description="Successfully created a new visa application or added services.",
#             examples={
#                 "application/json": {
#                     "message": "Visa application and services added successfully."
#                 }
#             }
#         ),
#         400: openapi.Response(
#             description="Invalid data provided.",
#             examples={
#                 "application/json": {
#                     "error": "Missing required fields. Provide 'user_id', 'passport_number', 'purpose', 'visa_type', and 'destination_country'."
#                 }
#             }
#         ),
#         401: openapi.Response(
#             description="Unauthorized access.",
#             examples={
#                 "application/json": {
#                     "error_message": "Unauthorized Access. Only Service Providers with roles (ServiceProvider_Admin, Individual_User) can add visa users.",
#                     "status_cd": 1
#                 }
#             }
#         ),
#         500: openapi.Response(
#             description="Internal server error.",
#             examples={
#                 "application/json": {
#                     "error": "An internal error occurred. Please try again later."
#                 }
#             }
#         )
#     }
# )
# @api_view(['POST'])
# @permission_classes([AllowAny])  # Add 'GroupPermission' if necessary for handling role-based permission
# @has_group_permission('VS_Task_Create')
# def manage_visa_applications(request):
#     try:
#         # Authorization check
#         if request.user.user_role not in ["ServiceProvider_Admin", "Individual_User"] or request.user.user_type != "ServiceProvider":
#             return Response(
#                 {
#                     'error_message': 'Unauthorized Access. Only Service Providers with roles '
#                                      '(ServiceProvider_Admin, Individual_User) can add visa users.',
#                     'status_cd': 1
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#
#         # Extract required fields from request data
#         user_id = request.data.get('user_id')
#         passport_number = request.data.get('passport_number', '')
#         purpose = request.data.get('purpose')
#         visa_type = request.data.get('visa_type')
#         destination_country = request.data.get('destination_country')
#
#
#         # Validate required fields
#         if not all([user_id, purpose, visa_type, destination_country]):
#             return Response(
#                 {"error": "Missing required fields. Provide 'user_id', "
#                           "'purpose', 'visa_type', and 'destination_country'."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Check if the visa application already exists
#         visa_applications = VisaApplications.objects.filter(
#             visa_type=visa_type, user_id=user_id, purpose=purpose, destination_country=destination_country
#         )
#         if visa_applications.exists():
#             visa_application = visa_applications.first()
#         else:
#             # Create a new visa application
#             visa_data = {
#                 'user': user_id,
#                 'passport_number': passport_number,
#                 'purpose': purpose,
#                 'visa_type': visa_type,
#                 'destination_country': destination_country
#             }
#             visa_serializer = VisaApplicationsSerializer(data=visa_data)
#             if visa_serializer.is_valid():
#                 visa_serializer.save()
#                 visa_application = VisaApplications.objects.get(id=visa_serializer.data['id'])
#             else:
#                 return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         # Process services data
#         services_data = request.data.get('services', [])
#         if services_data:
#             for service in services_data:
#                 service['visa_application'] = visa_application.id
#                 service_serializer = ServiceDetailsSerializer(data=service)
#                 if service_serializer.is_valid():
#                     service_serializer.save()
#                 else:
#                     return Response(service_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             return Response({"message": "Visa application and services added successfully."},
#                             status=status.HTTP_201_CREATED)
#
#         return Response(
#             {"error": "No services provided. Provide 'services' data to add to the visa application."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     except Exception as e:
#         logger.error(f"Error managing visa applications: {str(e)}", exc_info=True)
#         return Response({"error": "An internal error occurred. Please try again later."},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
#
# @swagger_auto_schema(
#     methods=['get'],
#     operation_description="Retrieve a list of all visa clients with their applications.",
#     tags=["VisaApplicantsList"],
#     responses={
#         200: VisaClientUserListSerializer(many=True),
#         403: "Unauthorized Access. Only Service Provider Admins can access this resource."
#     },
#     manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <JWT Token>",
#                 type=openapi.TYPE_STRING,
#             ),
#         ],
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_group_permission('VS_Task_View')
# def get_visa_clients_users_list(request):
#     try:
#         # Check if the user is a ServiceProvider_Admin with the correct type
#         print("****************")
#         if request.user.user_role == "ServiceProvider_Admin" and request.user.user_type == "ServiceProvider":
#             # Get all users created by the current ServiceProviderAdmin
#             created_by_id = request.user.id
#             users = User.objects.filter(created_by=created_by_id)
#
#             # Retrieve VisaApplications for these users
#             visa_applications = VisaApplications.objects.filter(user__in=users)
#             serializer = VisaClientUserListSerializer(visa_applications, many=True)
#
#         elif request.user.user_role == "Individual_User" and request.user.user_type == "ServiceProvider":
#             visa_applications = VisaApplications.objects.filter(user=request.user)
#             serializer = VisaClientUserListSerializer(visa_applications, many=True)
#
#         else:
#             return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
#
#         # Grouping visa applications and services by user
#         response_data = []
#         user_data_map = {}
#
#         for visa_app in serializer.data:  # Use serializer.data to get the serialized data
#             user = visa_app['email']
#
#             if user not in user_data_map:
#                 # Add user data to the map if not already added
#                 user_data_map[user] = {
#                     "email": visa_app['email'],
#                     "mobile_number": visa_app['mobile_number'],
#                     "first_name": visa_app['first_name'],
#                     "last_name": visa_app['last_name'],
#                     "services": [],
#                     "user": visa_app['user'],
#                 }
#
#             # Check if services list is empty
#             services = visa_app['services']
#             if len(services) > 0:
#                 for service in services:
#                     user_data_map[user]["services"].append({
#                         "id": service['id'],
#                         "service_type": service['service_type'],
#                         "service_name": service['service_name'],
#                         "date": service['date'],
#                         "status": service['status'],
#                         "comments": service['comments'],
#                         "quantity": service['quantity'],
#                         "visa_application": visa_app['id'],
#                         "last_updated_date": service['last_updated_date'],
#                         "passport_number": visa_app['passport_number'],
#                         "purpose": visa_app['purpose'],
#                         "visa_type": visa_app['visa_type'],
#                         "destination_country": visa_app['destination_country'],
#                         'user_id': visa_app['user']
#                     })
#             else:
#                 # If no services, add specific fields directly to user data
#                 user_data_map[user].update({
#                     "passport_number": visa_app['passport_number'],
#                     "purpose": visa_app['purpose'],
#                     "visa_type": visa_app['visa_type'],
#                     "destination_country": visa_app['destination_country'],
#                     'user_id': visa_app['user']
#                 })
#
#         # Convert the user data map to a list
#         response_data = list(user_data_map.values())
#
#         return Response(response_data, status=status.HTTP_200_OK)
#
#     except User.DoesNotExist:
#         return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     except VisaApplications.DoesNotExist:
#         return Response({"error": "No visa applications found."}, status=status.HTTP_404_NOT_FOUND)
#
#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
#
# @swagger_auto_schema(
#     methods=['get'],
#     operation_description="Retrieve a list of all visa clients with their applications and "
#                           "count the services based on status (progress, in progress, completed).",
#     tags=["VisaApplicantsOverallStatus"],
#     responses={
#         200: openapi.Response(
#             description="Counts of services based on status.",
#             examples={
#                 "application/json": {
#                     "progress": 1,
#                     "in_progress": 0,
#                     "completed": 0
#                 }
#             }
#         ),
#         403: "Unauthorized Access. Only Service Provider Admins can access this resource."
#     },
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#         ),
#     ],
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_group_permission('VS_Task_View')
# def service_status(request):
#     try:
#         # Check if the user has the appropriate role and type
#         if request.user.user_role in ["ServiceProvider_Admin", "Individual_User"] and request.user.user_type == "ServiceProvider":
#             # Determine the users and VisaApplications based on the role
#             if request.user.user_role == "ServiceProvider_Admin":
#                 created_by_id = request.user.id
#                 users = User.objects.filter(created_by=created_by_id)
#                 visa_applications = VisaApplications.objects.filter(user__in=users)
#             elif request.user.user_role == "Individual_User":
#                 visa_applications = VisaApplications.objects.filter(user=request.user)
#
#             # Serialize the VisaApplications data
#             serializer = VisaClientUserListSerializer(visa_applications, many=True)
#
#             # Initialize counters and data containers
#             counts = {
#                 'pending': 0,
#                 'pending_data': [],
#                 'in_progress': 0,
#                 'in_progress_data': [],
#                 'completed': 0,
#                 'completed_data': []
#             }
#
#             # Process each serialized item
#             for item in serializer.data:
#                 for service in item['services']:
#                     service_data = {
#                         'service_id': service['id'],
#                         'visa_applicant_name': item['first_name'] + ' ' + item['last_name'],
#                         'service_type': service['service_type'],
#                         'service_name': service['service_name'],
#                         'comments': service.get('comments', ''),
#                         'quantity': service.get('quantity', 0),
#                         'date': service.get('date', ''),
#                         'status': service['status'],
#                         'passport_number': item.get('passport_number'),
#                         'visa_type': item.get('visa_type'),
#                         'destination_country': item.get('destination_country'),
#                         'purpose': item.get('purpose'),
#                         'user': item.get('user')
#                     }
#
#                     # Categorize based on the service status
#                     if service['status'] == 'pending':
#                         counts['pending'] += 1
#                         counts['pending_data'].append(service_data)
#                     elif service['status'] == 'in progress':
#                         counts['in_progress'] += 1
#                         counts['in_progress_data'].append(service_data)
#                     elif service['status'] == 'completed':
#                         counts['completed'] += 1
#                         counts['completed_data'].append(service_data)
#
#             return Response(counts, status=status.HTTP_200_OK)
#
#         # If user is unauthorized
#         return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
#
#     except User.DoesNotExist:
#         # Handle the case where the user is not found
#         return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#
#     except VisaApplications.DoesNotExist:
#         # Handle the case where visa applications are not found
#         return Response({"error": "No visa applications found."}, status=status.HTTP_404_NOT_FOUND)
#
#     except Exception as e:
#         # Handle other unexpected errors
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# def parse_last_updated_date(last_updated):
#     """
#     Helper function to parse the last_updated field.
#     """
#     try:
#         # Parse the string to a datetime object using strptime
#         return datetime.strptime(last_updated, '%Y-%m-%dT%H:%M:%S.%fZ').date()
#     except (ValueError, TypeError) as e:
#         logger.error(f"Error parsing last_updated: {e}")
#         # Return an empty string if the date parsing fails
#         return ''
#
#
# def collect_service_data(serializer_data, user_role):
#     """
#     Helper function to collect and format service data.
#     """
#     all_services = []
#     for item in serializer_data:
#         if user_role == 'Individual_User':
#             if not item['services']:
#                 service_data = {
#                     'email': item.get('email'),
#                     'mobile_number': item.get('mobile_number'),
#                     'passport_number': item.get('passport_number'),
#                     'visa_type': item.get('visa_type'),
#                     'destination_country': item.get('destination_country'),
#                     'purpose': item.get('purpose'),
#                     'first_name': item['first_name'],
#                     'last_name': item['last_name'],
#                     'user': item.get('user')
#                 }
#                 all_services = service_data
#
#         for service in item['services']:
#             try:
#                 last_updated_date = parse_last_updated_date(service.get('last_updated'))
#                 service_data = {
#                     'email': item.get('email'),
#                     'mobile_number': item.get('mobile_number'),
#                     'passport_number': item.get('passport_number'),
#                     'visa_type': item.get('visa_type'),
#                     'destination_country': item.get('destination_country'),
#                     'purpose': item.get('purpose'),
#                     'id': service['id'],
#                     'service_type': service['service_type'],
#                     'service_name': service['service_name'],
#                     'first_name': item['first_name'],
#                     'last_name': item['last_name'],
#                     'comments': service.get('comments', ''),
#                     'quantity': service.get('quantity', 0),
#                     'date': service.get('date', ''),
#                     'last_updated': last_updated_date,
#                     'status': service['status'],
#                     'passport': item.get('passport_number'),
#                     'user': item.get('user')
#                 }
#                 all_services.append(service_data)
#             except KeyError as e:
#                 logger.error(f"Missing key in service data: {e}")
#                 return {"error": f"Missing key in service data: {e}"}, False
#             except Exception as e:
#                 logger.error(f"Unexpected error while processing service data: {e}")
#                 return {"error": f"Unexpected error: {e}"}, False
#     return all_services, True
#
# @swagger_auto_schema(
#     method='get',
#     operation_description="Retrieve all service data irrespective of their statuses"
#                           " (pending, in-progress, completed, etc.) for "
#                           "Visa Applications under the logged-in ServiceProviderAdmin.",
#     tags=["VisaApplicantsAllTasks"],
#     responses={
#         200: openapi.Response(
#             description="A list of all services.",
#             examples={
#                 "application/json": [
#                     {
#                         "service_id": 1,
#                         "service_type": "Visa Renewal",
#                         "service_name": "Renewal Service",
#                         "visa_application_name": "John Doe",
#                         "comments": "Urgent processing required",
#                         "quantity": 1,
#                         "date": "2024-12-11",
#                         "status": "in_progress"
#                     },
#                     {
#                         "service_id": 2,
#                         "service_type": "New Visa",
#                         "service_name": "New Application Service",
#                         "visa_application_name": "Jane Smith",
#                         "comments": "",
#                         "quantity": 1,
#                         "date": "2024-12-10",
#                         "status": "completed"
#                     }
#                 ]
#             }
#         ),
#         403: openapi.Response("Unauthorized access."),
#     },
#     manual_parameters=[
#         openapi.Parameter(
#             'Authorization',
#             openapi.IN_HEADER,
#             description="Bearer <JWT Token>",
#             type=openapi.TYPE_STRING,
#             required=True
#         )
#     ]
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_group_permission('VS_Task_View')
# def all_service_data(request):
#     user_role = request.user.user_role
#
#     try:
#         if user_role == "ServiceProvider_Admin":
#             # Get all VisaApplications for the current ServiceProviderAdmin
#             created_by_id = request.user.id
#             users = User.objects.filter(created_by=created_by_id)
#             visa_applications = VisaApplications.objects.filter(user__in=users)
#
#         elif user_role == "Individual_User":
#             # Get all VisaApplications for the current Individual User
#             user_id = request.user.id
#             visa_applications = VisaApplications.objects.filter(user=user_id)
#
#         else:
#             return Response(
#                 {"error": "Unauthorized access."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#
#         # Serialize the data
#         serializer = VisaClientUserListSerializer(visa_applications, many=True)
#
#         # Collect and format all services data
#         all_services, success = collect_service_data(serializer.data, user_role)
#         if not success:
#             return Response(all_services, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response(all_services, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         logger.error(f"Unexpected error in all_service_data: {e}")
#         return Response(
#             {"error": f"An unexpected error occurred: {e}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#
#
# auth_header = openapi.Parameter(
#     'Authorization',
#     in_=openapi.IN_HEADER,
#     description="Bearer <JWT Token>",
#     type=openapi.TYPE_STRING,
#     required=True
# )
#
# class ServiceDetailsAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     permission_required = "VS_Task_View"
#
#     def has_permission(self, user):
#         """
#         Check if the user has the required role and type.
#         """
#         return (
#                 user.user_role in ['ServiceProvider_Admin', 'Individual_User'] and
#                 user.user_type == 'ServiceProvider'
#         )
#
#     @swagger_auto_schema(
#         operation_description="Retrieve a specific ServiceDetails instance by ID.",
#         tags=["VisaServiceTasks"],
#         manual_parameters=[auth_header],
#         responses={
#             200: ServiceDetailsSerializer(),
#             401: "Unauthorized - Missing or invalid token.",
#             404: "Service not found.",
#         },
#     )
#     def get(self, request, pk):
#         """Retrieve a specific ServiceDetails instance by ID."""
#         print("****")
#         if not self.has_permission(request.user):
#             return Response(
#                 {"error": "You do not have permission to perform this action."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#         service = get_object_or_404(ServiceDetails, pk=pk)
#         serializer = ServiceDetailsSerializer(service)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     request_body = openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'visa_application': openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'user': openapi.Schema(type=openapi.TYPE_INTEGER),
#                     'passport_number': openapi.Schema(type=openapi.TYPE_STRING),
#                     'purpose': openapi.Schema(type=openapi.TYPE_STRING),
#                     'visa_type': openapi.Schema(type=openapi.TYPE_STRING),
#                     'destination_country': openapi.Schema(type=openapi.TYPE_STRING)
#                 },
#                 required=['user', 'passport_number', 'purpose', 'visa_type', 'destination_country']
#             ),
#             'service': openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'id': openapi.Schema(type=openapi.TYPE_INTEGER),
#                     'service_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
#                     'date': openapi.Schema(type=openapi.FORMAT_DATETIME),
#                     'status': openapi.Schema(type=openapi.TYPE_STRING),
#                     'comments': openapi.Schema(type=openapi.TYPE_STRING),
#                     'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
#                     'last_updated': openapi.Schema(type=openapi.FORMAT_DATETIME),
#                 },
#                 required=['id', 'service_type_id', 'date', 'status', 'comments', 'quantity', 'last_updated']
#             ),
#         },
#         required=['visa_application', 'service']
#     )
#
#     permission_required = "VS_Task_Edit"
#
#     @swagger_auto_schema(
#         operation_description="Partially update a specific ServiceDetails instance (partial=True).",
#         tags=["VisaServiceTasks"],
#         manual_parameters=[auth_header],
#         request_body=request_body,
#         responses={
#             200: ServiceDetailsSerializer(),
#             400: "Validation error.",
#             401: "Unauthorized - Missing or invalid token.",
#             404: "Service not found.",
#         },
#     )
#     def put(self, request, pk):
#         """Partially update a specific ServiceDetails instance (partial=True)."""
#         if not self.has_permission(request.user):
#             return Response(
#                 {"error": "You do not have permission to perform this action."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#         # service = get_object_or_404(ServiceDetails, pk=pk)
#         service = ServiceDetails.objects.get(id=pk)
#
#         visa_data = request.data.get('visa_application', {})
#         # Check if the VisaApplication exists
#         user_id = visa_data.get('user')
#         passport_number= visa_data.get('passport_number', '')
#         purpose= visa_data.get('purpose')
#         visa_type = visa_data.get('visa_type')
#         destination_country = visa_data.get('destination_country')
#         visa_application = VisaApplications.objects.filter(
#             user_id=visa_data.get('user'),
#             purpose=visa_data.get('purpose'),
#             visa_type=visa_data.get('visa_type'),
#             destination_country=visa_data.get('destination_country')
#         ).first()
#         if visa_application:
#             # Update existing VisaApplication with provided data
#             service_data = request.data.get('service', {})
#             service_data['visa_application'] = visa_application.id  # Set the existing visa application ID
#         else:
#             visa_data['passport_number'] = passport_number
#             visa_application_serializer = VisaApplicationsSerializer(data=visa_data)
#             if visa_application_serializer.is_valid():
#                 visa_application_ = visa_application_serializer.save()
#                 service_data = request.data.get('service', {})
#                 service_data['visa_application'] = visa_application_.id
#             else:
#                 return Response(visa_application_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 # Update the ServiceDetails instance
#         service = get_object_or_404(ServiceDetails, id=request.data.get('service').get('id'))
#         serializer = ServiceDetailsSerializer(service, data=service_data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     permission_required = "VS_Task_Delete"
#     @swagger_auto_schema(
#         operation_description="Delete a specific ServiceDetails instance by ID.",
#         tags=["VisaServiceTasks"],
#         manual_parameters=[auth_header],
#         responses={
#             204: "Service deleted successfully.",
#             401: "Unauthorized - Missing or invalid token.",
#             404: "Service not found.",
#         },
#     )
#     def delete(self, request, pk):
#         """Delete a specific ServiceDetails instance."""
#         if not self.has_permission(request.user):
#             return Response(
#                 {"error": "You do not have permission to perform this action."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#         service = get_object_or_404(ServiceDetails, pk=pk)
#         service.delete()
#         return Response({"message": "Service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def create_contact(request):
#     """ API to handle contact form submissions """
#     serializer = ContactSerializer(data=request.data)
#
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             {
#                 "message": "Request submitted successfully! One of our executives will get in touch with you."
#             },
#             status=status.HTTP_201_CREATED
#         )
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(["GET"])
# def list_contacts_by_date(request):
#     """API to list contacts for a specific date"""
#     date_str = request.GET.get("date")  # Get date from query parameters (YYYY-MM-DD)
#
#     if not date_str:
#         return Response({"error": "Date parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         contacts = Contact.objects.filter(created_date=date_str)  # Filter by created_date
#         serializer = ContactSerializer(contacts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#
# def send_email_notification(to_email, consultation):
#     # Initialize S3 client
#     ses_client = boto3.client(
#         'ses',
#         region_name=AWS_REGION,
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#     )
#
#     """ Sends an email notification using AWS SES """
#     subject = "Consultation Booking Confirmation"
#     body = f"""
#     Hello {consultation.name},
#
#     Your consultation has been successfully booked.
#
#     📅 Date: {consultation.date}
#     ⏰ Time: {consultation.time}
#     📞 Mobile: {consultation.mobile_number}
#
#     Our team will contact you soon.
#
#     Best Regards,
#     TaraFirst
#     """
#
#     response = ses_client.send_email(
#         Source="admin@tarafirst.com",  # Must be verified in AWS SES
#         Destination={"ToAddresses": [to_email]},
#         Message={
#             "Subject": {"Data": subject},
#             "Body": {"Text": {"Data": body}},
#         },
#     )
#     return response
#
#
# def send_admin_notification(consultation):
#     # Initialize SES client
#     ses_client = boto3.client(
#         'ses',
#         region_name=AWS_REGION,
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#     )
#
#     """ Sends an email notification to the admin when a consultation is booked """
#     subject = "New Consultation Booking Notification"
#     body = f"""
#     📢 New Consultation Booking Alert!
#
#     A new consultation has been scheduled:
#
#     🧑 Name: {consultation.name}
#     📧 Email: {consultation.email}
#     📞 Mobile: {consultation.mobile_number}
#     📅 Date: {consultation.date}
#     ⏰ Time: {consultation.time}
#
#     Please follow up with the customer as required.
#
#     Best Regards,
#     TaraFirst Admin
#     """
#
#     response = ses_client.send_email(
#         Source="admin@tarafirst.com",  # Must be verified in AWS SES
#         Destination={"ToAddresses": ["admin@tarafirst.com"]},  # Replace with actual admin email
#         Message={
#             "Subject": {"Data": subject},
#             "Body": {"Text": {"Data": body}},
#         },
#     )
#     return response
#
#
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def create_consultation(request):
#     """ API to create a new consultation with 30-minute slot validation """
#     serializer = ConsultationSerializer(data=request.data)
#
#     if serializer.is_valid():
#         consultation = serializer.save()
#         # Send email notification
#         send_email_notification(consultation.email, consultation)
#         send_admin_notification(consultation)
#         return Response({"message": "Consultation booked successfully! Email sent."},
#                         status=status.HTTP_201_CREATED)
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(["GET"])
# def list_consultations(request):
#     """ API to list all consultations or filter by date """
#     date = request.GET.get("date")  # User passes date as a query param (YYYY-MM-DD)
#
#     if date:
#         consultations = Consultation.objects.filter(date=date)
#     else:
#         consultations = Consultation.objects.all()
#
#     serializer = ConsultationSerializer(consultations, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
#
#
