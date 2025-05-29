from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import HousePropertyIncomeDetails
from .serializers import HousePropertyIncomeDetailsSerializer
import json


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_house_property_details(request):
    service_request_id = request.data.get('service_request')
    id = request.data.get('id', None)
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data.copy()

    if 'property_address' in data and isinstance(data["property_address"], str):
        try:
            property_address = json.loads(data["property_address"])
        except json.JSONDecodeError:
            return Response({"error": "Invalid property_address format"}, status=status.HTTP_400_BAD_REQUEST)
    data["property_address"] = json.dumps(property_address)
    print(type(data['property_address']))  # Will show <class 'str'> if wrong
    try:
        instance = HousePropertyIncomeDetails.objects.get(pk=id, service_request_id=service_request_id)
        serializer = HousePropertyIncomeDetailsSerializer(instance, data=data, partial=True)
    except HousePropertyIncomeDetails.DoesNotExist:
        serializer = HousePropertyIncomeDetailsSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def house_property_details_view(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = HousePropertyIncomeDetails.objects.get(service_request_id=service_request_id)
    except HousePropertyIncomeDetails.DoesNotExist:
        return Response({"error": "No House Property Income Details found"}, status=status.HTTP_404_NOT_FOUND)

    data = HousePropertyIncomeDetailsSerializer(instance).data
    return Response(data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_house_property_file(request, file_type, service_request_id):
    try:
        instance = HousePropertyIncomeDetails.objects.get(service_request_id=service_request_id)
        file_field = None

        if file_type == 'municipal_tax_receipt':
            file_field = instance.municipal_tax_receipt
            instance.municipal_tax_receipt = None
        elif file_type == 'loan_statement':
            file_field = instance.loan_statement
            instance.loan_statement = None
        elif file_type == 'upload_loan_interest_certificate':
            file_field = instance.upload_loan_interest_certificate
            instance.upload_loan_interest_certificate = None
        else:
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)

        if file_field:
            file_field.storage.delete(file_field.name)
        instance.save()

        return Response({"message": f"{file_type} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except HousePropertyIncomeDetails.DoesNotExist:
        return Response({"error": "HousePropertyIncomeDetails not found"}, status=status.HTTP_404_NOT_FOUND)
