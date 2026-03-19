from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversor_lista, name='conversor_lista'),
    path('converter/', views.conversor_converter, name='conversor_converter'),
]
