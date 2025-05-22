from django.apps import AppConfig
import sys

sys.dont_write_bytecode = True

class TripmindConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tripmind'