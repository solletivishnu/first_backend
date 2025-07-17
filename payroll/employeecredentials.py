from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import EmployeeManagement, EmployeeCredentials
from .serializers import EmployeeManagementSerializer, EmployeeCredentialsSerializer
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

            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "employee": {
                    "id": creds.employee.id,
                    "associate_id": creds.employee.associate_id,
                    "full_name": creds.employee.first_name + ' ' + creds.employee.last_name,
                },
                'id': creds.id,
            })
        else:
            return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
    except EmployeeCredentials.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)