from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_view, name='calendario_index'),
    path('api/mes/', views.api_compromissos_mes, name='api_compromissos_mes'),
    path('api/criar/', views.api_criar_compromisso, name='api_criar_compromisso'),
]
