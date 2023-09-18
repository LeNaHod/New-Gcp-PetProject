from django.apps import AppConfig


class SummaryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "summary"

    def ready(self):
        from .jobs import updater
        updater.start()
