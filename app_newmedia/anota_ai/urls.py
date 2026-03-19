from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.anotacao_lista, name='anotacao_lista'),
    path('criar/', views.anotacao_criar, name='anotacao_criar'),
    path('<int:pk>/', views.anotacao_detalhes, name='anotacao_detalhes'),
    path('<int:pk>/ticar/', views.anotacao_ticar, name='anotacao_ticar'),
    path('<int:pk>/editar/', views.anotacao_editar, name='anotacao_editar'),
    path('<int:pk>/deletar/', views.anotacao_deletar, name='anotacao_deletar'),
    path('<int:pk>/favoritar/', views.anotacao_favoritar, name='anotacao_favoritar'),
    path('<int:pk>/compartilhar-dados/', views.anotacao_compartilhar_dados, name='anotacao_compartilhar_dados'),
    path('<int:pk>/checklist-itens/', views.anotacao_checklist_itens, name='anotacao_checklist_itens'),
    path('item/<int:item_pk>/ticar/', views.anotacao_item_ticar, name='anotacao_item_ticar'),
]
