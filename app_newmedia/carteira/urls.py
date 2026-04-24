"""
URLs do app Carteira
"""
from django.urls import path
from . import views

urlpatterns = [
    # Página de listagem
    path('', views.carteira_lista, name='carteira_lista'),

    # API para E-mail (SendGrid Inbound)
    path('api/email/', views.api_receber_email, name='carteira_api_email'),
]
