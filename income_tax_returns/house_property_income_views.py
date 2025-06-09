from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import HousePropertyIncomeDetails, HousePropertyIncomeDetailsInfo
from .serializers import HousePropertyIncomeDetailsSerializer, HousePropertyIncomeDetailsInfoSerializer
import json

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


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_house_property_details(request):
    """
    Create both HousePropertyIncomeDetails and HousePropertyIncomeDetailsInfo in one API call
    """
    data = request.data.copy()
    service_request_id = request.data.get('service_request')
    try:
        main_details_data = {
            'service_request': request.data.get('service_request'),
            'service_task': request.data.get('service_task'),
            'status': request.data.get('status'),
            'assignee': request.data.get('assignee'),
            'reviewer': request.data.get('reviewer')
        }
        data.pop('service_request', None)
        data.pop('service_task', None)
        data.pop('status', None)
        data.pop('assignee', None)
        data.pop('reviewer', None)

        try:
            instance = HousePropertyIncomeDetails.objects.get(service_request_id=service_request_id)
            main_serializer = HousePropertyIncomeDetailsSerializer(instance, data=main_details_data, partial=True)
        except HousePropertyIncomeDetails.DoesNotExist:
            main_serializer = HousePropertyIncomeDetailsSerializer(data=main_details_data)
        if not main_serializer.is_valid():
            return Response(main_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        main_instance = main_serializer.save()

        id = request.data.get('id', None)
        if 'property_address' in data and isinstance(data["property_address"], str):
            try:
                property_address = json.loads(data["property_address"])
            except json.JSONDecodeError:
                return Response({"error": "Invalid property_address format"}, status=status.HTTP_400_BAD_REQUEST)
            data["property_address"] = json.dumps(property_address)
        if data:
            data['house_property_details'] = main_instance.id
            if id:
                try:
                    info_instance = HousePropertyIncomeDetailsInfo.objects.get(pk=id, house_property_details=main_instance)
                    info_serializer = HousePropertyIncomeDetailsInfoSerializer(info_instance, data=data, partial=True)
                except HousePropertyIncomeDetailsInfo.DoesNotExist:
                    info_serializer = HousePropertyIncomeDetailsInfoSerializer(data=data)
            else:
                info_serializer = HousePropertyIncomeDetailsInfoSerializer(data=data)

            if not info_serializer.is_valid():
                main_instance.delete()
                return Response(info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            info_serializer.save()

        return Response({
            'data': main_serializer.data,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def delete_house_property(request, pk):
    """
        Delete the House Property
    """
    try:
        instance = HousePropertyIncomeDetailsInfo.objects.get(pk=pk)
        instance.delete()
        return Response({'message': "Property Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
    except HousePropertyIncomeDetailsInfo.DoesNotExist:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
