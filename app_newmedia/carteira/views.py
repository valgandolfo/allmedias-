"""
Views do app Carteira - API para E-mail (SendGrid) e página de listagem
"""
import json
import logging
import re
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import NotificacaoCompra

logger = logging.getLogger(__name__)


@csrf_exempt
def api_receber_notificacao_tasker(request):
    """
    Endpoint para o Tasker (Android).
    Recebe o texto bruto da notificacao bancaria via HTTP POST.
    Autenticacao por api_token no header ou na URL.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Metodo nao permitido'}, status=405)

    # Autenticacao por token (header ou querystring)
    token = (
        request.headers.get('X-Api-Token')
        or request.GET.get('token')
        or request.POST.get('token')
    )
    if not token:
        return JsonResponse({'erro': 'Token nao fornecido'}, status=401)

    from django.contrib.auth.models import User
    try:
        usuario = User.objects.get(profile__api_token=token)
    except User.DoesNotExist:
        return JsonResponse({'erro': 'Token invalido'}, status=401)

    try:
        # Tasker pode enviar JSON ou form-data
        if request.content_type and 'application/json' in request.content_type:
            body = json.loads(request.body)
        else:
            body = request.POST.dict()

        texto = body.get('texto', '') or body.get('text', '') or body.get('notificacao', '')
        app_origem = body.get('app', '') or body.get('app_origem', 'TASKER')

        if not texto:
            return JsonResponse({'erro': 'Campo texto e obrigatorio'}, status=400)

        logger.info(f"[Tasker] Notificacao recebida de {usuario.username} | app={app_origem}")

        # Reutiliza o parser do modelo
        dados = NotificacaoCompra.parse_notificacao(texto)

        notificacao = NotificacaoCompra.objects.create(
            usuario=usuario,
            texto_completo=texto[:5000],
            app_origem=app_origem.upper() or dados.get('instituicao') or 'BANCO',
            valor=dados.get('valor'),
            estabelecimento=str(dados.get('estabelecimento') or 'DESCONHECIDO').upper(),
            data_compra=dados.get('data') or datetime.now().date(),
            hora_compra=dados.get('hora') or datetime.now().time(),
            tipo_transacao=str(dados.get('tipo_transacao') or 'COMPRA').upper(),
            origem='TASKER',
        )

        return JsonResponse({
            'sucesso': True,
            'id': notificacao.pk,
            'info': f'Salvo: R$ {notificacao.valor} em {notificacao.estabelecimento}'
        })

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON invalido'}, status=400)
    except Exception as e:
        logger.exception("[Tasker] Erro ao processar notificacao")
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
def api_receber_email(request):
    """
    Endpoint para o SendGrid Inbound Parse.
    Recebe e-mails de bancos e extrai os dados.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Metodo nao permitido'}, status=405)

    try:
        # SendGrid envia como multipart/form-data
        data = request.POST.dict()
        subject = data.get('subject', '')
        texto_corpo = data.get('text', '') or data.get('html', '')
        destinatario = data.get('to', '')

        logger.info(f"Email recebido para: {destinatario} | Assunto: {subject}")

        # 1. Identificar usuário pelo destinatário (ex: token@allmedias.com.br)
        # Tenta extrair o token do endereço de e-mail
        token = ''
        match_token = re.search(r'([a-f0-9]{32})', destinatario.lower())
        if match_token:
            token = match_token.group(1)
        
        if not token:
            # Fallback: tentar no campo 'from' ou no assunto se o usuário encaminhou manualmente
            # Mas o ideal é o Inbound Parse enviar direto para um endereço com token
            logger.warning(f"API Email: Token nao encontrado no destinatario: {destinatario}")
            return JsonResponse({'erro': 'Destinatario invalido ou sem token'}, status=400)

        from django.contrib.auth.models import User
        try:
            usuario = User.objects.get(profile__api_token=token)
        except Exception as e:
            logger.error(f"API Email: Token {token} nao encontrado. Erro: {e}")
            return JsonResponse({'erro': 'Usuario nao encontrado'}, status=401)

        # 2. Processar E-mail
        dados_parse = NotificacaoCompra.parse_email(subject, texto_corpo)
        
        # 3. Salvar
        notificacao = NotificacaoCompra.objects.create(
            usuario=usuario,
            texto_completo=f"E-MAIL: {subject}\n\n{texto_corpo}"[:5000], # Limita tamanho
            app_origem=dados_parse.get('instituicao') or 'E-MAIL BANCO',
            valor=dados_parse.get('valor'),
            estabelecimento=str(dados_parse.get('estabelecimento', 'DESCONHECIDO')).upper(),
            data_compra=dados_parse.get('data') or datetime.now().date(),
            hora_compra=dados_parse.get('hora') or datetime.now().time(),
            tipo_transacao=str(dados_parse.get('tipo_transacao', 'COMPRA')).upper(),
            origem='EMAIL'
        )

        return JsonResponse({
            'sucesso': True,
            'id': notificacao.pk,
            'info': f'E-mail processado: R$ {notificacao.valor} em {notificacao.estabelecimento}'
        })

    except Exception as e:
        logger.exception("Erro ao processar e-mail inbound")
        return JsonResponse({'erro': str(e)}, status=500)


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

    # Filtros e Busca
    search_query = request.GET.get('q', '')
    tipo_filtro = request.GET.get('tipo', '')

    if search_query:
        notificacoes = notificacoes.filter(
            models.Q(estabelecimento__icontains=search_query) |
            models.Q(texto_completo__icontains=search_query)
        )

    if tipo_filtro:
        notificacoes = notificacoes.filter(tipo_transacao=tipo_filtro)

    # Totais
    total_geral = notificacoes.aggregate(total=models.Sum('valor'))['total'] or 0
    
    # Subtotais (baseados na lista filtrada ou geral?)
    # O usuário pediu "total geral: pix compras". Geralmente isso se refere à base atual filtrada.
    total_pix = notificacoes.filter(tipo_transacao='PIX').aggregate(total=models.Sum('valor'))['total'] or 0
    total_compra = notificacoes.filter(tipo_transacao='COMPRA').aggregate(total=models.Sum('valor'))['total'] or 0

    return render(request, 'carteira/lista.html', {
        'notificacoes': notificacoes,
        'total_geral': total_geral,
        'total_pix': total_pix,
        'total_compra': total_compra,
        'search_query': search_query,
        'tipo_filtro': tipo_filtro,
    })


# Import necessário para o aggregate - já no topo do arquivo
