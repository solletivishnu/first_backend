from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
import json
from .models import CapitalGainsApplicableDetails, CapitalGainsProperty
from .serializers import CapitalGainsApplicableDetailsSerializer, CapitalGainsPropertySerializer



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_capital_gains_details(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = CapitalGainsApplicableDetails.objects.get(service_request_id=service_request_id)
        serializer = CapitalGainsApplicableDetailsSerializer(instance, data=request.data, partial=True)
    except CapitalGainsApplicableDetails.DoesNotExist:
        serializer = CapitalGainsApplicableDetailsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Capital Gains details saved successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_capital_gains_details(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = CapitalGainsApplicableDetails.objects.get(service_request_id=service_request_id)
    except CapitalGainsApplicableDetails.DoesNotExist:
        return Response({"error": "No details found"}, status=status.HTTP_404_NOT_FOUND)

    data = CapitalGainsApplicableDetailsSerializer(instance).data

    # Group property documents
    documents = []
    for p in instance.capital_gains_property_details.all():
        documents.append({
            "property_id": p.id,
            "property_type": p.property_type,
            "purchase_doc": p.purchase_doc.url if p.purchase_doc else None,
            "sale_doc": p.sale_doc.url if p.sale_doc else None,
            "reinvestment_details_docs": p.reinvestment_details_docs.url if p.reinvestment_details_docs else None,
        })

    data["documents"] = documents
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def add_capital_gains_property(request):
    request_data = request.data
    reinvestment = request_data.get('reinvestment_details')
    if isinstance(reinvestment, str):
        try:
            request_data['reinvestment_details'] = json.loads(reinvestment)
        except json.JSONDecodeError:
            return Response({'reinvestment_details': 'Invalid JSON format.'}, status=400)
    serializer = CapitalGainsPropertySerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Property added successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_capital_gains_property(request, property_id):
    try:
        prop = CapitalGainsProperty.objects.get(pk=property_id)

        if prop.purchase_doc:
            prop.purchase_doc.storage.delete(prop.purchase_doc.name)
        if prop.sale_doc:
            prop.sale_doc.storage.delete(prop.sale_doc.name)
        if prop.reinvestment_details_docs:
            prop.reinvestment_details_docs.storage.delete(prop.reinvestment_details_docs.name)

        prop.delete()
        return Response({"message": "Property deleted"}, status=status.HTTP_204_NO_CONTENT)
    except CapitalGainsProperty.DoesNotExist:
        return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, JSONParser, FormParser])
def update_capital_gains_property(request, property_id):
    try:
        property_obj = CapitalGainsProperty.objects.get(pk=property_id)
    except CapitalGainsProperty.DoesNotExist:
        return Response({'error': 'CapitalGainsProperty not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CapitalGainsPropertySerializer(property_obj, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Property updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)