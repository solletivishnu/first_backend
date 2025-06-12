from django.apps import AppConfig


class IncomeTaxReturnsConfig(AppConfig):
    name = 'income_tax_returns'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import income_tax_returns.signals  # 👈 ensure this line exists


