"""
Views de mídias - NewMedia PWA
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Midia
from .forms import MidiaForm

logger = logging.getLogger(__name__)


@login_required
def media_lista(request):
    """
    Lista todas as mídias do usuário logado
    URL: /medias/lista/
    """
    medias = Midia.objects.filter(usuario=request.user).order_by('-criado_em')

    return render(request, 'medias/lista.html', {
        'medias': medias,
        'crud_name': 'medias',
    })


@login_required
def media_form(request, pk=None):
    """
    Formulário unificado de criação e edição de mídia
    URL: /medias/criar/ ou /medias/<pk>/form/
    """
    if pk:
        midia = get_object_or_404(Midia, pk=pk, usuario=request.user)
        acao = 'editar'
    else:
        midia = None
        acao = 'criar'

    if request.method == 'POST':
        form = MidiaForm(request.POST, request.FILES, instance=midia)
        if form.is_valid():
            midia_obj = form.save(commit=False)
            midia_obj.usuario = request.user
            midia_obj.status = 'concluido' if midia_obj.arquivo else 'pendente'
            midia_obj.save()
            
            if acao == 'criar':
                logger.info(f"Mídia criada: ID={midia_obj.id} | usuário={request.user.email}")
                messages.success(request, 'Mídia criada com sucesso!')
            else:
                messages.success(request, 'Mídia atualizada com sucesso!')
                
            return redirect('media_lista')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = MidiaForm(instance=midia)

    return render(request, 'medias/detalhes.html', {
        'form': form,
        'midia': midia,
        'acao': acao
    })


@login_required
def media_detalhes(request, pk):
    """
    Exibe os detalhes de uma mídia ou a tela de exclusão
    URL: /medias/<pk>/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)
    acao = request.GET.get('acao', 'ver')

    if acao == 'deletar' and request.method == 'POST':
        midia.delete()
        messages.success(request, 'Mídia excluída com sucesso!')
        return redirect('media_lista')

    return render(request, 'medias/detalhes.html', {
        'midia': midia,
        'acao': acao
    })


@login_required
def media_favoritar(request, pk):
    """
    Alterna o campo favorito da mídia (toggle via AJAX)
    URL: /medias/<pk>/favoritar/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)
    midia.favorito = not midia.favorito
    midia.save(update_fields=['favorito'])
    return JsonResponse({'status': 'adicionado' if midia.favorito else 'removido', 'favorito': midia.favorito})
