from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json

def sync_schedules():
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=30,
        period=IntervalSchedule.MINUTES
    )

    task, _ = PeriodicTask.objects.get_or_create(
        name="Print Current Time Every Minute",
        defaults={
            'task': 'document_drafting.tasks.print_current_time',
            'args': json.dumps([]),
            'interval': schedule,
        }
    )

    task.interval = schedule  # force-assign
    task.save()
