import json
from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Compromisso

@login_required
def calendario_view(request):
    """Renderiza a página principal do calendário"""
    return render(request, 'calendario/calendario.html')

@login_required
def api_compromissos_mes(request):
    """Retorna os compromissos do usuário para um dado mês/ano"""
    try:
        ano = int(request.GET.get('ano', datetime.now().year))
        mes = int(request.GET.get('mes', datetime.now().month))
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Ano ou mês inválido'}, status=400)

    compromissos = Compromisso.objects.filter(
        usuario=request.user,
        data__year=ano,
        data__month=mes
    ).order_by('data', 'hora')

    # Agrupar por dia
    dados = {}
    for c in compromissos:
        dia = c.data.day
        if dia not in dados:
            dados[dia] = []
        dados[dia].append({
            'id': c.id,
            'hora': c.hora.strftime('%H:%M'),
            'titulo': c.titulo,
            'cor': c.cor,
            'observacoes': c.observacoes
        })

    return JsonResponse({'status': 'success', 'dados': dados})

@login_required
@require_POST
def api_criar_compromisso(request):
    """Endpoint para criar um novo compromisso via Fetch/AJAX"""
    try:
        dados = json.loads(request.body)
        data_str = dados.get('data') # YYYY-MM-DD
        hora_str = dados.get('hora') # HH:MM
        titulo = dados.get('titulo')
        cor = dados.get('cor', '#7C8EE0')
        observacoes = dados.get('observacoes', '')

        if not data_str or not hora_str or not titulo:
            return JsonResponse({'status': 'error', 'message': 'Data, hora ou título não fornecidos'}, status=400)

        # Trata a conversão
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora_str, '%H:%M').time()

        Compromisso.objects.create(
            usuario=request.user,
            data=data_obj,
            hora=hora_obj,
            titulo=titulo,
            cor=cor,
            observacoes=observacoes
        )
        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
