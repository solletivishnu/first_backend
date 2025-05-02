from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import json

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser,JSONParser])
def basic_details_list(request):
    if request.method == 'GET':
        details = BasicDetail.objects.all()
        serializer = BasicDetailsSerializerRetrieval(details, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        if 'upload_photo' not in request.FILES:
            data.pop('upload_photo', None)
        if 'address' in data:
            address_data = data.get('address')
            if isinstance(address_data, str):
                try:
                    address_data = json.loads(address_data)
                    data['address'] = address_data
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON format for address"},
                                    status=status.HTTP_400_BAD_REQUEST)

        try:
            details = BasicDetail.objects.get(user_id=data['user'])
            serializer = BasicDetailsSerializer(details,data=data,partial=True)
        except:
            serializer = BasicDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Retrieve, Update, Delete a Single Basic Detail
@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser,JSONParser])
def basic_detail(request, pk):
    detail = get_object_or_404(BasicDetail, pk=pk)

    if request.method == 'GET':
        serializer = BasicDetailsSerializerRetrieval(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])  # Convert string to dictionary
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for address"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BasicDetailsSerializer(detail, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 3. Trade License Exist
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def trade_license_exist_list(request):
    if request.method == 'GET':
        licenses = TradeLicenseExistOrNot.objects.all()
        serializer = TradeLicenseExistOrNotSerializer(licenses, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            data = request.data.copy()
            if 'trade_license_file' not in request.FILES:
                data.pop('trade_license_file', None)
            if 'upload_photo' not in request.FILES:
                data.pop('upload_photo', None)
            if 'address' in data:
                address_data = data.get('address')
                if isinstance(address_data, str):
                    try:
                        address_data = json.loads(address_data)  # Convert string to dict
                        data['address'] = address_data
                    except json.JSONDecodeError:
                        return Response({"error": "Invalid JSON format for address"},
                                        status=status.HTTP_400_BAD_REQUEST)
            try:
                licenses = TradeLicenseExistOrNot.objects.get(license_id=data['license'])
                serializer = TradeLicenseExistOrNotSerializer(licenses,data=data,partial=True)
            except:
                serializer = TradeLicenseExistOrNotSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format for address"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def trade_license_exist(request, pk):
    applicant = TradeLicenseExistOrNot.objects.get(license_id=pk)
    if request.method == 'GET':
        serializer = TradeLicenseExistOrNotSerializer(applicant)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        serializer = TradeLicenseExistOrNotSerializer(applicant, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        applicant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 5. Trade Entity
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def trade_entity_list(request):
    if request.method == 'GET':
        entities = TradeEntity.objects.all()
        serializer = TradeEntitySerializerRetrieval(entities, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data

        # ✅ Ensure 'address' is parsed correctly
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format for address"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            entities = TradeEntity.objects.get(license_id=data['license'])
            serializer = TradeEntitySerializer(entities,data=data,partial=True)
        except:
            serializer = TradeEntitySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def trade_entity_detail(request, pk):
    try:
        entity = TradeEntity.objects.get(license_id=pk)
    except TradeEntity.DoesNotExist:
        return Response({"error": "Trade Entity not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TradeEntitySerializerRetrieval(entity)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'address' in data:
            address_data = data.get('address')
            if isinstance(address_data, str):
                try:
                    address_data = json.loads(address_data)
                    data['address'] = address_data
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON format for address"},
                                    status=status.HTTP_400_BAD_REQUEST)
        serializer = TradeEntitySerializer(entity, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        entity.delete()
        return Response({"message": "Trade Entity deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# 6. Partner Details
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser,JSONParser])
def partner_details_list(request):
    if request.method == 'GET':
        partners = PartnerDetails.objects.all()
        serializer = PartnerDetailsSerializer(partners, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        if 'license' in data:
            existing_partners = PartnerDetails.objects.filter(
                license_id=data.get('license'),
                partner_name=data.get('partner_name'),
                partner_address=data.get('partner_address'),
                designation=data.get('designation')
            )
            if existing_partners.exists():
                return Response(
                    {"error": "A partner with the same details already exists for this trade_license"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = PartnerDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)

        return JsonResponse(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def partner_details(request, pk):
    try:
        partner = PartnerDetails.objects.filter(license_id=pk)
    except PartnerDetails.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = PartnerDetailsSerializer(partner,many=True)
        return Response(serializer.data)

    elif request.method == 'PUT':
        partner = PartnerDetails.objects.get(pk=pk)
        data = request.data.copy()
        serializer = PartnerDetailsSerializer(partner, data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        partner = PartnerDetails.objects.filter(pk=pk)
        partner.delete()
        return Response({"message": "Deleted Successfully"},status=204)