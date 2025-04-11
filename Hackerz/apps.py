from django.apps import AppConfig


class HackerzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Hackerz'

    def ready(self):
        import Hackerz.signals  # Importer les signaux au démarrage 