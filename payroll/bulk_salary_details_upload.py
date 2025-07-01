from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime
from .models import EmployeeSalaryDetails, EmployeeManagement


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_employee_salary_excel(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    file_name = file_obj.name.lower()
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_obj, sheet_name='SalaryTemplate', engine='openpyxl')
        elif file_name.endswith('.xls'):
            df = pd.read_excel(file_obj, sheet_name='SalaryTemplate', engine='xlrd')
        elif file_name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        else:
            return Response({"error": "Unsupported file format. Please upload .xlsx, .xls or .csv"}, status=400)
    except Exception as e:
        return Response({"error": f"Failed to read file: {str(e)}"}, status=400)

    def get(row, val, default=None):
        v = row.get(val, default)
        if pd.isna(v) or v == 'nan':
            return default
        return v

    # Dynamically determine max index for earnings, benefits, deductions
    def max_index(prefix):
        return max([
            int(col.split('_')[1])
            for col in df.columns if col.startswith(prefix)
        ] or [0])

    max_earnings = max_index('earning_')
    max_benefits = max_index('benefit_')
    max_deductions = max_index('deduction_')

    def is_empty_earning(e):
        return (
            (e.get('monthly') in [0, None, '', 'NA', 'nan'] or pd.isna(e.get('monthly')))
            and (e.get('annually') in [0, None, '', 'NA', 'nan'] or pd.isna(e.get('annually')))
        )

    def transform_row(row):
        record = {
            "annual_ctc": get(row, "annual_ctc", 0),
            "tax_regime_opted": get(row, "tax_regime_opted", "old"),
            "earnings": [],
            "gross_salary": {
                "monthly": get(row, "gross_salary_monthly", 0),
                "annually": get(row, "gross_salary_annually", 0)
            },
            "benefits": [],
            "total_ctc": {
                "monthly": get(row, "total_ctc_monthly", 0),
                "annually": get(row, "total_ctc_annually", 0)
            },
            "deductions": [],
            "net_salary": {
                "monthly": get(row, "net_salary_monthly", 0),
                "annually": get(row, "net_salary_annually", 0)
            },
            "valid_from": datetime.today().strftime("%Y-%m-%d"),
            "valid_to": None,
            "created_on": datetime.today().strftime("%Y-%m-%d"),
            "created_month": datetime.today().month,
            "created_year": datetime.today().year,
            "employee": EmployeeManagement.objects.get(pk=get(row, "employee_id", None)),
        }

        for i in range(1, max_earnings + 1):
            earning = {
                "component_name": get(row, f"earning_{i}_component_name", ""),
                "monthly": get(row, f"earning_{i}_monthly", 0),
                "annually": get(row, f"earning_{i}_annually", 0),
                "calculation": get(row, f"earning_{i}_calculation", 0),
                "calculation_type": get(row, f"earning_{i}_calculation_type", "")
            }
            if not is_empty_earning(earning):
                record["earnings"].append(earning)

        for i in range(1, max_benefits + 1):
            benefit = {
                "component_name": get(row, f"benefit_{i}_component_name", ""),
                "monthly": get(row, f"benefit_{i}_monthly", "NA"),
                "annually": get(row, f"benefit_{i}_annually", "NA"),
                "calculation_type": get(row, f"benefit_{i}_calculation_type", "Not Applicable")
            }
            record["benefits"].append(benefit)

        for i in range(1, max_deductions + 1):
            deduction = {
                "component_name": get(row, f"deduction_{i}_component_name", ""),
                "monthly": get(row, f"deduction_{i}_monthly", "NA"),
                "annually": get(row, f"deduction_{i}_annually", "NA"),
                "calculation_type": get(row, f"deduction_{i}_calculation_type", "Not Applicable")
            }
            record["deductions"].append(deduction)

        return record

    records = [transform_row(row) for _, row in df.iterrows()]
    objs = []
    errors = []
    for i, data in enumerate(records):
        try:
            objs.append(EmployeeSalaryDetails(**data))
        except Exception as e:
            errors.append(f"Row {i+2}: Error preparing record - {str(e)}")

    created_objs = []
    if objs:
        try:
            created_objs = EmployeeSalaryDetails.objects.bulk_create(objs)
        except Exception as e:
            errors.append(f"Bulk create error: {str(e)}")

    return Response({
        "created_count": len(created_objs),
        "error_count": len(errors),
        "errors": errors
    }, status=status.HTTP_200_OK if len(created_objs) > 0 else status.HTTP_400_BAD_REQUEST)
