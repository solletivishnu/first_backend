import base64
import numpy as np
from datetime import datetime
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AttendanceLog, EmployeeCredentials
from .serializers import AttendanceLogSerializer
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from datetime import datetime, timedelta, date
from calendar import monthrange
from collections import defaultdict


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def manual_check_in(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = now().date()
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
        check_in=now(),
        check_in_type='manual',
        location=location,
        device_info=device_info
    )

    serializer = AttendanceLogSerializer(new_log)
    return Response({'message': 'Check-in successful', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def manual_check_out(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = now().date()

    # Get the latest check-in with no checkout
    attendance = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today,
        check_out__isnull=True
    ).order_by('-check_in').first()

    if not attendance:
        return Response({'error': 'No active check-in record found for today'}, status=status.HTTP_404_NOT_FOUND)

    # Check out now
    attendance.check_out = now()
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({'message': 'Check-out successful', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def today_attendance_status(request):
    employee_credentials = request.user

    if not isinstance(employee_credentials, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = now().date()

    # Get all logs for today
    attendance_logs = AttendanceLog.objects.filter(
        employee=employee_credentials,
        date=today
    ).order_by('check_in')

    if not attendance_logs.exists():
        return Response({'message': 'No attendance records for today'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Extract month & year
    try:
        month = int(request.query_params.get('month', now().month))
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid month/year'}, status=status.HTTP_400_BAD_REQUEST)

    today = now().date()
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

    for log_date in all_dates:
        sessions = grouped_logs.get(log_date, [])
        session_count = len(sessions)

        in_time = out_time = None
        day_duration = timedelta()

        for session in sessions:
            if session.check_in and (not in_time or session.check_in < in_time):
                in_time = session.check_in
            if session.check_out and (not out_time or session.check_out > out_time):
                out_time = session.check_out
            if session.check_in and session.check_out:
                day_duration += session.check_out - session.check_in

        if session_count > 0:
            total_present_days += 1
            total_duration += day_duration

        report.append({
            "date": log_date.isoformat(),
            "in_time": in_time.strftime('%H:%M:%S') if in_time else "-",
            "out_time": out_time.strftime('%H:%M:%S') if out_time else "-",
            "total_hours": str(day_duration).split('.')[0],
            "session_count": session_count,
            "status": "Present" if session_count else "Absent"
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
    }, status=status.HTTP_200_OK)

