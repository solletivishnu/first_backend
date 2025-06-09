from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_tax_paid_details(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        tax_paid = TaxPaidDetails.objects.get(service_request_id=service_request_id)
        serializer = TaxPaidDetailsSerializer(tax_paid, data=request.data, partial=True)
    except TaxPaidDetails.DoesNotExist:
        serializer = TaxPaidDetailsSerializer(data=request.data)

    try:

        if serializer.is_valid():
            tax_paid = serializer.save()

        # Optional: Clear old files if doing full update
        # TaxPaidDetailsFile.objects.filter(income=tax_paid).delete()

            doc_map = {
                'form26as_files': '26AS',
                'ais_files': 'AIS',
                'advance_tax_files': 'AdvanceTax',
            }

            for field_name, doc_type in doc_map.items():
                files = request.FILES.getlist(field_name)
                for f in files:
                    TaxPaidDetailsFile.objects.create(
                        tax_paid=tax_paid,
                        document_type=doc_type,
                        file=f
                    )


            return Response({'message': 'Tax Paid Details saved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def tax_paid_details_view(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        tax_paid = TaxPaidDetails.objects.get(service_request_id=service_request_id)
    except TaxPaidDetails.DoesNotExist:
        return Response({"error": "No TaxPaidDetails found for given service_request"}, status=status.HTTP_404_NOT_FOUND)

    base_data = TaxPaidDetailsSerializer(tax_paid).data

    # Group files by document_type
    documents = {}
    for doc_type in ['26AS', 'AIS', 'AdvanceTax']:
        files = tax_paid.tax_paid_documents.filter(document_type=doc_type)
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
def delete_tax_paid_file(request, file_id):
    try:
        file = TaxPaidDetailsFile.objects.get(pk=file_id)

        # Step 1: Delete from S3
        if file.file:
            file.file.storage.delete(file.file.name)  # safely removes from S3

        # Step 2: Delete DB record
        file.delete()

        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    except TaxPaidDetailsFile.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
