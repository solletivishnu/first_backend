
from celery import shared_task
import datetime
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from Tara.settings.default import *

@shared_task
def print_current_time():
    now = datetime.datetime.now()
    print("✅ Task ran at:", now)

    # AWS SES Configuration
    ses_client = boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    sender_email = 'admin@tarafirst.com'  # ✅ Your verified sender in AWS SES
    recipient_email = 'saikiranmekala@tarafirst.com'  # ✅ Must be verified if SES in sandbox mode

    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email],
            },
            Message={
                'Subject': {
                    'Data': '🕒 Celery Task Executed',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': f'The Celery task ran at {now.strftime("%Y-%m-%d %H:%M:%S")}',
                        'Charset': 'UTF-8'
                    },
                },
            }
        )
        print("📧 Email sent! Message ID:", response['MessageId'])

    except (BotoCoreError, ClientError) as e:
        print("❌ Failed to send email:", str(e))

