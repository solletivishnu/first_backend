# views.py
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import Section80D, Section80DFile
from .serializers import *
from django.db import transaction


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_section_80d_with_files(request):
    deductions_id = request.data.get('deductions')

    if not deductions_id:
        return Response({"error": "Missing 'deductions' field"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = Section80D.objects.get(deductions_id=deductions_id)
        serializer = Section80DSerializer(instance, data=request.data, partial=True)
    except Section80D.DoesNotExist:
        serializer = Section80DSerializer(data=request.data)

    if serializer.is_valid():
        with transaction.atomic():
            section_80d = serializer.save()

            # Handle document upload
            files = request.FILES.getlist('files')  # Expected as `files` key in form-data
            for f in files:
                Section80DFile.objects.create(section_80d=section_80d, file=f)

            return Response({
                "message": "Section 80D data saved successfully",
                "data": serializer.data,
                "files_uploaded": len(files)
            }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Uncomment this section if you want to support both POST and PUT methods
# @api_view(['POST', 'PUT'])
# @parser_classes([MultiPartParser, FormParser])
# def upsert_section_80d_with_files(request):
#     """
#     POST: create new Section80D + files
#     PUT:  update existing Section80D + add new files
#           (requires 'id' field in form data to locate existing record)
#     """
#     if request.method == 'POST':
#         serializer = Section80DFileSerializer(data=request.data)
#     else:  # PUT
#         section_id = request.data.get('id')
#         if not section_id:
#             return Response({"error": "Missing Section80D id for update"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             instance = Section80D.objects.get(pk=section_id)
#         except Section80D.DoesNotExist:
#             return Response({"error": "Section80D not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = Section80DFileSerializer(instance, data=request.data, partial=True)
#
#     if serializer.is_valid():
#         section = serializer.save()
#         return Response(
#             Section80DFileSerializer(section).data,
#             status=(status.HTTP_201_CREATED if request.method=='POST' else status.HTTP_200_OK)
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ——— Retrieve Section80D (no files) ———
@api_view(['GET'])
def get_section_80d(request):
    """
    Retrieve a Section80D record by deductions id (?deductions=<id>)
    """
    deductions_id = request.query_params.get('deductions')
    if not deductions_id:
        return Response({"error": "Missing deductions"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        entry = Section80D.objects.get(deductions_id=deductions_id)
    except Section80D.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = Section80DSerializer(entry)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ——— Delete Section80D entirely ———
@api_view(['DELETE'])
def delete_section_80d(request, pk):
    """
    Deletes the Section80D record and all its files.
    """
    try:
        entry = Section80D.objects.get(pk=pk)
    except Section80D.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    entry.delete()
    return Response({"message": "Section80D deleted"}, status=status.HTTP_204_NO_CONTENT)


# ——— List & Delete individual files ———

@api_view(['GET'])
def list_section_80d_files(request):
    """
    List all files for a given Section80D via ?section_80d=<id>
    """
    section_id = request.query_params.get('section_80d')
    if not section_id:
        return Response({"error": "Missing section_80d"}, status=status.HTTP_400_BAD_REQUEST)

    qs = Section80DFile.objects.filter(section_80d_id=section_id)
    serializer = Section80DFileSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_section_80d_file(request, file_id):
    """
    Delete a single Section80DFile by its pk.
    """
    try:
        doc = Section80DFile.objects.get(pk=file_id)
    except Section80DFile.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    doc.delete()
    return Response({"message": "File deleted"}, status=status.HTTP_204_NO_CONTENT)