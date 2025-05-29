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
        applicant_detail = ApplicantDetails.objects.all()
        serializer = ApplicantDetailsSerializer(applicant_detail, many=True)
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
        applicant_detail = ApplicantDetails.objects.get(pk=pk)
    except ApplicantDetails.DoesNotExist:
        return Response({"error": "Applicant Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ApplicantDetailsSerializer(applicant_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ApplicantDetailsSerializer(applicant_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated files if they exist
        if applicant_detail.aadhaar_image:
            applicant_detail.aadhaar_image.storage.delete(applicant_detail.aadhaar_image.name)
        if applicant_detail.pan_image:
            applicant_detail.pan_image.storage.delete(applicant_detail.pan_image.name)
        if applicant_detail.passport_photo:
            applicant_detail.passport_photo.storage.delete(applicant_detail.passport_photo.name)
        applicant_detail.delete()
        return Response({"message": "Applicant Details deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


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
        serializer = SignatoryDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_detail(request, pk):
    try:
        signatory_details = SignatoryDetails.objects.get(pk=pk)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "Promoter or Directors Details not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignatoryDetailsSerializer(signatory_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SignatoryDetailsSerializer(signatory_details, data=request.data, partial=True)
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
            instance = SignatoryDetails.objects.filter(service_request_id=service_request_id)
        else:
            instance = SignatoryDetails.objects.get(service_task_id=service_task_id)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "Signatory Details not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SignatoryDetailsSerializer(instance, many=True)
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
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        data['address'] = json.dumps(address)
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
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        data['address'] = json.dumps(address)
        serializer = BusinessLocationSerializer(business_location, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            business_location.delete()
            return Response({"message": "Business Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


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
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        data['address'] = json.dumps(address)
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
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        data['address'] = json.dumps(address)
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
            additional_address_details.delete()
            return Response({"message": "Additional Address Details deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


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
            trade_license.delete()
            return Response({"message": "Trade License deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


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
            business_document.delete()
            return Response({"message": "Business Document Details deleted successfully"},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


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