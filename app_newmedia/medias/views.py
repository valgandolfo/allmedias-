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
    })


@login_required
def media_criar(request):
    """
    Formulário de criação de mídia
    URL: /medias/criar/
    """
    if request.method == 'POST':
        form = MidiaForm(request.POST, request.FILES)
        if form.is_valid():
            midia = form.save(commit=False)
            midia.usuario = request.user
            midia.status = 'concluido' if midia.arquivo else 'pendente'
            midia.save()
            logger.info(f"Mídia criada: ID={midia.id} | usuário={request.user.email}")
            messages.success(request, 'Mídia criada com sucesso!')
            return redirect('media_lista')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = MidiaForm()

    return render(request, 'medias/criar.html', {'form': form})


@login_required
def media_detalhes(request, pk):
    """
    Exibe os detalhes de uma mídia
    URL: /medias/<pk>/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)
    return render(request, 'medias/detalhes.html', {'midia': midia})


@login_required
def media_editar(request, pk):
    """
    Formulário de edição de mídia
    URL: /medias/<pk>/editar/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = MidiaForm(request.POST, request.FILES, instance=midia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mídia atualizada com sucesso!')
            return redirect('media_lista')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = MidiaForm(instance=midia)

    return render(request, 'medias/editar.html', {'form': form, 'midia': midia})


@login_required
def media_deletar(request, pk):
    """
    Confirmação e exclusão de mídia
    URL: /medias/<pk>/deletar/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)

    if request.method == 'POST':
        midia.delete()
        messages.success(request, 'Mídia excluída com sucesso!')
        return redirect('media_lista')

    return render(request, 'medias/deletar.html', {'midia': midia})


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
