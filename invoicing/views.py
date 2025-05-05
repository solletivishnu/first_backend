from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models
from .models import InvoicingProfile, CustomerProfile, GoodsAndServices, Invoice, CustomerInvoiceReceipt, InvoiceFormat
from .serializers import (InvoicingProfileSerializer, CustomerProfileSerializers,InvoiceFormatSerializer,
                          GoodsAndServicesSerializer, InvoicingProfileGoodsAndServicesSerializer, InvoiceSerializer,
                          InvoicingProfileSerializers, InvoicingProfileCustomersSerializer, InvoicingProfileInvoices,
                          InvoiceSerializerData, InvoiceDataSerializer,InvoicingExistsBusinessSerializers,
                          CustomerInvoiceReceiptSerializer, InvoicingProfileBusinessSerializers)
from django.http import QueryDict
import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser
from django.http.response import JsonResponse,HttpResponse
from datetime import datetime, timedelta
import json, base64
from num2words import num2words
# from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit
from calendar import isleap, monthrange
from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Case, When, F, Sum, Prefetch, FloatField
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from usermanagement.utils import *
from usermanagement.decorators import *
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# Create loggers for general and error logs
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoicing_profile(request):
    """
    Retrieve the invoicing profile for the logged-in user or by business_id.
    """
    try:
        # Retrieve the business_id from query parameters
        business_id = request.query_params.get('business_id')

        # If business_id is provided, fetch the invoicing profile for that business
        if business_id:
            invoicing_profile = InvoicingProfile.objects.get(business__id=business_id)
        else:
            # If no business_id is provided, fetch the invoicing profile for the logged-in user
            user = request.user.id
            invoicing_profile = InvoicingProfile.objects.get(business__client=user)

        # Serialize the invoicing profile data
        serializer = InvoicingProfileBusinessSerializers(invoicing_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in get_invoicing_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def invoicing_profile_exists(request):
    """
    Check if all related objects exist for an invoicing profile.
    Returns True if all exist, False otherwise.
    """
    try:
        # Retrieve the business_id from query parameters (if provided)
        business_id = request.query_params.get('business_id')

        # If business_id is provided, fetch the invoicing profile for that business
        if business_id:
            invoicing_profile = InvoicingProfile.objects.filter(business__id=business_id).first()

            if not invoicing_profile:
                return Response({"exists": False, "message": "Invoicing profile not found."}, status=status.HTTP_200_OK)

            # Serialize the invoicing profile data
            serializer = InvoicingExistsBusinessSerializers(invoicing_profile)

            # Check if all required objects exist
            all_exist = (
                    serializer.get_customer_profiles_exist(invoicing_profile) and
                    serializer.get_goods_and_services_exist(invoicing_profile) and
                    serializer.get_invoice_format_exist(invoicing_profile)
            )
            invoicing_profile_id = None
            if all_exist:
                invoicing_profile_id = invoicing_profile.id

            return Response({"exists": all_exist, "invoicing_profile_id": invoicing_profile_id},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Business data is needed to check the Invoicing Setting Status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def create_invoicing_profile(request):
    """
    Create a new invoicing profile for the logged-in user.
    Patches business fields if missing.
    """
    serializer = InvoicingProfileSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            serializer.save()  # Business is assigned and patched in serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Unexpected error in create_invoicing_profile: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def update_invoicing_profile(request, pk):
    """
    Update the existing invoicing profile for the logged-in user.
    Patches business fields if missing.
    """
    try:
        invoicing_profile = InvoicingProfile.objects.get(id=pk, business__client=request.user)
    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InvoicingProfileSerializer(
        invoicing_profile, data=request.data, partial=True, context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete the invoicing profile for the logged-in user.",
    tags=["Invoicing Profiles"],
    responses={
        204: openapi.Response("Invoicing profile deleted successfully."),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Invoicing profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invoicing_profile(request):
    """
    Delete the invoicing profile for the logged-in user.
    """
    try:
        invoicing_profile = InvoicingProfile.objects.get(business=request.user)
        invoicing_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in delete_invoicing_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new customer profile for the logged-in user.",
    tags=["Customer Profiles"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Customer name"),
            'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description="PAN number"),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description="Country"),
            'address_line1': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 1"),
            'address_line2': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 2"),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description="State"),
            'postal_code': openapi.Schema(type=openapi.TYPE_STRING, description="Postal code"),
            'gst_registered': openapi.Schema(type=openapi.TYPE_STRING, description="GST registered status"),
            'gstin': openapi.Schema(type=openapi.TYPE_STRING, description="GSTIN"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email address"),
            'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description="Mobile number"),
            "opening_balance": openapi.Schema(type=openapi.TYPE_STRING, description="Opening Balance"),
            "gst_type": openapi.Schema(type=openapi.TYPE_STRING, description="Gst Type")
        }
    ),
    responses={
        201: openapi.Response(
            description="Customer profile created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "address_line2": "XYZ Buddy",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890",
                    "opening_balance": 97000,
                    "gst_type": "Anything"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer_profile(request):
    """
    Create a new customer profile for the logged-in user.
    """
    serializer = CustomerProfileSerializers(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the customer profile of the logged-in user.",
    tags=["Customer Profiles"],
    responses={
        200: openapi.Response(
            description="Customer profile details.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_profile(request):
    """
    Retrieve the invoicing profile along with its associated customer profiles for the logged-in user.
    """
    try:
        business_id = request.query_params.get('business_id')
        invoicing_profile_id = request.query_params.get('invoicing_profile_id')

        # Check if invoicing_profile_id is provided first
        if invoicing_profile_id:
            invoicing_profile = InvoicingProfile.objects.get(id=invoicing_profile_id)

        # If not, check if business_id is provided
        elif business_id:
            invoicing_profile = InvoicingProfile.objects.get(business__id=business_id)

        # If neither is provided, return a bad request response
        else:
            return Response(
                {"message": "Either business_id or invoicing_profile_id must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serialize the data
        serializer = InvoicingProfileCustomersSerializer(invoicing_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except InvoicingProfile.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to access an invoicing profile, but none exist.")
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in get_customer_profile: {e}")
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update the customer profile for the logged-in user.",
    tags=["Customer Profiles"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Customer name"),
            'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description="PAN number"),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description="Country"),
            'address_line1': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 1"),
            'address_line2': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 2"),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description="State"),
            'postal_code': openapi.Schema(type=openapi.TYPE_STRING, description="Postal code"),
            'gst_registered': openapi.Schema(type=openapi.TYPE_STRING, description="GST registered status"),
            'gstin': openapi.Schema(type=openapi.TYPE_STRING, description="GSTIN"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email address"),
            'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description="Mobile number"),
            "opening_balance": openapi.Schema(type=openapi.TYPE_STRING, description="Opening Balance"),
            "gst_type": openapi.Schema(type=openapi.TYPE_STRING, description="Gst Type")
        }
    ),
    responses={
        200: openapi.Response(
            description="Customer profile updated successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe Updated",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "address_line2": "123 Main St",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890",
                    "opening_balance": 97000,
                    "gst_type": "Anything"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer_profile(request, id):
    """
    Update the customer profile for the given ID.
    """
    try:
        # Retrieve the customer profile by ID
        customer_profile = CustomerProfile.objects.get(id=id)
        serializer = CustomerProfileSerializers(customer_profile, data=request.data, partial=True)

        # Validate and save the updated data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except CustomerProfile.DoesNotExist:
        logger.warning(f"Customer profile with ID {id} does not exist.")
        return Response({"message": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in update_customer_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@swagger_auto_schema(
    method='delete',
    operation_description="Delete the customer profile of the logged-in user.",
    tags=["Customer Profiles"],
    responses={
        204: openapi.Response(
            description="Customer profile deleted successfully."
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer_profile(request, id):
    """
    Delete the customer profile by its ID.
    """
    try:
        # Get the customer profile with the given ID
        customer_profile = CustomerProfile.objects.get(id=id)
        customer_profile.delete()
        return Response({"message": "Customer profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except CustomerProfile.DoesNotExist:
        logger.warning(f"Attempt to delete a non-existent customer profile with ID {id}.")
        return Response({"message": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in delete_customer_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='post',
    operation_description="Create a new goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or services"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or services"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of the goods or services"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description="Price per unit"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the goods or services"),
        }
    ),
    responses={
        201: openapi.Response(
            description="Goods and services entry created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Service",
                    "name": "Consulting",
                    "units": "Hours",
                    "hsn_sac": "1234",
                    "gst_rate": "18",
                    "unit_price": 100.0,
                    "description": "Consulting services for software development"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goods_and_services(request):
    """
    Create a new goods and services entry for the logged-in user.
    """
    serializer = GoodsAndServicesSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve goods and services entries for the logged-in user.",
    tags=["Goods and Services"],
    responses={
        200: openapi.Response(
            description="Goods and services entry details.",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "invoicing_profile": 1,
                        "type": "Service",
                        "name": "Consulting",
                        "units": "Hours",
                        "hsn_sac": "1234",
                        "gst_rate": "18",
                        "unit_price": 100.0,
                        "description": "Consulting services for software development"
                    },
                    {
                        "id": 2,
                        "invoicing_profile": 1,
                        "type": "Product",
                        "name": "Laptop",
                        "units": "Piece",
                        "hsn_sac": "5678",
                        "gst_rate": "28",
                        "unit_price": 1000.0,
                        "description": "High-performance laptop"
                    }
                ]
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_goods_and_services(request):
    """
    Retrieve goods and services entries for the logged-in user.
    """
    try:
        goods_and_services_entries = GoodsAndServices.objects.filter(invoicing_profile__business=request.user)
        serializer = GoodsAndServicesSerializer(goods_and_services_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Unexpected error in get_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update a goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or services"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or services"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of the goods or services"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description="Price per unit"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the goods or services"),
        }
    ),
    responses={
        200: openapi.Response(
            description="Goods and services entry updated successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Service",
                    "name": "Consulting Updated",
                    "units": "Hours",
                    "hsn_sac": "1234",
                    "gst_rate": "18",
                    "unit_price": 110.0,
                    "description": "Updated consulting services for software development"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Goods and services entry not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_goods_and_services(request, pk):
    """
    Update a goods and services entry for the logged-in user.
    """
    try:
        goods_and_services_entry = GoodsAndServices.objects.get(pk=pk, invoicing_profile__business=request.user)
        serializer = GoodsAndServicesSerializer(goods_and_services_entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except GoodsAndServices.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to update a non-existent goods and services entry.")
        return Response({"message": "Goods and services entry not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in update_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='delete',
    operation_description="Delete a goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    responses={
        204: openapi.Response(
            description="Goods and services entry deleted successfully."
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Goods and services entry not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_goods_and_services(request, pk):
    """
    Delete a goods and services entry for the logged-in user.
    """
    try:
        goods_and_services_entry = GoodsAndServices.objects.get(pk=pk, invoicing_profile__business=request.user)
        goods_and_services_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except GoodsAndServices.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to delete a non-existent goods and services entry.")
        return Response({"message": "Goods and services entry not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in delete_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new goods or service entry.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or service"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or service"),
            'sku_value': openapi.Schema(type=openapi.TYPE_NUMBER, description="SKU value"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of measurement"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'tax_preference': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tax preference"),
            'selling_price': openapi.Schema(type=openapi.TYPE_INTEGER, description="Selling price"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description"),
        }
    ),
    responses={
        201: openapi.Response(
            description="Goods or service created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Product",
                    "name": "Laptop",
                    "sku_value": 12345.67,
                    "units": "piece",
                    "hsn_sac": "8471",
                    "gst_rate": "18",
                    "tax_preference": 1,
                    "selling_price": 50000,
                    "description": "High-end gaming laptop"
                }
            }
        ),
        400: openapi.Response("Bad Request."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goods_service(request):
    """
    Create a new goods or service entry.
    """
    serializer = GoodsAndServicesSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a goods or service entry by ID.",
    tags=["Goods and Services"],
    responses={
        200: openapi.Response(
            description="Successfully retrieved goods or service.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Product",
                    "name": "Laptop",
                    "sku_value": 12345.67,
                    "units": "piece",
                    "hsn_sac": "8471",
                    "gst_rate": "18",
                    "tax_preference": 1,
                    "selling_price": 50000,
                    "description": "High-end gaming laptop"
                }
            }
        ),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_goods_service(request, pk):
    """
    Retrieve a goods or service entry by ID.
    """
    try:
        # Retrieve a single invoicing profile by ID
        invoicing_profile = InvoicingProfile.objects.get(id=pk)

        # Serialize the data
        serializer = InvoicingProfileGoodsAndServicesSerializer(invoicing_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except InvoicingProfile.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to access an invoicing profile with ID {pk}, but it does not exist.")
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in retrieve_goods_service: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='put',
    operation_description="Update an existing goods or service entry by ID.",
    tags=["Goods and Services"],
    request_body=GoodsAndServicesSerializer,
    responses={
        200: openapi.Response("Successfully updated the goods or service."),
        400: openapi.Response("Bad Request."),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_goods_service(request, id):
    """
    Update an existing goods or service entry by ID.
    """
    try:
        goods_service = GoodsAndServices.objects.get(id=id)
        serializer = GoodsAndServicesSerializer(goods_service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except GoodsAndServices.DoesNotExist:
        return Response({"message": "Goods or service not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete a goods or service entry by ID.",
    tags=["Goods and Services"],
    responses={
        204: openapi.Response("Successfully deleted the goods or service."),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_goods_service(request, id):
    """
    Delete a goods or service entry by ID.
    """
    try:
        goods_service = GoodsAndServices.objects.get(id=id)
        goods_service.delete()
        return Response({"message": "Goods or service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except GoodsAndServices.DoesNotExist:
        return Response({"message": "Goods or service not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    operation_description="Create a new invoice.",
    tags=["Invoices"],
    request_body=InvoiceSerializer,
    responses={
        201: openapi.Response("Invoice created successfully."),
        400: openapi.Response("Bad request."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    """
    Create a new invoice.
    """
    try:
        # Extract the invoice_date from request.data
        invoice_date = request.data.get("invoice_date")
        if invoice_date:
            try:
                # Convert the string to a date object and extract the month
                invoice_date_obj = datetime.strptime(invoice_date, "%Y-%m-%d").date()  # Convert to a date object
                request.data["month"] = invoice_date_obj.month
            except ValueError as e:
                logger.warning(f"Invalid invoice_date format: {e}")
                return Response(
                    {"error": "Invalid invoice_date format. Expected format: YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Serialize and save the data
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error in create_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all invoices associated with an invoicing profile.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            description="List of invoices retrieved successfully.",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "invoicing_profile": 1,
                        "customer": "John Doe",
                        "terms": "Net 30",
                        "financial_year": "2023-24",
                        "invoice_number": "INV-0001",
                        "invoice_date": "2024-12-18T00:00:00Z",
                        "place_of_supply": "California",
                        "billing_address": {
                            "line1": "123 Main St",
                            "city": "Los Angeles",
                            "state": "CA",
                            "zipcode": "90001"
                        },
                        "shipping_address": {
                            "line1": "456 Oak Ave",
                            "city": "San Francisco",
                            "state": "CA",
                            "zipcode": "94101"
                        },
                        "item_details": [
                            {"name": "Product A", "price": 100, "quantity": 2},
                            {"name": "Service B", "price": 200, "quantity": 1}
                        ],
                        "total_amount": 400,
                        "subtotal_amount": 350,
                        "shipping_amount": 50,
                        "cgst_amount": 18,
                        "sgst_amount": 18,
                        "igst_amount": 0,
                        "pending_amount": 200,
                        "amount_invoiced": 400,
                        "payment_status": "Partial",
                        "is_same_as_billing": True,
                        "notes": "Thank you for your business.",
                        "terms_and_conditions": "No returns after 30 days."
                    }
                ]
            }
        ),
        400: openapi.Response(
            description="Invalid request parameters.",
            examples={
                "application/json": {
                    "error": "Invoicing profile ID is required."
                }
            }
        ),
        404: openapi.Response(
            description="No invoices found for the provided invoicing profile.",
            examples={
                "application/json": {
                    "error": "Invoicing profile not found."
                }
            }
        ),
        500: openapi.Response(
            description="An unexpected server error occurred.",
            examples={
                "application/json": {
                    "error": "An unexpected error occurred. Please try again later."
                }
            }
        ),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'invoicing_profile_id',
            openapi.IN_QUERY,
            description="ID of the invoicing profile.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'financial_year',
            openapi.IN_QUERY,
            description="Financial year to filter invoices (optional).",
            type=openapi.TYPE_STRING,
            required=False
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_invoices(request):
    """
    Retrieve all invoices for a given invoicing profile.
    """
    try:
        # Retrieve query parameters
        invoicing_profile_id = request.query_params.get('invoicing_profile_id')
        financial_year = request.query_params.get('financial_year')

        # Validate input
        invoicing_profile = InvoicingProfile.objects.get(id=invoicing_profile_id)

        # Pass the request context to the serializer
        serializer = InvoicingProfileInvoices(invoicing_profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except InvoicingProfile.DoesNotExist:
        logger.warning(
            f"User {request.user.id} tried to access an invoicing profile with ID {invoicing_profile_id}, "
            f"financial year {financial_year}, but it does not exist."
        )
        return Response(
            {"error": "Invoicing profile not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        logger.error(f"Unexpected error in retrieve_invoices: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@swagger_auto_schema(
    method='put',
    operation_description="Update an existing invoice by ID.",
    tags=["Invoices"],
    request_body=InvoiceSerializer,
    responses={
        200: openapi.Response("Invoice updated successfully."),
        404: openapi.Response("Invoice not found."),
        400: openapi.Response("Validation error."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_invoice(request, invoice_id):
    """
    Update an existing invoice by ID.
    """
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()

        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return Response({"message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the shipping_address is correctly formatted as a dictionary
        if 'shipping_address' in request.data:
            if not isinstance(request.data['shipping_address'], dict):
                return Response({"message": "shipping_address must be a valid JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Validation error while updating invoice: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error in update_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@swagger_auto_schema(
    method='delete',
    operation_description="Delete an existing invoice by ID.",
    tags=["Invoices"],
    responses={
        204: openapi.Response("Invoice deleted successfully."),
        404: openapi.Response("Invoice not found."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invoice(request, invoice_id):
    """
    Delete an existing invoice by ID. To be tested
    """
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()

        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return Response({"message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        invoice.delete()
        return Response({"message": "Invoice deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Unexpected error in delete_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# def generate_document(self, generator, template_name):
#     try:
#         pdf = generator.generate_document(template_name)
#         eventSerializer = Invoicing_profileSerializers(data=self.data)
#         if eventSerializer.is_valid():
#             eventSerializer.save()
#         else:
#             return Response(eventSerializer.errors, status=400)
#
#         response = HttpResponse(pdf, content_type='application/pdf')
#         return response
#     except Exception as e:
#         return Response({'error': str(e)}, status=500)


def formatStringDate(date):
    if isinstance(date, datetime):
        # If it's already a datetime object, format it directly
        return date.strftime('%d-%b-%Y')
    elif isinstance(date, str) and date:
        # If it's a string, parse it and then format
        try:
            parsed_date = datetime.strptime(date, '%d-%m-%Y')
            return parsed_date.strftime('%d-%b-%Y')
        except ValueError:
            return ''  # Handle invalid date formats as needed
    return ''  # Handle cases where date is None or an empty string

class DocumentGenerator:
    def __init__(self, request, invoicing_profile, context):
        self.request = request
        self.invoicing_profile = invoicing_profile
        self.context = context

    def generate_document(self, template_name):
        try:
            # Render the HTML template with the context data
            html_content = render_to_string(template_name, self.context)

            # Generate the PDF from the HTML content using pdfkit
            try:
                pdf = pdfkit.from_string(html_content, False)  # False to get the PDF as a byte string
                print("PDF generation successful.")
            except Exception as pdf_error:
                print(f"Error in generating PDF: {pdf_error}")
                raise

            # Return the generated PDF as an HTTP response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="invoice.pdf"'
            print(response)
            return response
        except Exception as e:
            print(f"Error generating document: {e}")
            raise


def split_address(address):
    half = len(address) // 2
    space_index = address.rfind(' ', 0, half)

    if space_index != -1:
        first_half = address[:space_index]
        second_half = address[space_index + 1:]
    else:
        first_half = address[:half]
        second_half = address[half:]

    return first_half + '<br/>' + second_half

@swagger_auto_schema(
    method='get',
    operation_description="Generate a PDF document for the specified invoice.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            "PDF document generated successfully",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'file': openapi.Schema(type=openapi.TYPE_FILE, description="Generated PDF file"),
                }
            ),
        ),
        404: openapi.Response("Invoice not found"),
        500: openapi.Response("Internal server error"),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="The ID of the invoice to generate the document for.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@api_view(["GET"])
# @require_permissions(2, required_actions=['Invoice.print'])
def createDocument(request, id):
    try:
        # Fetch the invoice object
        invoice = Invoice.objects.get(id=id)
        signature_base64 = ''
        # if invoice.invoicing_profile.signature:
        #     with open(invoice.invoicing_profile.signature.path, "rb") as image_file:
        #         signature_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        # No need to check 'if not invoice' since it's already guaranteed to be set by .get()
        contexts = []

        total = invoice.total_amount
        total_str = f"{total:.2f}"
        total_in_words = num2words(total)
        total_in_words = total_in_words.capitalize()
        total_in_words = total_in_words.replace("<br/>", ' ')
        total_in_words = total_in_words.title() + ' ' + 'Rupees Only'

        invoice_date = invoice.invoice_date
        # terms = int(invoice.terms) if invoice else 0
        # due_date = invoice_date + timedelta(days=terms)
        invoice_date_str = invoice_date.strftime('%d-%m-%Y')
        due_date_str = invoice.due_date.strftime('%d-%m-%Y')

        if len(getattr(invoice.invoicing_profile.business, 'email', '')) > 26:
            business_name = split_address(invoice.invoicing_profile.business.email)
            adjust_layout = True
        else:
            business_name = invoice.invoicing_profile.business.email
            adjust_layout = False

        context = {
            'company_name': getattr(invoice.invoicing_profile.business, 'nameOfBusiness', ''),
            'business_type': getattr(invoice.invoicing_profile.business, 'entityType', '') or
                               getattr(invoice.invoicing_profile, 'business_type', ''),
            'address': invoice.invoicing_profile.business.headOffice.get('address_line1', ''),
            'state': invoice.invoicing_profile.business.headOffice.get('state', ''),
            'country': "India",
            'pincode': invoice.invoicing_profile.business.headOffice.get('pincode', ''),
            'registration_number': getattr(invoice.invoicing_profile.business, 'registrationNumber', ''),
            'gst_registered': getattr(invoice.invoicing_profile, 'gst_registered', ''),
            'gstin': getattr(invoice.invoicing_profile, 'gstin', ''),
            'email': getattr(invoice.invoicing_profile.business, 'email', ''),
            'mobile': getattr(invoice.invoicing_profile.business, 'mobile_number', ''),
            'pan': getattr(invoice.invoicing_profile.business, 'pan', ''),
            'bank_name': getattr(invoice.invoicing_profile, 'bank_name', ''),
            'account_number': getattr(invoice.invoicing_profile, 'account_number', ''),
            'ifsc_code': getattr(invoice.invoicing_profile, 'ifsc_code', ''),
            'invoice_format': getattr(invoice.invoicing_profile, 'ifsc_code', ''),
            'swift_code': getattr(invoice.invoicing_profile, 'ifsc_code', ''),
            'signature': signature_base64,
            # Invoice data fields (only for the selected invoice)
            'customer_name': getattr(invoice, 'customer', ''),
            'terms': getattr(invoice, 'terms', ''),
            'due_date': due_date_str,
            'financial_year': getattr(invoice, 'financial_year', ''),
            'invoice_number': getattr(invoice, 'invoice_number', ''),
            'invoice_date': invoice_date_str,
            'place_of_supply': getattr(invoice, 'place_of_supply', ''),


            # Bill To address fields
            'bill_to_address': invoice.billing_address.get('address_line1', '') if hasattr(invoice,
                                                                                           'billing_address') else '',
            'bill_to_state': invoice.billing_address.get('state', '') if hasattr(invoice, 'billing_address') else '',
            'bill_to_country': invoice.billing_address.get('country', '') if hasattr(invoice,
                                                                                     'billing_address') else '',
            'customer_gstin': getattr(invoice, 'customer_gstin', ''),
            'customer_pan': getattr(invoice, 'customer_pan', ''),
            'bill_to_pincode': invoice.billing_address.get('postal_code', '') if hasattr(invoice,
                                                                                         'billing_address') else '',

            # Ship To address fields
            'ship_to_address': invoice.shipping_address.get('address_line1') if invoice.shipping_address else None,
            'ship_to_state': invoice.shipping_address.get('state') if invoice.shipping_address else None,
            'ship_to_country': invoice.shipping_address.get('country') if invoice.shipping_address else None,
            'ship_to_pincode': invoice.shipping_address.get('postal_code') if invoice.shipping_address else None,

            # Item Details
            'item_details': [
                            {
                                'item': item.get('item', ''),
                                'note': item.get('note',''),
                                'hsn_sac': item.get('hsn_sac', ''),
                                'units': item.get('units', '-') if item.get('units') and item['units'] != 'NA' else '-',
                                'quantity': "{:,}".format(int(float(item.get('quantity', 0)))),
                                'rate': "{:,}".format(float(item.get('rate', 0))) if float(item.get('rate', 0)) % 1 else "{:,}".format(int(float(item.get('rate', 0)))),
                                'discount': "{:,}".format(float(item.get('discount', 0))) if float(item.get('discount', 0)) % 1 else "{:,}".format(int(float(item.get('discount', 0)))),
                                'amount': "{:,}".format(float(item.get('amount', 0))) if float(item.get('amount', 0)) % 1 else "{:,}".format(int(float(item.get('amount', 0)))),
                                'taxamount': "{:,}".format(float(item.get('taxamount', 0))) if float(item.get('taxamount', 0)) % 1 else "{:,}".format(int(float(item.get('taxamount', 0)))),
                                'tax': "{}%".format(int(float(item.get('tax', 0)))),  # Ensures percentage format
                                'total_amount': "{:,}".format(float(item.get('total_amount', 0))) if float(item.get('total_amount', 0)) % 1 else "{:,}".format(int(float(item.get('total_amount', 0))))
                            }
                            for item in getattr(invoice, 'item_details', [])
            ],
            'subtotal': "{:,}".format(round(float(getattr(invoice, 'subtotal_amount', 0)))),
            'shipping': f"{round(float(getattr(invoice, 'shipping_amount', 0)), 2):.2f}",
            'cgst_amt': f"{round(float(getattr(invoice, 'total_cgst_amount', 0)), 2):.2f}",
            'sgst_amt': f"{round(float(getattr(invoice, 'total_sgst_amount', 0)), 2):.2f}",
            'total': "{:,}".format(round(float(getattr(invoice, 'total_amount', 0)))),
            'total_in_words': total_in_words,
            'cgst': "{:,}".format(round(float(getattr(invoice, 'total_cgst_amount', 0)))),
            'sgst': "{:,}".format(round(float(getattr(invoice, 'total_sgst_amount', 0)))),
            'igst_amt': "{:,}".format(round(float(getattr(invoice, 'total_igst_amount', 0)))),
            'payment_status': getattr(invoice, 'payment_status', ''),
            'terms_and_conditions': getattr(invoice, 'terms_and_conditions', ''),
            'note': getattr(invoice, 'notes', ''),
            'account_name': business_name,
            'adjust_layout': adjust_layout
        }

        # Assuming you have a DocumentGenerator class that generates the PDF
        document_generator = DocumentGenerator(request, invoice, context)

        # Assuming `template_name` is the path to your HTML template
        template_name = "invoice.html"

        # Generate the PDF document
        pdf_response = document_generator.generate_document(template_name)

        # Return the PDF response
        return pdf_response

    except Invoice.DoesNotExist:
        return Response({'error': 'Invoicing profile not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def get_financial_year():
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month

    if current_month < 4:  # January, February, March
        financial_year = f"{current_year - 1}-{str(current_year)[-2:]}"
    else:  # April to December
        financial_year = f"{current_year}-{str(current_year + 1)[-2:]}"

    return financial_year


def calculate_revenue_last_month(invoicing_profile_id, financial_year, last_month):
    """
    Calculate the revenue for the last month, adjusting the financial year if necessary.
    """
    # Filter invoices for the last month with adjusted financial year and invoicing_profile_id
    invoices = Invoice.objects.filter(
        invoicing_profile_id=invoicing_profile_id,
        financial_year=financial_year,
        month=last_month
    )

    # Calculate the total revenue for the last month
    revenue_last_month = invoices.aggregate(total=Sum('total_amount'))['total'] or 0

    return revenue_last_month


# Calculate the total number of days in the financial year
def get_days_in_financial_year(financial_year):
    start_year = int(financial_year.split("-")[0])
    end_year = start_year + 1
    # Leap year check for both years
    days_in_start_year = 366 if isleap(start_year) else 365
    days_in_end_year = 366 if isleap(end_year) else 365
    # Financial year is always 365 or 366 days
    return 365 if days_in_start_year == 365 and days_in_end_year == 365 else 366


# Get the number of days in the current month
def get_days_in_current_month(current_year, current_month):
    return monthrange(current_year, current_month)[1]


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve invoice statistics for the given invoicing profile and financial year.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            "Invoice statistics retrieved successfully.",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'today_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'revenue_this_month': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'revenue_last_month': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'average_revenue_per_day': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'over_dues': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'due_today': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'due_within_30_days': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_recievables': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        400: openapi.Response("Invalid parameters or missing invoicing profile ID."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'invoicing_profile_id',
            openapi.IN_QUERY,
            description="The invoicing profile ID to filter the invoices.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'financial_year',
            openapi.IN_QUERY,
            description="The financial year for filtering invoices. "
                        "If not provided, the current financial year will be used.",
            type=openapi.TYPE_STRING,
            required=False
        ),
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invoice_stats(request):
    try:
        # Get the financial year
        invoicing_profile_id = request.query_params.get('invoicing_profile_id')
        financial_year = request.query_params.get('financial_year')
        if financial_year is None:
            financial_year = get_financial_year()

        # Filter invoices based on invoicing_profile_id and financial_year
        invoices = Invoice.objects.filter(invoicing_profile_id=invoicing_profile_id, financial_year=financial_year)

        # Calculate total revenue
        total_revenue = round(invoices.aggregate(total=Sum('total_amount'))['total'] or 0, 2)

        # Calculate today's revenue
        today_revenue = round(invoices.filter(invoice_date=datetime.today()).aggregate(total=Sum('total_amount'))['total'] or 0, 2)

        # Calculate revenue for this month
        current_month = datetime.today().month
        revenue_this_month = round(invoices.filter(month=current_month).aggregate(total=Sum('total_amount'))['total'] or 0, 2)

        # Calculate revenue for last month
        last_month = current_month - 1 if current_month > 1 else 12
        if current_month == 5:  # April, so last month is March
            start_year, end_year = map(int, financial_year.split('-'))
            financial_year = f"{start_year - 1}-{str(start_year)[-2:]}"

        # Calculate revenue for the last month
        revenue_last_month = round(calculate_revenue_last_month(invoicing_profile_id, financial_year, last_month), 2)

        # Calculate average revenue per day
        days_in_financial_year = get_days_in_financial_year(financial_year)
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Days in the current month
        days_in_current_month = get_days_in_current_month(current_year, current_month)

        # Average revenue per day based on total revenue
        average_revenue_per_day_on_total_revenue = round(total_revenue / days_in_financial_year, 2)

        # Average revenue per day for the current month
        average_revenue_per_day_on_current_month = round(revenue_this_month / days_in_current_month, 2)

        # Calculate overdues
        over_dues = round(Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
            due_date__lt=datetime.today().date()  # Filter invoices with due_date before today's date
        ).exclude(
            payment_status__in=["NA", "Paid", "Written Off", "Partially Written Off"]  # Exclude unwanted statuses
        ).aggregate(
            total_due=Sum('pending_amount')
        ).get('total_due') or 0, 2)

        # Calculate dues for today
        due_today = round(Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
            due_date=datetime.today()
        ).exclude(
            payment_status__in=["Paid", "Written Off", "Partially Written Off"]
        ).aggregate(
            total=Sum('pending_amount')
        )['total'] or 0, 2)

        # Calculate dues within the next 30 days
        due_within_30_days = round(Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
            invoice_date__lte=datetime.today().date() + timedelta(days=30),  # Invoices due within the next 30 days
        ).exclude(
            payment_status__in=["Paid", "Written Off", "Partially Written Off"]  # Exclude unwanted statuses
        ).aggregate(
            total=Sum('pending_amount')
        ).get('total') or 0, 2)

        # Calculate total receivables (excluding unwanted statuses)
        total_recievables = round(Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
        ).exclude(
            payment_status__in=["Paid", "Written Off", "Partially Written Off"]  # Exclude unwanted statuses
        ).aggregate(
            total=Sum('total_amount')
        ).get('total') or 0, 2)

        try:
            bad_debt = round(
                CustomerInvoiceReceipt.objects.filter(
                    invoice__invoicing_profile_id=invoicing_profile_id,
                    method="written off"
                ).aggregate(
                    total_wave_off_amount=Sum('amount')
                )['total_wave_off_amount'] or 0, 2
            )
            print(bad_debt)
        except Exception as e:
            print(f"Error occurred: {e}")


        # Prepare the response data
        response_data = {
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
            "revenue_this_month": revenue_this_month,
            "revenue_last_month": revenue_last_month,
            "average_revenue_per_day": average_revenue_per_day_on_total_revenue,
            "average_revenue_per_day_current_month": average_revenue_per_day_on_current_month,
            "over_dues": over_dues,
            "due_today": due_today,
            "due_within_30_days": due_within_30_days,
            "total_recievables": total_recievables,
            "bad_debt": bad_debt,
        }

        return Response(response_data)

    except Exception as e:
        # Return a response with the error message and status code 500 if something goes wrong
        error_message = str(e)
        return Response({"error": f"An error occurred: {error_message}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve invoices based on the provided invoicing profile and filter type.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            "Invoices retrieved successfully.",
            openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'invoice_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'invoice_number': openapi.Schema(type=openapi.TYPE_STRING),
                        'customer_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'pending_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'payment_status': openapi.Schema(type=openapi.TYPE_STRING),
                        'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    }
                )
            )
        ),
        400: openapi.Response("Invalid parameters or missing invoicing profile ID."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'invoicing_profile_id',
            openapi.IN_QUERY,
            description="The invoicing profile ID to filter the invoices.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'filter_type',
            openapi.IN_QUERY,
            description="The filter type for the invoices. Required to specify the filter criteria.",
            type=openapi.TYPE_STRING,
            required=True,
            enum=["total_revenue", "today_revenue", "revenue_this_month", "revenue_last_month",
                  "average_revenue_per_day", "over_dues", "due_today", "due_within_30_days",
                  "total_recievables", "bad_debt"]
        ),
        openapi.Parameter(
            'financial_year',
            openapi.IN_QUERY,
            description="The financial year for filtering invoices."
                        " If not provided, the current financial year will be used.",
            type=openapi.TYPE_STRING,
            required=False
        ),
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invoices(request):
    try:
        # Get the financial year
        invoicing_profile_id = request.query_params.get('invoicing_profile_id')
        filter_type = request.query_params.get('filter_type')
        financial_year = request.query_params.get('financial_year')

        if financial_year is None:
            financial_year = get_financial_year()

        # Base queryset for filtering invoices
        invoices = Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
            financial_year=financial_year
        )

        # Apply filter based on the filter_type
        if filter_type == "total_revenue":
            # No additional filtering, list all invoices
            filtered_invoices = invoices
        elif filter_type == "today_revenue":
            # Filter invoices for today's date
            filtered_invoices = invoices.filter(invoice_date=datetime.today().date())
        elif filter_type == "revenue_this_month":
            # Filter invoices for the current month
            filtered_invoices = invoices.filter(month=datetime.today().month)
            print(filtered_invoices)
        elif filter_type == "revenue_last_month":
            # Determine last month and filter invoices
            current_month = datetime.today().month
            last_month = (current_month - 1) if current_month > 1 else 12
            year_for_last_month = datetime.today().year if last_month != 12 else datetime.today().year - 1
            if current_month == 5:  # April, so last month is March
                start_year, end_year = map(int, financial_year.split('-'))
                financial_year = f"{start_year - 1}-{str(start_year)[-2:]}"
            filtered_invoices = Invoice.objects.filter(
                            invoicing_profile_id=invoicing_profile_id,
                            financial_year=financial_year,
                            month=last_month
                        )
        elif filter_type == "average_revenue_per_day":
            # No specific filtering; return all invoices (same as total_revenue)
            filtered_invoices = invoices
        elif filter_type == "over_dues":
            filtered_invoices = Invoice.objects.filter(
                            invoicing_profile_id=invoicing_profile_id,
                            payment_status="Pending",
                            due_date__lt=datetime.today().date()
                        )

        elif filter_type == "due_today":
            filtered_invoices = Invoice.objects.filter(
                invoicing_profile_id=invoicing_profile_id,
                payment_status="Pending",
                due_date=datetime.today()
            )
        elif filter_type == "due_within_30_days":
            filtered_invoices = Invoice.objects.filter(invoicing_profile_id=invoicing_profile_id,
                                                       payment_status="Pending",
                                                       invoice_date__lte=datetime.today().date() + timedelta(days=30))
        elif filter_type == "total_recievables":
            filtered_invoices = Invoice.objects.filter(
                invoicing_profile_id=invoicing_profile_id,
                payment_status="Pending"
            )
        elif filter_type == "bad_debt":
            filtered_invoices = Invoice.objects.filter(
                invoicing_profile_id=invoicing_profile_id,
                payment_status__in=['Written Off', 'Partially Written Off']
            )

        else:
            return Response({"error": "Invalid filter type."}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the invoice data
        # serialized_invoices = [
        #     {
        #         "id": invoice.id,
        #         "invoice_date": invoice.invoice_date,
        #         "invoice_number": invoice.invoice_number,
        #         "customer": invoice.customer,
        #         "total_amount": invoice.total_amount,
        #         "pending_amount": invoice.pending_amount,
        #         "payment_status": invoice.payment_status,
        #         "due_date": invoice.due_date,
        #     }
        #     for invoice in filtered_invoices
        # ]
        serialized_invoices = InvoiceDataSerializer(filtered_invoices, many=True).data
        return Response(serialized_invoices, status=status.HTTP_200_OK)


    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve an invoice by its ID.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            "Invoice retrieved successfully.",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer': openapi.Schema(type=openapi.TYPE_STRING),
                    # Add more fields here based on your serializer
                }
            )
        ),
        404: openapi.Response("Invoice not found.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
def get_invoice_by_id(request, id):
    try:
        invoice = Invoice.objects.get(id=id)
        serializer = InvoiceSerializerData(invoice)
        invoice_data = serializer.data

        # Add the address_check field to the response
        address_check = invoice.billing_address == invoice.shipping_address
        invoice_data['address_check'] = address_check

        return Response(invoice_data, status=status.HTTP_200_OK)
    except Invoice.DoesNotExist:
        return Response(
            {"error": "Invoice not found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def latest_invoice_id(request, invoicing_profile_id):
    try:
        # Fetch the invoicing profile
        invoicing_profile = get_object_or_404(InvoicingProfile, id=invoicing_profile_id)

        # Fetch the InvoiceFormat using gstin from the InvoicingProfile
        invoice_format = InvoiceFormat.objects.get(gstin=invoicing_profile.gstin,
                                                   invoicing_profile_id=invoicing_profile_id)

        # Get the current format version
        current_format_version = invoice_format.invoice_format.get("format_version")

        # Fetch the latest invoice for the given invoicing_profile_id and gstin
        latest_invoice = (
            Invoice.objects.filter(
                invoicing_profile_id=invoicing_profile_id,
                gstin=invoicing_profile.gstin
            )
            .order_by('-id')  # Sort by ID to get the latest
            .first()
        )

        # Initialize new_invoice_number
        new_invoice_number = None

        if latest_invoice:
            # Check if the format version matches
            if latest_invoice.format_version == current_format_version:
                # Split the invoice_number into prefix, number, and suffix
                parts = latest_invoice.invoice_number.split('-')
                if len(parts) == 3:
                    prefix, number, suffix = parts
                    new_number = int(number) + 1  # Increment the numeric part
                    new_invoice_number = f"{prefix}-{new_number:03d}-{suffix}"
                else:
                    return JsonResponse(
                        {"error": "Existing invoice format is invalid."},
                        status=400
                    )
            else:
                # Format version has changed, start with the new format
                prefix = invoice_format.invoice_format.get("prefix")
                starting_number = invoice_format.invoice_format.get("startingNumber", 1)
                suffix = invoice_format.invoice_format.get("suffix")
                starting_number = int(starting_number)
                new_invoice_number = f"{prefix}-{starting_number:03d}-{suffix}"
        else:
            # No previous invoices, start with the new format
            prefix = invoice_format.invoice_format.get("prefix")
            starting_number = invoice_format.invoice_format.get("startingNumber")
            suffix = invoice_format.invoice_format.get("suffix")

            # Ensure starting_number is an integer before formatting
            starting_number = int(starting_number)

            new_invoice_number = f"{prefix}-{starting_number:03d}-{suffix}"

        # Return the new invoice number along with the format version
        return JsonResponse({
            "latest_invoice_number": new_invoice_number,
            "format_version": current_format_version
        })

    except InvoiceFormat.DoesNotExist:
        return JsonResponse({
            "error": "No Invoice Format found for the provided GSTIN."
        }, status=404)

    except Exception as e:
        # Return error response if an exception occurs
        return JsonResponse({"error": str(e)}, status=500)

@swagger_auto_schema(
    method='get',  # Keeping GET method
    operation_description="Filter invoices based on provided filters.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            description="Filtered invoices retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'invoice_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoice ID"),
                    'invoice_date': openapi.Schema(type=openapi.TYPE_STRING, description="Invoice Date"),
                    'invoice_number': openapi.Schema(type=openapi.TYPE_STRING, description="Invoice Number"),
                    'customer': openapi.Schema(type=openapi.TYPE_STRING, description="Customer name or ID"),
                    'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Total Amount"),
                    'pending_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Pending Amount"),
                    'payment_status': openapi.Schema(type=openapi.TYPE_STRING, description="Payment Status"),
                    'due_date': openapi.Schema(type=openapi.TYPE_STRING, description="Due Date"),
                }
            )
        ),
        400: openapi.Response(description="Bad request - Missing or invalid data."),
        500: openapi.Response(description="Internal server error.")
    },
    manual_parameters=[
        openapi.Parameter('invoicing_profile_id', openapi.IN_QUERY, description="Invoicing profile ID", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('financial_year', openapi.IN_QUERY, description="Financial year", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('invoice_id', openapi.IN_QUERY, description="Invoice ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('payment_status', openapi.IN_QUERY, description="Payment status (e.g., Paid, Pending, Overdue)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('due_date', openapi.IN_QUERY, description="Due date of the invoice (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('invoice_date', openapi.IN_QUERY, description="Date of the invoice (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('invoice_number', openapi.IN_QUERY, description="Invoice number", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('customer', openapi.IN_QUERY, description="Customer name or ID", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('total_amount', openapi.IN_QUERY, description="Total amount", type=openapi.TYPE_NUMBER, required=False),
        openapi.Parameter('invoice_status', openapi.IN_QUERY, description="Invoice status", type=openapi.TYPE_NUMBER, required=False),
    ]
)
@api_view(['GET'])  # Keeping GET method
def filter_invoices(request):
    try:
        # Extract required parameters from query params
        invoicing_profile_id = request.query_params.get('invoicing_profile_id')
        financial_year = request.query_params.get('financial_year')

        # Validate the required parameters
        if not invoicing_profile_id or not financial_year:
            return Response(
                {"error": "invoicing_profile_id and financial_year are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize the base queryset
        invoices = Invoice.objects.filter(
            invoicing_profile_id=invoicing_profile_id,
            financial_year=financial_year
        )

        # Dynamically apply filters if they are passed as query params
        invoice_id = request.query_params.get('invoice_id')
        payment_status = request.query_params.get('payment_status')
        due_date = request.query_params.get('due_date')
        invoice_date = request.query_params.get('invoice_date')
        invoice_number = request.query_params.get('invoice_number')
        customer = request.query_params.get('customer')
        total_amount = request.query_params.get('total_amount')
        pending_amount = request.query_params.get('pending_amount')
        invoice_status = request.query_params.get('invoice_status')

        # Apply the filters based on the query parameters
        if invoice_id:
            invoices = invoices.filter(id=invoice_id)

        if payment_status:
            invoices = invoices.filter(payment_status=payment_status)

        if due_date:
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                invoices = invoices.filter(due_date=due_date)
            except ValueError:
                return Response({"error": "Invalid due_date format. Expected format: YYYY-MM-DD."},
                                 status=status.HTTP_400_BAD_REQUEST)

        if invoice_date:
            try:
                invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                invoices = invoices.filter(invoice_date=invoice_date)
            except ValueError:
                return Response({"error": "Invalid invoice_date format. Expected format: YYYY-MM-DD."},
                                 status=status.HTTP_400_BAD_REQUEST)

        if invoice_number:
            invoices = invoices.filter(invoice_number__icontains=invoice_number)

        if customer:
            invoices = invoices.filter(customer__icontains=customer)

        if total_amount:
            try:
                total_amount = float(total_amount)
                invoices = invoices.filter(total_amount=total_amount)
            except ValueError:
                return Response({"error": "Invalid total_amount. Expected a numeric value."},
                                 status=status.HTTP_400_BAD_REQUEST)

        if pending_amount:
            try:
                pending_amount = float(pending_amount)
                invoices = invoices.filter(pending_amount=pending_amount)
            except ValueError:
                return Response({"error": "Invalid pending_amount. Expected a numeric value."},
                                 status=status.HTTP_400_BAD_REQUEST)
        if invoice_status:
            invoices = invoices.filter(invoice_status=invoice_status)
        # Serialize the filtered invoice data
        serialized_invoices = InvoiceDataSerializer(invoices, many=True).data
        return Response(serialized_invoices, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new customer invoice receipt.",
    tags=["CustomerInvoiceReceipts"],
    request_body=CustomerInvoiceReceiptSerializer,
    responses={
        201: openapi.Response("Customer Invoice Receipt created successfully."),
        400: openapi.Response("Bad request."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer_invoice_receipt(request):
    """
    Create a new Customer Invoice Receipt with auto-incremented payment_number.
    """
    try:
        # Extract and validate invoice_id
        invoice_id = request.data.get("invoice")
        if not invoice_id:
            return Response(
                {"error": "Invoice ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Automatically determine the next payment_number for the given invoice
        max_payment_number = CustomerInvoiceReceipt.objects.filter(invoice_id=invoice_id).aggregate(
            max_number=models.Max('payment_number')
        )['max_number'] or 0
        next_payment_number = max_payment_number + 1
        request.data["payment_number"] = next_payment_number

        # Serialize and save the data
        serializer = CustomerInvoiceReceiptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error in create_customer_invoice_receipt: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve customer invoice receipts.",
    tags=["CustomerInvoiceReceipts"],
    responses={
        200: openapi.Response("Success"),
        404: openapi.Response("Not Found"),
    },
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_QUERY,
            description="Receipt ID (optional)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_invoice_receipts(request):
    """
    Retrieve a customer invoice receipt by ID or all receipts if no ID is provided.
    """
    try:
        receipt_id = request.query_params.get('id')
        if receipt_id:
            receipt = CustomerInvoiceReceipt.objects.get(id=receipt_id)
            serializer = CustomerInvoiceReceiptSerializer(receipt)
            return Response(serializer.data, status=status.HTTP_200_OK)

    except CustomerInvoiceReceipt.DoesNotExist:
        return Response(
            {"error": "Customer Invoice Receipt not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update a customer invoice receipt.",
    tags=["CustomerInvoiceReceipts"],
    request_body=CustomerInvoiceReceiptSerializer,
    responses={
        200: openapi.Response("Customer Invoice Receipt updated successfully."),
        404: openapi.Response("Not Found."),
        400: openapi.Response("Bad request."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer_invoice_receipt(request, receipt_id):
    """
    Update an existing customer invoice receipt.
    """
    try:
        receipt = CustomerInvoiceReceipt.objects.get(id=receipt_id)
        serializer = CustomerInvoiceReceiptSerializer(receipt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except CustomerInvoiceReceipt.DoesNotExist:
        return Response(
            {"error": "Customer Invoice Receipt not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a customer invoice receipt.",
    tags=["CustomerInvoiceReceipts"],
    responses={
        204: openapi.Response("Customer Invoice Receipt deleted successfully."),
        404: openapi.Response("Not Found."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer_invoice_receipt(request, receipt_id):
    """
    Delete a customer invoice receipt.
    """
    try:
        receipt = CustomerInvoiceReceipt.objects.get(id=receipt_id)
        receipt.delete()
        return Response({"message": "Customer Invoice Receipt deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except CustomerInvoiceReceipt.DoesNotExist:
        return Response(
            {"error": "Customer Invoice Receipt not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='put',
    operation_description="Mark an invoice as written off or partially written off.",
    tags=["Invoices"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "invoice_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="ID of the invoice to be written off"
            )
        },
        required=[]  # No request body fields are required as invoice_id comes from the URL
    ),
    responses={
        200: openapi.Response(
            "Wave-off processed successfully.",
            examples={
                "application/json": {
                    "message": "Wave-off processed successfully.",
                    "wave_off_receipt": {
                        "id": 6,
                        "date": "2025-01-10",
                        "amount": 600.0,
                        "method": "wave off",
                        "payment_number": 3
                    }
                }
            }
        ),
        404: openapi.Response(
            "Invoice not found.",
            examples={
                "application/json": {
                    "error": "Invoice not found."
                }
            }
        ),
        400: openapi.Response(
            "Bad request.",
            examples={
                "application/json": {
                    "error": "The invoice is already fully paid or written off."
                }
            }
        )
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
def wave_off_invoice(request, invoice_id):
    """
    Handle the wave-off action for an invoice.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        existing_receipts = invoice.customer_invoice_receipts.all()

        # Calculate the total paid amount from existing receipts
        total_paid = sum(receipt.amount for receipt in existing_receipts)

        # Calculate the pending amount
        pending_amount = invoice.total_amount - total_paid

        # Determine the amount to wave off
        if not existing_receipts:
            # No previous payments; full wave-off
            wave_off_amount = invoice.total_amount
            payment_number = 1
        else:
            # Partial wave-off of the pending amount
            wave_off_amount = pending_amount
            # Get the maximum payment number from existing receipts
            payment_number = existing_receipts.aggregate(max_payment_number=models.Max('payment_number'))[
                                 'max_payment_number'] or 0
            payment_number += 1

        if wave_off_amount <= 0:
            return Response({
                "error": "The invoice is already fully paid"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for validation
        data = {
            "invoice": invoice.id,  # Ensure you pass the foreign key as its ID
            "date": datetime.now().date(),
            "amount": wave_off_amount,
            "method": "written off",
            "reference_number": "",
            "payment_number": payment_number,
            "tax_deducted": "no_tax",
            "amount_withheld": 0,
            "comments": "No comments",
        }

        # Validate the data using the serializer
        serializer = CustomerInvoiceReceiptSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save the validated data
        wave_off_receipt = serializer.save()

        # Update invoice status and pending amount
        invoice.pending_amount = max(0, pending_amount - wave_off_amount)
        invoice.payment_status = "Written Off" if total_paid == 0 else "Partially Written Off"
        invoice.save()

        return Response({
            "message": "Wave-off processed successfully.",
            "wave_off_receipt": serializer.data
        }, status=status.HTTP_200_OK)

    except Invoice.DoesNotExist:
        return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def invoice_format_list(request):
    # GET Method - List all Invoice Formats
    if request.method == 'GET':
        invoice_profile_id = request.GET.get('invoice_profile_id')

        # Filter by invoice_profile_id if provided, else return all
        if invoice_profile_id:
            invoice_formats = InvoiceFormat.objects.filter(invoicing_profile=invoice_profile_id)
        else:
            invoice_formats = InvoiceFormat.objects.all()

        serializer = InvoiceFormatSerializer(invoice_formats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST Method - Create a new Invoice Format
    elif request.method == 'POST':
        serializer = InvoiceFormatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, Update, and Delete View
@api_view(['GET', 'PUT', 'DELETE'])
def invoice_format_detail(request, pk):
    invoice_format = get_object_or_404(InvoiceFormat, pk=pk)

    # GET Method - Retrieve a single Invoice Format
    if request.method == 'GET':
        serializer = InvoiceFormatSerializer(invoice_format)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT Method - Update an existing Invoice Format
    elif request.method == 'PUT':
        serializer = InvoiceFormatSerializer(invoice_format, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE Method - Delete an Invoice Format
    elif request.method == 'DELETE':
        invoice_format.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


