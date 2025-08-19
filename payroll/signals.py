from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import PayrollWorkflow, EmployeeSalaryHistory
import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from django.core.cache import cache
from .views import generate_payslip_from_history
from Tara.settings.default import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PRIVATE_BUCKET_NAME

@receiver(pre_save, sender=PayrollWorkflow)
def trigger_payslip_generation(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = PayrollWorkflow.objects.get(pk=instance.pk)

    if not old_instance.lock_payroll and instance.lock_payroll:
        payroll = instance.payroll
        month = (
            instance.month)
        financial_year = instance.financial_year
        generate_and_upload_all_payslips(
            payroll,
            month,
            financial_year
        )

def generate_and_upload_all_payslips(payroll_id, month, financial_year):
    """
    Generates and uploads payslips for all employees in a payroll to S3.
    Triggered when lock_payroll changes from False → True.
    """
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    bucket_name = AWS_PRIVATE_BUCKET_NAME

    salary_histories = EmployeeSalaryHistory.objects.filter(
        payroll=payroll_id,
        month=month,
        financial_year=financial_year
    )

    if not salary_histories:
        print(f"[WARNING] No salary histories found for payroll={payroll_id}, month={month}, FY={financial_year}")
        return

    print(f"[INFO] Generating payslips for payroll={payroll_id}, month={month}, FY={financial_year}")
    year = int(financial_year.split("-")[0]) if month >= 4 else int(financial_year.split("-")[1])

    for history in salary_histories:
        pdf_bytes = generate_payslip_from_history(
            history,
            month,
            year,
            financial_year
        )

        if not pdf_bytes:
            print(f"[ERROR] No PDF generated for employee {history.employee_id}")
            continue

        object_key = f"salary_slips/{history.employee_id}/{financial_year}/{month}_{year}.pdf"
        print(f"[DEBUG] Uploading to S3 key={object_key}, size={len(pdf_bytes)} bytes")

        try:
            response = s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=pdf_bytes,
                ContentType="application/pdf"
            )
            print(f"[DEBUG] S3 upload response: {response}")

            # Cache signed URL
            signed_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=7200  # 2 hours in seconds
            )
            cache_key = f"salary_slip_url_{history.employee_id}_{month}_{year}_{financial_year}"
            cache.set(cache_key, signed_url, timeout=7200)

        except (BotoCoreError, ClientError) as e:
            print(f"[ERROR] Failed to upload to S3 for employee {history.employee_id}: {e}")

    print(f"[INFO] Completed payslip generation for payroll={payroll_id}")

