from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
import logging

from app_newmedia.medias.models import Midia
from app_newmedia.anota_ai.models import Anotacao, ItemAnotacao
from .models import Transferencia

logger = logging.getLogger(__name__)

@login_required
def transferir_medias(request):
    """
    Dashboard de Transferências - HTML responsivo
    URL: /transferir/medias/
    """
    # Lista de transferências recebidas que foram aceitas
    recebidos = Transferencia.objects.filter(
        destinatario=request.user,
        status='aceito'
    ).order_by('-data_envio')
    
    # Lista de transferências enviadas (todas)
    enviados = Transferencia.objects.filter(
        remetente=request.user
    ).order_by('-data_envio')
    
    return render(request, 'transferir/dashboard.html', {
        'recebidos': recebidos,
        'enviados': enviados,
    })


@login_required
def transferir_caixa_entrada(request):
    """
    Caixa de Entrada de Transferências Pendentes
    URL: /transferir/caixa-entrada/
    """
    pendentes = Transferencia.objects.filter(
        destinatario=request.user,
        status='pendente'
    ).order_by('-data_envio')
    
    return render(request, 'transferir/caixa_entrada.html', {
        'pendentes': pendentes,
    })


@login_required
def transferir_enviar(request):
    """
    Tela para escolher e enviar um item
    URL: /transferir/enviar/
    """
    medias = Midia.objects.filter(usuario=request.user).order_by('-criado_em')
    anotacoes = Anotacao.objects.filter(usuario=request.user).order_by('-criado_em')
    favoritos_medias = set(Midia.objects.filter(usuario=request.user, favorito=True).values_list('id', flat=True))
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_tipo = request.POST.get('item_tipo')
        email_destino = request.POST.get('email_destino', '').strip()
        
        try:
            try:
                usuario_destino = User.objects.get(email__iexact=email_destino)
            except User.DoesNotExist:
                messages.error(request, f'Usuário com e-mail "{email_destino}" não encontrado.')
                return redirect('transferir_enviar')

            if usuario_destino == request.user:
                messages.warning(request, 'Você não pode enviar para você mesmo.')
                return redirect('transferir_enviar')

            # Buscar dados do item para o cache na transferência
            titulo = ""
            subtitulo = ""
            if item_tipo == 'media':
                item = get_object_or_404(Midia, id=item_id, usuario=request.user)
                titulo = item.descricao
                subtitulo = item.get_tipo_display()
            else:
                item = get_object_or_404(Anotacao, id=item_id, usuario=request.user)
                titulo = item.titulo
                subtitulo = f"Anotação ({item.get_tipo_display()})"

            # Criar registro de transferência pendente
            Transferencia.objects.create(
                remetente=request.user,
                destinatario=usuario_destino,
                tipo_item=item_tipo,
                item_id=item_id,
                titulo=titulo,
                subtitulo=subtitulo,
                status='pendente'
            )
            
            logger.info(f"[TRANSFERENCIA] Item {item_id} ({item_tipo}) enviado de {request.user.email} para {email_destino}")
            messages.success(request, f'Item "{titulo}" enviado para a caixa de entrada de {email_destino}!')
            return redirect('transferir_medias')

        except Exception as e:
            logger.error(f"[TRANSFERENCIA] Erro ao enviar: {e}")
            messages.error(request, f'Erro ao realizar o envio: {str(e)}')
            return redirect('transferir_enviar')

    return render(request, 'transferir/enviar_item.html', {
        'medias': medias,
        'anotacoes': anotacoes,
        'favoritos_medias': favoritos_medias,
    })


@login_required
def transferir_media_individual(request, mid_id):
    """
    Tela para enviar uma mídia específica
    URL: /transferir/media/<mid_id>/
    """
    media = get_object_or_404(Midia, id=mid_id, usuario=request.user)
    
    if request.method == 'POST':
        email_destino = request.POST.get('email_destino', '').strip()
        
        try:
            try:
                usuario_destino = User.objects.get(email__iexact=email_destino)
            except User.DoesNotExist:
                messages.error(request, f'Usuário com e-mail "{email_destino}" não encontrado.')
                return render(request, 'transferir/enviar_individual.html', {'media': media})

            if usuario_destino == request.user:
                messages.warning(request, 'Você não pode enviar para você mesmo.')
                return render(request, 'transferir/enviar_individual.html', {'media': media})

            # Criar registro de transferência pendente
            Transferencia.objects.create(
                remetente=request.user,
                destinatario=usuario_destino,
                tipo_item='media',
                item_id=mid_id,
                titulo=media.descricao,
                subtitulo=media.get_tipo_display(),
                status='pendente'
            )
            
            logger.info(f"[TRANSFERENCIA] Mídia {mid_id} enviada de {request.user.email} para {email_destino}")
            messages.success(request, f'Mídia "{media.descricao}" enviada para a caixa de entrada de {email_destino}!')
            return redirect('media_lista')

        except Exception as e:
            logger.error(f"[TRANSFERENCIA] Erro ao enviar individual: {e}")
            messages.error(request, f'Erro ao realizar o envio: {str(e)}')
            return render(request, 'transferir/enviar_individual.html', {'media': media})

    return render(request, 'transferir/enviar_individual.html', {
        'media': media,
    })


