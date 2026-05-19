from django.apps import AppConfig


class AppContentConfig(AppConfig):
    name = 'app_content'

    def ready(self):
        import app_content.signals