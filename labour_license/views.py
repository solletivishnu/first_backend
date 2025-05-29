from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import IsPlatformOrAssociatedUser
from rest_framework.decorators import api_view, permission_classes, parser_classes


# 1. Entrepreneur Details Views
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_structure_list(request):
    if request.method == 'GET':
        records = BusinessIdentityStructure.objects.all()
        serializer = BusinessIdentityStructureSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BusinessIdentityStructureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_identity_structure(request):
    """
    Retrieve BusinessIdentityStructure based on either service_request_id or service_task_id (query param).
    Query Params: ?service_request_id=<id> or ?service_task_id=<id>
    """
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = BusinessIdentityStructure.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessIdentityStructure.objects.get(service_task_id=service_task_id)
    except BusinessIdentityStructure.DoesNotExist:
        return Response({"error": "No matching BusinessIdentityStructure found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessIdentityStructureSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_structure_detail(request, pk):
    try:
        record = BusinessIdentityStructure.objects.get(pk=pk)
    except BusinessIdentityStructure.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessIdentityStructureSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BusinessIdentityStructureSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 2. Establishment Details Views
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_details_list(request):
    if request.method == 'GET':
        records = SignatoryDetails.objects.all()
        serializer = SignatoryDetailsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SignatoryDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_signatory_details(request):
    """
    Retrieve SignatoryDetails based on either service_request_id or service_task_id.
    Query Params: ?service_request_id=<id> or ?service_task_id=<id>
    """
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
            instance = SignatoryDetails.objects.filter(service_task_id=service_task_id)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "No matching SignatoryDetails found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SignatoryDetailsSerializer(instance, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_location_proofs(request):
    """
    Retrieve BusinessLocationProofs based on either service_request_id or service_task_id.
    Query Params: ?service_request_id=<id> or ?service_task_id=<id>
    """
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = BusinessLocationProofs.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessLocationProofs.objects.get(service_task_id=service_task_id)
    except BusinessLocationProofs.DoesNotExist:
        return Response({"error": "No matching BusinessLocationProofs found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessLocationProofsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_details_detail(request, pk):
    try:
        record = SignatoryDetails.objects.get(pk=pk)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignatoryDetailsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = SignatoryDetailsSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_proofs_list(request):
    if request.method == 'GET':
        records = BusinessLocationProofs.objects.all()
        serializer = BusinessLocationProofsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if 'principal_place_of_business' in data and isinstance(data['principal_place_of_business'], str):
            try:
                address = json.loads(data['principal_place_of_business'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        data['principal_place_of_business'] = json.dumps(address)
        serializer = BusinessLocationProofsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_proofs_detail(request, pk):
    try:
        record = BusinessLocationProofs.objects.get(pk=pk)
    except BusinessLocationProofs.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessLocationProofsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        if 'principal_place_of_business' in data and isinstance(data['principal_place_of_business'], str):
            try:
                address = json.loads(data['principal_place_of_business'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        data['principal_place_of_business'] = json.dumps(address)
        serializer = BusinessLocationProofsSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_business_registration_documents(request):
    """
    Retrieve BusinessRegistrationDocuments based on either service_request_id or service_task_id.
    """
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = BusinessRegistrationDocuments.objects.get(service_request_id=service_request_id)
        else:
            instance = BusinessRegistrationDocuments.objects.get(service_task_id=service_task_id)
    except BusinessRegistrationDocuments.DoesNotExist:
        return Response({"error": "No matching BusinessRegistrationDocuments found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BusinessRegistrationDocumentsSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_space_business_list(request):
    if request.method == 'GET':
        records = AdditionalSpaceBusiness.objects.all()
        serializer = AdditionalSpaceBusinessSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])  # convert string to dict
            except json.JSONDecodeError:
                return Response({"address": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)
            data['address'] = json.dumps(address)  # convert dict back to string for storage

        serializer = AdditionalSpaceBusinessSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_space_business_detail(request, pk):
    try:
        record = AdditionalSpaceBusiness.objects.get(pk=pk)
    except AdditionalSpaceBusiness.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AdditionalSpaceBusinessSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                address = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        data['address'] = json.dumps(address)
        serializer = AdditionalSpaceBusinessSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_additional_space_business_details(request):
    business_location_proofs_id = request.query_params.get('business_location_proofs')
    if not business_location_proofs_id:
        return Response({'error': "Provide either 'business_location_proofs_id' as a query parameter."})

    try:
        instance = AdditionalSpaceBusiness.objects.filter(business_location_proofs_id=business_location_proofs_id)
    except AdditionalSpaceBusiness.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdditionalSpaceBusinessSerializer(instance, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_registration_documents_list(request):
    if request.method == 'GET':
        records = BusinessRegistrationDocuments.objects.all()
        serializer = BusinessRegistrationDocumentsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BusinessRegistrationDocumentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_registration_documents_detail(request, pk):
    try:
        record = BusinessRegistrationDocuments.objects.get(pk=pk)
    except BusinessRegistrationDocuments.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessRegistrationDocumentsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BusinessRegistrationDocumentsSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_review_filing_certificate(request):
    """
    Retrieve ReviewFilingCertificate based on either service_request_id or service_task_id.
    """
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
        return Response({"error": "No matching ReviewFilingCertificate found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewFilingCertificateSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)
