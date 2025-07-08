from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PayrollWorkflow
from .serializers import PayrollWorkflowSerializer


@api_view(['POST'])
def payroll_workflow_create(request):
    try:
        serializer = PayrollWorkflowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def payroll_workflow_list(request):
    try:
        workflows = PayrollWorkflow.objects.all()
        serializer = PayrollWorkflowSerializer(workflows, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def payroll_workflow_detail_or_create(request):
    try:
        payroll_id = request.query_params.get('payroll')
        month = request.query_params.get('month')
        financial_year = request.query_params.get('financial_year')

        if not all([payroll_id, month, financial_year]):
            return Response(
                {"error": "Missing query parameters: 'payroll', 'month', and 'financial_year' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to find the workflow
        workflow = PayrollWorkflow.objects.filter(
            payroll_id=payroll_id,
            month=month,
            financial_year=financial_year
        ).first()

        if workflow:
            serializer = PayrollWorkflowSerializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Else create a new one
        default_data = {
            "payroll": payroll_id,
            "month": int(month),
            "financial_year": financial_year,
            "new_joinees": "in progress",
            "exits": "in progress",
            "attendance": "in progress",
            "bonuses": "in progress",
            "salary_revision": "in progress",
            "tds": "in progress",
            "finalize": False
        }

        serializer = PayrollWorkflowSerializer(data=default_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def payroll_workflow_update(request, pk):
    try:
        workflow = PayrollWorkflow.objects.get(pk=pk)
        serializer = PayrollWorkflowSerializer(workflow, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except PayrollWorkflow.DoesNotExist:
        return Response({"error": "PayrollWorkflow not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def payroll_workflow_delete(request, pk):
    try:
        workflow = PayrollWorkflow.objects.get(pk=pk)
        workflow.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except PayrollWorkflow.DoesNotExist:
        return Response({"error": "PayrollWorkflow not found"}, status=status.HTTP_404_NOT_FOUND)
