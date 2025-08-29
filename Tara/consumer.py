# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import localdate
from channels.db import database_sync_to_async
from django.utils import timezone
from payroll.utils import format_time_style


class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Expect URL like ws://localhost:8000/ws/attendance/7/
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]

        # Join employee-specific group
        self.user_group = f"user_{self.employee_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Optionally: also join their business group if needed
        # For now just user-based
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "ws_connected",
            "employee_id": self.employee_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    # Server push handler
    async def send_attendance_update(self, event):
        await self.send(text_data=json.dumps(event.get("payload", {})))






class LeaveNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]
        print(f"WebSocket connected for employee_id: {self.employee_id}")

        self.user_group = f"user_{self.employee_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "ws_connected",
            "employee_id": self.employee_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        data = json.loads(text_data)

        if data.get('type') == 'mark_read':
            notification_id = data.get('notification_id')
            try:
                notification = await self.get_notification(notification_id)
                if notification:
                    await self.mark_notification_read(notification)
                    notifications_data = await self.get_all_notifications()
                    unread_count = await self.get_unread_count()

                    # Format read time for the notification that was just read
                    read_time = format_time_style(timezone.now())

                    payload = {
                        "type": "leave_notifications_update",
                        "notifications": notifications_data,
                        "unread_count": unread_count,
                        "last_read_notification": {
                            "notification_id": notification_id,
                            "read_at": read_time
                        }
                    }

                    await self.channel_layer.group_send(
                        self.user_group,
                        {
                            "type": "send_leave_notification",
                            "payload": payload
                        }
                    )

            except Exception as e:
                print(f"Error in receive: {str(e)}")  # Debug log
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": str(e)
                }))

    async def send_leave_notification(self, event):
        try:
            payload = event["payload"]
            await self.send(text_data=json.dumps(payload))
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Error processing notification"
            }))


    @database_sync_to_async
    def get_all_notifications(self):
        """Get all notifications for the reviewer"""
        from payroll.models import LeaveNotification

        notifications = LeaveNotification.objects.select_related(
            'leave_application',
            'leave_application__employee',
            'leave_application__employee__employee',
            'leave_application__employee__employee__designation',
            'leave_application__employee__employee__department',
            'leave_application__leave_type'
        ).filter(
            reviewer_id=self.employee_id
        ).order_by('-created_at')

        notifications_data = []
        for notif in notifications:
            leave = notif.leave_application
            employee = leave.employee.employee

            notification_data = {
                "type": "leave_notification",
                "action": "view_leave",
                "notification_id": notif.id,
                "title": f"{employee.first_name} {employee.last_name} - {leave.leave_type.name_of_leave} Request",
                "data": {
                    "employee": {
                        "name": f"{employee.first_name} {employee.last_name}",
                        "designation": employee.designation.designation_name if employee.designation else "N/A",
                        "department": employee.department.dept_name if employee.department else "N/A",
                        "role": "Reviewer" if leave.reviewer_id == self.employee_id else "CC"
                    },
                    "leave": {
                        "id": leave.id,
                        "type": leave.leave_type.name_of_leave,
                        "days": (leave.end_date - leave.start_date).days + 1,
                        "period": f"{leave.start_date.strftime('%d %b %Y')} to {leave.end_date.strftime('%d %b %Y')}",
                        "reason": leave.reason,
                        "status": leave.status
                    }
                },
                "message": notif.message,
                "created_at": format_time_style(notif.created_at),
                "is_read": notif.is_read,
                "read_at": format_time_style(notif.read_at)
            }
            notifications_data.append(notification_data)

        return notifications_data

    @database_sync_to_async
    def get_notification(self, notification_id):
        from payroll.models import LeaveNotification
        try:
            return LeaveNotification.objects.select_related(
                'leave_application',
                'leave_application__employee'
            ).get(
                id=notification_id,
                reviewer_id=self.employee_id
            )
        except LeaveNotification.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_notification_read(self, notification):
        current_time = timezone.now()
        notification.is_read = True
        notification.read_at = current_time
        notification.save(update_fields=['is_read', 'read_at'])
        return notification

    @database_sync_to_async
    def get_unread_count(self):
        from payroll.models import LeaveNotification
        return LeaveNotification.objects.filter(
            reviewer_id=self.employee_id,
            is_read=False
        ).count()