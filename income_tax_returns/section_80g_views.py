from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Section80G
from .serializers import Section80GSerializer


# Create a new Section80G entry
@api_view(['POST'])
def add_section_80g(request):
    try:
        serializer = Section80GSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Section 80G donation added successfully", 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Update an existing Section80G entry
@api_view(['PUT'])
def update_section_80g(request, pk):
    try:
        entry = Section80G.objects.get(pk=pk)
    except Section80G.DoesNotExist:
        return Response(
            {"error": "Section80G entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = Section80GSerializer(entry, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Section 80G donation updated successfully"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a Section80G entry
@api_view(['DELETE'])
def delete_section_80g(request, pk):
    try:
        entry = Section80G.objects.get(pk=pk)
    except Section80G.DoesNotExist:
        return Response(
            {"error": "Section80G entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    entry.delete()
    return Response(
        {"message": "Section 80G donation deleted successfully"},
        status=status.HTTP_204_NO_CONTENT
    )


# List all Section80G entries for a given Deductions record
@api_view(['GET'])
def list_section_80g(request):
    deductions_id = request.query_params.get('deductions')
    if not deductions_id:
        return Response(
            {"error": "Missing deductions parameter"},
            status=status.HTTP_400_BAD_REQUEST
        )
    entries = Section80G.objects.filter(deductions_id=deductions_id)
    serializer = Section80GSerializer(entries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
