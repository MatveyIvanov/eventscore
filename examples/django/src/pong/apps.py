from django.apps import AppConfig


class PongConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pong"

    def ready(self):
        from config.ecore import ecore

        ecore.spawn_workers()
