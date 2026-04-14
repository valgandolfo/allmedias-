"""
Config do app Carteira
"""
from django.apps import AppConfig


class CarteiraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_newmedia.carteira'
    verbose_name = 'Carteira - Notificações de Compras'
