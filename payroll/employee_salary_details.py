import base64
import numpy as np
from django.utils.timezone import now, localtime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeCredentials, EmployeeSalaryHistory, EmployeeSalaryDetails
from .serializers import (EmployeeCredentialsSerializer, EmployeeSalaryHistorySerializer, EmployeeSalaryDetailsSerializer,
                          EmployeeFinancialYearPayslipSerializer)
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange, month_name
from rest_framework import status
from collections import defaultdict
from .views import number_to_words_in_indian_format
from django.db.models import Sum


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def employee_payslip_details(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    month = request.query_params.get('month', now().month)
    financial_year = request.query_params.get('financial_year')


    try:
        salary_details = EmployeeSalaryHistory.objects.filter(employee=employee.employee,
                                month=month, financial_year=financial_year).first()
        if not salary_details:
            return Response({'error': 'Salary details not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSalaryHistorySerializer(salary_details)
        data = serializer.data.copy()
        data['bank_name'] = employee.employee.employee_bank_details.bank_name if (
            employee.employee.employee_bank_details.bank_name) else None
        data['bank_account_number'] = employee.employee.employee_bank_details.account_number if (
            employee.employee.employee_bank_details.account_number) else None
        data['pf_account_number'] = employee.employee.statutory_components.get('employee_provident_fund',
                        {}).get('pf_account_number') if (employee.employee.statutory_components.get('epf_enabled') is
                                                         True) else None
        data['net_pay_in_words'] = number_to_words_in_indian_format(data['net_salary']).title() + " Rupees Only"

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_valid_fy_months_upto(month_limit):
    """
    Returns a list of fiscal year months from April (4) up to the given month (inclusive),
    wrapping correctly through Jan/Feb/Mar if needed.
    """
    fiscal_months = list(range(4, 13)) + list(range(1, 4))  # [4,5,6,...12,1,2,3]
    result = []

    for m in fiscal_months:
        result.append(m)
        if m == month_limit:
            break

    return result


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_month_and_ytd_salary_data(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    selected_month = request.query_params.get('month')

    if not financial_year or not selected_month:
        return Response({'error': 'financial_year and month are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        selected_month = int(selected_month)
    except ValueError:
        return Response({'error': 'Invalid month value'}, status=status.HTTP_400_BAD_REQUEST)

    today = date.today()
    current_month = today.month

    if selected_month > current_month:
        return Response({'error': 'You cannot access future months'}, status=status.HTTP_400_BAD_REQUEST)

    if selected_month == current_month and today.day < 26:
        return Response({'error': 'You cannot access the current month before the 26th'},
                        status=status.HTTP_400_BAD_REQUEST)

    valid_months = get_valid_fy_months_upto(selected_month)

    salary_qs = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year,
        month__in=valid_months
    ).order_by('month')

    if not salary_qs.exists():
        return Response({'message': 'No salary records found'}, status=status.HTTP_200_OK)

    earnings_fields = [
        "basic_salary", "hra", "conveyance_allowance", "travelling_allowance",
        "commission", "children_education_allowance", "overtime_allowance",
        "transport_allowance", "special_allowance", "bonus"
    ]
    deduction_fields = [
        "epf", "esi", "pt", "tds", "loan_emi"
    ]

    month_earnings = defaultdict(float)
    ytd_earnings = defaultdict(float)
    month_deductions = defaultdict(float)
    ytd_deductions = defaultdict(float)

    total_net_salary_month = 0.0
    total_net_salary_ytd = 0.0
    total_gross_income_month = 0.0
    total_gross_income_ytd = 0.0
    total_deduction_month = 0.0
    total_deduction_ytd = 0.0

    for record in salary_qs:
        is_selected_month = (record.month == selected_month)

        # Earnings
        for field in earnings_fields:
            value = getattr(record, field, 0) or 0
            ytd_earnings[field] += value
            if is_selected_month:
                month_earnings[field] = value

        for item in record.other_earnings_breakdown or []:
            for k, v in item.items():
                ytd_earnings[k] += v or 0
                if is_selected_month:
                    month_earnings[k] = v or 0

        # Deductions
        for field in deduction_fields:
            value = getattr(record, field, 0) or 0
            ytd_deductions[field] += value
            if is_selected_month:
                month_deductions[field] = value

        for item in record.other_deductions_breakdown or []:
            for k, v in item.items():
                ytd_deductions[k] += v or 0
                if is_selected_month:
                    month_deductions[k] = v or 0

        total_net_salary_ytd += record.net_salary or 0
        total_gross_income_ytd += record.earned_salary or 0
        total_deduction_ytd += record.total_deductions or 0

        if is_selected_month:
            total_net_salary_month = record.net_salary or 0
            total_gross_income_month = record.earned_salary or 0
            total_deduction_month = record.total_deductions or 0

    # Format earnings in given order
    earnings = []
    for key in earnings_fields + [k for k in month_earnings.keys() if k not in earnings_fields]:
        month_val = round(month_earnings.get(key, 0), 2)
        ytd_val = round(ytd_earnings.get(key, 0), 2)
        if month_val > 0 or ytd_val > 0:
            earnings.append({
                "component_name": key.replace("_", " ").title(),
                "month_data": month_val,
                "ytd": ytd_val
            })

    # Format deductions in given order
    deductions = []
    for key in deduction_fields + [k for k in month_deductions.keys() if k not in deduction_fields]:
        month_val = round(month_deductions.get(key, 0), 2)
        ytd_val = round(ytd_deductions.get(key, 0), 2)
        if month_val > 0 or ytd_val > 0:
            deductions.append({
                "component_name": key.replace("_", " ").title(),
                "month_data": month_val,
                "ytd": ytd_val
            })

    # Final summary
    response_data = {
        "earnings": earnings,
        "deductions": deductions,
        "gross_income": {
            "month_data": round(total_gross_income_month, 2),
            "ytd": round(total_gross_income_ytd, 2)
        },
        "net_salary": {
            "month_data": round(total_net_salary_month, 2),
            "ytd": round(total_net_salary_ytd, 2)
        },
        "deduction_total": {
            "month_data": round(total_deduction_month, 2),
            "ytd": round(total_deduction_ytd, 2)
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_employee_financial_year_payslip_details(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    if not financial_year:
        return Response({'error': 'financial_year is required'}, status=status.HTTP_400_BAD_REQUEST)

    salary_history = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year
    ).order_by('-month')

    if not salary_history.exists():
        return Response([], status=status.HTTP_200_OK)

    serializer = EmployeeFinancialYearPayslipSerializer(salary_history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_pf_breakdown(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    selected_month = request.query_params.get('month')

    if not financial_year or not selected_month:
        return Response({'error': 'financial_year and month are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        selected_month = int(selected_month)
    except ValueError:
        return Response({'error': 'Invalid month value'}, status=status.HTTP_400_BAD_REQUEST)

    # 🔐 Restriction: Disallow access to future months and current month if today is before the 26th
    today = date.today()
    current_month = today.month

    if selected_month > current_month:
        return Response({'error': 'You cannot access future months'}, status=status.HTTP_400_BAD_REQUEST)

    if selected_month == current_month and today.day < 26:
        return Response({'error': 'You cannot access the current month before the 26th'}, status=status.HTTP_400_BAD_REQUEST)

    valid_months = get_valid_fy_months_upto(selected_month)

    salary_qs = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year,
        month__in=valid_months
    ).order_by('month')

    if not salary_qs.exists():
        return Response({'message': 'No salary records found'}, status=status.HTTP_200_OK)

    employee_pf_month = 0.0
    employee_pf_ytd = 0.0
    employer_pf_month = 0.0
    employer_pf_ytd = 0.0

    for record in salary_qs:
        is_selected_month = (record.month == selected_month)

        # Employee PF
        epf = record.epf or 0
        employee_pf_ytd += epf
        if is_selected_month:
            employee_pf_month = epf
            employer_pf_month = min(((record.gross_salary or 0) * 0.5) * 0.12, 1800)

    employer_pf_ytd = employer_pf_month * len(valid_months)

    pf_breakdown = {
        "employee_pf": {
            "month_data": round(employee_pf_month, 2),
            "ytd": round(employee_pf_ytd, 2)
        },
        "employer_pf": {
            "month_data": round(employer_pf_month, 2),
            "ytd": round(employer_pf_ytd, 2)
        },
        "total_pf": {
            "month_data": round(employee_pf_month + employer_pf_month, 2),
            "ytd": round(employee_pf_ytd + employer_pf_ytd, 2)
        }
    }

    return Response(pf_breakdown, status=status.HTTP_200_OK)

