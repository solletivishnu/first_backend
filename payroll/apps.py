from django.apps import AppConfig
import sys


class PayrollConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payroll'

    def ready(self):
        if any(cmd in sys.argv[0] for cmd in ['gunicorn', 'celery']):
            try:
                from Tara.scheduler_scripts.salary_processing_payroll import schedule_salary_processing
                schedule_salary_processing()
                print("✅ Salary schedule synced in payroll app.")
            except Exception as e:
                print(f"⚠️ Failed to sync salary schedule in payroll app: {e}")
        # Import signals here so they are connected
        try:
            import payroll.signals
            print("✅ Payroll signals imported.")
        except Exception as e:
            print(f"⚠️ Failed to import payroll signals: {e}")