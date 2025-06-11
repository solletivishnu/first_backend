from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
import json


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_list(request):
    if request.method == 'GET':
        business_identity = BusinessIdentity.objects.all()
        serializer = BusinessIdentitySerializer(business_identity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = BusinessIdentitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_detail(request, pk):
    try:
        business_identity = BusinessIdentity.objects.get(pk=pk)
    except BusinessIdentity.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessIdentitySerializer(business_identity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BusinessIdentitySerializer(business_identity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated business_pan file if it exists
        if business_identity.business_pan:
            business_identity.business_pan.storage.delete(business_identity.business_pan.name)
        business_identity.delete()
        return Response({"message": "Business Identity deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_business_identity_file(request):
    """
    DELETE: Business Identity file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        business_identity = BusinessIdentity.objects.get(pk=pk)
    except BusinessIdentity.DoesNotExist:
        return Response({"error": "Business Identity not found"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'business_pan':
        if business_identity.business_pan:
            business_identity.business_pan.storage.delete(business_identity.business_pan.name)
            business_identity.business_pan = None
            business_identity.save()
            return Response({"message": "Business PAN file deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Business PAN file does not exist"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_identity(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = BusinessIdentity.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessIdentity.objects.get(service_task_id=service_task_id)
    except BusinessIdentity.DoesNotExist:
        return Response({"error": "Business Identity not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessIdentitySerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def applicant_detail_list(request):
    if request.method == 'GET':
        applicant_details = ApplicantDetails.objects.all()
        serializer = ApplicantDetailsSerializer(applicant_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ApplicantDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def applicant_detail(request, pk):
    try:
        applicant_details = ApplicantDetails.objects.get(pk=pk)
    except ApplicantDetails.DoesNotExist:
        return Response({"error": "Applicant Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ApplicantDetailsSerializer(applicant_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ApplicantDetailsSerializer(applicant_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated files if they exist
        if applicant_details.aadhaar_image:
            applicant_details.aadhaar_image.storage.delete(applicant_details.aadhaar_image.name)
        if applicant_details.pan_image:
            applicant_details.pan_image.storage.delete(applicant_details.pan_image.name)
        if applicant_details.passport_photo:
            applicant_details.passport_photo.storage.delete(applicant_details.passport_photo.name)
        applicant_details.delete()
        return Response({"message": "Applicant Details deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_applicant_detail_file(request):
    """
    DELETE: Applicant Details file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        applicant_details = ApplicantDetails.objects.get(pk=pk)
    except ApplicantDetails.DoesNotExist:
        return Response({"error": "Applicant Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if file_type == 'aadhaar_image':
        if applicant_details.aadhaar_image:
            applicant_details.aadhaar_image.storage.delete(applicant_details.aadhaar_image.name)
            applicant_details.aadhaar_image = None
            applicant_details.save()
            return Response({"message": "Aadhaar Image deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Aadhaar Image does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'pan_image':
        if applicant_details.pan_image:
            applicant_details.pan_image.storage.delete(applicant_details.pan_image.name)
            applicant_details.pan_image = None
            applicant_details.save()
            return Response({"message": "PAN Image deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "PAN Image does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'passport_photo':
        if applicant_details.passport_photo:
            applicant_details.passport_photo.storage.delete(applicant_details.passport_photo.name)
            applicant_details.passport_photo = None
            applicant_details.save()
            return Response({"message": "Passport Photo deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Passport Photo does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_applicant_detail(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = ApplicantDetails.objects.get(service_request_id=service_request_id)
        else:
            instance = ApplicantDetails.objects.get(service_task_id=service_task_id)
    except ApplicantDetails.DoesNotExist:
        return Response({"error": "Applicant Details not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicantDetailsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_detail_list(request):
    if request.method == 'GET':
        signatory_details = SignatoryDetails.objects.all()
        serializer = SignatoryDetailsSerializer(signatory_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        service_request = data.get('service_request')
        try:
            instance = SignatoryDetails.objects.get(service_request_id=service_request)
            serializer = SignatoryDetailsSerializer(instance, data=data, partial=True)
        except SignatoryDetails.DoesNotExist:
            serializer = SignatoryDetailsSerializer(data=data)
        if serializer.is_valid():
            main_data = serializer.save()
            if data.get('name'):
                try:
                    data['signatory_details'] = main_data.id
                    serializer_info = SignatoryInfoSerializer(data=data)
                    if not serializer_info.is_valid():
                        return Response(serializer_info.errors, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        serializer_info.save()
                    except Exception as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    main_data.delete()
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Status Updated Successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_detail(request, pk):
    try:
        signatory_details = SignatoryInfo.objects.get(pk=pk)
    except SignatoryInfo.DoesNotExist:
        return Response({"error": "Promoter or Directors Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignatoryInfoSerializer(signatory_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SignatoryInfoSerializer(signatory_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated files if they exist
        if signatory_details.aadhar_image:
            signatory_details.aadhar_image.storage.delete(signatory_details.aadhar_image.name)
        if signatory_details.pan_image:
            signatory_details.pan_image.storage.delete(signatory_details.pan_image.name)
        if signatory_details.passport_photo:
            signatory_details.passport_photo.storage.delete(signatory_details.passport_photo.name)

        signatory_details.delete()
        return Response({"message": "Promoter or Directors Details deleted successfully"},
                        status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_signatory_detail_file(request):
    """
    DELETE: Signatory Details file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        signatory_details = SignatoryInfo.objects.get(pk=pk)
    except SignatoryInfo.DoesNotExist:
        return Response({"error": "Signatory Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if file_type == 'aadhar_image':
        if signatory_details.aadhar_image:
            signatory_details.aadhar_image.storage.delete(signatory_details.aadhar_image.name)
            signatory_details.aadhar_image = None
            signatory_details.save()
            return Response({"message": "Aadhaar Image deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Aadhaar Image does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'pan_image':
        if signatory_details.pan_image:
            signatory_details.pan_image.storage.delete(signatory_details.pan_image.name)
            signatory_details.pan_image = None
            signatory_details.save()
            return Response({"message": "PAN Image deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "PAN Image does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'passport_photo':
        if signatory_details.passport_photo:
            signatory_details.passport_photo.storage.delete(signatory_details.passport_photo.name)
            signatory_details.passport_photo = None
            signatory_details.save()
            return Response({"message": "Passport Photo deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Passport Photo does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_signatory_detail(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = SignatoryDetails.objects.get(service_request_id=service_request_id)
        else:
            instance = SignatoryDetails.objects.get(service_task_id=service_task_id)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "Signatory Details not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SignatoryDetailsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_list(request):
    if request.method == 'GET':
        business_location = BusinessLocation.objects.all()
        serializer = BusinessLocationSerializer(business_location, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()

        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])
                data['address'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)


        serializer = BusinessLocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_detail(request, pk):
    try:
        business_location = BusinessLocation.objects.get(pk=pk)
    except BusinessLocation.DoesNotExist:
        return Response({"error": "Business Location not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessLocationSerializer(business_location)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data.copy()

        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])
                data['address'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BusinessLocationSerializer(business_location, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            if business_location.address_proof:
                business_location.address_proof.storage.delete(business_location.address_proof.name)
            if business_location.rental_agreement:
                business_location.rental_agreement.storage.delete(business_location.rental_agreement.name)
            if business_location.bank_statement:
                business_location.bank_statement.storage.delete(business_location.bank_statement.name)
            business_location.delete()
            return Response({"message": "Business Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_business_location_file(request):
    """
    DELETE: Business Location file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        business_location = BusinessLocation.objects.get(pk=pk)
    except BusinessLocation.DoesNotExist:
        return Response({"error": "Business Location not found"}, status=status.HTTP_404_NOT_FOUND)

    if file_type == 'address_proof':
        if business_location.address_proof:
            business_location.address_proof.storage.delete(business_location.address_proof.name)
            business_location.address_proof = None
            business_location.save()
            return Response({"message": "Address Proof deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Address Proof does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'rental_agreement':
        if business_location.rental_agreement:
            business_location.rental_agreement.storage.delete(business_location.rental_agreement.name)
            business_location.rental_agreement = None
            business_location.save()
            return Response({"message": "Rental Agreement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Rental Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'bank_statement':
        if business_location.bank_statement:
            business_location.bank_statement.storage.delete(business_location.bank_statement.name)
            business_location.bank_statement = None
            business_location.save()
            return Response({"message": "Bank Statement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Bank Statement does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_location(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = BusinessLocation.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessLocation.objects.get(service_task_id=service_task_id)
    except BusinessLocation.DoesNotExist:
        return Response({"error": "Business Location not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessLocationSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_address_detail_list(request):
    if request.method == 'GET':
        additional_address_details = AdditionalSpaceBusiness.objects.all()
        serializer = AdditionalSpaceBusinessSerializer(additional_address_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()

        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])
                data['address'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdditionalSpaceBusinessSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_address_detail(request, pk):
    if request.method == 'GET':
        try:
            additional_address_details = AdditionalSpaceBusiness.objects.get(business_locations=pk)
        except AdditionalSpaceBusiness.DoesNotExist:
            return Response({"error": "Additional Address Details not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdditionalSpaceBusinessSerializer(additional_address_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        try:
            additional_address_details = AdditionalSpaceBusiness.objects.get(pk=pk)
        except AdditionalSpaceBusiness.DoesNotExist:
            return Response({"error": "Additional Address Details not found"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()

        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])
                data['address'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdditionalSpaceBusinessSerializer(additional_address_details, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            additional_address_details = AdditionalSpaceBusiness.objects.get(pk=pk)
        except AdditionalSpaceBusiness.DoesNotExist:
            return Response({"error": "Additional Address Details not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if additional_address_details.address_proof:
                additional_address_details.address_proof.storage.delete(additional_address_details.address_proof.name)
            if additional_address_details.rental_agreement:
                additional_address_details.rental_agreement.storage.delete(additional_address_details.rental_agreement.name)
            additional_address_details.delete()
            return Response({"message": "Additional Address Details deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_additional_address_file(request):
    """
    DELETE: Additional Address file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        additional_address_details = AdditionalSpaceBusiness.objects.get(pk=pk)
    except AdditionalSpaceBusiness.DoesNotExist:
        return Response({"error": "Additional Address Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if file_type == 'address_proof':
        if additional_address_details.address_proof:
            additional_address_details.address_proof.storage.delete(additional_address_details.address_proof.name)
            additional_address_details.address_proof = None
            additional_address_details.save()
            return Response({"message": "Address Proof deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Address Proof does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'rental_agreement':
        if additional_address_details.rental_agreement:
            additional_address_details.rental_agreement.storage.delete(additional_address_details.rental_agreement.name)
            additional_address_details.rental_agreement = None
            additional_address_details.save()
            return Response({"message": "Rental Agreement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Rental Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def trade_license_list(request):
    if request.method == 'GET':
        trade_license = TradeLicenseDetails.objects.all()
        serializer = TradeLicenseDetailsSerializer(trade_license, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TradeLicenseDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def trade_license_detail(request, pk):
    if request.method == 'GET':
        try:
            trade_license = TradeLicenseDetails.objects.get(service_request=pk)
        except TradeLicenseDetails.DoesNotExist:
            return Response({"error": "Trade License not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TradeLicenseDetailsSerializer(trade_license)
        return Response(serializer.data)

    elif request.method == 'PUT':
        try:
            trade_license = TradeLicenseDetails.objects.get(pk=pk)
        except TradeLicenseDetails.DoesNotExist:
            return Response({"error": "Trade License not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TradeLicenseDetailsSerializer(trade_license, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            trade_license = TradeLicenseDetails.objects.get(pk=pk)
        except TradeLicenseDetails.DoesNotExist:
            return Response({"error": "Trade License not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if trade_license.trade_license_file:
                trade_license.trade_license_file.storage.delete(trade_license.trade_license_file.name)
            trade_license.delete()
            return Response({"message": "Trade License deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_trade_license_file(request):
    """
    DELETE: Trade License file deletion
    """
    pk = request.query_params.get('pk')
    if not pk:
        return Response({"error": "Missing 'pk' query parameter"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        trade_license = TradeLicenseDetails.objects.get(pk=pk)
    except TradeLicenseDetails.DoesNotExist:
        return Response({"error": "Trade License not found"}, status=status.HTTP_404_NOT_FOUND)

    if trade_license.trade_license_file:
        trade_license.trade_license_file.storage.delete(trade_license.trade_license_file.name)
        trade_license.trade_license_file = None
        trade_license.save()
        return Response({"message": "Trade License file deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({"error": "Trade License file does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_trade_license(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = TradeLicenseDetails.objects.get(service_request_id=service_request_id)
        else:
            instance = TradeLicenseDetails.objects.get(service_task_id=service_task_id)
    except TradeLicenseDetails.DoesNotExist:
        return Response({"error": "Trade License not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TradeLicenseDetailsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_document_detail_list(request):
    if request.method == 'GET':
        business_document = BusinessDocumentDetails.objects.all()
        serializer = BusinessDocumentDetailsSerializer(business_document, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BusinessDocumentDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_document_detail(request, pk):
    if request.method == 'GET':
        try:
            business_document = BusinessDocumentDetails.objects.get(service_request=pk)
        except BusinessDocumentDetails.DoesNotExist:
            return Response({"error": "Business Document Details not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessDocumentDetailsSerializer(business_document)
        return Response(serializer.data)

    elif request.method == 'PUT':
        try:
            business_document = BusinessDocumentDetails.objects.get(pk=pk)
        except BusinessDocumentDetails.DoesNotExist:
            return Response({"error": "Business Document Details not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessDocumentDetailsSerializer(business_document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            business_document = BusinessDocumentDetails.objects.get(pk=pk)
        except BusinessDocumentDetails.DoesNotExist:
            return Response({"error": "Business Document Details not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if business_document.incorporation_certificate:
                business_document.incorporation_certificate.storage.delete(business_document.incorporation_certificate.name)
            if business_document.photo_of_premises:
                business_document.photo_of_premises.storage.delete(business_document.photo_of_premises.name)
            if business_document.property_tax_receipt:
                business_document.property_tax_receipt.storage.delete(business_document.property_tax_receipt.name)
            if business_document.rental_agreement:
                business_document.rental_agreement.storage.delete(business_document.rental_agreement.name)
            business_document.delete()
            return Response({"message": "Business Document Details deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_business_document_file(request):
    """
    DELETE: Business Document file deletion
    """
    pk = request.query_params.get('pk')
    file_type = request.query_params.get('file_type')
    if not pk or not file_type:
        return Response({"error": "Missing 'pk' or 'file_type' query parameters"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        business_document = BusinessDocumentDetails.objects.get(pk=pk)
    except BusinessDocumentDetails.DoesNotExist:
        return Response({"error": "Business Document Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if file_type == 'incorporation_certificate':
        if business_document.incorporation_certificate:
            business_document.incorporation_certificate.storage.delete(business_document.incorporation_certificate.name)
            business_document.incorporation_certificate = None
            business_document.save()
            return Response({"message": "Incorporation Certificate deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Incorporation Certificate does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'photo_of_premises':
        if business_document.photo_of_premises:
            business_document.photo_of_premises.storage.delete(business_document.photo_of_premises.name)
            business_document.photo_of_premises = None
            business_document.save()
            return Response({"message": "Photo of Premises deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Photo of Premises does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'property_tax_receipt':
        if business_document.property_tax_receipt:
            business_document.property_tax_receipt.storage.delete(business_document.property_tax_receipt.name)
            business_document.property_tax_receipt = None
            business_document.save()
            return Response({"message": "Property Tax Receipt deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Property Tax Receipt does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if file_type == 'rental_agreement':
        if business_document.rental_agreement:
            business_document.rental_agreement.storage.delete(business_document.rental_agreement.name)
            business_document.rental_agreement = None
            business_document.save()
            return Response({"message": "Rental Agreement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Rental Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_document(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = BusinessDocumentDetails.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessDocumentDetails.objects.get(service_task_id=service_task_id)
    except BusinessDocumentDetails.DoesNotExist:
        return Response({"error": "Business Document Details not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessDocumentDetailsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_list(request):
    if request.method == 'GET':
        records = ReviewFilingCertificate.objects.all()
        serializer = ReviewFilingCertificateSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ReviewFilingCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_detail(request, pk):
    try:
        record = ReviewFilingCertificate.objects.get(pk=pk)
    except ReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewFilingCertificateSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ReviewFilingCertificateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_review_filing_certificate(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if service_request_id:
            instance = ReviewFilingCertificate.objects.get(service_request_id=service_request_id)
        else:
            instance = ReviewFilingCertificate.objects.get(service_task_id=service_task_id)
    except ReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Review Filing Certificate not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewFilingCertificateSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


Task_Model_Serializer_Map = {
    "Business Identity": (BusinessIdentity, BusinessIdentitySerializer, False),
    "Applicant Details": (ApplicantDetails, ApplicantDetailsSerializer, False),
    "Signatory Details": (SignatoryDetails, SignatoryDetailsSerializer, False),
    "Business Location": (BusinessLocation, BusinessLocationSerializer, False),
    "Trade License Details": (TradeLicenseDetails, TradeLicenseDetailsSerializer, False),
    "Business Document Details": (BusinessDocumentDetails, BusinessDocumentDetailsSerializer, False),
    "Review Filing Certificate": (ReviewFilingCertificate, ReviewFilingCertificateSerializer, False),
}


@api_view(['GET'])
def get_service_request_full_details(request, service_request_id):
    if not service_request_id:
        return Response({"error": "Missing 'service_request_id'"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(id=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "Service Request not found"}, status=status.HTTP_404_NOT_FOUND)

    tasks = service_request.service_tasks.all()
    full_data = {}
    for task in tasks:
        category_name = task.category_name.strip()
        config = Task_Model_Serializer_Map.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assigned_to": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }

        if config:
            model_class, serializer_class, is_multiple = config
            try:
                instance = model_class.objects.get(service_task=task)
                serializer = serializer_class(instance)
                task_info["data"] = serializer.data
            except model_class.DoesNotExist:
                task_info["data"] = None
        else:
            task_info["data"] = "No model/serializer mapping defined"
        full_data[category_name] = task_info

    return Response({
        "service_request_id": service_request.id,
        "client": service_request.user.id,
        "tasks": full_data
    }, status=status.HTTP_200_OK)


Category_Task_Map = {
    "applicant_and_business_info": ["Business Identity", "Applicant Details",
                                    "Signatory Details", "Business Location"],
    "document_related_info": ["Trade License Details", "Business Document Details"],
    "review": ["Review Filing Certificate"]
}


@api_view(['GET'])
def get_service_request_section_data(request):

    service_request_id = request.query_params.get('service_request_id')
    section_key = request.query_params.get('section')

    if not service_request_id or not section_key:
        return Response({"error": "Missing 'service_request_id' or 'section'"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "Service Request not found"}, status=status.HTTP_404_NOT_FOUND)

    section_tasks = Category_Task_Map.get(section_key)

    if not section_tasks:
        return Response({"error": "Invalid section key"}, status=status.HTTP_400_BAD_REQUEST)

    section_data = {}

    tasks = service_request.service_tasks.filter(category_name__in=section_tasks)

    for task in tasks:
        category_name = task.category_name.strip()
        config = Task_Model_Serializer_Map.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assigned_to": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }

        if config:
            model_class, serializer_class, is_multiple = config
            try:
                instance = model_class.objects.get(service_task=task)
                serializer = serializer_class(instance)
                task_info["data"] = serializer.data
            except model_class.DoesNotExist:
                task_info["data"] = None
        else:
            task_info["data"] = "No model/serializer mapping defined"

        section_data[category_name] = task_info

    return Response({
        "service_request_id": service_request.id,
        "client": service_request.user.id,
        "section": section_key,
        "tasks": section_data
    }, status=status.HTTP_200_OK)
