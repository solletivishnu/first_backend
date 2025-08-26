from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveApplication, EmployeeLeaveBalance, EmployeeReportingManager, EmployeeCredentials
from .serializers import LeaveApplicationSerializer, EmployeeLeaveBalanceSerializer
from .authentication import EmployeeJWTAuthentication
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from datetime import date
from Tara.broadcast import broadcast_leave_notification_to_employee
from payroll.models import LeaveNotification
from payroll.serializers import LeaveNotificationSerializer
from .utils import format_time_style
from django.db import transaction
import logging



@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_leave_notifications(request):
    """Get all leave notifications for the reviewer"""
    try:
        notifications = LeaveNotification.objects.select_related(
            'leave_application',
            'leave_application__employee',
            'leave_application__employee__employee',
            'leave_application__employee__employee__designation',
            'leave_application__employee__employee__department',
            'leave_application__leave_type'
        ).filter(
            reviewer=request.user
        ).order_by('-created_at')

        response_data = []
        for notification in notifications:
            leave = notification.leave_application
            employee = leave.employee.employee

            # Format time with new structure
            time_format = format_time_style(notification.created_at)
            read_at_format = format_time_style(notification.read_at) if notification.read_at else None

            notification_data = {
                "type": "leave_notification",
                "action": "view_leave",
                "notification_id": notification.id,
                "title": f"{employee.first_name} {employee.last_name} - {leave.leave_type.name_of_leave} Request",
                "data": {
                    "employee": {
                        "name": f"{employee.first_name} {employee.last_name}",
                        "designation": employee.designation.designation_name if employee.designation else "N/A",
                        "department": employee.department.dept_name if employee.department else "N/A"
                    },
                    "leave": {
                        "id": leave.id,
                        "type": leave.leave_type.name_of_leave,
                        "days": (leave.end_date - leave.start_date).days + 1,
                        "start_date": leave.start_date.strftime("%d %b %Y"),
                        "end_date": leave.end_date.strftime("%d %b %Y"),
                        "reason": leave.reason,
                        "status": leave.status
                    },
                    "created_at": time_format
                },
                "message": notification.message,
                "is_read": notification.is_read,
                "read_at": read_at_format
            }
            response_data.append(notification_data)

        return Response({
            "notifications": response_data,
            "unread_count": sum(1 for n in notifications if not n.is_read)
        })

    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")  # Debug log
        return Response(
            {
                "type": "error",
                "message": "Failed to fetch notifications",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_unread_count_for_reviewer(reviewer):
    return LeaveNotification.objects.filter(reviewer=reviewer, is_read=False).count()

@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def unread_leave_notification_count(request):
    count = LeaveNotification.objects.filter(reviewer=request.user, is_read=False).count()
    return Response({"unread_count": count})



logger = logging.getLogger(__name__)

def create_notification_data(notif, recipient):
    """Format notification data for a single notification"""
    leave_app = notif.leave_application
    emp = leave_app.employee.employee
    is_reviewer = leave_app.reviewer == recipient

    return {
        "type": "leave_notification",
        "action": "new_leave",
        "notification_id": notif.id,
        "title": f"{emp.first_name} {emp.last_name} - {leave_app.leave_type.name_of_leave} Request",
        "data": {
            "employee": {
                "name": f"{emp.first_name} {emp.last_name}",
                "designation": emp.designation.designation_name if emp.designation else "N/A",
                "department": emp.department.dept_name if emp.department else "N/A",
                "role": "Reviewer" if is_reviewer else "CC"
            },
            "leave": {
                "id": leave_app.id,
                "type": leave_app.leave_type.name_of_leave,
                "days": (leave_app.end_date - leave_app.start_date).days + 1,
                "period": f"{leave_app.start_date.strftime('%d %b %Y')} to {leave_app.end_date.strftime('%d %b %Y')}",
                "reason": leave_app.reason,
                "status": leave_app.status
            }
        },
        "message": notif.message,
        "created_at": format_time_style(notif.created_at),
        "is_read": notif.is_read,
        "read_at": format_time_style(notif.read_at) if notif.read_at else None
    }

def get_notification_message(leave, employee_name, employee_designation, employee_department, days):
    """Create notification message"""
    return (
        f"{employee_name}, {employee_designation} from the {employee_department} department, "
        f"has requested {days} day{'s' if days > 1 else ''} of {leave.leave_type.name_of_leave}. "
        f"The leave period is from {leave.start_date.strftime('%d %b %Y')} to {leave.end_date.strftime('%d %b %Y')}. "
        f"Reason for leave: {leave.reason}"
    )

@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
@transaction.atomic  # Add atomic transaction
def apply_leave(request):
    try:
        employee_credentials = request.user
        employee = employee_credentials.employee

        # Validate employee
        if str(employee_credentials.id) != str(request.data.get('employee')):
            return Response(
                {'error': 'You are not allowed to apply leave for another employee.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get reviewing team
        try:
            reviewing_team = EmployeeReportingManager.objects.select_related(
                'reporting_manager',
                'head_of_department'
            ).get(employee=employee)
        except EmployeeReportingManager.DoesNotExist:
            return Response(
                {'error': 'Reviewing manager info not configured for this employee.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare data with reviewer and CC
        data = request.data.copy()
        manager_creds = EmployeeCredentials.objects.get(employee=reviewing_team.reporting_manager)
        data['reviewer'] = manager_creds.id

        cc_list = []
        if reviewing_team.head_of_department:
            try:
                hod_creds = EmployeeCredentials.objects.get(employee=reviewing_team.head_of_department)
                cc_list.append(hod_creds.id)
            except EmployeeCredentials.DoesNotExist:
                pass
        data.setlist('cc_to', cc_list)

        # Validate and save leave application
        serializer = LeaveApplicationSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            leave = serializer.save(employee=employee_credentials)
            reviewer = leave.reviewer
            cc_recipients = leave.cc_to.all()

            if not (reviewer or cc_recipients.exists()):
                raise ValueError("No reviewer or CC recipients specified")

            # Get employee details once
            employee_name = f"{employee.first_name} {employee.last_name}"
            employee_designation = employee.designation.designation_name if employee.designation else "N/A"
            employee_department = employee.department.dept_name if employee.department else "N/A"
            days = (leave.end_date - leave.start_date).days + 1

            # Create notification message
            detailed_message = get_notification_message(
                leave, employee_name, employee_designation, employee_department, days
            )

            # Get unique recipients
            recipients_to_notify = set(cc_recipients)
            if reviewer:
                recipients_to_notify.add(reviewer)

            # Bulk create notifications
            notifications = [
                LeaveNotification(
                    leave_application=leave,
                    reviewer=recipient,
                    message=detailed_message
                )
                for recipient in recipients_to_notify
            ]
            created_notifications = LeaveNotification.objects.bulk_create(notifications)

            # Send notifications to all recipients
            for recipient in recipients_to_notify:
                # Get all notifications efficiently
                all_notifications = LeaveNotification.objects.select_related(
                    'leave_application',
                    'leave_application__employee__employee',
                    'leave_application__employee__employee__designation',
                    'leave_application__employee__employee__department',
                    'leave_application__leave_type'
                ).filter(reviewer=recipient).order_by('-created_at')

                notifications_data = [
                    create_notification_data(notif, recipient)
                    for notif in all_notifications
                ]

                unread_count = LeaveNotification.objects.filter(
                    reviewer=recipient,
                    is_read=False
                ).count()

                payload = {
                    "type": "leave_notifications_update",
                    "notifications": notifications_data,
                    "unread_count": unread_count
                }

                broadcast_leave_notification_to_employee(recipient.id, payload)

            return Response({
                "data": LeaveNotificationSerializer(created_notifications[0]).data,
                "id": leave.id,
                "message": "Leave application submitted successfully.",
                "status": leave.status
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error processing leave application: {str(e)}", exc_info=True)
        return Response({
            "error": "Failed to process leave application"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    print(user)

    try:
        leave = LeaveApplication.objects.get(id=leave_id)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found.'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')
    comment = request.data.get('comment', '')

    if action not in ['approve', 'reject', 'cancel']:
        return Response({'error': 'Invalid action. Must be approve, reject, or cancel.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate credentials
    if not hasattr(user, 'employee'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    employee = user

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
    if not hasattr(user, 'employee'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        leave = LeaveApplication.objects.get(pk=pk, employee=user)
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
    if not hasattr(request.user, 'employee'):
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
        employee=request.user,
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
    if not hasattr(request.user, 'employee'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    year = int(year or timezone.now().year)
    leaves = LeaveApplication.objects.filter(
        employee=request.user,
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