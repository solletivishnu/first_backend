from celery import shared_task
from .services.salary_processor import EmployeeSalaryProcessor, AllOrgPayrollProcessor
from payroll.models import PayrollOrg
from datetime import date


@shared_task
def process_all_orgs_salary_task():
    today = date.today()

    # Financial year format: "2024-2025"
    fy_start = today.year if today.month >= 4 else today.year - 1
    financial_year = f"{fy_start}-{fy_start + 1}"
    month = today.month

    print(f"[INFO] Running salary processing for all orgs: FY={financial_year}, Month={month}")
    AllOrgPayrollProcessor(financial_year, month).run()
    print("[INFO] Payroll processing completed.")



@shared_task
def send_birthday_emails():
    """
    Send birthday emails to employees whose birthday is today.
    This task runs daily at 6 AM to check for birthdays.
    """
    from datetime import date as _date
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from .models import EventManagement
    import boto3

    today = _date.today()

    # Find all birthday events for today (irrespective of year)
    birthday_events = (
        EventManagement.objects
        .filter(
            is_birthday=True,
            date__month=today.month,
            date__day=today.day,
        )
        .select_related('employee', 'payroll__business')
    )

    emails_sent = 0
    errors = []

    # Initialize AWS SES client (requires AWS_REGION and credentials in env)
    ses_client = boto3.client("ses", region_name=getattr(settings, 'AWS_REGION', 'ap-south-1'))

    for event in birthday_events:
        employee = event.employee
        if employee and employee.work_email:
            try:
                subject = f"{event.title or 'Happy Birthday'}!"
                org_name = getattr(getattr(event.payroll, 'business', None), 'nameOfBusiness', 'TaraFirst')
                context = {
                    "title": event.title or "Happy Birthday",
                    "description": event.description,
                    "org_name": org_name,
                }
                html_body = render_to_string("email/birthday_wish.html", context)
                text_body = strip_tags(html_body)

                sender_email = 'admin@tarafirst.com'
                recipient_email = employee.work_email

                response = ses_client.send_email(
                    Source=sender_email,
                    Destination={
                        'ToAddresses': [recipient_email],
                    },
                    Message={
                        'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                        'Body': {
                            'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                            'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                        },
                    },
                )

                emails_sent += 1
                print(f"[INFO] Birthday email sent to {employee.work_email} via SES. Message ID: {response.get('MessageId')}")
            except Exception as e:
                error_msg = f"[ERROR] Failed to send birthday email to {employee.work_email}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)

    print(f"[INFO] Birthday email task completed. {emails_sent} emails sent, {len(errors)} errors.")
    return {
        'emails_sent': emails_sent,
        'errors': errors,
        'total_birthdays': birthday_events.count(),
    }