from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import re
import sys

from .models import Anotacao, ItemAnotacao
from .forms import AnotacaoForm
from .utils import gerar_payload_pix

@login_required
def anotacao_lista(request):
    """
    Lista todas as anotações do usuário
    """
    anotacoes = Anotacao.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'anota_ai/lista.html', {'anotacoes': anotacoes})

@login_required
def anotacao_form(request, pk=None):
    """
    View unificada: cria e edita anotacao.
    Se pk=None → criar (form zerado)
    Se pk existe → editar (form com dados)
    """
    anotacao = None
    if pk is not None:
        anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
        # Se for lista ou checklist, reconstruir texto a partir dos itens
        if anotacao.tipo in ['lista_numerada', 'checklist'] and not anotacao.texto:
            itens = anotacao.itens.all().order_by('numero')
            linhas = []
            for item in itens:
                prefixo = ""
                if anotacao.tipo == 'checklist':
                    prefixo = "☑ " if item.concluido else "☐ "
                elif anotacao.tipo == 'lista_numerada':
                    prefixo = f"{item.numero} - "
                linhas.append(f"{prefixo}{item.texto}")
            anotacao.texto = "\n".join(linhas)

    if request.method == 'POST':
        if anotacao:
            form = AnotacaoForm(request.POST, instance=anotacao)
        else:
            form = AnotacaoForm(request.POST)

        if form.is_valid():
            anotacao = form.save(commit=False)
            if not anotacao.usuario_id:
                anotacao.usuario = request.user
            anotacao.save()

            texto_post = request.POST.get('texto', '')
            processar_itens_anotacao(anotacao, texto_post)
            if anotacao.tipo in ('lista_numerada', 'checklist'):
                Anotacao.objects.filter(pk=anotacao.pk).update(texto=None)

            messages.success(request, 'Anotação salva com sucesso!')
            return redirect('anotacao_lista')
    else:
        if anotacao:
            form = AnotacaoForm(instance=anotacao)
        else:
            form = AnotacaoForm()

    return render(request, 'anota_ai/form.html', {
        'form': form,
        'anotacao': anotacao,
    })

@login_required
@require_POST
def anotacao_salvar_itens(request, pk):
    """
    Grava só os itens (lista numerada / checklist) a partir do texto do textarea.
    Usado após Enter no editor para persistir master/detail sem exigir «Salvar» no fim.
    """
    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    if anotacao.tipo not in ('lista_numerada', 'checklist'):
        return JsonResponse({'erro': 'Apenas lista numerada ou checklist.'}, status=400)

    texto = request.POST.get('texto', '')
    processar_itens_anotacao(anotacao, texto)
    Anotacao.objects.filter(pk=anotacao.pk).update(texto=None)
    return JsonResponse({'sucesso': True})


@login_required
def anotacao_detalhes(request, pk=None):
    """
    View unificada de detalhes/confirmacao de exclusao.
    Se pk=None → redireciona para lista
    Se ?acao=deletar → confirma exclusao inline
    Caso contrario → mostra conteudo da anotacao
    """
    if pk is None:
        return redirect('anotacao_lista')

    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    acao = request.GET.get('acao', 'ver')

    pix_payload = ""
    if anotacao.tipo == 'pix':
        pix_payload = gerar_payload_pix(
            anotacao.pix_chave,
            anotacao.pix_favorecido,
            anotacao.pix_cidade,
            anotacao.pix_valor
        )

    # Se acao = deletar e POST confirmado
    if acao == 'deletar' and request.method == 'POST':
        anotacao.delete()
        messages.success(request, 'Anotação excluída com sucesso!')
        return redirect('anotacao_lista')

    return render(request, 'anota_ai/detalhes.html', {
        'anotacao': anotacao,
        'pix_payload': pix_payload,
        'acao': acao,
    })

