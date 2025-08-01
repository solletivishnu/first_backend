from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


def schedule_salary_processing():
    # Use filter to safely get or create schedule
    schedule = CrontabSchedule.objects.filter(
        minute='10',
        hour='12',
        day_of_month='26-30',
        month_of_year='*',
        day_of_week='*'
    ).first()

    if not schedule:
        schedule = CrontabSchedule.objects.create(
            minute='0',
            hour='2',
            day_of_month='26-30',
            month_of_year='*',
            day_of_week='*'
        )

    # Get or create the periodic task
    task, created = PeriodicTask.objects.get_or_create(
        name='Run Employee Salary Processing',
        defaults={
            'task': 'payroll.tasks.process_all_orgs_salary_task',
            'crontab': schedule,
            'args': json.dumps([]),
        }
    )

    if not created:
        task.crontab = schedule
        task.enabled = True
        task.save()
