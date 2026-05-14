from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_view, name='calendario_index'),
    path('api/mes/', views.api_compromissos_mes, name='api_compromissos_mes'),
    path('api/criar/', views.api_criar_compromisso, name='api_criar_compromisso'),
    path('api/editar/<int:id>/', views.api_editar_compromisso, name='api_editar_compromisso'),
    path('api/excluir/<int:id>/', views.api_excluir_compromisso, name='api_excluir_compromisso'),
]
