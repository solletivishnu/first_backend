from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.db import transaction



@api_view(['POST'])
@parser_classes([JSONParser])
def upsert_interest_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = InterestIncome.objects.get(service_request_id=service_request_id)
        serializer = InterestIncomeSerializer(instance, data=request.data, partial=True)
    except InterestIncome.DoesNotExist:
        serializer = InterestIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Interest income saved"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_interest_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = InterestIncome.objects.get(service_request_id=service_request_id)
        serializer = InterestIncomeSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except InterestIncome.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_interest_income_document(request):
    serializer = InterestIncomeDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Document added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_interest_income_document(request, document_id):
    try:
        doc = InterestIncomeDocument.objects.get(pk=document_id)
        if doc.file:
            doc.file.storage.delete(doc.file.name)  # delete from S3
        doc.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except InterestIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_interest_income_document(request, document_id):
    try:
        doc = InterestIncomeDocument.objects.get(pk=document_id)
        serializer = InterestIncomeDocumentSerializer(doc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Document updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except InterestIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_interest_income_documents(request):
    try:
        interest_income_id = request.query_params.get('interest_income_id')
        if not interest_income_id:
            return Response({"error": "Missing interest_income_id"}, status=status.HTTP_400_BAD_REQUEST)
        documents = InterestIncomeDocument.objects.filter(interest_income_id=interest_income_id)
        serializer = InterestIncomeDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except InterestIncomeDocument.DoesNotExist:
        return Response({"error": "No documents found"}, status=status.HTTP_404_NOT_FOUND)
