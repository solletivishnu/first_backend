from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveApplication, EmployeeLeaveBalance
from .serializers import LeaveApplicationSerializer, EmployeeLeaveBalanceSerializer
from .authentication import EmployeeJWTAuthentication
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from datetime import date


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def apply_leave(request):
    employee_credentials = request.user  # Already EmployeeCredentials instance
    employee = employee_credentials.employee  # Actual EmployeeManagement instance

    # Check if employee in payload matches logged-in employee
    payload_employee_id = request.data.get('employee')
    if str(employee_credentials.id) != str(payload_employee_id):
        return Response(
            {'error': 'You are not allowed to apply leave for another employee.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = LeaveApplicationSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        leave = serializer.save(employee=employee_credentials)  # Save with actual employee instance
        return Response({
            'id': leave.id,
            'message': 'Leave application submitted successfully.',
            'status': leave.status
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def current_financial_year_range():
    today = date.today()
    year = today.year
    if today.month < 4:
        start = date(year - 1, 4, 1)
        end = date(year, 3, 31)
    else:
        start = date(year, 4, 1)
        end = date(year + 1, 3, 31)
    return start, end


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_leave_applications(request):
    user = request.user

    if not hasattr(user, 'employee'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    start_date, end_date = current_financial_year_range()

    leaves = LeaveApplication.objects.filter(
        employee=user,
        start_date__gte=start_date,
        start_date__lte=end_date
    )

    serializer = LeaveApplicationSerializer(leaves, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def handle_leave_action(request, leave_id):
    user = request.user

    try:
        leave = LeaveApplication.objects.get(id=leave_id)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found.'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')
    comment = request.data.get('comment', '')

    if action not in ['approve', 'reject', 'cancel']:
        return Response({'error': 'Invalid action. Must be approve, reject, or cancel.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate credentials
    if not hasattr(user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    employee = user.employeecredentials

    # Handle rejection or approval by reviewer or cc_to
    if action in ['approve', 'reject']:
        if leave.reviewer != employee and employee not in leave.cc_to.all():
            return Response({'error': 'You are not authorized to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if leave.status != 'pending':
            return Response({'error': f'Cannot {action} a leave with status {leave.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        leave.reviewer = employee
        leave.reviewed_on = timezone.now()
        leave.reviewer_comment = comment

        if action == 'approve':
            leave.status = 'approved'
            message = 'Leave approved successfully.'
        else:
            if not comment:
                return Response({'error': 'Comment is required for rejection.'}, status=status.HTTP_400_BAD_REQUEST)
            leave.status = 'rejected'
            message = 'Leave rejected successfully.'

    elif action == 'cancel':
        if leave.employee != employee:
            return Response({'error': 'You can only cancel your own leave.'}, status=status.HTTP_403_FORBIDDEN)

        if leave.status != 'pending':
            return Response({'error': 'Only pending leaves can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = 'cancelled'
        message = 'Leave cancelled successfully.'

    leave.save()
    serializer = LeaveApplicationSerializer(leave)
    return Response({'message': message, 'data': serializer.data}, status=status.HTTP_200_OK)



@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def reject_leave(request, leave_id):
    user = request.user

    try:
        leave = LeaveApplication.objects.get(id=leave_id)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user is the reviewer or in the cc list
    if leave.reviewer != user and user not in leave.cc_to.all():
        return Response({'error': 'You are not authorized to reject this leave.'}, status=status.HTTP_403_FORBIDDEN)

    # Only allow rejection if leave is still pending
    if leave.status != 'pending':
        return Response({'error': f'Cannot reject a leave with status {leave.status}.'}, status=status.HTTP_400_BAD_REQUEST)

    leave.status = 'rejected'
    leave.rejection_reason = request.data.get('rejection_reason', 'Rejected by reviewer.')
    leave.reviewed_at = timezone.now()
    leave.save()

    return Response({'message': 'Leave application rejected successfully.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def cancel_leave(request, pk):
    user = request.user
    if not hasattr(user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        leave = LeaveApplication.objects.get(pk=pk, employee=user.employeecredentials)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found'}, status=status.HTTP_404_NOT_FOUND)

    if leave.status != 'pending':
        return Response({'error': 'Only pending leaves can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

    leave.status = 'cancelled'
    leave.reviewed_on = timezone.now().date()
    leave.save(update_fields=['status', 'reviewed_on'])

    serializer = LeaveApplicationSerializer(leave)
    return Response({'message': 'Leave cancelled', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_monthly_leaves(request, year, month):
    """Get leaves for specific month (format: YYYY/MM)"""
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Validate month/year
        month_start = datetime(year=year, month=month, day=1).date()
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        month_end = datetime(year=next_year, month=next_month, day=1).date() - timedelta(days=1)
    except ValueError:
        return Response({'error': 'Invalid month/year'}, status=status.HTTP_400_BAD_REQUEST)

    leaves = LeaveApplication.objects.filter(
        employee=request.user.employeecredentials,
        start_date__lte=month_end,
        end_date__gte=month_start
    ).order_by('start_date')

    serializer = LeaveApplicationSerializer(leaves, many=True)
    return Response({
        'month': f"{year}-{month:02d}",
        'count': leaves.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_current_month_leaves(request):
    """Get leaves for current month"""
    today = timezone.now().date()
    return get_monthly_leaves(request._request, today.year, today.month)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_leave_summary(request, year=None):
    """Get monthly leave summary for a year"""
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    year = int(year or timezone.now().year)
    leaves = LeaveApplication.objects.filter(
        employee=request.user.employeecredentials,
        start_date__year=year
    )

    summary = []
    for month in range(1, 13):
        month_leaves = leaves.filter(start_date__month=month)
        approved = month_leaves.filter(status='approved')

        # Get the first and last date of the month
        start_of_month = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_of_month = datetime(year, month, last_day).date()

        total_days = sum(
            (min(leave.end_date, end_of_month) - max(leave.start_date, start_of_month)).days + 1
            for leave in approved
            if leave.end_date >= start_of_month and leave.start_date <= end_of_month
        )

        summary.append({
            'month': f"{year}-{month:02d}",
            'total_leaves': month_leaves.count(),
            'approved_leaves': approved.count(),
            'pending_leaves': month_leaves.filter(status='pending').count(),
            'rejected_leaves': month_leaves.filter(status='rejected').count(),
            'total_days': total_days
        })

    return Response({
        'year': year,
        'summary': summary
    })


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_my_leave_balances(request):
    """Get leave balances for the currently authenticated employee."""
    try:
        employee = request.user.employee  # Assuming request.user is an instance of EmployeeCredentials
    except AttributeError:
        return Response({'error': 'Invalid user context'}, status=status.HTTP_400_BAD_REQUEST)

    leave_balances = EmployeeLeaveBalance.objects.filter(employee=employee)
    serializer = EmployeeLeaveBalanceSerializer(leave_balances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)