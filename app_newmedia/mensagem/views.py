import os
import requests as http_requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Mensagem
from .forms import MensagemForm


def _normalizar_telefone(telefone: str) -> str:
    """Mantém apenas dígitos e adiciona DDI 55 se necessário."""
    numero = ''.join(filter(str.isdigit, telefone))
    if len(numero) in [10, 11] and not numero.startswith('55'):
        numero = '55' + numero
    return numero


def _enviar_whatsapp(telefone: str, mensagem: str) -> dict:
    """Envia mensagem via Evolution API. Retorna {'sucesso': bool, 'erro': str}."""
    evolution_url   = os.environ.get('EVOLUTION_API_URL', '').rstrip('/')
    evolution_token = os.environ.get('EVOLUTION_API_TOKEN', '')
    instance_name   = os.environ.get('EVOLUTION_INSTANCE_NAME', '')

    if not evolution_url or not evolution_token or not instance_name:
        return {'sucesso': False, 'erro': 'Variáveis da Evolution API não configuradas.'}

    numero = _normalizar_telefone(telefone)
    endpoint = f"{evolution_url}/message/sendText/{instance_name}"
    headers  = {'apikey': evolution_token, 'Content-Type': 'application/json'}
    payload  = {'number': numero, 'text': mensagem}

    try:
        resp = http_requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if resp.status_code in [200, 201]:
            return {'sucesso': True, 'erro': ''}
        return {'sucesso': False, 'erro': f'HTTP {resp.status_code}: {resp.text[:200]}'}
    except http_requests.Timeout:
        return {'sucesso': False, 'erro': 'Timeout ao conectar na Evolution API.'}
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


@login_required
def mensagem_lista(request):
    """Lista todas as mensagens do usuário."""
    mensagens = Mensagem.objects.filter(usuario=request.user)
    return render(request, 'mensagem/lista.html', {'mensagens': mensagens})


@login_required
def mensagem_form(request, pk=None):
    """View unificada: cria e edita mensagem. Envia imediatamente se ocorrência = Agora."""
    mensagem = None
    if pk:
        mensagem = get_object_or_404(Mensagem, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = MensagemForm(request.POST, instance=mensagem)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user

            if obj.men_ocorrencia == 'agora':
                resultado = _enviar_whatsapp(obj.men_telefone, obj.men_mensagem)
                if resultado['sucesso']:
                    obj.men_status = True
                    obj.save()
                    messages.success(request, f'✅ Mensagem enviada para {obj.men_nome}!')
                else:
                    obj.men_status = False
                    obj.save()
                    messages.error(request, f'❌ Falha ao enviar: {resultado["erro"]}')
            else:
                obj.men_status = False
                obj.save()
                messages.success(request, f'📅 Mensagem agendada para {obj.men_nome}.')

            return redirect('mensagem_lista')
    else:
        form = MensagemForm(instance=mensagem)

    return render(request, 'mensagem/detalhes.html', {
        'form': form,
        'mensagem': mensagem,
        'acao': 'editar' if mensagem else 'criar',
    })


@login_required
def mensagem_detalhes(request, pk):
    """View de detalhes/confirmação de exclusão."""
    mensagem = get_object_or_404(Mensagem, pk=pk, usuario=request.user)
    acao = request.GET.get('acao', 'ver')

    if acao == 'deletar' and request.method == 'POST':
        mensagem.delete()
        messages.success(request, 'Mensagem excluída com sucesso!')
        return redirect('mensagem_lista')

    return render(request, 'mensagem/detalhes.html', {
        'mensagem': mensagem,
        'acao': acao,
    })


@login_required
@require_POST
def mensagem_reenviar(request, pk):
    """Reenvia uma mensagem já existente via Evolution API (chamada AJAX)."""
    mensagem = get_object_or_404(Mensagem, pk=pk, usuario=request.user)
    resultado = _enviar_whatsapp(mensagem.men_telefone, mensagem.men_mensagem)
    if resultado['sucesso']:
        mensagem.men_status = True
        mensagem.save(update_fields=['men_status'])
        return JsonResponse({'sucesso': True})
    return JsonResponse({'sucesso': False, 'erro': resultado['erro']}, status=400)
