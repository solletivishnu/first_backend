from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import NRIEmployeeSalaryDetails, ForeignEmployeeSalaryDetailsFiles
from .serializers import NRIEmployeeSalaryDetailsSerializer, ForeignEmployeeSalaryDetailsFilesSerializer
import json


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_nri_salary_details(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    doc_map = {
        'salary_slip_files': 'SALARY_SLIP',
        'tax_paid_certificate_board_files': 'TAX_PAID_CERTIFICATE_BOARD',
        'bank_statement_files': 'BANK_STATEMENT',
    }

    # Check if all file inputs are empty
    all_files_empty = all(len(request.FILES.getlist(field_name)) == 0 for field_name in doc_map)

    # Choose data based on file presence
    data = request.data.copy() if all_files_empty else request.data

    # Handle employment_history JSON string
    if 'employment_history' in data and isinstance(data['employment_history'], str):
        try:
            employment_history = json.loads(data['employment_history'])
            data['employment_history'] = json.dumps(employment_history)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format for employment_history"}, status=status.HTTP_400_BAD_REQUEST)


    try:
        nri_salary = NRIEmployeeSalaryDetails.objects.get(service_request_id=service_request_id)
        serializer = NRIEmployeeSalaryDetailsSerializer(nri_salary, data=data, partial=True)
    except NRIEmployeeSalaryDetails.DoesNotExist:
        serializer = NRIEmployeeSalaryDetailsSerializer(data=data)

    if serializer.is_valid():
        nri_salary = serializer.save()

        for field_name, doc_type in doc_map.items():
            files = request.FILES.getlist(field_name)
            for f in files:
                ForeignEmployeeSalaryDetailsFiles.objects.create(
                    nri=nri_salary,
                    document_type=doc_type,
                    file=f
                )

        return Response({'message': 'NRI Salary Details saved successfully'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def nri_salary_details_view(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        nri_salary = NRIEmployeeSalaryDetails.objects.get(service_request_id=service_request_id)
    except NRIEmployeeSalaryDetails.DoesNotExist:
        return Response({"error": "No NRIEmployeeSalaryDetails found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    base_data = NRIEmployeeSalaryDetailsSerializer(nri_salary).data

    # Group files by document_type
    documents = {}
    for doc_type in ['SALARY_SLIP', 'TAX_PAID_CERTIFICATE_BOARD', 'BANK_STATEMENT']:
        files = nri_salary.foreigner_documents.filter(document_type=doc_type)
        documents[doc_type] = {
            "count": files.count(),
            "files": [
                {
                    "id": f.id,
                    "url": f.file.url if f.file else None,
                    "uploaded_at": f.uploaded_at
                } for f in files
            ]
        }

    base_data["documents"] = documents
    return Response(base_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_nri_salary_file(request, file_id):
    try:
        file = ForeignEmployeeSalaryDetailsFiles.objects.get(pk=file_id)

        # Step 1: Delete from S3 or storage
        if file.file:
            file.file.storage.delete(file.file.name)

        # Step 2: Delete DB record
        file.delete()

        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    except ForeignEmployeeSalaryDetailsFiles.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
