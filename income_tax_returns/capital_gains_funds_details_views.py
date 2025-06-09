from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db import transaction
from .models import CapitalGainsEquityMutualFund, CapitalGainsEquityMutualFundDocument
from .serializers import CapitalGainsEquityMutualFundSerializer, CapitalGainsEquityMutualFundDocumentSerializer
import json


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_equity_mutual_fund_with_files(request):
    try:
        request_data = request.data.copy()

        # Coerce investment_types if sent as a string
        investment_types = request_data.get('equity_mutual_fund_type')
        if isinstance(investment_types, str):
            try:
                request_data['equity_mutual_fund_type'] = json.dumps(json.loads(investment_types))
            except json.JSONDecodeError:
                return Response({"investment_types": "Invalid JSON format"}, status=400)
        service_request = request.data.get('service_request')
        service_task = request.data.get('service_task')

        if not service_request or not service_task:
            return Response({"error": "Missing service_request or service_task"}, status=400)

        try:
            instance = CapitalGainsEquityMutualFund.objects.get(service_request=service_request)
            serializer = CapitalGainsEquityMutualFundSerializer(instance, data=request_data, partial=True)
        except CapitalGainsEquityMutualFund.DoesNotExist:
            serializer = CapitalGainsEquityMutualFundSerializer(data=request_data)

        with transaction.atomic():
            if serializer.is_valid(raise_exception=True):
                fund_instance = serializer.save()

                # Handle multiple file uploads
                files = request.FILES.getlist('documents')
                for file in files:
                    CapitalGainsEquityMutualFundDocument.objects.create(
                        capital_gains_equity_mutual_fund=fund_instance,
                        file=file
                    )

                return Response({
                    "message": "Capital Gains Equity Mutual Fund details saved",
                    "data": serializer.data,
                    "files_uploaded": len(files)
                }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_equity_mutual_fund_details(request, service_request_id):
    try:
        fund = CapitalGainsEquityMutualFund.objects.get(service_request_id=service_request_id)
        serializer = CapitalGainsEquityMutualFundSerializer(fund)

        return Response(serializer.data, status=200)

    except CapitalGainsEquityMutualFund.DoesNotExist:
        return Response({"error": "Details not found"}, status=404)


@api_view(['DELETE'])
def delete_equity_mutual_fund(request, service_request_id):
    try:
        fund = CapitalGainsEquityMutualFund.objects.get(service_request__id=service_request_id)
        fund.delete()
        return Response({"message": "Deleted successfully"})

    except CapitalGainsEquityMutualFund.DoesNotExist:
        return Response({"error": "Record not found"}, status=404)


@api_view(['DELETE'])
def delete_equity_mutual_fund_file(request, file_id):
    try:
        doc = CapitalGainsEquityMutualFundDocument.objects.get(id=file_id)
        doc.delete()
        return Response({"message": "File deleted"})

    except CapitalGainsEquityMutualFundDocument.DoesNotExist:
        return Response({"error": "File not found"}, status=404)



