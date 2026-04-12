import os
import re
import string
import tempfile
import logging
from collections import Counter
import pytesseract
import PyPDF2
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

STOPWORDS_PT = {
    'a', 'o', 'e', 'é', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 
    'por', 'para', 'com', 'um', 'uma', 'uns', 'umas', 'se', 'os', 'as', 'que', 'não', 'sim',
    'ao', 'aos', 'ou', 'eu', 'você', 'ele', 'ela', 'eles', 'elas', 'nós', 'vós', 'me', 'te',
    'se', 'lhe', 'lhes', 'mais', 'mas', 'como', 'sua', 'seu', 'suas', 'seus', 'este', 'esta',
    'estes', 'estas', 'isso', 'isto', 'aquilo', 'aquele', 'aquela', 'já', 'são', 'ser', 'ter',
    'foi', 'qual', 'quando', 'onde', 'quem', 'porque', 'sem', 'sob', 'sobre', 'entre', 'até',
    'também', 'muito', 'pouco', 'nada', 'tudo', 'quem', 'nem', 'tem', 'tém', 'têm', 'como',
    'pelo', 'pela', 'pelos', 'pelas', 'das'
}

def extrair_texto_imagem(image_path):
    try:
        from PIL import Image
        img = Image.open(image_path)
        # Tenta usar português; se não estiver instalado usa o padrão (eng)
        try:
            return pytesseract.image_to_string(img, lang='por')
        except pytesseract.TesseractError:
            return pytesseract.image_to_string(img)
    except Exception as e:
        logger.error(f"[OCR] Erro em imagem: {e}")
        return ""

def extrair_texto_pdf(pdf_path):
    try:
        texto = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    texto += t + " "
        return texto
    except Exception as e:
        logger.error(f"[OCR] Erro em PDF: {e}")
        return ""

def processar_ocr_arquivo(midia_id):
    from .models import Midia
    try:
        midia = Midia.objects.get(id=midia_id)
    except Midia.DoesNotExist:
        logger.warning(f"[OCR] Mídia {midia_id} não encontrada.")
        return

    if not midia.arquivo:
        return

    ext = os.path.splitext(midia.arquivo.name)[1].lower()
    is_img = ext in ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp']
    is_pdf = ext == '.pdf'

    if not is_img and not is_pdf:
        return

    logger.info(f"[OCR] Iniciando processamento da mídia {midia_id} ({ext})")

    # Baixar o arquivo temporariamente do Wasabi S3 ou local
    try:
        with default_storage.open(midia.arquivo.name, 'rb') as f_in:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f_out:
                f_out.write(f_in.read())
                temp_path = f_out.name
    except Exception as e:
        logger.error(f"[OCR] Erro ao baixar arquivo: {e}")
        return

    texto = ""
    try:
        if is_img:
            texto = extrair_texto_imagem(temp_path)
        elif is_pdf:
            texto = extrair_texto_pdf(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    if not texto.strip():
        logger.info(f"[OCR] Nenhum texto extraído da mídia {midia_id}")
        return

    # NLP Básica
    texto = texto.lower()
    # Manter letras acentuadas (remover o que não é letra acentuada nem espaço)
    texto = re.sub(r'[^a-záéíóúâêôãõç\s]', ' ', texto)
    
    palavras = texto.split()
    # Filtra palavras pequenas (<3 letras) e as stopwords
    palavras_limpas = [p for p in palavras if len(p) > 2 and p not in STOPWORDS_PT]

    contador = Counter(palavras_limpas)
    top_5 = contador.most_common(5)

    if not top_5:
        return

    novas_tags = [f"#{word}" for word, freq in top_5]
    
    tags_atuais = []
    if midia.tags:
        tags_atuais = [t.strip() for t in midia.tags.split(',') if t.strip()]
        
    for nt in novas_tags:
        if nt not in tags_atuais:
            tags_atuais.append(nt)

    todas_tags_str = ', '.join(tags_atuais)
    
    # Atualiza via .update() para evitar disparar o signal/save de novo
    Midia.objects.filter(id=midia.id).update(tags=todas_tags_str)
    logger.info(f"[OCR] Sucesso na mídia {midia_id}. Tags adicionadas/atualizadas: {novas_tags}")
