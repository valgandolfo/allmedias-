"""
Views do conversor de mídias - NewMedia PWA
Converte imagens (foto) em PDF e salva como nova Mídia
"""
import io
import logging
import os
import re
import zipfile
import xml.etree.ElementTree as ET

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.template.defaultfilters import filesizeformat

from app_newmedia.medias.models import Midia

logger = logging.getLogger(__name__)


@login_required
def conversor_lista(request):
    """
    Lista mídias conversíveis (fotos, documentos) do usuário
    URL: /conversor/
    """
    medias = Midia.objects.filter(
        usuario=request.user,
        tipo__in=['foto', 'documento', 'texto']
    ).order_by('-criado_em')

    return render(request, 'conversor/conversor.html', {'medias': medias})


@login_required
def conversor_converter(request):
    """
    Recebe AJAX POST, converte imagem em PDF e salva como nova Mídia
    URL: /conversor/converter/
    """
    if request.method != 'POST':
        return JsonResponse({'sucesso': False, 'erro': 'Método não permitido.'}, status=405)

    mid_id = request.POST.get('mid_id')
    descricao = request.POST.get('descricao', '').strip()
    tags = request.POST.get('tags', '').strip()

    if not mid_id or not descricao:
        return JsonResponse({'sucesso': False, 'erro': 'Preencha todos os campos obrigatórios.'})

    try:
        midia_origem = Midia.objects.get(id=mid_id, usuario=request.user)
    except Midia.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'Mídia não encontrada.'})

    if not midia_origem.arquivo:
        return JsonResponse({'sucesso': False, 'erro': 'Mídia sem arquivo para converter.'})

    try:
        pdf_bytes = _converter_arquivo_para_pdf(midia_origem.arquivo)
    except Exception as e:
        logger.error(f"[CONVERSOR] Erro na conversão: {e}")
        return JsonResponse({'sucesso': False, 'erro': f'Falha na conversão: {str(e)}'})

    nome_arquivo = f"{descricao.replace(' ', '_')}.pdf"
    pdf_file = ContentFile(pdf_bytes, name=nome_arquivo)

    try:
        nova_midia = Midia(
            usuario=request.user,
            descricao=descricao,
            tipo='pdf',
            tags=tags,
            status='concluido',
        )
        nova_midia.arquivo = pdf_file
        nova_midia.tamanho = filesizeformat(len(pdf_bytes))
        nova_midia.save()

        logger.info(f"[CONVERSOR] PDF criado: ID={nova_midia.id} | usuário={request.user.email}")
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'"{descricao}.pdf" criado com sucesso!',
            'redirect': '/medias/lista/',
        })

    except Exception as e:
        logger.error(f"[CONVERSOR] Erro ao salvar mídia: {e}")
        return JsonResponse({'sucesso': False, 'erro': f'Erro ao salvar: {str(e)}'})


def _ler_arquivo_bytes(arquivo_field):
    arquivo_field.open('rb')
    conteudo = arquivo_field.read()
    arquivo_field.close()
    return conteudo


def _converter_arquivo_para_pdf(arquivo_field):
    nome = getattr(arquivo_field, 'name', '') or ''
    ext = os.path.splitext(nome)[1].lower()
    arquivo_bytes = _ler_arquivo_bytes(arquivo_field)

    ext_imagem = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tif', '.tiff'}
    ext_texto = {'.txt', '.md', '.csv', '.log'}

    if ext in ext_imagem:
        return _converter_imagem_bytes_para_pdf(arquivo_bytes)

    if ext in ext_texto:
        texto = _decodificar_texto(arquivo_bytes)
        return _converter_texto_para_pdf(texto or '(Arquivo de texto vazio)')

    if ext == '.docx':
        texto_docx = _extrair_texto_docx(arquivo_bytes)
        if not texto_docx.strip():
            texto_docx = 'Nao foi possivel extrair texto do arquivo DOCX.'
        return _converter_texto_para_pdf(texto_docx)

    if ext == '.doc':
        # DOC binario antigo: sem dependencia externa, manter fluxo com fallback claro.
        nome_base = os.path.basename(nome) or 'arquivo.doc'
        aviso = (
            f'Arquivo: {nome_base}\n\n'
            'Formato DOC detectado. A conversao automatica de conteudo '
            'desse formato nao e suportada neste ambiente.'
        )
        return _converter_texto_para_pdf(aviso)

    raise ValueError(f'Tipo de arquivo nao suportado para conversao: {ext or "desconhecido"}')


def _converter_imagem_bytes_para_pdf(img_bytes):
    """
    Converte bytes de imagem em bytes de PDF usando Pillow + reportlab.
    """
    from PIL import Image
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    img = Image.open(io.BytesIO(img_bytes))

    # Converter para RGB se necessário (PNG com alpha, etc.)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    img_w, img_h = img.size
    page_w, page_h = A4  # 595.27 x 841.89 pts

    # Calcular escala mantendo proporção
    scale = min(page_w / img_w, page_h / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x_offset = (page_w - draw_w) / 2
    y_offset = (page_h - draw_h) / 2

    # Salvar imagem temporariamente em bytes para o reportlab
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85)
    img_buffer.seek(0)

    # reportlab precisa de ImageReader para aceitar BytesIO
    from reportlab.lib.utils import ImageReader
    img_reader = ImageReader(img_buffer)

    # Gerar PDF em memória
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.drawImage(
        img_reader,
        x_offset, y_offset,
        width=draw_w, height=draw_h,
        preserveAspectRatio=True
    )
    c.showPage()
    c.save()

    return pdf_buffer.getvalue()


def _decodificar_texto(arquivo_bytes):
    for encoding in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try:
            return arquivo_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return arquivo_bytes.decode('utf-8', errors='replace')


def _extrair_texto_docx(docx_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
            xml_bytes = zf.read('word/document.xml')
    except Exception:
        return ''

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ''

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragrafos = []
    for p in root.findall('.//w:p', ns):
        partes = [t.text or '' for t in p.findall('.//w:t', ns)]
        linha = ''.join(partes).strip()
        if linha:
            paragrafos.append(linha)
    return '\n'.join(paragrafos)


def _quebrar_linha(texto, largura_max, font_name='Helvetica', font_size=11):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    if not texto:
        return ['']

    palavras = re.split(r'(\s+)', texto)
    linhas = []
    atual = ''

    for token in palavras:
        candidato = atual + token
        if stringWidth(candidato, font_name, font_size) <= largura_max:
            atual = candidato
        else:
            if atual.strip():
                linhas.append(atual.rstrip())
                atual = token.lstrip()
            else:
                # Palavra extremamente longa
                linhas.append(token[:120])
                atual = token[120:]

    if atual.strip() or not linhas:
        linhas.append(atual.rstrip())
    return linhas


def _converter_texto_para_pdf(texto):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    page_w, page_h = A4
    margin_x = 40
    margin_y = 40
    line_height = 16
    y = page_h - margin_y

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.setFont('Helvetica', 11)

    for linha_raw in (texto or '').splitlines():
        linhas = _quebrar_linha(linha_raw, page_w - (margin_x * 2))
        for linha in linhas:
            if y <= margin_y:
                c.showPage()
                c.setFont('Helvetica', 11)
                y = page_h - margin_y
            c.drawString(margin_x, y, linha)
            y -= line_height

        # Espaço entre parágrafos
        if y <= margin_y:
            c.showPage()
            c.setFont('Helvetica', 11)
            y = page_h - margin_y
        y -= 4

    c.showPage()
    c.save()
    return pdf_buffer.getvalue()
