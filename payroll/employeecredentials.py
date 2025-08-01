from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import (EmployeeManagement, EmployeeCredentials, EmployeeEducationDetails, EmployeeFaceRecognition,
                     EmployeePersonalDetails, EmployeeBankDetails)
from .serializers import (EmployeeManagementSerializer, EmployeeCredentialsSerializer, EmployeePersonalDetailsSerializer,
                          EmployeeEducationDetailsSerializer, EmployeeBankDetailsSerializer, EmployeeProfileSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def credentials_list_create(request):
    if request.method == 'GET':
        creds = EmployeeCredentials.objects.select_related('employee').all()
        serializer = EmployeeCredentialsSerializer(creds, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EmployeeCredentialsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def credentials_detail(request, pk):
    try:
        creds = EmployeeCredentials.objects.get(pk=pk)
    except EmployeeCredentials.DoesNotExist:
        return Response({'error': 'Credentials not found'}, status=404)

    if request.method == 'GET':
        serializer = EmployeeCredentialsSerializer(creds)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EmployeeCredentialsSerializer(creds, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        creds.delete()
        return Response({'message': 'Deleted'}, status=204)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any user to login
def employee_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        creds = EmployeeCredentials.objects.select_related('employee').get(username=username)
        if creds.check_password(password):
            # Update last login
            creds.last_login = timezone.now()
            creds.save()

            # Create JWT manually (since we don't use Django user model)
            refresh = RefreshToken()
            refresh['employee_id'] = creds.employee.id
            refresh['username'] = creds.username
            refresh['associate_id'] = creds.employee.associate_id

            full_name = f"{creds.employee.first_name} "
            if creds.employee.middle_name:
                full_name += f"{creds.employee.middle_name} "
            full_name += creds.employee.last_name

            # Get employee image if exists
            try:
                employee_image = EmployeeFaceRecognition.objects.get(employee=creds,
                                                                     direction="front").image_file.url
            except EmployeeFaceRecognition.DoesNotExist:
                employee_image = None

            try:
                personal = EmployeePersonalDetails.objects.get(employee=creds.employee)
            except EmployeePersonalDetails.DoesNotExist:
                personal = None

            data = {
                "profile": EmployeeProfileSerializer(EmployeeManagement.objects.get(id=creds.employee.id)).data,
                "photo": employee_image,
                "personal_details": EmployeePersonalDetailsSerializer(personal).data if personal else None,
                "bank_details": EmployeeBankDetailsSerializer(
                    EmployeeBankDetails.objects.get(employee=creds.employee)).data,
                "education_details": EmployeeEducationDetailsSerializer(
                    EmployeeEducationDetails.objects.filter(employee=creds), many=True).data,
            }

            return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "employee": data,
                'id': creds.id,
            })
        else:
            return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
    except EmployeeCredentials.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)