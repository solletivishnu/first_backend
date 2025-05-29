from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import WinningIncome, WinningIncomeDocument
from .serializers import WinningIncomeSerializer, WinningIncomeDocumentSerializer


# WinningIncome APIs

@api_view(['POST'])
def upsert_winning_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        winning_income = WinningIncome.objects.get(service_request_id=service_request_id)
        serializer = WinningIncomeSerializer(winning_income, data=request.data, partial=True)
    except WinningIncome.DoesNotExist:
        serializer = WinningIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Winning Income saved successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_winning_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        winning_income = WinningIncome.objects.get(service_request_id=service_request_id)
    except WinningIncome.DoesNotExist:
        return Response({"error": "No Winning Income found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    serializer = WinningIncomeSerializer(winning_income)
    return Response(serializer.data, status=status.HTTP_200_OK)


# WinningIncomeDocument APIs

@api_view(['POST'])
def add_winning_income_document(request):
    serializer = WinningIncomeDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Winning Income Document added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_winning_income_document(request, document_id):
    try:
        document = WinningIncomeDocument.objects.get(pk=document_id)
    except WinningIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = WinningIncomeDocumentSerializer(document, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Winning Income Document updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_winning_income_document(request, document_id):
    try:
        document = WinningIncomeDocument.objects.get(pk=document_id)
        document.delete()
        return Response({"message": "Winning Income Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except WinningIncomeDocument.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_winning_income_documents(request):
    winning_income_id = request.query_params.get('winning_income_id')
    if not winning_income_id:
        return Response({"error": "Missing winning_income_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        documents = WinningIncomeDocument.objects.filter(winning_income_id=winning_income_id)
        serializer = WinningIncomeDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except WinningIncomeDocument.DoesNotExist:
        return Response({"error": "No documents found for the given winning_income_id"}, status=status.HTTP_404_NOT_FOUND)