@login_required
def anotacao_ticar(request, pk):
    """
    Tela de marcação de checklist (estilo módulo de edição).
    """
    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    if anotacao.tipo != 'checklist':
        messages.error(request, 'A opção Ticar está disponível apenas para checklist.')
        return redirect('anotacao_lista')

    itens = anotacao.itens.all().order_by('numero')
    total_itens = itens.count()
    concluidos = itens.filter(concluido=True).count()
    return render(request, 'anota_ai/ticar.html', {
        'anotacao': anotacao,
        'itens': itens,
        'total_itens': total_itens,
        'concluidos': concluidos,
    })

@login_required
def anotacao_favoritar(request, pk):
    """
    Toggle favorito via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
        
    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    anotacao.favorito = not anotacao.favorito
    anotacao.save(update_fields=['favorito'])
    
    return JsonResponse({
        'status': 'success',
        'favorito': anotacao.favorito
    })

def _montar_texto_compartilhamento(anotacao):
    if anotacao.tipo == 'link':
        titulo = anotacao.titulo or 'Link'
        url = (anotacao.texto or '').strip()
        if url:
            return f"{titulo}\n\n{url}"
        return titulo

    if anotacao.tipo == 'pix':
        linhas = [
            f"Nome: {anotacao.pix_nome or '-'}",
            f"Chave PIX: {anotacao.pix_chave or '-'}",
            f"Favorecido: {anotacao.pix_favorecido or '-'}",
            f"Banco: {anotacao.pix_banco or '-'}",
        ]
        if anotacao.pix_cidade:
            linhas.append(f"Cidade: {anotacao.pix_cidade}")
        if anotacao.pix_valor:
            linhas.append(f"Valor: R$ {anotacao.pix_valor}")
            
        pix_payload = gerar_payload_pix(
            anotacao.pix_chave,
            anotacao.pix_favorecido,
            anotacao.pix_cidade,
            anotacao.pix_valor
        )
        if pix_payload:
            linhas.append("\nPix Copia e Cola:")
            linhas.append(pix_payload)
            
        conteudo = "\n".join(linhas)
    elif anotacao.tipo == 'checklist':
        itens = anotacao.itens.all().order_by('numero')
        linhas = []
        for item in itens:
            marcador = "[X]" if item.concluido else "[ ]"
            linhas.append(f"{marcador} {item.texto}")
        conteudo = "\n".join(linhas) if linhas else (anotacao.texto or "")
    elif anotacao.tipo == 'lista_numerada':
        itens = anotacao.itens.all().order_by('numero')
        linhas = [f"{item.numero} - {item.texto}" for item in itens]
        conteudo = "\n".join(linhas) if linhas else (anotacao.texto or "")
    else:
        conteudo = anotacao.texto or ""

    titulo = anotacao.titulo or "Anotação"
    if conteudo.strip():
        return f"{titulo}\n\n{conteudo}"
    return titulo

@login_required
def anotacao_compartilhar_dados(request, pk):
    """
    Retorna texto pronto para compartilhamento da anotação.
    """
    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    texto = _montar_texto_compartilhamento(anotacao)
    return JsonResponse({
        'sucesso': True,
        'titulo': anotacao.titulo,
        'texto_compartilhar': texto,
        'tipo': anotacao.tipo,
    })

@login_required
def anotacao_checklist_itens(request, pk):
    """
    Retorna os itens da anotação checklist para exibição no modal de ticar.
    """
    anotacao = get_object_or_404(Anotacao, pk=pk, usuario=request.user)
    if anotacao.tipo != 'checklist':
        return JsonResponse({'erro': 'Esta anotação não é um checklist.'}, status=400)

    itens = anotacao.itens.all().order_by('numero')
    payload = [
        {
            'id': item.id,
            'numero': item.numero,
            'texto': item.texto,
            'concluido': item.concluido,
        }
        for item in itens
    ]
    return JsonResponse({'sucesso': True, 'itens': payload})

@login_required
@require_POST
def anotacao_item_ticar(request, item_pk):
    """
    Alterna concluído de um item de checklist.
    """
    item = get_object_or_404(
        ItemAnotacao.objects.select_related('anotacao'),
        pk=item_pk,
        anotacao__usuario=request.user
    )

    if item.anotacao.tipo != 'checklist':
        return JsonResponse({'erro': 'Item não pertence a checklist.'}, status=400)

    item.concluido = not item.concluido
    item.save(update_fields=['concluido'])

    return JsonResponse({
        'sucesso': True,
        'item_id': item.id,
        'concluido': item.concluido
    })

def processar_itens_anotacao(anotacao, texto_bruto):
    """
    Processa o texto bruto e cria itens de anotação se for lista ou checklist.
    Usa o padrão "Delete All + Bulk Create" com transação atômica.
    Para texto simples e PIX, apenas limpa os itens antigos.
    """
    from django.db import transaction

    sys.stderr.write(f'[DEBUG-AI] processar_itens: tipo={anotacao.tipo}, texto_bruto_len={len(texto_bruto)}, texto_bruto={repr(texto_bruto[:100])}\n')
    sys.stderr.flush()

    # Sempre limpar itens antigos ao salvar para recriar baseados no texto atual
    anotacao.itens.all().delete()

    if anotacao.tipo not in ('lista_numerada', 'checklist'):
        sys.stderr.write(f'[DEBUG-AI] processar_itens: tipo nao e lista/checklist, saindo.\n')
        sys.stderr.flush()
        return

    if not texto_bruto:
        sys.stderr.write(f'[DEBUG-AI] processar_itens: texto_bruto vazio, saindo.\n')
        sys.stderr.flush()
        return

    linhas = texto_bruto.split('\n')
    sys.stderr.write(f'[DEBUG-AI] processar_itens: linhas_count={len(linhas)}\n')
    sys.stderr.flush()
    novos_itens = []
    numero = 1

    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        concluido = False
        texto_item = linha_limpa

        if anotacao.tipo == 'checklist':
            if linha_limpa.startswith('☑') or linha_limpa.startswith('[x]') or linha_limpa.startswith('[X]') or linha_limpa.startswith('- [x]') or linha_limpa.startswith('- [X]'):
                concluido = True
                texto_item = re.sub(r'^(-\s*)?(☑|\[x\]|\[X\])\s*', '', linha_limpa)
            elif linha_limpa.startswith('☐') or linha_limpa.startswith('[]') or linha_limpa.startswith('[ ]') or linha_limpa.startswith('- []') or linha_limpa.startswith('- [ ]'):
                concluido = False
                texto_item = re.sub(r'^(-\s*)?(☐|\[\]|\[ \])\s*', '', linha_limpa)

        elif anotacao.tipo == 'lista_numerada':
            texto_item = re.sub(r'^\d+\s*[\.\-]\s*', '', linha_limpa)

        if texto_item.strip():
            novos_itens.append(ItemAnotacao(
                anotacao=anotacao,
                numero=numero,
                concluido=concluido,
                texto=texto_item.strip()
            ))
            sys.stderr.write(f'[DEBUG-AI] processar_itens: adicionou item numero={numero}, texto={repr(texto_item[:50])}\n')
            sys.stderr.flush()
            numero += 1

    sys.stderr.write(f'[DEBUG-AI] processar_itens: novos_itens_count={len(novos_itens)}\n')
    sys.stderr.flush()

    if novos_itens:
        with transaction.atomic():
            ItemAnotacao.objects.bulk_create(novos_itens)
            sys.stderr.write(f'[DEBUG-AI] processar_itens: bulk_create executado com sucesso!\n')
            sys.stderr.flush()
    else:
        sys.stderr.write(f'[DEBUG-AI] processar_itens: nenhum item para criar.\n')
        sys.stderr.flush()
