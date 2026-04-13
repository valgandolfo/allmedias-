from django.urls import path
from . import views

urlpatterns = [
    path('', views.smartplan_lista, name='smartplan_lista'),
    path('extrair/', views.smartplan_extrair, name='smartplan_extrair'),
]
