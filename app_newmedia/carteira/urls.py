"""
URLs do app Carteira
"""
from django.urls import path
from . import views

urlpatterns = [
    # Página de listagem
    path('', views.carteira_lista, name='carteira_lista'),

    # API para MacroDroid
    path('api/notificacao/', views.api_receber_notificacao, name='carteira_api_notificacao'),
]
