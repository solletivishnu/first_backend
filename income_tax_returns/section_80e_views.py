from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.db import transaction


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upsert_section80e_with_files(request):
    try:
        deductions_id = request.data.get('deductions')
        if not deductions_id:
            return Response({"error": "Missing deductions id"}, status=400)

        # Try to update if exists, else create
        try:
            instance = Section80E.objects.get(deductions_id=deductions_id)
            serializer = Section80ESerializer(instance, data=request.data, partial=True)
        except Section80E.DoesNotExist:
            serializer = Section80ESerializer(data=request.data)

        if serializer.is_valid():
            section_instance = serializer.save()

            # Map form field names to document types
            doc_map = {
                'sanction_letter_files': 'Sanction Letter',
                'interest_certificate_files': 'Interest Certificate',
                'repayment_schedule_files': 'Repayment Schedule',
                'other_files': 'Other',
            }

            for field_name, doc_type in doc_map.items():
                for file in request.FILES.getlist(field_name):
                    Section80EDocuments.objects.create(
                        section_80e=section_instance,
                        document_type=doc_type,
                        file=file
                    )

            return Response({
                "message": "Section 80E details saved successfully",
                "data": serializer.data
            }, status=200)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_section80e_details(request, deductions_id):
    try:
        section = Section80E.objects.get(deductions_id=deductions_id)
        serializer = Section80ESerializer(section)

        # Fetch documents
        documents = Section80EDocuments.objects.filter(section_80e=section)
        document_data = [
            {
                "id": doc.id,
                "document_type": doc.document_type,
                "file_url": doc.file.url if doc.file else None,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents
        ]

        return Response({
            "section_80e": serializer.data,
            "documents": document_data
        }, status=200)
    except Section80E.DoesNotExist:
        return Response({"error": "Section 80E entry not found"}, status=404)


@api_view(['DELETE'])
def delete_section80e(request, deductions_id):
    try:
        section = Section80E.objects.get(deductions_id=deductions_id)

        # Delete related documents
        documents = Section80EDocuments.objects.filter(section_80e=section)
        for doc in documents:
            if doc.file:
                doc.file.delete(save=False)
            doc.delete()

        section.delete()
        return Response({"message": "Section 80E entry and documents deleted successfully"}, status=204)
    except Section80E.DoesNotExist:
        return Response({"error": "Record not found"}, status=404)
