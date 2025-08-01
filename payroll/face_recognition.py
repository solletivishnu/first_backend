import boto3
from uuid import uuid4
from datetime import date, timedelta
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.utils.timezone import localtime, now
from calendar import monthrange
from collections import defaultdict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, localtime
from .models import EmployeeCredentials, EmployeeFaceRecognition, AttendanceLog, PaySchedule, HolidayManagement, LeaveManagement
from .serializers import EmployeeCredentialsSerializer, AttendanceLogSerializer, EmployeeFaceRecognitionSerializer

rekognition = boto3.client(
    'rekognition',
    region_name=settings.AWS_REGION  # <- use region from settings
)
s3 = boto3.client('s3')
s3_bucket = settings.AWS_STORAGE_BUCKET_NAME


@csrf_exempt
@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def upload_employee_images(request):
    """
    Upload 4 directional employee images (front, back, left, right),
    analyze them using AWS Rekognition, store images and labels.
    """
    name = request.data.get('username')
    email = request.data.get('email')
    directions = ['front', 'upper_angle', 'left', 'right', 'lower_angle', 'back']

    if not name:
        return Response({"error": "Name and email are required."}, status=400)

    # Create or fetch employee
    employee = EmployeeCredentials.objects.get(username=name)

    for direction in directions:
        image_file = request.FILES.get(direction)
        if not image_file:
            continue

        # Save image (Django will handle upload to S3)
        employee_image = EmployeeFaceRecognition.objects.create(
            employee=employee,
            direction=direction,
            image_file=image_file
        )

        # Get the file key for Rekognition
        s3_key = f"media/{employee_image.image_file.name}"
        try:
            rekog_response = rekognition.detect_labels(
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
                MaxLabels=10,
                MinConfidence=70
            )
            labels = rekog_response.get('Labels', [])
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save labels
        employee_image.labels = labels
        employee_image.save()

    return Response(EmployeeCredentialsSerializer(employee).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def face_recognition_check_in(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    image_file = request.FILES.get('image')
    location = request.data.get('location', '')
    device_info = request.data.get('device_info', '')
    today = now().date()

    if not image_file:
        return Response({'error': 'Image is required for face recognition check-in.'}, status=400)

    # Prevent duplicate check-in
    last_log = AttendanceLog.objects.filter(
        employee=employee,
        date=today
    ).order_by('-check_in').first()

    if last_log and last_log.check_in and not last_log.check_out:
        return Response({'message': 'You must check out before checking in again.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Upload temporary check-in image
    temp_key = f"checkin/{employee.id}/checkin_{now().timestamp()}.jpg"
    s3.upload_fileobj(image_file, s3_bucket, temp_key)

    # Fetch employee's stored reference images
    reference_images = EmployeeFaceRecognition.objects.filter(employee=employee)
    if not reference_images.exists():
        return Response({'error': 'No reference images found for face recognition.'}, status=404)

    matched = False
    match_results = []

    for ref in reference_images:
        ref_key = f"media/{ref.image_file.name}"
        try:
            response = rekognition.compare_faces(
                SourceImage={'S3Object': {'Bucket': s3_bucket, 'Name': ref_key}},
                TargetImage={'S3Object': {'Bucket': s3_bucket, 'Name': temp_key}},
                SimilarityThreshold=80
            )
            for match in response.get('FaceMatches', []):
                similarity = match['Similarity']
                match_results.append({
                    "reference": ref.direction,
                    "similarity": similarity
                })
                if similarity >= 90:
                    matched = True

        except Exception as e:
            return Response({'error': f"Rekognition error: {str(e)}"}, status=500)

    if not matched:
        return Response({
            "message": "Face not recognized. Please try again.",
            "match_results": match_results
        }, status=401)

    # If match found, allow check-in
    new_log = AttendanceLog.objects.create(
        employee=employee,
        date=today,
        check_in=now(),
        check_in_type='face',
        location=location,
        device_info=device_info
    )

    serializer = AttendanceLogSerializer(new_log)
    return Response({
        "message": "Check-in successful via face recognition",
        "data": serializer.data,
        "match_results": match_results
    }, status=200)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def face_recognition_check_out(request):
    employee = request.user
    print(localtime(now()))


    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'error': 'Image is required for face recognition check-out.'}, status=400)

    today = now().date()

    # Find the latest active check-in (with no check-out)
    attendance = AttendanceLog.objects.filter(
        employee=employee,
        date=today,
        check_out__isnull=True
    ).order_by('-check_in').first()

    if not attendance:
        return Response({'error': 'No active check-in record found for today'}, status=404)

    # Upload check-out image temporarily to S3
    temp_key = f"checkout/{employee.id}/checkout_{now().timestamp()}.jpg"
    print(now().timestamp())
    s3.upload_fileobj(image_file, s3_bucket, temp_key)

    # Get stored reference images for matching
    reference_images = EmployeeFaceRecognition.objects.filter(employee=employee)
    if not reference_images.exists():
        return Response({'error': 'No stored reference images for face recognition.'}, status=404)

    matched = False
    match_results = []

    for ref in reference_images:
        ref_key = f"media/{ref.image_file.name}"
        try:
            response = rekognition.compare_faces(
                SourceImage={'S3Object': {'Bucket': s3_bucket, 'Name': ref_key}},
                TargetImage={'S3Object': {'Bucket': s3_bucket, 'Name': temp_key}},
                SimilarityThreshold=80
            )
            for match in response.get('FaceMatches', []):
                similarity = match['Similarity']
                match_results.append({
                    "reference": ref.direction,
                    "similarity": similarity
                })
                if similarity >= 90:
                    matched = True

        except Exception as e:
            return Response({'error': f"Rekognition error: {str(e)}"}, status=500)

    if not matched:
        return Response({
            "message": "Face not recognized. Check-out denied.",
            "match_results": match_results
        }, status=401)

    # If match successful → check out
    attendance.check_out = now()
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({
        "message": "Check-out successful via face recognition",
        "data": serializer.data,
        "match_results": match_results
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def attendance_summary_view(request):
    employee = request.user

    try:
        month = int(request.query_params.get('month', now().month))
        year = int(request.query_params.get('year', now().year))
    except ValueError:
        return Response({'error': 'Invalid month/year format'}, status=400)

    today = localtime(now()).date()
    if year > today.year or (year == today.year and month > today.month):
        return Response({'error': 'Cannot fetch future data'}, status=400)

    # Date range
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    all_days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    # Attendance logs
    logs = AttendanceLog.objects.filter(
        employee=employee,
        date__range=(first_day, last_day)
    ).only("date", "check_in", "check_out")

    present_dates = set(log.date for log in logs)

    # Week-off and holidays
    employee_obj = employee.employee
    payroll = employee_obj.payroll
    pay_schedule = PaySchedule.objects.filter(payroll=payroll).first()

    week_off_dates = set()
    for single_date in all_days:
        weekday = single_date.weekday()
        d = single_date.day
        if pay_schedule:
            if (weekday == 0 and pay_schedule.monday) or \
               (weekday == 1 and pay_schedule.tuesday) or \
               (weekday == 2 and pay_schedule.wednesday) or \
               (weekday == 3 and pay_schedule.thursday) or \
               (weekday == 4 and pay_schedule.friday) or \
               (weekday == 5 and pay_schedule.saturday) or \
               (weekday == 6 and pay_schedule.sunday):
                week_off_dates.add(single_date)
            if pay_schedule.second_saturday and (8 <= d <= 14 and weekday == 5):
                week_off_dates.add(single_date)
            if pay_schedule.fourth_saturday and (22 <= d <= 28 and weekday == 5):
                week_off_dates.add(single_date)

    holiday_dates = set()
    holidays = HolidayManagement.objects.filter(
        payroll=payroll,
        start_date__lte=last_day,
        end_date__gte=first_day
    )
    for h in holidays:
        current = max(h.start_date, first_day)
        end = min(h.end_date, last_day)
        while current <= end:
            holiday_dates.add(current)
            current += timedelta(days=1)

    non_working_days = week_off_dates | holiday_dates

    absent_days = [
        d for d in all_days
        if d not in present_dates and
           d not in non_working_days and
           d <= today
    ]

    summary = {
        "month": month,
        "year": year,
        "total_days": len(all_days),
        "present_days": len(present_dates),
        "week_off_days": len(week_off_dates),
        "holiday_days": len(holiday_dates),
        "absent_days": len(absent_days),
        "payable_days": len(present_dates),
        "lop_days": len(absent_days)
    }

    return Response(summary)
