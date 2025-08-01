from payroll.models import (EmployeeEducationDetails, EmployeeCredentials, PayrollOrg, EmployeePersonalDetails,
                            EmployeeManagement, EmployeeFaceRecognition, EmployeeBankDetails)
from rest_framework.response import Response
from payroll.serializers import (EmployeeEducationDetailsSerializer, EmployeePersonalDetailsSerializer,
                                 EmployeeManagementSerializer, EmployeeBankDetailsSerializer, EmployeeProfileSerializer)
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange
from rest_framework import status
from django.utils.timezone import now, localtime
from collections import defaultdict


@api_view(['GET', 'POST'])
@authentication_classes([EmployeeJWTAuthentication])
def employee_education_list_create(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    if request.method == 'GET':
        # List all education details for the employee
        education_details = EmployeeEducationDetails.objects.filter(employee=employee)
        serializer = EmployeeEducationDetailsSerializer(education_details, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Create a new education detail entry
        serializer = EmployeeEducationDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([EmployeeJWTAuthentication])
def employee_education_detail(request, education_id):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    try:
        education_detail = EmployeeEducationDetails.objects.get(id=education_id, employee=employee)
    except EmployeeEducationDetails.DoesNotExist:
        return Response({'error': 'Education detail not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmployeeEducationDetailsSerializer(education_detail)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EmployeeEducationDetailsSerializer(education_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the education detail entry Before delete the record delete file from s3 storage if exists
        if education_detail.upload_certificate:
            try:
                # Assuming you have a function to delete files from S3
                education_detail.upload_certificate.delete(save=False)
            except Exception as e:
                return Response({'error': f'Failed to delete document: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        education_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def employee_profile_details(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=401)

    full_name = f"{employee.employee.first_name} "
    if employee.employee.middle_name:
        full_name += f"{employee.employee.middle_name} "
    full_name += employee.employee.last_name

    #Get employee image if exists
    try:
        employee_image = EmployeeFaceRecognition.objects.get(employee=employee, direction="front").image_file.url
    except EmployeeFaceRecognition.DoesNotExist:
        employee_image = None

    try:
        personal = EmployeePersonalDetails.objects.get(employee=employee.employee)
    except EmployeePersonalDetails.DoesNotExist:
        personal = None

    data = {
        "id": employee.pk,
        "profile": EmployeeProfileSerializer(EmployeeManagement.objects.get(id=employee.employee.id)).data,
        "photo": employee_image,
        "personal_details": EmployeePersonalDetailsSerializer(personal).data if personal else None,
        "bank_details": EmployeeBankDetailsSerializer(
            EmployeeBankDetails.objects.get(employee=employee.employee)).data,
        "education_details": EmployeeEducationDetailsSerializer(
            EmployeeEducationDetails.objects.filter(employee=employee), many=True).data,
    }

    return Response(data, status=status.HTTP_200_OK)

