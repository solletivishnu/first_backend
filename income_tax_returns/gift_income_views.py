from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import GiftIncomeDetails, GiftIncomeDocument
from .serializers import GiftIncomeDetailsSerializer, GiftIncomeDocumentSerializer

# --- GiftIncomeDetails APIs ---


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_gift_income_details(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gift_income = GiftIncomeDetails.objects.get(service_request_id=service_request_id)
        serializer = GiftIncomeDetailsSerializer(gift_income, data=request.data, partial=True)
    except GiftIncomeDetails.DoesNotExist:
        serializer = GiftIncomeDetailsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Gift Income Details saved successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_gift_income_details(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gift_income = GiftIncomeDetails.objects.get(service_request_id=service_request_id)
    except GiftIncomeDetails.DoesNotExist:
        return Response({"error": "No GiftIncomeDetails found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    serializer = GiftIncomeDetailsSerializer(gift_income)
    return Response(serializer.data, status=status.HTTP_200_OK)


# --- GiftIncomeDocument APIs ---

@api_view(['POST'])
def add_gift_income_document(request):
    serializer = GiftIncomeDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Gift Income Document added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_gift_income_document(request, document_id):
    try:
        document = GiftIncomeDocument.objects.get(pk=document_id)
    except GiftIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = GiftIncomeDocumentSerializer(document, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Gift Income Document updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_gift_income_document(request, document_id):
    try:
        document = GiftIncomeDocument.objects.get(pk=document_id)
        document.delete()
        return Response({"message": "Gift Income Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except GiftIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_gift_income_documents(request):
    gift_income_id = request.query_params.get('gift_income')
    if not gift_income_id:
        return Response({"error": "Missing gift_income"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        documents = GiftIncomeDocument.objects.filter(gift_income_id=gift_income_id)
        serializer = GiftIncomeDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except GiftIncomeDocument.DoesNotExist:
        return Response({"error": "No documents found for the given gift income"}, status=status.HTTP_404_NOT_FOUND)

