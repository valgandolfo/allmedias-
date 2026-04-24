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
def api_receber_notificacao(request):
    """
    API ultra-resiliente para o MacroDroid.
    """
    try:
        # 1. Coleta de dados (GET + POST + JSON)
        data = {}
        data.update(request.GET.dict())
        data.update(request.POST.dict())
        
        if request.content_type == 'application/json' and request.body:
            try:
                json_data = json.loads(request.body)
                if isinstance(json_data, dict):
                    data.update(json_data)
            except: pass

        # 2. Busca de Texto e Token (mesmo se vierem bagunçados)
        texto = data.get('texto') or data.get('notification_text') or ''
        token = data.get('user_token') or data.get('token') or ''

        # Fallback: Procura em todos os campos se estiverem vazios
        if not texto or not token:
            for k, v in data.items():
                val = str(k) if not v else str(v)
                val_strip = val.strip()
                # Se parece um token (32 chars)
                if not token and len(val_strip) == 32: 
                    token = val_strip
                # Se parece uma notificação (contém cifrão ou termos financeiros)
                if not texto and any(x in val.lower() for x in ['r$', 'compra', 'pix', 'pagamento', 'recebido', 'transferencia']):
                    texto = val

        if not texto:
            return JsonResponse({'erro': 'Texto da notificacao nao encontrado na requisicao'}, status=400)

        # 3. Identificar usuário
        from django.contrib.auth.models import User
        try:
            usuario = User.objects.get(profile__api_token=token)
        except:
            return JsonResponse({'erro': f'Token invalido ou usuario nao encontrado: {token}'}, status=401)

        # 4. Processar e Salvar
        dados_parse = NotificacaoCompra.parse_notificacao(texto)
        
        notificacao = NotificacaoCompra.objects.create(
            usuario=usuario,
            texto_completo=texto,
            app_origem=data.get('app') or data.get('package') or dados_parse.get('instituicao') or 'Banco',
            valor=dados_parse.get('valor'),
            estabelecimento=dados_parse.get('estabelecimento', 'Desconhecido'),
            data_compra=dados_parse.get('data') or datetime.now().date(),
            hora_compra=dados_parse.get('hora') or datetime.now().time(),
            tipo_transacao=dados_parse.get('tipo_transacao', 'COMPRA'),
            cartao_final=dados_parse.get('cartao_final', ''),
        )

        return JsonResponse({
            'sucesso': True, 
            'id': notificacao.pk,
            'info': f'Compra de R$ {notificacao.valor} em {notificacao.estabelecimento} salva.'
        })

    except Exception as e:
        return JsonResponse({'erro': f'Erro Interno: {str(e)}'}, status=500)


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
