import base64
import numpy as np
from django.utils.timezone import now, localtime
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from .models import EmployeeCredentials, EmployeeSalaryHistory, EmployeeSalaryDetails
from .serializers import (EmployeeCredentialsSerializer, EmployeeSalaryHistorySerializer, EmployeeSalaryDetailsSerializer,
                          EmployeeFinancialYearPayslipSerializer)
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange, month_name
from rest_framework.permissions import AllowAny
from .employee_salary_details import get_valid_fy_months_upto
from collections import defaultdict
from .views import number_to_words_in_indian_format
from django.db.models import Sum
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.exceptions import ValidationError
from .tokens import employee_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from django.conf import settings
from Tara.settings.default import *


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def tds_summary_view(request):
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

    # Valid months in FY up to selected month
    valid_months = get_valid_fy_months_upto(selected_month)

    salaries = EmployeeSalaryHistory.objects.filter(
        employee_id=employee.employee,
        financial_year=financial_year,
        month__in=valid_months,
    ).order_by("month")

    last_month_record = salaries.order_by("-month").first()
    if selected_month > last_month_record.month and selected_month != datetime.now().month:
        return Response({'error': 'Selected month exceeds the last available salary record'},
                        status=status.HTTP_400_BAD_REQUEST)
    if selected_month == datetime.now().month:
        return Response({"message": "Salary processing will be initiated between the 26th and 30th of the month."},
                        status=status.HTTP_200_OK)
    total_tds_deducted = last_month_record.tds_ytd if last_month_record else 0
    tds_deducted = last_month_record.tds if last_month_record else 0
    tax_regime = employee.employee.employee_salary.tax_regime_opted if employee.employee.employee_salary else None


    monthly_data = []
    previous_ctc = 0

    for salary in salaries:
        if previous_ctc !=0 and previous_ctc != salary.ctc:
            note = "CTC revised this month"
        elif salary.bonus_incentive > 0:
            note = "Bonus/Incentive received this month"
        elif salary.lop > 0:
            note = "Salary adjusted due to Loss of Pay (LOP)"
        else:
            note = "-"
        previous_ctc = salary.ctc
        year_part = financial_year.split('-')[0] if salary.month >= 4 else financial_year.split('-')[1]
        month_label = f"{month_name[salary.month]} {year_part}"
        monthly_data.append({
            "month_label": month_label,
            "month": salary.month,
            "tds_deducted": salary.tds,
            "gross_income": salary.earned_salary,
            "net_salary": salary.net_salary,
            "notes": note,
        })

    response_data = {
        "employee": EmployeeCredentialsSerializer(employee).data,
        "employee_id": employee.employee.associate_id,
        "tds_deducted": tds_deducted,
        "total_tds_ytd": total_tds_deducted,
        "till_month": last_month_record.month,
        "tax_regime": tax_regime,
        "monthly_summary": monthly_data,
    }

    return Response(response_data)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def change_password(request):
    """
    Check the current password for the authenticated employee. If the password is correct, allow the user to change it.
    Change the password for the authenticated employee.

    Args:
    - request: The HTTP request containing the new password and the current password.

    Returns:
    - Success: Message indicating password change was successful.
    - Error: Error message with appropriate status code.
    """
    creds = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        raise ValidationError({"error": "Both 'old_password' and 'new_password' are required."})

    # Check if the old password is correct
    if not creds.check_password(old_password):
        raise ValidationError({"error": "Old password is incorrect."})

    # Get the new password from the request data
    new_password = request.data.get('new_password')

    creds.set_password(new_password)
    creds.save()

    return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Handle forgot password request for the authenticated employee.

    Args:
    - request: The HTTP request containing the new password.

    Returns:
    - Success: Message indicating password reset was successful.
    - Error: Error message with appropriate status code.
    """
    email_or_username = request.data.get('email_or_username')
    if not email_or_username:
        raise ValidationError({"error": "Email or Username is required."})

    try:
        creds = EmployeeCredentials.objects.get(username=email_or_username)
    except EmployeeCredentials.DoesNotExist:
        try:
            creds = EmployeeCredentials.objects.get(employee__work_email=email_or_username)
        except EmployeeCredentials.DoesNotExist:
            raise ValidationError({"error": "Employee not found with the provided email or username."})

    email = creds.employee.work_email
    token = employee_token_generator.make_token(creds)
    uid = urlsafe_base64_encode(str(creds.pk).encode())
    reset_link = f"{Reference_link}employee-login/reset-password?uid={uid}&token={token}"


    try:
        ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        subject = "Reset Your Password"
        body = f"""
        Hello {creds.employee.first_name}{' ' + creds.employee.middle_name if creds.employee.middle_name else ''}{' ' + creds.employee.last_name if creds.employee.last_name else ''},

        You requested to reset your password. Click the link below to reset it:
        {reset_link}

        If you did not request this, please ignore this email.

        Thanks,
        TaraFirst
        """

        response = ses_client.send_email(
            Source=settings.EMAIL_HOST_USER,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        return Response({"message": "You will receive a reset link."},
                        status=status.HTTP_200_OK)

    except (BotoCoreError, ClientError) as e:
        # Log SES-related errors
        return Response({"message": "Unable to send reset email. Please try again later."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset the password for an employee using a token and user ID.

    Args:
    - request: The HTTP request containing the new password, user ID, and token.

    Returns:
    - Success: Message indicating password reset was successful.
    - Error: Error message with appropriate status code.
    """
    password = request.data.get("password")
    if not password:
        raise ValidationError("Password is required.")

    uid_b64 = request.query_params.get("uid")
    token = request.query_params.get("token")

    if not uid_b64 or not token:
        return Response({"message": "Missing UID or token in query parameters."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = urlsafe_base64_decode(uid_b64).decode()
        creds = EmployeeCredentials.objects.get(pk=uid)
    except (ValueError, EmployeeCredentials.DoesNotExist):
        raise ValidationError({"error": "Invalid user ID."})

    if not employee_token_generator.check_token(creds, token):
        raise ValidationError({"error": "Invalid or expired token."})
    if employee_token_generator.check_token(creds, token):
        creds.set_password(password)
        creds.save()

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

    return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

