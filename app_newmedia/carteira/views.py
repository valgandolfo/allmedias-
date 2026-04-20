"""
Views do app Carteira - API para MacroDroid e página de listagem
"""
import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import NotificacaoCompra


@csrf_exempt
@require_POST
def api_receber_notificacao(request):
    """
    API que o MacroDroid envia para gravar a notificação.
    Recebe JSON com: texto, app_origem, timestamp, e dados do usuário.
    """
    try:
        print(f"--- NOVA REQUISICAO MACRODROID ---")
        print(f"Content-Type: {request.content_type}")
        
        # MacroDroid pode enviar via POST form ou JSON
        if request.content_type == 'application/json':
            print(f"Body Bruto: {request.body}")
            data = json.loads(request.body)
        else:
            print(f"POST Data: {request.POST}")
            print(f"GET Data: {request.GET}")
            # Se enviou na aba 2 (Query Parameters), cai no GET. Se mandou na aba 3 (Body), cai no POST.
            data = request.POST if request.POST else request.GET

        texto = data.get('texto', data.get('notification_text', ''))
        app_origem = data.get('app', data.get('notification_application', ''))
        timestamp = data.get('timestamp', '')

        print(f"Texto: '{texto}' | App: '{app_origem}'")

        if not texto:
            print("Erro: Texto vazio")
            return JsonResponse({
                'sucesso': False,
                'erro': 'Texto da notificação é obrigatório'
            }, status=400)

        # Identificar usuário via token/chave
        user_token = data.get('user_token', '')
        print(f"Token Recebido: '{user_token}'")
        
        from django.contrib.auth.models import User
        try:
            usuario = User.objects.get(profile__api_token=user_token)
            print(f"Usuário identificado: {usuario.username}")
        except (User.DoesNotExist, Exception) as e:
            print(f"Erro ao identificar usuário: {e}")
            # Fallback: tenta por email no header ou token
            return JsonResponse({
                'sucesso': False,
                'erro': 'Usuário não identificado. Verifique o user_token.'
            }, status=401)

        # Parse do texto
        dados_parse = NotificacaoCompra.parse_notificacao(texto)

        # Salva a notificação
        notificacao = NotificacaoCompra.objects.create(
            usuario=usuario,
            texto_completo=texto,
            app_origem=app_origem,
            valor=dados_parse['valor'],
            estabelecimento=dados_parse['estabelecimento'],
        )

        return JsonResponse({
            'sucesso': True,
            'id': notificacao.pk,
            'valor': str(notificacao.valor) if notificacao.valor else None,
            'estabelecimento': notificacao.estabelecimento,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'sucesso': False,
            'erro': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'erro': str(e)
        }, status=500)


@login_required
def carteira_lista(request):
    """
    Lista de notificações de compras do usuário logado
    """
    # Garante que o usuário tem um token de API gerado
    if hasattr(request.user, 'profile') and not request.user.profile.api_token:
        import secrets
        request.user.profile.api_token = secrets.token_hex(16)
        request.user.profile.save(update_fields=['api_token'])

    notificacoes = NotificacaoCompra.objects.filter(
        usuario=request.user
    ).order_by('-criado_em')

    total_gasto = notificacoes.aggregate(
        total=models.Sum('valor')
    )['total'] or 0

    return render(request, 'carteira/lista.html', {
        'notificacoes': notificacoes,
        'total_gasto': total_gasto,
    })


# Import necessário para o aggregate - já no topo do arquivo
