from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db import transaction
from .models import BusinessProfessionalIncome, BusinessProfessionalIncomeDocument
from .serializers import *
import json


# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser, JSONParser])
# def upsert_business_professional_income_with_files(request):
#     request_data = request.data
#
#     # Coerce investment_types if sent as a string
#     opting_data = request_data.get('opting_data')
#     if isinstance(opting_data, str):
#         try:
#             request_data['opting_data'] = json.loads(opting_data)
#         except json.JSONDecodeError:
#             return Response({"opting_data": "Invalid JSON format"}, status=400)
#     service_request_id = request.data.get('service_request')
#     if not service_request_id:
#         return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         instance = BusinessProfessionalIncome.objects.get(service_request_id=service_request_id)
#         serializer = BusinessProfessionalIncomeSerializer(instance, data=request_data, partial=True)
#     except BusinessProfessionalIncome.DoesNotExist:
#         serializer = BusinessProfessionalIncomeSerializer(data=request_data)
#
#     if serializer.is_valid():
#         with transaction.atomic():
#             income_instance = serializer.save()
#
#             doc_map = {
#                 'form26as_files': '26AS',
#                 'ais_files': 'AIS',
#                 'gst_returns_files': 'GST Returns',
#                 'bank_statements_files': 'Bank Statements',
#                 'other_files': 'Other'
#             }
#
#             for field_name, doc_type in doc_map.items():
#                 files = request.FILES.getlist(field_name)
#                 for file in files:
#                     BusinessProfessionalIncomeDocument.objects.create(
#                         business_professional_income=income_instance,
#                         document_type=doc_type,
#                         file=file
#                     )
#
#             return Response({
#                 "message": "Business Professional Income details saved successfully"
#             }, status=status.HTTP_200_OK)
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_professional_income_upsert(request):
    request_data = request.data

    # Coerce investment_types if sent as a string
    opting_data = request_data.get('opting_data')
    if isinstance(opting_data, str):
        try:
            request_data['opting_data'] = json.loads(opting_data)
        except json.JSONDecodeError:
            return Response({"opting_data": "Invalid JSON format"}, status=400)

    # POST: Create new record (no check for existing)
    if request.method == 'POST':
        serializer = BusinessProfessionalIncomeSerializer(data=request_data)
        if serializer.is_valid():
            with transaction.atomic():
                income_instance = serializer.save()
                _handle_business_professional_income_files(request, income_instance)
            return Response({
                "message": "Business Professional Income created successfully",
                "id": income_instance.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT: Update existing record by id
    elif request.method == 'PUT':
        instance_id = request_data.get('id')
        if not instance_id:
            return Response({"error": "Missing id for update"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = BusinessProfessionalIncome.objects.get(id=instance_id)
        except BusinessProfessionalIncome.DoesNotExist:
            return Response({"error": "BusinessProfessionalIncome with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BusinessProfessionalIncomeSerializer(instance, data=request_data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                income_instance = serializer.save()
                _handle_business_professional_income_files(request, income_instance)
            return Response({
                "message": "Business Professional Income updated successfully",
                "id": income_instance.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _handle_business_professional_income_files(request, income_instance):
    doc_map = {
        'form26as_files': '26AS',
        'ais_files': 'AIS',
        'gst_returns_files': 'GST Returns',
        'bank_statements_files': 'Bank Statements',
        'other_files': 'Other'
    }
    for field_name, doc_type in doc_map.items():
        files = request.FILES.getlist(field_name)
        for file in files:
            BusinessProfessionalIncomeDocument.objects.create(
                business_professional_income=income_instance,
                document_type=doc_type,
                file=file
            )


@api_view(['GET'])
def get_business_professional_income(request, service_request_id):
    try:
        instance = BusinessProfessionalIncome.objects.filter(service_request__id=service_request_id)
        serializer = BusinessProfessionalIncomeSerializer(instance, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except BusinessProfessionalIncome.DoesNotExist:
        return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_business_professional_income(request, service_request_id):
    try:
        instance = BusinessProfessionalIncome.objects.get(service_request__id=service_request_id)
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)

    except BusinessProfessionalIncome.DoesNotExist:
        return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_business_professional_income_file(request, file_id):
    try:
        file = BusinessProfessionalIncomeDocument.objects.get(id=file_id)
        file.delete()
        return Response({"message": "File deleted"}, status=status.HTTP_200_OK)

    except BusinessProfessionalIncomeDocument.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
