"""
Views do app Carteira - API para MacroDroid e página de listagem
"""
import json
import logging
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
            except Exception as e:
                logger.warning(f"Erro ao parsear JSON: {e}")

        logger.info(f"API Notificacao recebida: {data}")

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
            logger.warning("API Notificacao: Texto nao encontrado")
            return JsonResponse({'erro': 'Texto da notificacao nao encontrado na requisicao'}, status=400)

        # 2.5 Converter para maiúsculas para comparações e salvamento padronizado
        texto = texto.upper()

        # 3. Identificar usuário
        from django.contrib.auth.models import User
        try:
            usuario = User.objects.get(profile__api_token=token)
        except Exception as e:
            logger.error(f"API Notificacao: Token invalido ou usuario nao encontrado. Token: {token}. Erro: {e}")
            return JsonResponse({'erro': f'Token invalido ou usuario nao encontrado: {token}'}, status=401)

        # 4. Processar e Salvar
        dados_parse = NotificacaoCompra.parse_notificacao(texto)
        
        try:
            notificacao = NotificacaoCompra.objects.create(
                usuario=usuario,
                texto_completo=texto,
                app_origem=(data.get('app') or data.get('package') or dados_parse.get('instituicao') or 'BANCO').upper(),
                valor=dados_parse.get('valor'),
                estabelecimento=str(dados_parse.get('estabelecimento', 'DESCONHECIDO')).upper(),
                data_compra=dados_parse.get('data') or datetime.now().date(),
                hora_compra=dados_parse.get('hora') or datetime.now().time(),
                tipo_transacao=str(dados_parse.get('tipo_transacao', 'COMPRA')).upper(),
                cartao_final=dados_parse.get('cartao_final', ''),
            )
        except Exception as e:
            logger.error(f"API Notificacao: Erro ao salvar no banco. Dados: {dados_parse}. Erro: {e}")
            raise e

        return JsonResponse({
            'sucesso': True, 
            'id': notificacao.pk,
            'info': f'Compra de R$ {notificacao.valor} em {notificacao.estabelecimento} salva.',
            'texto_extraido': {
                'valor': str(notificacao.valor),
                'estabelecimento': notificacao.estabelecimento,
                'tipo': notificacao.tipo_transacao
            },
            'debug_texto_recebido': texto
        })

    except Exception as e:
        logger.exception("Erro interno na API de Notificacao")
        return JsonResponse({'erro': f'Erro Interno: {str(e)}'}, status=500)


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
