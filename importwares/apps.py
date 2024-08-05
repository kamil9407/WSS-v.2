from django.apps import AppConfig


class ImportwaresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'importwares'
    
    def ready(self):
        import importwares.signals

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        import products.signals  # Import sygnałów