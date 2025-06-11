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


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_professional_income_upsert(request):
    FILE_KEYS = {
        'form26as_files': '26AS',
        'ais_files': 'AIS',
        'gst_returns_files': 'GST Returns',
        'bank_statements_files': 'Bank Statements',
        'other_files': 'Other',
        'profit_loss_statement_files': 'Profit & Loss Statement',
        'balance_sheet_files': 'Balance Sheet',
    }

    # If any file key is in request.FILES, make a mutable copy
    if any(key in request.FILES for key in FILE_KEYS):
        request_data = request.data
    else:
        request_data = request.data.copy()

    # Coerce investment_types if sent as a string
    opting_data = request_data.get('opting_data')
    if isinstance(opting_data, str):
        try:
            request_data['opting_data'] = json.dumps(json.loads(opting_data))
        except json.JSONDecodeError:
            return Response({"opting_data": "Invalid JSON format"}, status=400)
    main_details_data = {
        'service_request': request.data.get('service_request'),
        'service_task': request.data.get('service_task'),
        'status': request.data.get('status'),
        'assignee': request.data.get('assignee'),
        'reviewer': request.data.get('reviewer')
    }
    request_data.pop('service_request', None)
    request_data.pop('service_task', None)
    request_data.pop('status', None)
    request_data.pop('assignee', None)
    request_data.pop('reviewer', None)
    try:
        instance = BusinessProfessionalIncome.objects.get(service_request_id=main_details_data['service_request'])
        serializer = BusinessProfessionalIncomeSerializer(instance, data=main_details_data, partial=True)
    except BusinessProfessionalIncome.DoesNotExist:
        serializer = BusinessProfessionalIncomeSerializer(data=main_details_data)
    if serializer.is_valid():
        with transaction.atomic():
            income_instance = serializer.save()
            if request_data:
                id = request_data.get('id', None)
                request_data['business_professional_income'] = income_instance.id
                if id:
                    try:
                        info_instance = BusinessProfessionalIncomeInfo.objects.get(pk=id)
                        info_serializer = BusinessProfessionalIncomeInfoSerializer(info_instance, data=request_data, partial=True)
                    except BusinessProfessionalIncome.DoesNotExist:
                        info_serializer = BusinessProfessionalIncomeInfoSerializer(data=request_data)
                else:
                    info_serializer = BusinessProfessionalIncomeInfoSerializer(data=request_data)
                if not info_serializer.is_valid():
                    income_instance.delete()
                    return Response(info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                info_instances = info_serializer.save()
                _handle_business_professional_income_files(request, info_instances)
        return Response({
            "message": "Business Professional Income created successfully",
            "id": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # PUT: Update existing record by id
    # elif request.method == 'PUT':
    #     instance_id = request_data.get('id')
    #     if not instance_id:
    #         return Response({"error": "Missing id for update"}, status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         instance = BusinessProfessionalIncome.objects.get(id=instance_id)
    #     except BusinessProfessionalIncome.DoesNotExist:
    #         return Response({"error": "BusinessProfessionalIncome with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #
    #     serializer = BusinessProfessionalIncomeSerializer(instance, data=request_data, partial=True)
    #     if serializer.is_valid():
    #         with transaction.atomic():
    #             income_instance = serializer.save()
    #             _handle_business_professional_income_files(request, income_instance)
    #         return Response({
    #             "message": "Business Professional Income updated successfully",
    #             "id": income_instance.id
    #         }, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _handle_business_professional_income_files(request, income_instance):
    doc_map = {
        'form26as_files': '26AS',
        'ais_files': 'AIS',
        'gst_returns_files': 'GST Returns',
        'bank_statements_files': 'Bank Statements',
        'other_files': 'Other',
        'profit_loss_statement_files': 'Profit & Loss Statement',
        'balance_sheet_files': 'Balance Sheet',
    }
    for field_name, doc_type in doc_map.items():
        files = request.FILES.getlist(field_name)
        for file in files:
            BusinessProfessionalIncomeDocument.objects.create(
                business_professional_income_info=income_instance,
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
def delete_business_professional_income(request, pk):
    try:
        instance = BusinessProfessionalIncomeInfo.objects.get(pk=pk)
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)

    except BusinessProfessionalIncomeInfo.DoesNotExist:
        return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_business_professional_income_file(request, file_id):
    try:
        file = BusinessProfessionalIncomeDocument.objects.get(id=file_id)
        file.delete()
        return Response({"message": "Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

    except BusinessProfessionalIncomeDocument.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
