"""
Views do SmartPlan - NewMedia PWA
Extrai dados de PDFs e converte para planilhas (CSV/XLSX)
"""
import io
import logging
import os
import re

import pandas as pd
import pdfplumber

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat

from app_newmedia.medias.models import Midia

logger = logging.getLogger(__name__)


@login_required
def smartplan_lista(request):
    """
    Lista PDFs do usuário para extração de planilha
    URL: /smartplan/
    """
    medias = Midia.objects.filter(
        usuario=request.user,
        tipo__in=['pdf', 'documento']
    ).order_by('-criado_em')

    return render(request, 'smartplan/smartplan.html', {'medias': medias})


@login_required
def smartplan_extrair(request):
    """
    Recebe AJAX POST, extrai dados do PDF e retorna CSV/XLSX
    URL: /smartplan/extrair/
    """
    if request.method != 'POST':
        return JsonResponse({'sucesso': False, 'erro': 'Método não permitido.'}, status=405)

    mid_id = request.POST.get('mid_id')
    formato = request.POST.get('formato', 'csv').strip().lower()

    if not mid_id:
        return JsonResponse({'sucesso': False, 'erro': 'ID da mídia não fornecido.'})

    try:
        midia = Midia.objects.get(id=mid_id, usuario=request.user)
    except Midia.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'Mídia não encontrada.'})

    if not midia.arquivo:
        return JsonResponse({'sucesso': False, 'erro': 'Mídia sem arquivo para processar.'})

    try:
        dados = _extrair_dados_pdf(midia.arquivo)
    except Exception as e:
        logger.error(f"[SMARTPLAN] Erro na extração: {e}")
        return JsonResponse({'sucesso': False, 'erro': f'Falha na extração: {str(e)}'})

    if not dados:
        return JsonResponse({'sucesso': False, 'erro': 'Nenhum dado tabular encontrado no PDF.'})

    try:
        df = pd.DataFrame(dados)
        arquivo_bytes, content_type, ext = _converter_dataframe(df, formato)

        nome_base = os.path.splitext(midia.arquivo.name)[0] if midia.arquivo.name else 'planilha'
        nome_arquivo = f"{nome_base}.{ext}"

        response = HttpResponse(arquivo_bytes, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        response['X-File-Size'] = filesizeformat(len(arquivo_bytes))
        return response

    except Exception as e:
        logger.error(f"[SMARTPLAN] Erro ao converter dados: {e}")
        return JsonResponse({'sucesso': False, 'erro': f'Erro ao gerar planilha: {str(e)}'})


def _extrair_dados_pdf(arquivo_field):
    """
    Extrai dados tabulares de um PDF usando pdfplumber.
    Retorna lista de dicionários.
    """
    arquivo_field.open('rb')
    conteudo = arquivo_field.read()
    arquivo_field.close()

    with pdfplumber.open(io.BytesIO(conteudo)) as pdf:
        todas_tabelas = []

        for pagina in pdf.pages:
            tabelas = pagina.extract_tables()
            if tabelas:
                for tabela in tabelas:
                    if tabela and len(tabela) > 1:
                        # Primeira linha como cabeçalho
                        cabecalho = tabela[0]
                        # Limpar cabeçalhos
                        cabecalho_limpo = [
                            _limpar_cabecalho(col) if col else f'Coluna_{i}'
                            for i, col in enumerate(cabecalho)
                        ]
                        # Dados das linhas restantes
                        for linha in tabela[1:]:
                            if any(cell is not None for cell in linha):
                                registro = {}
                                for i, valor in enumerate(linha):
                                    chave = cabecalho_limpo[i] if i < len(cabecalho_limpo) else f'Coluna_{i}'
                                    registro[chave] = valor if valor is not None else ''
                                todas_tabelas.append(registro)

        # Se não encontrou tabelas estruturadas, tenta extrair por regex
        if not todas_tabelas:
            todas_tabelas = _extrair_por_regex(pdf)

        return todas_tabelas


def _limpar_cabecalho(texto):
    """Limpa texto de cabeçalho para ser usado como nome de coluna."""
    if not texto:
        return ''
    # Remove caracteres especiais, mantendo letras, números, espaços e underscores
    texto = re.sub(r'[^\w\s]', '', str(texto))
    # Substitui espaços por underscores
    texto = texto.strip().replace(' ', '_')
    # Garante que não começa com número
    if texto and texto[0].isdigit():
        texto = f'_{texto}'
    return texto or 'Coluna'


def _extrair_por_regex(pdf):
    """
    Fallback: extrai dados por padrões regex quando não há tabelas estruturadas.
    Útil para PDFs com dados em formato de texto livre (ex: faturas).
    """
    dados = []

    for pagina in pdf.pages:
        texto = pagina.extract_text()
        if not texto:
            continue

        # Padrão para datas + descrição + valor (ex: faturas, extratos)
        padrao_fatura = re.compile(
            r'(\d{2}/\d{2})\s+(.*?)\s+(\d+[\.,]\d{2})'
        )

        # Padrão com parcelas
        padrao_parcelas = re.compile(
            r'(\d{2}/\d{2})\s+(.*?)\s+(\d{2}/\d{2})\s+(\d+[\.,]\d{2})'
        )

        for linha in texto.split('\n'):
            # Tenta padrão com parcelas primeiro
            match_p = padrao_parcelas.search(linha)
            if match_p:
                descricao = match_p.group(2).strip().upper()
                if 'TOTAL' in descricao or 'RESUMO' in descricao:
                    continue
                dados.append({
                    'Data': match_p.group(1),
                    'Descricao': descricao,
                    'Parcela': match_p.group(3),
                    'Valor': match_p.group(4).replace('.', '').replace(',', '.')
                })
                continue

            # Tenta padrão comum
            match_c = padrao_fatura.search(linha)
            if match_c:
                descricao = match_c.group(2).strip().upper()
                if 'TOTAL' in descricao or 'RESUMO' in descricao:
                    continue
                dados.append({
                    'Data': match_c.group(1),
                    'Descricao': descricao,
                    'Valor': match_c.group(3).replace('.', '').replace(',', '.')
                })

    return dados


def _converter_dataframe(df, formato):
    """
    Converte DataFrame para bytes no formato solicitado.
    Retorna (bytes, content_type, extensao)
    """
    if formato == 'xlsx':
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
        buffer.seek(0)
        return buffer.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'

    # Default: CSV
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, sep=';', encoding='utf-8-sig')
    return buffer.getvalue().encode('utf-8-sig'), 'text/csv; charset=utf-8', 'csv'
