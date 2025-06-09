from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Section80EEB
from .serializers import *


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upsert_section80eeb_with_files(request):
    try:
        deductions_id = request.data.get('deductions')
        if not deductions_id:
            return Response({"error": "Missing deductions id"}, status=400)

        try:
            instance = Section80EEB.objects.get(deductions_id=deductions_id)
            serializer = Section80EEBSerializer(instance, data=request.data, partial=True)
        except Section80EEB.DoesNotExist:
            serializer = Section80EEBSerializer(data=request.data)

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
                    Section80EEBDocuments.objects.filter(
                        section_80eeb=section_instance,
                        document_type=doc_type
                    ).delete()

                    for file in files:
                        Section80EEBDocuments.objects.create(
                            section_80eeb=section_instance,
                            document_type=doc_type,
                            file=file
                        )

            return Response({
                "message": "Section 80EEB details saved successfully",
                "data": serializer.data
            }, status=200)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_section80eeb_details(request, deductions_id):
    try:
        section = Section80EEB.objects.get(deductions_id=deductions_id)
        serializer = Section80EEBSerializer(section)
        return Response({
            "section_80eeb": serializer.data
        }, status=200)
    except Section80EEB.DoesNotExist:
        return Response({"error": "Section 80EEB entry not found"}, status=404)


@api_view(['DELETE'])
def delete_section80eeb(request, deductions_id):
    try:
        section = Section80EEB.objects.get(deductions_id=deductions_id)

        # Delete all attached files
        for doc in section.section_80eeb_documents.all():
            if doc.file:
                doc.file.delete(save=False)
            doc.delete()

        section.delete()
        return Response({"message": "Section 80EEB entry and documents deleted successfully"}, status=204)

    except Section80EEB.DoesNotExist:
        return Response({"error": "Record not found"}, status=404)
