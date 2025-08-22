from payroll.models import HolidayManagement, EmployeeCredentials, PayrollOrg, EventManagement
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


def get_holidays_for_period(payroll, work_location, start_date, end_date):
    """
    Helper function to fetch holidays for a given period.
    
    Args:
        payroll: PayrollOrg instance
        work_location: Employee's work location
        start_date: Start date of the period
        end_date: End date of the period
    
    Returns:
        QuerySet of holidays overlapping the period
    """
    return HolidayManagement.objects.filter(
        payroll_id=payroll,
        start_date__lte=end_date,
        end_date__gte=start_date,
        applicable_for=work_location,
    )


def get_events_for_period(payroll, work_location, start_date, end_date):
    """
    Helper function to fetch events for a given period.
    
    Args:
        payroll: PayrollOrg instance
        work_location: Employee's work location
        start_date: Start date of the period
        end_date: End date of the period
    
    Returns:
        QuerySet of events in the period
    """
    return EventManagement.objects.filter(
        payroll=payroll,
        date__gte=start_date,
        date__lte=end_date,
        is_birthday=False,  # Exclude birthdays, handle separately
        applicable_to=work_location,
    )


def get_birthdays_for_year(payroll, work_location, year):
    """
    Helper function to fetch birthdays for a given year.
    
    Args:
        payroll: PayrollOrg instance
        work_location: Employee's work location
        year: Year to fetch birthdays for
    
    Returns:
        QuerySet of birthdays with birth year <= requested year
    """
    return EventManagement.objects.filter(
        payroll=payroll,
        is_birthday=True,
        date__year__lte=year,  # Only birthdays with birth year <= requested year
        applicable_to=work_location,
    )


def process_holidays_to_list(holidays, start_date, end_date):
    """
    Helper function to process holidays into a flat list.
    
    Args:
        holidays: QuerySet of holidays
        start_date: Start date of the period
        end_date: End date of the period
    
    Returns:
        List of holiday dictionaries
    """
    holiday_list = []
    for holiday in holidays:
        current_date = max(holiday.start_date, start_date)
        holiday_end_date = min(holiday.end_date, end_date)

        while current_date <= holiday_end_date:
            holiday_list.append({
                "date": current_date.strftime("%d-%m-%Y"),
                "title": holiday.holiday_name,
                "type": "holiday"
            })
            current_date += timedelta(days=1)
    
    return holiday_list


def process_events_to_list(events):
    """
    Helper function to process events into a flat list.
    
    Args:
        events: QuerySet of events
    
    Returns:
        List of event dictionaries
    """
    event_list = []
    for event in events:
        event_list.append({
            "date": event.date.strftime("%d-%m-%Y"),
            "title": event.title,
            "description": event.description,
            "time": event.time.strftime("%H:%M") if event.time else None,
            "type": "event"
        })
    
    return event_list


def process_birthdays_to_list(birthdays, year, start_date, end_date):
    """
    Helper function to process birthdays into a flat list.
    
    Args:
        birthdays: QuerySet of birthdays
        year: Year to calculate birthdays for
        start_date: Start date of the period
        end_date: End date of the period
    
    Returns:
        List of birthday dictionaries
    """
    birthday_list = []
    for birthday in birthdays:
        # Calculate birthday date for the current year
        birthday_this_year = birthday.date.replace(year=year)
        
        # Check if birthday falls within the requested period
        if start_date <= birthday_this_year <= end_date:
            birthday_list.append({
                "date": birthday_this_year.strftime("%d-%m-%Y"),
                "title": f"🎂 {birthday.title}",
                "description": birthday.description,
                "time": birthday.time.strftime("%H:%M") if birthday.time else None,
                "type": "birthday",
                "employee_name": birthday.employee.first_name if birthday.employee else None
            })
    
    return birthday_list


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_month_wise_holiday_calendar(request):
    """
    Get monthly calendar with holidays, events, and birthdays for the authenticated employee.
    
    Returns a flat list of all calendar items (holidays, events, birthdays) for the specified month.
    Birthdays are recurring yearly, so they're calculated for the current year.
    Birthdays won't show for years before the employee's birth year.
    """
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

    # Fetch data using helper functions
    holidays = get_holidays_for_period(payroll, employee_obj.work_location, start_of_month, end_of_month)
    events = get_events_for_period(payroll, employee_obj.work_location, start_of_month, end_of_month)
    birthdays = get_birthdays_for_year(payroll, employee_obj.work_location, year)

    # Process data using helper functions
    flat_calendar_list = []
    flat_calendar_list.extend(process_holidays_to_list(holidays, start_of_month, end_of_month))
    flat_calendar_list.extend(process_events_to_list(events))
    flat_calendar_list.extend(process_birthdays_to_list(birthdays, year, start_of_month, end_of_month))

    # Sort by date
    flat_calendar_list.sort(key=lambda x: datetime.strptime(x["date"], "%d-%m-%Y"))

    return Response(flat_calendar_list)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_yearly_holiday_calendar(request):
    """
    Get yearly calendar with holidays, events, and birthdays for the authenticated employee.
    
    Returns a flat list of all calendar items (holidays, events, birthdays) for the specified year.
    Birthdays are recurring yearly, so they're calculated for the current year.
    Birthdays won't show for years before the employee's birth year.
    """
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

    # Fetch data using helper functions
    holidays = get_holidays_for_period(payroll, employee_obj.work_location, start_of_year, end_of_year)
    events = get_events_for_period(payroll, employee_obj.work_location, start_of_year, end_of_year)
    birthdays = get_birthdays_for_year(payroll, employee_obj.work_location, year)

    # Process data using helper functions
    calendar_list = []
    calendar_list.extend(process_holidays_to_list(holidays, start_of_year, end_of_year))
    calendar_list.extend(process_events_to_list(events))
    calendar_list.extend(process_birthdays_to_list(birthdays, year, start_of_year, end_of_year))

    # Sort by date
    calendar_list.sort(key=lambda x: datetime.strptime(x["date"], "%d-%m-%Y"))

    return Response(calendar_list)