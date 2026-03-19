"""
URLs de mídias - NewMedia PWA
"""
from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.media_lista, name='media_lista'),
    path('criar/', views.media_criar, name='media_criar'),
    path('<int:pk>/', views.media_detalhes, name='media_detalhes'),
    path('<int:pk>/editar/', views.media_editar, name='media_editar'),
    path('<int:pk>/deletar/', views.media_deletar, name='media_deletar'),
    path('<int:pk>/favoritar/', views.media_favoritar, name='media_favoritar'),
]
