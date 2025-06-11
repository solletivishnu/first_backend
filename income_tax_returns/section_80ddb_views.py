from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upsert_section80ddb_with_files(request):
    try:
        deductions_id = request.data.get('deductions')
        if not deductions_id:
            return Response({"error": "Missing deductions id"}, status=400)

        # Try to update if exists
        try:
            instance = Section80DDB.objects.get(deductions_id=deductions_id)
            serializer = Section80DDBSerializer(instance, data=request.data, partial=True)
        except Section80DDB.DoesNotExist:
            serializer = Section80DDBSerializer(data=request.data)

        if serializer.is_valid():
            section_instance = serializer.save()

            # Replace existing documents
            files = request.FILES.getlist('files')
            if files:
                for file in files:
                    Section80DDBDocuments.objects.create(
                        section_80ddb=section_instance,
                        file=file
                    )

            return Response({
                "message": "Section 80DDB details saved successfully",
                "data": serializer.data
            }, status=200)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_section80ddb_details(request, deductions_id):
    try:
        section = Section80DDB.objects.get(deductions_id=deductions_id)
        serializer = Section80DDBSerializer(section)

        documents = Section80DDBDocuments.objects.filter(section_80ddb=section)
        document_data = [
            {
                "id": doc.id,
                "file_url": doc.file.url if doc.file else None,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents
        ]

        return Response({
            "section_80ddb": serializer.data,
            "documents": document_data
        }, status=200)
    except Section80DDB.DoesNotExist:
        return Response({"error": "Section 80DDB entry not found"}, status=404)


@api_view(['DELETE'])
def delete_section80ddb(request, deductions_id):
    try:
        section = Section80DDB.objects.get(deductions_id=deductions_id)

        # Delete associated files
        documents = Section80DDBDocuments.objects.filter(section_80ddb=section)
        for doc in documents:
            if doc.file:
                doc.file.delete(save=False)
            doc.delete()

        section.delete()
        return Response({"message": "Section 80DDB entry and documents deleted successfully"}, status=204)
    except Section80DDB.DoesNotExist:
        return Response({"error": "Record not found"}, status=404)


@api_view(['DELETE'])
def delete_section80ddb_file(request, file_id):
    try:
        file = Section80DDBDocuments.objects.get(id=file_id)
        if file.file:
            file.file.delete(save=False)  # Delete from storage
        file.delete()
        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Section80DDBDocuments.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)