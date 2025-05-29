from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def other_income_details_list(request):
    if request.method == 'GET':
        records = OtherIncomeDetails.objects.all()
        serializer = OtherIncomeDetailsSerializer(records, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OtherIncomeDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def other_income_details_detail(request, pk):
    try:
        record = OtherIncomeDetails.objects.get(pk=pk)
    except OtherIncomeDetails.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OtherIncomeDetailsSerializer(record)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OtherIncomeDetailsSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def other_income_details_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        records = OtherIncomeDetails.objects.filter(service_request_id=service_request_id)
        serializer = OtherIncomeDetailsSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except OtherIncomeDetails.DoesNotExist:
        return Response({"error": "No records found for the given service request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def add_other_income_document(request, pk=None):
    """
    - POST: Create a new OtherIncomeDetailFile
    - PUT: Update an existing OtherIncomeDetailFile by pk
    - DELETE: Delete an OtherIncomeDetailFile by pk
    """
    if request.method == 'POST':
        serializer = OtherIncomeDetailFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        document = OtherIncomeDetailsData.objects.get(pk=pk)
    except OtherIncomeDetailsData.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = OtherIncomeDetailFileSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        document.delete()
        return Response({"detail": "Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
