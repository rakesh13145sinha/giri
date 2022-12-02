from django.apps import AppConfig


class LicenseholderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'licenseHolder'
    def ready(self):
        import licenseHolder.signals
