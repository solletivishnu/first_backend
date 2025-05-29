from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import FamilyPensionIncome, FamilyPensionIncomeInfo
from .serializers import *

# FamilyPensionIncome APIs

@api_view(['POST'])
def upsert_family_pension_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pension_income = FamilyPensionIncome.objects.get(service_request_id=service_request_id)
        serializer = FamilyPensionIncomeSerializer(pension_income, data=request.data, partial=True)
    except FamilyPensionIncome.DoesNotExist:
        serializer = FamilyPensionIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Family Pension Income saved successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_family_pension_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pension_income = FamilyPensionIncome.objects.get(service_request_id=service_request_id)
    except FamilyPensionIncome.DoesNotExist:
        return Response({"error": "No Family Pension Income found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    serializer = FamilyPensionIncomeSerializer(pension_income)
    return Response(serializer.data, status=status.HTTP_200_OK)


# FamilyPensionIncomeDocuments APIs

@api_view(['POST'])
def add_family_pension_income_document(request):
    serializer = FamilyPensionIncomeInfoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Family Pension Income Document added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_family_pension_income_document(request, document_id):
    try:
        document = FamilyPensionIncomeInfo.objects.get(pk=document_id)
    except FamilyPensionIncomeInfo.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = FamilyPensionIncomeInfoSerializer(document, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Family Pension Income Document updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_family_pension_income_document(request, document_id):
    try:
        document = FamilyPensionIncomeInfo.objects.get(pk=document_id)
        document.delete()
        return Response({"message": "Family Pension Income Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except FamilyPensionIncomeInfo.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_family_pension_income_documents(request):
    family_pension_id = request.query_params.get('family_pension_id')
    if not family_pension_id:
        return Response({"error": "Missing family_pension_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        documents = FamilyPensionIncomeInfo.objects.filter(family_pension_id=family_pension_id)
        serializer = FamilyPensionIncomeInfoSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except FamilyPensionIncomeInfo.DoesNotExist:
        return Response({"error": "No documents found for the given family_pension_id"}, status=status.HTTP_404_NOT_FOUND)
