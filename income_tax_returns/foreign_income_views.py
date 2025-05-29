from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ForeignIncome, ForeignIncomeInfo
from .serializers import ForeignIncomeSerializer, ForeignIncomeInfoSerializer

# ForeignIncome APIs

@api_view(['POST'])
def upsert_foreign_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        income = ForeignIncome.objects.get(service_request_id=service_request_id)
        serializer = ForeignIncomeSerializer(income, data=request.data, partial=True)
    except ForeignIncome.DoesNotExist:
        serializer = ForeignIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Foreign Income saved successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_foreign_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        income = ForeignIncome.objects.get(service_request_id=service_request_id)
    except ForeignIncome.DoesNotExist:
        return Response({"error": "No Foreign Income found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ForeignIncomeSerializer(income)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ForeignIncomeInfo (Documents) APIs

@api_view(['POST'])
def add_foreign_income_info(request):
    serializer = ForeignIncomeInfoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Foreign Income Info added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_foreign_income_info(request, document_id):
    try:
        document = ForeignIncomeInfo.objects.get(pk=document_id)
    except ForeignIncomeInfo.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ForeignIncomeInfoSerializer(document, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Foreign Income Info updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_foreign_income_info(request, document_id):
    try:
        document = ForeignIncomeInfo.objects.get(pk=document_id)
        document.delete()
        return Response({"message": "Foreign Income Info deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except ForeignIncomeInfo.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_foreign_income_info_list(request):
    foreign_income_id = request.query_params.get('foreign_income_id')
    if not foreign_income_id:
        return Response({"error": "Missing foreign_income_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        documents = ForeignIncomeInfo.objects.filter(foreign_income_id=foreign_income_id)
        serializer = ForeignIncomeInfoSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ForeignIncomeInfo.DoesNotExist:
        return Response({"error": "No documents found for the given foreign_income_id"}, status=status.HTTP_404_NOT_FOUND)
