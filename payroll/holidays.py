from payroll.models import HolidayManagement, EmployeeCredentials, PayrollOrg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from payroll.serializers import HolidayManagementSerializer
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange
from rest_framework import status
from django.utils.timezone import now, localtime
from collections import defaultdict


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_month_wise_holiday_calendar(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    employee_obj = employee.employee
    payroll = employee_obj.payroll

    try:
        month = int(request.query_params.get('month', now().month))
    except ValueError:
        return Response({'error': 'Invalid month'}, status=400)

    try:
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid year'}, status=400)

    start_of_month = date(year, month, 1)
    end_of_month = date(year, month, monthrange(year, month)[1])

    holidays = HolidayManagement.objects.filter(
        payroll_id=payroll,
        start_date__lte=end_of_month,
        end_date__gte=start_of_month,
        applicable_for=employee_obj.work_location,
    )

    flat_holiday_list = []

    for holiday in holidays:
        current_date = max(holiday.start_date, start_of_month)
        end_date = min(holiday.end_date, end_of_month)

        while current_date <= end_date:
            flat_holiday_list.append({
                "date": current_date.strftime("%d-%m-%Y"),
                "title": holiday.holiday_name,
                "type": "holiday"
            })
            current_date += timedelta(days=1)

    return Response(flat_holiday_list)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_yearly_holiday_calendar(request):

    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    employee_obj = employee.employee
    payroll = employee_obj.payroll

    try:
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid year'}, status=400)

    # Start and end of the year
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)

    # Fetch holidays overlapping this year and applicable to employee’s location
    holidays = HolidayManagement.objects.filter(
        payroll_id=payroll,
        start_date__lte=end_of_year,
        end_date__gte=start_of_year,
        applicable_for=employee_obj.work_location,
    )

    # Prepare flat list of holidays
    holiday_list = []

    for holiday in holidays:
        current_date = max(holiday.start_date, start_of_year)
        end_date = min(holiday.end_date, end_of_year)

        while current_date <= end_date:
            holiday_list.append({
                "date": current_date.strftime("%d-%m-%Y"),
                "title": holiday.holiday_name,
                "type": "holiday"
            })
            current_date += timedelta(days=1)

    return Response(holiday_list)
