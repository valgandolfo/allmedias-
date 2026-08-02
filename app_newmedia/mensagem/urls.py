from django.urls import path
from . import views

urlpatterns = [
    path('lista/',           views.mensagem_lista,    name='mensagem_lista'),
    path('criar/',           views.mensagem_form,     name='mensagem_criar'),
    path('<int:pk>/',        views.mensagem_detalhes, name='mensagem_detalhes'),
    path('<int:pk>/form/',   views.mensagem_form,     name='mensagem_form'),
    path('<int:pk>/reenviar/', views.mensagem_reenviar, name='mensagem_reenviar'),
]
