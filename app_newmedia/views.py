"""
Views principais do AllMedias PWA
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


def welcome(request):
    """
    Página pública de boas-vindas (opcional)
    Redireciona usuários logados para home
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'welcome.html')


@login_required
def home(request):
    """
    Página inicial do AllMedias PWA - REQUER LOGIN
    Usuários não logados são redirecionados para /login/
    """
    from app_newmedia.medias.models import Midia

    try:
        profile = request.user.profile
    except Exception:
        from .registration.models import UserProfile
        profile = UserProfile.objects.create(user=request.user)

    total_midias = Midia.objects.filter(usuario=request.user).count()
    total_favoritos = Midia.objects.filter(usuario=request.user, favorito=True).count()
    recentes = Midia.objects.filter(usuario=request.user).order_by('-criado_em')[:3]

    import datetime
    agora = datetime.datetime.now()
    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    data_formatada = f"Hoje, {agora.day} {meses_pt[agora.month - 1]}"

    context = {
        'profile': profile,
        'user': request.user,
        'nome_exibicao': profile.nome_completo or request.user.username,
        'dias_restantes': profile.dias_restantes,
        'acesso_ativo': profile.acesso_ativo,
        'total_midias': total_midias,
        'total_favoritos': total_favoritos,
        'recentes': recentes,
        'data_formatada': data_formatada,
    }

    return render(request, "home.html", context)


@login_required
def dashboard(request):
    """
    Dashboard principal para usuários logados
    """
    profile = request.user.profile
    
    context = {
        'profile': profile,
        'user': request.user,
        'estatisticas': {
            'total_midias': profile.total_midias,
            'total_anotacoes': profile.total_anotacoes,
            'dias_restantes': profile.dias_restantes,
            'plano': profile.get_plano_display(),
        }
    }
    
    return render(request, 'dashboard.html', context)


def handler404(request, exception):
    """
    Página de erro 404 personalizada
    """
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """
    Página de erro 500 personalizada
    """
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    """
    Página de erro 403 personalizada
    """
    return render(request, 'errors/403.html', status=403)


def health_check(request):
    """
    Endpoint de health check para monitoramento
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'AllMedias PWA',
        'version': '1.0.0'
    })

