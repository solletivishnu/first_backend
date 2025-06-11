from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
from .models import *
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
        if record.business_pan:
            try:
                record.business_pan.storage.delete(record.business_pan.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
        data = request.data.copy()
        service_request = data.get('service_request')
        try:
            instance = SignatoryDetails.objects.get(service_request=service_request)
            serializer = SignatoryDetailsSerializer(instance, data=data, partial=True)
        except SignatoryDetails.DoesNotExist:
            serializer = SignatoryDetailsSerializer(data=data)

        if serializer.is_valid():
            main_data = serializer.save()
            if data.get('name'):
                try:
                    data['signatory_details'] = main_data.id
                    serializer_info = signatoryDetailsInfoSerializer(data=data)
                    if not serializer_info.is_valid():
                        return Response(serializer_info.errors, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        serializer_info.save()
                    except Exception as e:
                        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Status Updated Successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
            instance = SignatoryDetails.objects.get(service_request_id=service_request_id)
        else:
            instance = SignatoryDetails.objects.get(service_task_id=service_task_id)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "No matching SignatoryDetails found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SignatoryDetailsSerializer(instance)
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
        record = signatoryDetailsInfo.objects.get(pk=pk)
    except signatoryDetailsInfo.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = signatoryDetailsInfoSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = signatoryDetailsInfoSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if record.aadhar_image:
            try:
                record.aadhar_image.storage.delete(record.aadhar_image.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.pan_image:
            try:
                record.pan_image.storage.delete(record.pan_image.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.photo_image:
            try:
                record.photo_image.storage.delete(record.photo_image.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
                data['principal_place_of_business'] = json.dumps(address)

            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
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
                data['principal_place_of_business'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BusinessLocationProofsSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if record.address_proof:
            try:
                record.address_proof.storage.delete(record.address_proof.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.rental_agreement:
            try:
                record.rental_agreement.storage.delete(record.rental_agreement.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.bank_statement:
            try:
                record.bank_statement.storage.delete(record.bank_statement.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
                data['address'] = json.dumps(address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdditionalSpaceBusinessSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if record.address_proof:
            try:
                record.address_proof.storage.delete(record.address_proof.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.rental_agreement:
            try:
                record.rental_agreement.storage.delete(record.rental_agreement.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        if record.certificate_of_incorporation:
            try:
                record.certificate_of_incorporation.storage.delete(record.certificate_of_incorporation.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.memorandum_of_articles:
            try:
                record.memorandum_of_articles.storage.delete(record.memorandum_of_articles.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.local_language_name_board_photo_business:
            try:
                record.local_language_name_board_photo_business.storage.delete(record.local_language_name_board_photo_business.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if record.authorization_letter:
            try:
                record.authorization_letter.storage.delete(record.authorization_letter.name)  # delete from S3
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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


Task_Model_Serializer_Map = {
    "Business Identity Structure": (BusinessIdentityStructure, BusinessIdentityStructureSerializer),
    "Signatory Details": (SignatoryDetails, SignatoryDetailsSerializer),
    "Business Location Proofs": (BusinessLocationProofs, BusinessLocationProofsSerializer),
    "Business Registration Documents": (BusinessRegistrationDocuments, BusinessRegistrationDocumentsSerializer),
    "Review Filing Certificate": (ReviewFilingCertificate, ReviewFilingCertificateSerializer),
}


@api_view(['GET'])
def get_service_request_full_data(request, service_request_id):
    """
    Retrieve full data for a service request by its ID.
    """

    try:
        service_request = ServiceRequest.objects.get(id=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "Service request not found"}, status=status.HTTP_404_NOT_FOUND)

    data={}
    tasks = service_request.service_tasks.all()
    for task in tasks:
        category_name = task.category_name.strip()
        config = Task_Model_Serializer_Map.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }
        if config:
            model, serializer_class = config
            try:
                instance = model.objects.get(service_task=task, service_request=service_request)
                serializer = serializer_class(instance)
                task_info["data"] = serializer.data
            except model.DoesNotExist:
                task_info["data"] = None
        else:
            task_info["data"] = "No model/serializer mapping defined"

        data[category_name] = task_info

    return Response({
        "service_request_id": service_request.id,
        "client": service_request.user.id if service_request.user else None,
        "task_data": data
    }, status=status.HTTP_200_OK)


Category_Task_Map = {
    "applicant_and_business_info": ["Business Identity Structure", "Signatory Details", "Business Location Proofs"],
    "document_related_info": ["Business Registration Documents"],
    "review": ["Review Filing Certificate"]
}


@api_view(['GET'])
def get_service_request_tasks_by_category(request):
    """
    Retrieve tasks for a service request by category.
    """
    service_request_id = request.query_params.get('service_request_id')
    section_key = request.query_params.get('section')

    try:
        service_request = ServiceRequest.objects.get(id=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "Service request not found"}, status=status.HTTP_404_NOT_FOUND)

    section_tasks = Category_Task_Map.get(section_key)

    if not section_tasks:
        return Response({"error": "Invalid section key"}, status=status.HTTP_400_BAD_REQUEST)

    tasks = service_request.service_tasks.filter(category_name__in=section_tasks)
    data = {}
    for task in tasks:
        category_name = task.category_name.strip()
        config = Task_Model_Serializer_Map.get(category_name)
        task_info = {
                "task_id": task.id,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "assignee": task.assignee.id if task.assignee else None,
                "reviewer": task.reviewer.id if task.reviewer else None,
                "data": None
            }
        if config:
            model, serializer_class = config
            try:
                instance = model.objects.get(service_task=task, service_request=service_request)
                serializer = serializer_class(instance)
                task_info["data"] = serializer.data
            except model.DoesNotExist:
                task_info["data"] = None
        else:
            task_info["data"] = "No model/serializer mapping defined"

        data[category_name] = task_info

    return Response({
        "service_request_id": service_request.id,
        "client": service_request.user.id if service_request.user else None,
        "task_data": data
    }, status=status.HTTP_200_OK)