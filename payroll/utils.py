from django.utils import timezone

def format_time_style(timestamp):
    """Format time for notifications"""
    if not timestamp:
        return None

    now = timezone.now()
    created = timezone.localtime(timestamp)
    diff = now - created

    if diff.days == 0:
        return {
            "display": created.strftime("%I:%M %p").lstrip('0')
        }
    elif diff.days == 1:
        return {
            "date": "Yesterday",
            "time": created.strftime("%I:%M %p").lstrip('0')
        }
    else:
        return {
            "date": created.strftime("%d %B, %Y"),
            "time": created.strftime("%I:%M %p").lstrip('0')
        }