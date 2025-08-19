# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import localdate


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
