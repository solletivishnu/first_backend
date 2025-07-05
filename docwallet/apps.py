from django.apps import AppConfig

class DocwalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'docwallet'

    def ready(self):
        from .helpers import build_context_tries
        import threading
        threading.Thread(target=build_context_tries).start()
