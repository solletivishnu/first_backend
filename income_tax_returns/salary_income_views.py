from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import SalaryIncome, SalaryDocumentFile
from .serializers import SalaryIncomeSerializer



@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def salary_income_list(request):
    if request.method == 'GET':
        records = SalaryIncome.objects.all()
        serializer = SalaryIncomeSerializer(records, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SalaryIncomeSerializer(data=request.data)
        if serializer.is_valid():
            salary_income = serializer.save()

            # Handle file uploads
            doc_map = {
                'form16_files': 'FORM_16',
                'payslip_files': 'PAYSLIP',
                'bank_statement_files': 'BANK_STATEMENT',
            }

            for field_name, doc_type in doc_map.items():
                for file in request.FILES.getlist(field_name):
                    SalaryDocumentFile.objects.create(
                        income=salary_income,
                        document_type=doc_type,
                        file=file
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def salary_income_detail(request, pk):
    try:
        income = SalaryIncome.objects.get(pk=pk)
    except SalaryIncome.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SalaryIncomeSerializer(income)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SalaryIncomeSerializer(income, data=request.data, partial=True)
        if serializer.is_valid():
            salary_income = serializer.save()

            doc_map = {
                'form16_files': 'FORM_16',
                'payslip_files': 'PAYSLIP',
                'bank_statement_files': 'BANK_STATEMENT',
            }

            for field_name, doc_type in doc_map.items():
                for file in request.FILES.getlist(field_name):
                    SalaryDocumentFile.objects.create(
                        income=salary_income,
                        document_type=doc_type,
                        file=file
                    )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_salary_document(request, pk):
    try:
        file = SalaryDocumentFile.objects.get(pk=pk)

        # Step 1: Delete from S3
        if file.file:
            file.file.storage.delete(file.file.name)  # safely removes from S3

        # Step 2: Delete DB record
        file.delete()

        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    except SalaryDocumentFile.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def salary_document_summary(request, income_id):
    """
    Get count of files by document_type for a given SalaryIncome ID
    """
    try:
        income = SalaryIncome.objects.get(pk=income_id)
    except SalaryIncome.DoesNotExist:
        return Response({"error": "Income record not found"}, status=status.HTTP_404_NOT_FOUND)

    summary = {}
    for doc_type, _ in SalaryDocumentFile.DOCUMENT_TYPES:
        count = income.documents.filter(document_type=doc_type).count()
        summary[doc_type] = count

    return Response(summary)


@api_view(['GET'])
def salary_income_by_service_request(request):
    """
    Get all salary income records for a specific service request
    """
    service_request_id = request.query_params.get('service_request_id')
    records = SalaryIncome.objects.filter(service_request_id=service_request_id)
    serializer = SalaryIncomeSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)