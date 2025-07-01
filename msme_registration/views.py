from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import *
from .serializers import *
import json


@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_list(request):
    if request.method == 'POST':
        serializer = BusinessIdentitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = BusinessIdentity.objects.all()
        serializer = BusinessIdentitySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_detail(request, pk):
    try:
        item = BusinessIdentity.objects.get(pk=pk)
    except BusinessIdentity.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessIdentitySerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BusinessIdentitySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated files if they exist
        file_type = request.query_params.get('file_type')
        if file_type:
            try:
                if file_type == 'pan_of_business_or_COI' and item.pan_of_business_or_COI:
                    item.pan_of_business_or_COI.storage.delete(item.pan_of_business_or_COI.name)
                    item.pan_of_business_or_COI = None
                elif file_type == 'aadhar_of_signatory' and item.aadhar_of_signatory:
                    item.aadhar_of_signatory.storage.delete(item.aadhar_of_signatory.name)
                    item.aadhar_of_signatory = None
                item.save()
                return Response({"message": "{} deleted successfully".format(file_type)},
                                status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if item.pan_of_business_or_COI:
            item.pan_of_business_or_COI.storage.delete(item.pan_of_business_or_COI.name)
        if item.aadhar_of_signatory:
            item.aadhar_of_signatory.storage.delete(item.aadhar_of_signatory.name)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def business_identity_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = BusinessIdentity.objects.get(service_request_id=service_request_id)
        serializer = BusinessIdentitySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except BusinessIdentity.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_classification_list(request):
    if request.method == 'POST':
        data = request.data.copy()

        if 'nic_codes' in data and isinstance(data['nic_codes'], str):
            try:
                nic_codes = json.loads(data['nic_codes'])
                data['nic_codes'] = json.dumps(nic_codes)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for nic_codes"},
                                status=status.HTTP_400_BAD_REQUEST)

        if 'number_of_persons_employed' in data and isinstance(data['number_of_persons_employed'], str):
            try:
                number_of_persons_employed = json.loads(data['number_of_persons_employed'])
                data['number_of_persons_employed'] = json.dumps(number_of_persons_employed)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for number_of_persons_employed"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = BusinessClassificationInputsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = BusinessClassificationInputs.objects.all()
        serializer = BusinessClassificationInputsSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_classification_detail(request, pk):
    try:
        item = BusinessClassificationInputs.objects.get(pk=pk)
    except BusinessClassificationInputs.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessClassificationInputsSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()

        if 'nic_codes' in data and isinstance(data['nic_codes'], str):
            try:
                nic_codes = json.loads(data['nic_codes'])
                data['nic_codes'] = json.dumps(nic_codes)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for nic_codes"},
                                status=status.HTTP_400_BAD_REQUEST)

        if 'number_of_persons_employed' in data and isinstance(data['number_of_persons_employed'], str):
            try:
                number_of_persons_employed = json.loads(data['number_of_persons_employed'])
                data['number_of_persons_employed'] = json.dumps(number_of_persons_employed)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for number_of_persons_employed"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = BusinessClassificationInputsSerializer(item, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def business_classification_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = BusinessClassificationInputs.objects.get(service_request_id=service_request_id)
        serializer = BusinessClassificationInputsSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except BusinessClassificationInputs.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def turnover_declaration_list(request):
    if request.method == 'POST':
        data = request.data.copy()
        if 'turnover_in_inr' in data and isinstance(data['turnover_in_inr'], str):
            try:
                turnover_in_inr = json.loads(data['turnover_in_inr'])
                data['turnover_in_inr'] = json.dumps(turnover_in_inr)

            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for turnover_in_inr"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = TurnoverAndInvestmentDeclarationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        declarations = TurnoverAndInvestmentDeclaration.objects.all()
        serializer = TurnoverAndInvestmentDeclarationSerializer(declarations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def turnover_declaration_detail(request, pk):
    try:
        declaration = TurnoverAndInvestmentDeclaration.objects.get(pk=pk)
    except TurnoverAndInvestmentDeclaration.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TurnoverAndInvestmentDeclarationSerializer(declaration)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'turnover_in_inr' in data and isinstance(data['turnover_in_inr'], str):
            try:
                turnover_in_inr = json.loads(data['turnover_in_inr'])
                data['turnover_in_inr'] = json.dumps(turnover_in_inr)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for turnover_in_inr"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = TurnoverAndInvestmentDeclarationSerializer(declaration, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated gst_certificate file if it exists
        file_type = request.query_params.get('file_type')
        if file_type:
            try:
                if file_type == 'gst_certificate' and declaration.gst_certificate:
                    declaration.gst_certificate.storage.delete(declaration.gst_certificate.name)
                    declaration.gst_certificate = None
                    declaration.save()
                    return Response({"message": "GST Certificate deleted successfully"},
                                    status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if declaration.gst_certificate:
            declaration.gst_certificate.storage.delete(declaration.gst_certificate.name)
        declaration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def turnover_declaration_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = TurnoverAndInvestmentDeclaration.objects.get(service_request_id=service_request_id)
        serializer = TurnoverAndInvestmentDeclarationSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TurnoverAndInvestmentDeclaration.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def registered_address_list(request):
    if request.method == 'POST':
        data = request.data.copy()
        if 'official_address_of_enterprise' in data and isinstance(data['official_address_of_enterprise'], str):
            try:
                official_address = json.loads(data['official_address_of_enterprise'])
                data['official_address_of_enterprise'] = json.dumps(official_address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for official_address_of_enterprise"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisteredAddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = RegisteredAddress.objects.all()
        serializer = RegisteredAddressSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def registered_address_detail(request, pk):
    try:
        item = RegisteredAddress.objects.get(pk=pk)
    except RegisteredAddress.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RegisteredAddressSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'official_address_of_enterprise' in data and isinstance(data['official_address_of_enterprise'], str):
            try:
                official_address = json.loads(data['official_address_of_enterprise'])
                data['official_address_of_enterprise'] = json.dumps(official_address)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for official_address_of_enterprise"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisteredAddressSerializer(item, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated files if they exist
        file_type = request.query_params.get('file_type')
        if file_type:
            try:
                if file_type == 'bank_statement_or_cancelled_cheque' and item.bank_statement_or_cancelled_cheque:
                    item.bank_statement_or_cancelled_cheque.storage.delete(item.bank_statement_or_cancelled_cheque.name)
                    item.bank_statement_or_cancelled_cheque = None
                elif file_type == 'official_address_of_proof' and item.official_address_of_proof:
                    item.official_address_of_proof.storage.delete(item.official_address_of_proof.name)
                    item.official_address_of_proof = None
                item.save()
                return Response({"message": "{} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if item.bank_statement_or_cancelled_cheque:
            item.bank_statement_or_cancelled_cheque.storage.delete(item.bank_statement_or_cancelled_cheque.name)
        if item.official_address_of_proof:
            item.official_address_of_proof.storage.delete(item.official_address_of_proof.name)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def registered_address_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = RegisteredAddress.objects.get(service_request_id=service_request_id)
        serializer = RegisteredAddressSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except RegisteredAddress.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def location_of_plant_or_unit_list(request):
    if request.method == 'POST':
        data = request.data.copy()
        if 'unit_details' in data and isinstance(data['unit_details'], str):
            try:
                unit_details = json.loads(data['unit_details'])
                data['unit_details'] = json.dumps(unit_details)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for unit_details"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = LocationOfPlantOrUnitSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        locations = LocationOfPlantOrUnit.objects.all()
        serializer = LocationOfPlantOrUnitSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def location_of_plant_or_unit_detail(request, pk):
    try:
        location = LocationOfPlantOrUnit.objects.get(pk=pk)
    except LocationOfPlantOrUnit.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LocationOfPlantOrUnitSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'unit_details' in data and isinstance(data['unit_details'], str):
            try:
                unit_details = json.loads(data['unit_details'])
                data['unit_details'] = json.dumps(unit_details)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for unit_details"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = LocationOfPlantOrUnitSerializer(location, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def location_of_plant_or_unit_by_registration_address_id(request):
    registration_address_id = request.query_params.get('registration_address_id')
    if not registration_address_id:
        return Response({"error": "Missing registration_address_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = LocationOfPlantOrUnit.objects.filter(registered_address_id=registration_address_id)
        serializer = LocationOfPlantOrUnitSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except LocationOfPlantOrUnit.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_list(request):
    if request.method == 'POST':
        serializer = ReviewFilingCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        records = MsmeReviewFilingCertificate.objects.all()
        serializer = ReviewFilingCertificateSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_detail(request, pk):
    try:
        record = MsmeReviewFilingCertificate.objects.get(pk=pk)
    except MsmeReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewFilingCertificateSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ReviewFilingCertificateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated review_certificate file if it exists
        if record.review_certificate:
            record.review_certificate.storage.delete(record.review_certificate.name)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
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
            instance = MsmeReviewFilingCertificate.objects.get(service_request_id=service_request_id)
        else:
            instance = MsmeReviewFilingCertificate.objects.get(service_task_id=service_task_id)
    except MsmeReviewFilingCertificate.DoesNotExist:
        return Response({"error": "No matching ReviewFilingCertificate found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewFilingCertificateSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


MSME_MODEL_SERIALIZER_MAP = {
    "Business Identity": (BusinessIdentity, BusinessIdentitySerializer),
    "Business Classification Inputs": (BusinessClassificationInputs, BusinessClassificationInputsSerializer),
    "Turnover And InvestmentDeclaration": (TurnoverAndInvestmentDeclaration,
                                           TurnoverAndInvestmentDeclarationSerializer),
    "Registered Address": (RegisteredAddress, RegisteredAddressWithLocationPlantSerializer),
    "Review Filing Certificate": (MsmeReviewFilingCertificate, ReviewFilingCertificateSerializer),
}


@api_view(['GET'])
def get_msme_data_by_service_request(request, service_request_id):
    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'ServiceRequest not found'}, status=status.HTTP_404_NOT_FOUND)

    msme_data = {}

    for label, (model_class, serializer_class, is_multiple) in MSME_MODEL_SERIALIZER_MAP.items():
        queryset = model_class.objects.filter(service_request=service_request)

        if queryset.exists():
            data = serializer_class(queryset, many=True).data if is_multiple else (
                serializer_class(queryset.first()).data)
        else:
            data = [] if is_multiple else None

        msme_data[label] = data

    return Response({
        "service_request": service_request.id,
        "client": service_request.user.id,
        "msme_data": msme_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_msme_full_data_by_service_request(request, service_request_id):
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "ServiceRequest not found"}, status=status.HTTP_404_NOT_FOUND)

    tasks = service_request.service_tasks.all()
    full_data = {}
    for task in tasks:
        category_name = task.category_name.strip()
        config = MSME_MODEL_SERIALIZER_MAP.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "task_status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }
        if config:
            model_class, serializer_class = config
            try:
                instance = model_class.objects.get(service_task=task)
                serializer = serializer_class(instance)
                task_info["data"] = serializer.data
            except model_class.DoesNotExist:
                task_info["data"] = None
        else:
            task_info["data"] = "No model/Serializer mapping defined"
        full_data[category_name] = task_info

    return Response({
        "service_request_id": service_request.id,
        "client": service_request.user.id,
        "tasks": full_data
    }, status=status.HTTP_200_OK)


Category_Task_Map = {
    "enterprise_profile_info": ["Business Identity", "Business Classification Inputs"],
    "financial_and_location_info": ["Turnover And InvestmentDeclaration", "Registered Address"],
    "review_filing_certificate": ["Review Filing Certificate"]
}


@api_view(['GET'])
def get_msme_tasks_using_section_name(request):

    service_request_id = request.query_params.get('service_request_id')
    section_key = request.query_params.get('section')

    if not service_request_id or not section_key:
        return Response({"error": "Missing service_request_id or section"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({"error": "ServiceRequest not found"}, status=status.HTTP_404_NOT_FOUND)

    section_tasks = Category_Task_Map.get(section_key)

    if not section_tasks:
        return Response({"error": "Invalid Section Name"}, status=status.HTTP_400_BAD_REQUEST)

    section_data = {}

    tasks = service_request.service_tasks.filter(category_name__in=section_tasks)

    for task in tasks:
        category_name = task.category_name.strip()
        config = MSME_MODEL_SERIALIZER_MAP.get(category_name)

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
            model_class, serializer_class = config
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
