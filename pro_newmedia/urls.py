"""
URL configuration for AllMedias PWA project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from app_newmedia.views import home

urlpatterns = [
    # ===================================================================
    # FAVICON (redireciona /favicon.ico para o static)
    # ===================================================================
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),

    # ===================================================================
    # ADMINISTRAÇÃO
    # ===================================================================
    path("admin/", admin.site.urls),
    
    # ===================================================================
    # PÁGINAS PRINCIPAIS
    # ===================================================================
    path("", home, name="home"),
    
    # ===================================================================
    # AUTENTICAÇÃO
    # ===================================================================
    path("", include('app_newmedia.registration.urls')),

    # ===================================================================
    # MÍDIAS
    # ===================================================================
    path("medias/", include('app_newmedia.medias.urls')),

    # ===================================================================
    # ANOTA AÍ+
    # ===================================================================
    path("anotacoes/", include('app_newmedia.anota_ai.urls')),

    # ===================================================================
    # CONVERSOR
    # ===================================================================
    path("conversor/", include('app_newmedia.conversor.urls')),

    # ===================================================================
    # TRANSFERIR
    # ===================================================================
    path("transferir/", include('app_newmedia.transferir.urls')),

    # ===================================================================
    # CALENDÁRIO
    # ===================================================================
    path("calendario/", include('app_newmedia.calendario.urls')),

    # ===================================================================
    # SMARTPLAN
    # ===================================================================
    path("smartplan/", include('app_newmedia.smartplan.urls')),

    # ===================================================================
    # CARTEIRA (notificações de compras)
    # ===================================================================
    path("carteira/", include('app_newmedia.carteira.urls')),
]

# ===================================================================
# ARQUIVOS DE MÍDIA E ESTÁTICOS (desenvolvimento)
# ===================================================================
if settings.DEBUG:
    # Servir arquivos de mídia em desenvolvimento
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
    
    # Servir arquivos estáticos em desenvolvimento (se necessário)
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )

# ===================================================================
# HANDLER DE ERROS PERSONALIZADOS
# ===================================================================
# handler404 = 'app_newmedia.views.handler404'
# handler500 = 'app_newmedia.views.handler500'
# handler403 = 'app_newmedia.views.handler403'
