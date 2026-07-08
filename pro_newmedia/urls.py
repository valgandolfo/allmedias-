"""
URL configuration for AllMedias PWA project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.http import FileResponse, HttpResponse
import os

from app_newmedia.views import home


def service_worker_view(request):
    """Serve o service worker da raiz para garantir escopo completo (/)."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'service-worker.js')
    try:
        with open(sw_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/javascript')
    except FileNotFoundError:
        # Em produção, tenta no STATIC_ROOT (após collectstatic)
        sw_path = os.path.join(settings.STATIC_ROOT, 'service-worker.js')
        with open(sw_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def manifest_view(request):
    """Serve o manifest.webmanifest da raiz."""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.webmanifest')
    try:
        with open(manifest_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/manifest+json')
    except FileNotFoundError:
        manifest_path = os.path.join(settings.STATIC_ROOT, 'manifest.webmanifest')
        with open(manifest_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/manifest+json')
    response['Cache-Control'] = 'no-cache'
    return response

urlpatterns = [
    # ===================================================================
    # PWA — Service Worker e Manifest servidos da raiz (escopo total)
    # ===================================================================
    path('sw.js', service_worker_view, name='service_worker'),
    path('manifest.webmanifest', manifest_view, name='manifest'),

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
