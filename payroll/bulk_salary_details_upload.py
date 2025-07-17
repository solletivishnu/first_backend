from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime
from .models import EmployeeSalaryDetails, EmployeeManagement, PayrollOrg, Earnings
from .generate_salary_upload_template import default_earnings, default_benefits, default_deductions, Deduction
from .serializers import EarningsSerializer, DeductionSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_employee_salary_excel(request):
    payroll_id = request.data.get('payroll_id')
    if not payroll_id:
        return Response({"error": "Payroll ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    payroll = PayrollOrg.objects.get(pk=payroll_id)
    if not payroll:
        return Response({"error": "Invalid Payroll ID."}, status=status.HTTP_400_BAD_REQUEST)

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

    def transform_row(row):
        # Get basic salary first for ESI calculations
        basic_monthly = get(row, "Monthly (Basic)", 0)

        record = {
            "annual_ctc": get(row, "Annual CTC", 0),
            "tax_regime_opted": get(row, "Tax Regime Opted", "old"),
            "earnings": [],
            "gross_salary": {
                "monthly": get(row, "Gross Salary (Monthly)", 0),
                "annually": get(row, "Gross Salary (Annually)", 0)
            },
            "benefits": [],
            "total_ctc": {
                "monthly": get(row, "Total CTC (Monthly)", 0),
                "annually": get(row, "Total CTC (Annually)", 0)
            },
            "deductions": [],
            "net_salary": {
                "monthly": get(row, "Net Salary (Monthly)", 0),
                "annually": get(row, "Net Salary (Annually)", 0)
            },
            "valid_from": datetime.today().strftime("%Y-%m-%d"),
            "valid_to": None,
            "created_on": datetime.today().strftime("%Y-%m-%d"),
            "created_month": datetime.today().month,
            "created_year": datetime.today().year,
            "employee": EmployeeManagement.objects.get(pk=get(row, "Employee Id", None)),
        }

        earnings = EarningsSerializer(Earnings.objects.filter(payroll=payroll).order_by('id'), many=True).data

        # Process Earnings
        for earning in earnings:
            component = earning['component_name']
            ct = earning['calculation_type']['type']

            if ct == "Percentage of CTC":
                input_col = f"{component} (% of CTC)"
            elif ct == "Percentage of Basic":
                input_col = f"{component} (% of Basic)"
            elif ct == "Flat Amount":
                input_col = f"{component} (Flat Amount)"
            else:
                input_col = component

            earning_data = {
                "component_name": component,
                "monthly": get(row, f"Monthly ({component})", 0),
                "annually": get(row, f"Annually ({component})", 0),
                "calculation": get(row, input_col, 0),
                "calculation_type": ct
            }

            if earning_data['monthly'] or earning_data['annually']:
                record["earnings"].append(earning_data)

        # Process Benefits
        for benefit in default_benefits:
            component = benefit['component_name']
            ct = benefit['calculation_type']['type']

            benefit_data = {
                "component_name": component,
                "monthly": get(row, f"Monthly ({component})", "NA"),
                "annually": get(row, f"Annually ({component})", "NA"),
                "calculation_type": ct if ct != "Not Applicable" else "Not Applicable"
            }

            # Special handling for ESI Employer
            if component == "ESI Employer Contribution":
                if basic_monthly <= 21000:
                    benefit_data.update({
                        "monthly": get(row, f"Monthly ({component})", 0),
                        "calculation_type": "Percentage (3.25%) of PF wage"
                    })

            record["benefits"].append(benefit_data)

        # Process Deductions
        for deduction in default_deductions:
            component = deduction['component_name']
            ct = deduction['calculation_type']['type']


            deduction_data = {
                "component_name": component,
                "monthly": get(row, f"Monthly ({component})", "NA"),
                "annually": get(row, f"Annually ({component})", "NA"),
                "calculation_type": ct if ct != "Not Applicable" else "Not Applicable"
            }

            # Special handling for ESI Employee and Professional Tax
            if component == "ESI Employee Contribution":
                if basic_monthly <= 21000:
                    deduction_data.update({
                        "monthly": get(row, f"Monthly ({component})", 0),
                        "calculation_type": "Percentage (0.75%) of PF wage"
                    })
            elif component == "Professional Tax (PT)":
                deduction_data.update({
                    "monthly": get(row, f"Monthly ({component})", 200),
                    "calculation_type": "Fixed Amount"
                })

            record["deductions"].append(deduction_data)
        deduction_data = DeductionSerializer(Deduction.objects.filter(payroll=payroll).order_by('id'), many=True).data

        for deduction_row in deduction_data:
            # Get component and calculation type
            component = deduction_row['deduction_name']
            ct = deduction_row['calculation_type']['type']
            if ct == "Percentage of CTC":
                input_col = f"{component} (% of CTC)"
            elif ct == "Percentage of Basic":
                input_col = f"{component} (% of Basic)"
            elif ct == "Flat Amount":
                input_col = f"{component} (Flat Amount)"
            else:
                input_col = component

            deduction_data = {
                "component_name": component,
                "monthly": get(row, f"Monthly ({component})", "NA"),
                "annually": get(row, f"Annually ({component})", "NA"),
                "calculation_type": get(row, input_col, 0)
            }
            if deduction_data['monthly'] or deduction_data['annually']:
                record["deductions"].append(deduction_data)

        return record

    records = []
    errors = []
    for i, row in df.iterrows():
        try:
            records.append(transform_row(row))
        except Exception as e:
            errors.append(f"Row {i + 2}: Error processing - {str(e)}")

    created_objs = []
    if records:
        try:
            created_objs = [EmployeeSalaryDetails(**data) for data in records]
            EmployeeSalaryDetails.objects.bulk_create(created_objs)
        except Exception as e:
            errors.append(f"Bulk create error: {str(e)}")

    return Response({
        "created_count": len(created_objs),
        "error_count": len(errors),
        "errors": errors
    }, status=status.HTTP_200_OK if len(created_objs) > 0 else status.HTTP_400_BAD_REQUEST)
