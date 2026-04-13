"""
App configuration for SmartPlan module
"""
from django.apps import AppConfig


class SmartplanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_newmedia.smartplan'
    verbose_name = 'SmartPlan - Extrator de Planilhas'
