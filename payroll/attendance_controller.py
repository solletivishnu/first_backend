import base64
import numpy as np
from datetime import datetime
from django.utils.timezone import now, localtime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AttendanceLog, EmployeeCredentials, AttendanceGeoTag
from .serializers import AttendanceLogSerializer, AttendanceGeoTagSerializer
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange
from rest_framework import status
from collections import defaultdict
from payroll.models import HolidayManagement
from payroll.models import PaySchedule
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def manual_check_in(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()
    location = request.data.get('location', '')
    device_info = request.data.get('device_info', '')

    # Get the latest log for today
    last_log = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today
    ).order_by('-check_in').first()

    # If last entry exists and not checked out yet — block duplicate check-in
    if last_log and last_log.check_in and not last_log.check_out:
        return Response({'message': 'You must check out before checking in again.'}, status=status.HTTP_400_BAD_REQUEST)

    # Else allow new check-in
    new_log = AttendanceLog.objects.create(
        employee=employee_credentials,
        date=today,
        check_in=localtime(now()),
        check_in_type='manual',
        location=location,
        device_info=device_info
    )

    # ✅ Send WebSocket notification
    channel_layer = get_channel_layer()
    context_id = employee_credentials.business.id
    business = employee_credentials.employee.payroll.business
    context = business.contexts  # reverse OneToOneField from Business to Context
    context_id = context.id
    group_name = f'business_{context_id}'  # Assuming FK: employee -> business

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': f'{employee_credentials.employee.first_name} {employee_credentials.employee.last_name} '
                       f'checked in at {new_log.check_in.strftime("%I:%M %p")}'
        }
    )

    serializer = AttendanceLogSerializer(new_log)
    return Response({'message': 'Check-in successful', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def manual_check_out(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()

    # Get the latest check-in with no checkout
    attendance = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today,
        check_out__isnull=True
    ).order_by('-check_in').first()

    if not attendance:
        return Response({'error': 'No active check-in record found for today'}, status=status.HTTP_404_NOT_FOUND)

    # Check out now
    attendance.check_out = localtime(now())
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({'message': 'Check-out successful', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def today_attendance_status(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()

    # Get all logs for today
    attendance_logs = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today
    ).order_by('check_in')

    if not attendance_logs.exists():
        return Response({'message': 'No attendance records for today'}, status=status.HTTP_200_OK)

    serializer = AttendanceLogSerializer(attendance_logs, many=True)

    return Response({
        'date': str(today),
        'logs': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def truetime_monthly_view(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    # Extract month & year
    try:
        month = int(request.query_params.get('month', now().month))
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid month/year'}, status=200)

    today = localtime(now()).date()
    # --- Restrict future months/years ---
    if year > today.year or (year == today.year and month > today.month):
        return Response({"message": "No data available for future months/years."})
    is_current_month = (month == today.month and year == today.year)
    last_day = today.day if is_current_month else monthrange(year, month)[1]

    all_dates = [date(year, month, day) for day in range(1, last_day + 1)]

    # Fetch all logs once
    logs = AttendanceLog.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        date__day__lte=last_day
    ).only('date', 'check_in', 'check_out').order_by('date', 'check_in')

    # Group logs by date
    grouped_logs = defaultdict(list)
    for log in logs:
        grouped_logs[log.date].append(log)

    report = []
    total_present_days = 0
    total_duration = timedelta()

    # 1. Get payroll and pay schedule
    employee_obj = request.user.employee  # EmployeeCredentials -> EmployeeManagement
    payroll = employee_obj.payroll
    pay_schedule = PaySchedule.objects.filter(payroll=payroll).first()

    # 2. Fetch holidays for the month
    first_day = date(year, month, 1)
    last_day_of_month = date(year, month, last_day)
    holidays = HolidayManagement.objects.filter(
        payroll=payroll,
        start_date__lte=last_day_of_month,
        end_date__gte=first_day,
        applicable_for=employee.employee.work_location
    )

    # 3. Build set of holiday dates
    holiday_dates = set()
    for holiday in holidays:
        current = max(holiday.start_date, first_day)
        end = min(holiday.end_date, last_day_of_month)
        while current <= end:
            holiday_dates.add(current)
            current += timedelta(days=1)

    # 2. Build set of week off dates
    week_off_dates = set()
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()  # Monday=0, Sunday=6

        # Check regular week offs
        if pay_schedule:
            if (weekday == 0 and pay_schedule.monday) or \
               (weekday == 1 and pay_schedule.tuesday) or \
               (weekday == 2 and pay_schedule.wednesday) or \
               (weekday == 3 and pay_schedule.thursday) or \
               (weekday == 4 and pay_schedule.friday) or \
               (weekday == 5 and pay_schedule.saturday) or \
               (weekday == 6 and pay_schedule.sunday):
                week_off_dates.add(current_date)

            # Second Saturday
            if pay_schedule.second_saturday and (8 <= day <= 14 and weekday == 5):
                week_off_dates.add(current_date)
            # Fourth Saturday
            if pay_schedule.fourth_saturday and (22 <= day <= 28 and weekday == 5):
                week_off_dates.add(current_date)

    # 3. Combine with holiday dates
    all_holiday_dates = holiday_dates | week_off_dates

    for log_date in all_dates:
        sessions = grouped_logs.get(log_date, [])
        session_count = len(sessions)

        time_pairs = []
        day_duration = timedelta()

        for session in sessions:
            in_time_str = localtime(session.check_in).strftime('%H:%M:%S') if session.check_in else "-"
            out_time_str = localtime(session.check_out).strftime('%H:%M:%S') if session.check_out else "-"
            time_pairs.append({
                "check_in": in_time_str,
                "check_out": out_time_str,
                "location": session.location if session.location else "-",
                "device_info": session.device_info if session.device_info else "-"
            })
            if session.check_in and session.check_out:
                day_duration += session.check_out - session.check_in

        if log_date in all_holiday_dates:
            status = "Holiday"
        elif session_count > 0:
            total_present_days += 1
            total_duration += day_duration
            status = "Present"
        else:
            status = "Absent"

        report.append({
            "date": log_date.strftime('%d-%m-%Y'),
            "sessions": time_pairs,
            "total_hours": str(day_duration).split('.')[0],
            "session_count": session_count,
            "status": status
        })

    avg_hours = total_duration / total_present_days if total_present_days else timedelta()

    return Response({
        "month": month,
        "year": year,
        "till_day": last_day,
        "total_present_days": total_present_days,
        "total_hours_worked": str(total_duration).split('.')[0],
        "average_daily_hours": str(avg_hours).split('.')[0],
        "report": report
    }, status=200)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def truetime_weekly_view(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    try:
        month = int(request.query_params.get('month', now().month))
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid month/year format'}, status=200)

    today = localtime(now()).date()
    # --- Restrict future months/years ---
    if year > today.year or (year == today.year and month > today.month):
        return Response({"message": "No data available for future months/years."}, status=200)
    is_current_month = (month == today.month and year == today.year)
    days_in_month = today.day if is_current_month else monthrange(year, month)[1]
    first_day_of_month = date(year, month, 1)
    last_day_of_month = date(year, month, days_in_month)

    # Calculate padding days before and after to align Sunday-Saturday weeks
    first_weekday = first_day_of_month.weekday()  # Monday=0, Sunday=6
    pad_start = (first_weekday + 1) % 7  # Days to pad before first of month
    pad_end = (6 - last_day_of_month.weekday()) % 7  # Days to pad after last of month

    # Generate full calendar grid (including padding)
    full_dates = [
        first_day_of_month - timedelta(days=pad_start - i)
        for i in range(pad_start)
    ] + [
        date(year, month, day)
        for day in range(1, days_in_month + 1)
    ] + [
        last_day_of_month + timedelta(days=i + 1)
        for i in range(pad_end)
    ]

    # Fetch logs only for current month
    logs = AttendanceLog.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).only('date', 'check_in', 'check_out').order_by('date', 'check_in')

    grouped_logs = defaultdict(list)
    for log in logs:
        grouped_logs[log.date].append(log)

    weekly_report = []
    total_present_days = 0
    total_duration = timedelta()
    current_week = []

    # Get payroll and pay schedule
    employee_obj = request.user.employee
    payroll = employee_obj.payroll
    pay_schedule = PaySchedule.objects.filter(payroll=payroll).first()

    # For the relevant month (month/year for weekly, target_date for datewise)
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    # Build holiday_dates set
    holidays = HolidayManagement.objects.filter(
        payroll=payroll,
        start_date__lte=last_day,
        end_date__gte=first_day,
        applicable_for=employee.employee.work_location
    )
    holiday_dates = set()
    for holiday in holidays:
        current = max(holiday.start_date, first_day)
        end = min(holiday.end_date, last_day)
        while current <= end:
            holiday_dates.add(current)
            current += timedelta(days=1)

    # Build week_off_dates set
    week_off_dates = set()
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()
        if pay_schedule:
            # Check regular week offs
            if (weekday == 0 and pay_schedule.monday) or \
               (weekday == 1 and pay_schedule.tuesday) or \
               (weekday == 2 and pay_schedule.wednesday) or \
               (weekday == 3 and pay_schedule.thursday) or \
               (weekday == 4 and pay_schedule.friday) or \
               (weekday == 5 and pay_schedule.saturday) or \
               (weekday == 6 and pay_schedule.sunday):
                week_off_dates.add(current_date)
            # Second Saturday
            if pay_schedule.second_saturday and (8 <= day <= 14 and weekday == 5):
                week_off_dates.add(current_date)
            # Fourth Saturday
            if pay_schedule.fourth_saturday and (22 <= day <= 28 and weekday == 5):
                week_off_dates.add(current_date)

    # Combine
    all_holiday_dates = holiday_dates | week_off_dates

    for current_date in full_dates:
        # Only show data for days up to today
        if is_current_month and current_date > today:
            current_week.append({
                "date": current_date.strftime('%d-%m-%Y'),
                "sessions": [],
                "total_hours": "0:00:00",
                "session_count": 0,
                "status": "-"
            })
            if len(current_week) == 7:
                weekly_report.append(current_week)
                current_week = []
            continue

        is_in_month = current_date.month == month

        sessions = grouped_logs.get(current_date, [])
        session_count = len(sessions)
        time_pairs = []
        day_duration = timedelta()

        for session in sessions:
            in_time = localtime(session.check_in).strftime('%H:%M:%S') if session.check_in else "-"
            out_time = localtime(session.check_out).strftime('%H:%M:%S') if session.check_out else "-"
            time_pairs.append({
                "check_in": in_time,
                "check_out": out_time,
                "location": session.location if session.location else "-",
                "device_info": session.device_info if session.device_info else "-"
            })
            if session.check_in and session.check_out:
                day_duration += session.check_out - session.check_in

        if session_count > 0:
            total_present_days += 1
            total_duration += day_duration

        if current_date in all_holiday_dates:
            status = "Holiday"
        elif session_count > 0:
            status = "Present"
        else:
            status = "Absent"

        current_week.append({
            "date": current_date.strftime('%d-%m-%Y'),
            "sessions": time_pairs,
            "total_hours": str(day_duration).split('.')[0],
            "session_count": session_count,
            "status": status
        })

        # Once we have 7 days, finalize the week
        if len(current_week) == 7:
            weekly_report.append(current_week)
            current_week = []

    avg_hours = total_duration / total_present_days if total_present_days else timedelta()

    return Response({
        "month": month,
        "year": year,
        "total_present_days": total_present_days,
        "total_hours_worked": str(total_duration).split('.')[0],
        "average_daily_hours": str(avg_hours).split('.')[0],
        "weekly_report": weekly_report
    }, status=200)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def truetime_datewise_view(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    try:
        query_date = request.query_params.get('date', localtime(now()).date().isoformat())
        target_date = date.fromisoformat(query_date)
    except Exception as e:
        return Response({'error': str(e)}, status=200)

    today = localtime(now()).date()

    if target_date > today:
        return Response({
            "date": target_date.strftime('%d-%m-%Y'),
            "total_hours": "0:00:00",
            "session_count": 0,
            "sessions": [],
            "status": "-"
        }, status=200)

    # Get payroll and pay schedule
    employee_obj = employee.employee
    payroll = employee_obj.payroll
    pay_schedule = PaySchedule.objects.filter(payroll=payroll).first()

    # Holiday dates
    holidays = HolidayManagement.objects.filter(
        payroll=payroll,
        start_date__lte=target_date,
        end_date__gte=target_date,
        applicable_for=employee.employee.work_location
    )
    is_holiday = holidays.exists()

    # Week-off logic
    is_week_off = False
    weekday = target_date.weekday()
    day = target_date.day

    if pay_schedule:
        if (weekday == 0 and pay_schedule.monday) or \
           (weekday == 1 and pay_schedule.tuesday) or \
           (weekday == 2 and pay_schedule.wednesday) or \
           (weekday == 3 and pay_schedule.thursday) or \
           (weekday == 4 and pay_schedule.friday) or \
           (weekday == 5 and pay_schedule.saturday) or \
           (weekday == 6 and pay_schedule.sunday):
            is_week_off = True
        if pay_schedule.second_saturday and (8 <= day <= 14 and weekday == 5):
            is_week_off = True
        if pay_schedule.fourth_saturday and (22 <= day <= 28 and weekday == 5):
            is_week_off = True

    # Attendance logs
    logs = AttendanceLog.objects.filter(
        employee=employee,
        date=target_date
    ).only('check_in', 'check_out').order_by('check_in')

    in_time = out_time = None
    total_duration = timedelta()
    sessions = []

    for log in logs:
        check_in = localtime(log.check_in).strftime('%H:%M:%S') if log.check_in else "-"
        check_out = localtime(log.check_out).strftime('%H:%M:%S') if log.check_out else "-"
        sessions.append({
            "check_in": check_in,
            "check_out": check_out,
            "location": log.location if log.location else "-",
            "device_info": log.device_info if log.device_info else "-"
        })

        if log.check_in and (not in_time or log.check_in < in_time):
            in_time = log.check_in
        if log.check_out and (not out_time or log.check_out > out_time):
            out_time = log.check_out
        if log.check_in and log.check_out:
            total_duration += log.check_out - log.check_in

    # Final status logic
    if is_holiday or is_week_off:
        status = "Holiday"
    elif logs.exists():
        status = "Present"
    else:
        status = "Absent"

    return Response({
        "date": target_date.strftime('%d-%m-%Y'),
        "total_hours": str(total_duration).split('.')[0],
        "session_count": logs.count(),
        "sessions": sessions,
        "status": status
    }, status=200)


@api_view(['GET', 'POST'])
def geo_location_list_create(request):
    if request.method == 'GET':
        geos = AttendanceGeoTag.objects.all()
        serializer = AttendanceGeoTagSerializer(geos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AttendanceGeoTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def geo_location_detail(request, pk):
    try:
        geo = AttendanceGeoTag.objects.get(pk=pk)
    except AttendanceGeoTag.DoesNotExist:
        return Response({"error": "GeoLocation not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AttendanceGeoTagSerializer(geo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AttendanceGeoTagSerializer(geo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        geo.delete()
        return Response({"message": "GeoLocation deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def geo_locations_details_based_on_payroll_and_worklocation(request):
    payroll_id = request.query_params.get("payroll")
    branch = request.query_params.get("work_location")

    if not payroll_id:
        return Response({"error": "Payroll ID is missing"}, status=status.HTTP_200_OK)

    try:
        geo_locations = AttendanceGeoTag.objects.get(payroll=payroll_id, branch=branch)
        if not geo_locations.exists():
            return Response({"error": "No GeoLocations found for the provided payroll ID."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceGeoTagSerializer(geo_locations)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def geo_location_check_in(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()
    location = request.data.get('location', '')
    device_info = request.data.get('device_info', '')

    # Get the latest log for today
    last_log = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today
    ).order_by('-check_in').first()

    # If last entry exists and not checked out yet — block duplicate check-in
    if last_log and last_log.check_in and not last_log.check_out:
        return Response({'message': 'You must check out before checking in again.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Else allow new check-in
    new_log = AttendanceLog.objects.create(
        employee=employee_credentials,
        date=today,
        check_in=localtime(now()),
        check_in_type='geo',
        location=location,
        device_info=device_info
    )

    serializer = AttendanceLogSerializer(new_log)
    return Response({'message': 'Check-in successful', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def geo_location_check_out(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()

    # Get the latest check-in with no checkout
    attendance = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today,
        check_out__isnull=True
    ).order_by('-check_in').first()

    if not attendance:
        return Response({'error': 'No active check-in record found for today'}, status=status.HTTP_404_NOT_FOUND)

    # Check out now
    attendance.check_out = localtime(now())
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({'message': 'Check-out successful', 'data': serializer.data}, status=status.HTTP_200_OK)
