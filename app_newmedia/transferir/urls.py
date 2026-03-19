from django.urls import path
from . import views

urlpatterns = [
    path('medias/', views.transferir_medias, name='transferir_medias'),
    path('caixa-entrada/', views.transferir_caixa_entrada, name='transferir_caixa_entrada'),
    path('enviar/', views.transferir_enviar, name='transferir_enviar'),
    path('media/<int:mid_id>/', views.transferir_media_individual, name='transferir_media_individual'),
    path('anotacao/<int:ano_id>/', views.transferir_anotacao_individual, name='transferir_anotacao_individual'),
    path('acao/<int:tra_id>/<str:acao>/', views.transferir_acao, name='transferir_acao'),
]
