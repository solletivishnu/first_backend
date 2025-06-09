from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Section80TTATTBU
from .serializers import Section80TTATTBUSerializer


@api_view(['GET', 'POST'])
def section_80ettattbu_list(request):
    """
    GET: list all records, or filter by ?deductions=<id>
    POST: create a new record
    """
    if request.method == 'GET':
        deductions_id = request.query_params.get('deductions')
        qs = Section80TTATTBU.objects.all()
        if deductions_id:
            qs = qs.filter(deductions_id=deductions_id)
        serializer = Section80TTATTBUSerializer(qs, many=True)
        return Response(serializer.data)

    # POST
    serializer = Section80TTATTBUSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def section_80ettattbu_detail(request, pk):
    """
    GET:    retrieve one record
    PUT:    update (partial) one record
    DELETE: remove one record
    """
    try:
        obj = Section80TTATTBU.objects.get(pk=pk)
    except Section80TTATTBU.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Section80TTATTBUSerializer(obj)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = Section80TTATTBUSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
