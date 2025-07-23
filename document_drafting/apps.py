from django.apps import AppConfig
import sys

class DocumentDraftingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_drafting'

    def ready(self):
        if any(cmd in sys.argv[0] for cmd in ['gunicorn', 'celery']):
            try:
                from Tara.scheduler_scripts.schedule_tasks import sync_schedules
                sync_schedules()
                print("✅ Celery schedule synced on startup.")
            except Exception as e:
                print(f"⚠️ Failed to sync schedule: {e}")
