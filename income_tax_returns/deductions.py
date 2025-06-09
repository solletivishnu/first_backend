from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Deductions
from .serializers import DeductionsSerializer


# Create or update (upsert) Deductions
@api_view(['POST'])
def upsert_deductions(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response(
            {"error": "Missing service_request"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ded = Deductions.objects.get(service_request_id=service_request_id)
        serializer = DeductionsSerializer(ded, data=request.data, partial=True)
    except Deductions.DoesNotExist:
        serializer = DeductionsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"data":serializer.data, "message": "Deductions saved successfully"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve Deductions by service_request
@api_view(['GET'])
def get_deductions(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response(
            {"error": "Missing service_request"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ded = Deductions.objects.get(service_request_id=service_request_id)
    except Deductions.DoesNotExist:
        return Response(
            {"error": "No Deductions found for given service_request"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = DeductionsSerializer(ded)
    return Response(serializer.data, status=status.HTTP_200_OK)