@login_required
def transferir_anotacao_individual(request, ano_id):
    """
    Tela para enviar uma anotação específica
    URL: /transferir/anotacao/<ano_id>/
    """
    anotacao = get_object_or_404(Anotacao, id=ano_id, usuario=request.user)
    
    if request.method == 'POST':
        email_destino = request.POST.get('email_destino', '').strip()
        
        try:
            try:
                usuario_destino = User.objects.get(email__iexact=email_destino)
            except User.DoesNotExist:
                messages.error(request, f'Usuário com e-mail "{email_destino}" não encontrado.')
                return render(request, 'transferir/enviar_anotacao.html', {'anotacao': anotacao})

            if usuario_destino == request.user:
                messages.warning(request, 'Você não pode enviar para você mesmo.')
                return render(request, 'transferir/enviar_anotacao.html', {'anotacao': anotacao})

            # Criar registro de transferência pendente
            Transferencia.objects.create(
                remetente=request.user,
                destinatario=usuario_destino,
                tipo_item='anotacao',
                item_id=ano_id,
                titulo=anotacao.titulo,
                subtitulo=f"Anotação ({anotacao.get_tipo_display()})",
                status='pendente'
            )
            
            logger.info(f"[TRANSFERENCIA] Anotação {ano_id} enviada de {request.user.email} para {email_destino}")
            messages.success(request, f'Anotação "{anotacao.titulo}" enviada para a caixa de entrada de {email_destino}!')
            return redirect('anotacao_lista')

        except Exception as e:
            logger.error(f"[TRANSFERENCIA] Erro ao enviar anotação individual: {e}")
            messages.error(request, f'Erro ao realizar o envio: {str(e)}')
            return render(request, 'transferir/enviar_anotacao.html', {'anotacao': anotacao})

    return render(request, 'transferir/enviar_anotacao.html', {
        'anotacao': anotacao,
    })


@login_required
def transferir_acao(request, tra_id, acao):
    """
    Processa Aceitar, Recusar ou Excluir uma transferência
    URL: /transferir/acao/<id>/<acao>/
    """
    transferencia = get_object_or_404(Transferencia, id=tra_id)
    
    # Verificar permissões
    if acao in ['aceitar', 'recusar'] and transferencia.destinatario != request.user:
        messages.error(request, 'Você não tem permissão para esta ação.')
        return redirect('transferir_medias')
    
    if acao == 'excluir' and transferencia.destinatario != request.user and transferencia.remetente != request.user:
        messages.error(request, 'Você não tem permissão para excluir esta transferência.')
        return redirect('transferir_medias')

    try:
        if acao == 'aceitar':
            # Realizar a cópia definitiva do item
            if transferencia.tipo_item == 'media':
                item_origem = Midia.objects.get(id=transferencia.item_id)
                Midia.objects.create(
                    usuario=request.user,
                    descricao=f"[Recebido] {item_origem.descricao}",
                    tipo=item_origem.tipo,
                    arquivo=item_origem.arquivo,
                    tags=item_origem.tags,
                    favorito=False
                )
            else:
                item_origem = Anotacao.objects.get(id=transferencia.item_id)
                anota_nova = Anotacao.objects.create(
                    usuario=request.user,
                    titulo=f"[Recebido] {item_origem.titulo}",
                    texto=item_origem.texto,
                    tipo=item_origem.tipo,
                    pix_chave=item_origem.pix_chave,
                    pix_favorecido=item_origem.pix_favorecido,
                    pix_banco=item_origem.pix_banco,
                    favorito=False
                )
                # Copiar itens se houver
                for item in ItemAnotacao.objects.filter(anotacao=item_origem):
                    ItemAnotacao.objects.create(
                        anotacao=anota_nova,
                        numero=item.numero,
                        concluido=item.concluido,
                        texto=item.texto
                    )
            
            transferencia.status = 'aceito'
            transferencia.data_resposta = timezone.now()
            transferencia.save()
            messages.success(request, f'Item "{transferencia.titulo}" aceito com sucesso!')

        elif acao == 'recusar':
            transferencia.status = 'recusado'
            transferencia.data_resposta = timezone.now()
            transferencia.save()
            messages.info(request, f'Item "{transferencia.titulo}" recusado.')

        elif acao == 'excluir':
            transferencia.delete()
            messages.success(request, 'Registro de transferência excluído.')

    except Exception as e:
        logger.error(f"[TRANSFERENCIA] Erro na ação {acao}: {e}")
        messages.error(request, f'Erro ao processar ação: {str(e)}')

    # Retornar para a tela adequada
    if acao in ['aceitar', 'recusar']:
        return redirect('transferir_caixa_entrada')
    return redirect('transferir_medias')
