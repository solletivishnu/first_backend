from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *


# DividendIncome Upsert (POST: create or update)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_dividend_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        dividend_income = DividendIncome.objects.get(service_request_id=service_request_id)
        serializer = DividendIncomeSerializer(dividend_income, data=request.data, partial=True)
    except DividendIncome.DoesNotExist:
        serializer = DividendIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DividendIncome GET by service_request
@api_view(['GET'])
def get_dividend_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        dividend_income = DividendIncome.objects.get(service_request_id=service_request_id)
        serializer = DividendIncomeSerializer(dividend_income)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DividendIncome.DoesNotExist:
        return Response({"error": "DividendIncome not found"}, status=status.HTTP_404_NOT_FOUND)


# Add DividendIncomeDocument (POST)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def add_dividend_income_document(request):
    serializer = DividendIncomeDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Dividend Income Document added successfully', 'data':serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update DividendIncomeDocument (PUT)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_dividend_income_document(request, document_id):
    try:
        document = DividendIncomeDocument.objects.get(pk=document_id)
    except DividendIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DividendIncomeDocumentSerializer(document, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Dividend Income Document updated successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete DividendIncomeDocument (DELETE)
@api_view(['DELETE'])
def delete_dividend_income_document(request, document_id):
    try:
        document = DividendIncomeDocument.objects.get(pk=document_id)
        # Delete file from storage if present
        if document.file:
            document.file.delete(save=False)
        document.delete()
        return Response({"message": "Dividend Income Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except DividendIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_dividend_income_documents(request):
    try:
        dividend_income_id = request.query_params.get('dividend_income_id')
        if not dividend_income_id:
            return Response({"error": "Missing dividend_income_id"}, status=status.HTTP_400_BAD_REQUEST)
        documents = DividendIncomeDocument.objects.filter(dividend_income_id=dividend_income_id)
        serializer = DividendIncomeDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DividendIncomeDocument.DoesNotExist:
        return Response({"error": "No documents found for the given dividend income"}, status=status.HTTP_404_NOT_FOUND)


