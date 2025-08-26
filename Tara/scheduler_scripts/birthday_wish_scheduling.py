from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


def birthday_wish_scheduling():
    # Use filter to safely get or create schedule
    schedule = CrontabSchedule.objects.filter(
        minute='0',
        hour='8',
        day_of_month='*',
        month_of_year='*',
        day_of_week='*'
    ).first()

    if not schedule:
        schedule = CrontabSchedule.objects.create(
            minute='0',
            hour='8',
            day_of_month='*',
            month_of_year='*',
            day_of_week='*'
        )

    # Get or create the periodic task
    task, created = PeriodicTask.objects.get_or_create(
        name='Send Birthday Wishes to Employees',
        defaults={
            'task': 'payroll.tasks.send_birthday_emails',
            'crontab': schedule,
            'args': json.dumps([]),
        }
    )

    if not created:
        task.crontab = schedule
        task.enabled = True
        task.save()