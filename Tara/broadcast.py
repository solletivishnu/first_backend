# broadcast.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

_channel = get_channel_layer()


def broadcast_to_employee(employee_id: int, payload: dict):
    """
    Sends payload to the employee-specific group.
    Your consumer must add connections to group: f"user_{employee_id}"
    """
    async_to_sync(_channel.group_send)(
        f"user_{employee_id}",
        {"type": "send_attendance_update", "payload": payload}
    )


def broadcast_to_business(business_id: int, payload: dict):
    """
    Sends payload to the whole business/team group.
    Your consumer must add connections to group: f"business_{business_id}"
    """
    async_to_sync(_channel.group_send)(
        f"business_{business_id}",
        {"type": "send_attendance_update", "payload": payload}
    )
