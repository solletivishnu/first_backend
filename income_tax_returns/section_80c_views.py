from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Section80C, Section80CDocuments
from .serializers import Section80CSerializer, Section80CDocumentsSerializer

@api_view(['GET', 'POST'])
def section_80c_list(request):
    """
    GET:  list all Section80C records, or filter by ?deductions=<id>
    POST: create a new Section80C record
    """
    if request.method == 'GET':
        deductions_id = request.query_params.get('deductions')
        qs = Section80C.objects.all()
        if deductions_id:
            qs = qs.filter(deductions_id=deductions_id)
        serializer = Section80CSerializer(qs, many=True)
        return Response(serializer.data)

    # POST
    serializer = Section80CSerializer(data=request.data)
    if serializer.is_valid():
        section_instance = serializer.save()
        # Handle file uploads if any
        file = request.FILES.get('file')
        if file:
            Section80CDocuments.objects.create(
                section_80c=section_instance,
                file=file
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def section_80c_detail(request, pk):
    """
    GET:    retrieve one Section80C record
    PUT:    update (partial) one Section80C record
    DELETE: delete one Section80C record
    """
    try:
        obj = Section80C.objects.get(pk=pk)
    except Section80C.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Section80CSerializer(obj)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Section80CSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            section_instance = serializer.save()
            # Handle file uploads if any
            file = request.FILES.get('file')
            if file:
                document = Section80CDocuments.objects.get(section_80c=section_instance)
                if document:
                    document.file = file
                    document.save()
                else:
                    Section80CDocuments.objects.create(
                        section_80c=section_instance,
                        file=file
                    )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def delete_section_80c_file(request, file_id):
    """
    Delete a single Section80CFile by its pk.
    """
    try:
        doc = Section80CDocuments.objects.get(pk=file_id)
    except Section80CDocuments.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    doc.delete()
    return Response({"message": "File deleted"}, status=status.HTTP_204_NO_CONTENT)