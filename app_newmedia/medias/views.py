"""
Views de mídias - NewMedia PWA
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
import urllib.request

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
            midia_obj.status = 'concluido'
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
        'acao': acao,
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


@login_required
def media_download(request, pk):
    """
    Proxy para baixar/compartilhar a mídia contornando problemas de CORS do Storage (R2/S3).
    URL: /medias/<pk>/download/
    """
    midia = get_object_or_404(Midia, pk=pk, usuario=request.user)
    if not midia.arquivo:
        return HttpResponse("Arquivo não encontrado", status=404)
        
    url = midia.arquivo.url
    
    def file_iterator(response, chunk_size=8192):
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            yield chunk

    try:
        req = urllib.request.Request(url)
        # Adiciona User-Agent para evitar alguns bloqueios
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req)
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        resp = StreamingHttpResponse(file_iterator(response), content_type=content_type)
        resp['Content-Disposition'] = f'attachment; filename="{midia.nome_exibicao}"'
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        logger.error(f"Erro ao baixar midia {pk}: {e}")
        return HttpResponse("Erro ao baixar o arquivo", status=500)
