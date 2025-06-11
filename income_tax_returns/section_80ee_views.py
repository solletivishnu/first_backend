from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Section80EE, Section80EEDocuments
from .serializers import Section80EESerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upsert_section80ee_with_files(request):
    try:
        deductions_id = request.data.get('deductions')
        if not deductions_id:
            return Response({"error": "Missing deductions id"}, status=400)

        with transaction.atomic():
            try:
                instance = Section80EE.objects.get(deductions_id=deductions_id)
                serializer = Section80EESerializer(instance, data=request.data, partial=True)
            except Section80EE.DoesNotExist:
                serializer = Section80EESerializer(data=request.data)

            if serializer.is_valid():
                section_instance = serializer.save()

                doc_map = {
                    'sanction_letter_files': 'Sanction Letter',
                    'interest_certificate_files': 'Interest Certificate',
                    'repayment_schedule_files': 'Repayment Schedule',
                    'other_files': 'Other',
                }

                for field_name, doc_type in doc_map.items():
                    files = request.FILES.getlist(field_name)
                    if files:
                        for file in files:
                            Section80EEDocuments.objects.create(
                                section_80ee=section_instance,
                                document_type=doc_type,
                                file=file
                            )

                return Response({
                    "message": "Section 80EE details saved successfully",
                    "data": Section80EESerializer(section_instance).data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_section80ee_details(request, deductions_id):
    try:
        section = Section80EE.objects.get(deductions_id=deductions_id)
        serializer = Section80EESerializer(section)

        # Get and format documents
        documents = Section80EEDocuments.objects.filter(section_80ee=section)
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
            "section_80ee": serializer.data,
            "documents": document_data
        }, status=200)
    except Section80EE.DoesNotExist:
        return Response({"error": "Section 80EE entry not found"}, status=404)


@api_view(['DELETE'])
def delete_section80ee(request, deductions_id):
    try:
        section = Section80EE.objects.get(deductions_id=deductions_id)

        # Delete related documents and actual files
        documents = Section80EEDocuments.objects.filter(section_80ee=section)
        for doc in documents:
            if doc.file:
                doc.file.delete(save=False)
            doc.delete()

        section.delete()
        return Response({"message": "Section 80EE entry and documents deleted successfully"}, status=204)
    except Section80EE.DoesNotExist:
        return Response({"error": "Record not found"}, status=404)


@api_view(['DELETE'])
def delete_section80ee_document(request, document_id):
    try:
        document = Section80EEDocuments.objects.get(id=document_id)
        if document.file:
            document.file.delete(save=False)  # Delete the file from storage
        document.delete()
        return Response({"message": "Document deleted successfully"}, status=204)
    except Section80EEDocuments.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)