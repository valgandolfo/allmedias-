"""
Utilitários de processamento de imagem - NewMedia PWA
"""
import io
import os
import logging
from PIL import Image, ImageOps
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def otimizar_imagem(arquivo, max_width=1280, max_height=1280, quality=75):
    """
    Redimensiona e converte a imagem para JPEG otimizado.
    Recebe um file-like object, retorna um ContentFile.
    """
    try:
        arquivo.seek(0)
        img = Image.open(arquivo)

        # Garante modo RGB (sem transparência)
        if img.mode not in ('RGB',):
            img = img.convert('RGB')

        # Redimensiona se necessário
        w, h = img.size
        if w > max_width or h > max_height:
            ratio = min(max_width / w, max_height / h)
            novo_tamanho = (int(w * ratio), int(h * ratio))
            img = img.resize(novo_tamanho, Image.Resampling.LANCZOS)
            logger.info("[otimizar_imagem] Redimensionado: %dx%d → %dx%d", w, h, *novo_tamanho)

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        buf.seek(0)

        nome_original = getattr(arquivo, 'name', 'imagem')
        base = os.path.splitext(os.path.basename(nome_original))[0]
        result = ContentFile(buf.read(), name=f"{base}.jpg")

        logger.info("[otimizar_imagem] OK — %d KB", result.size // 1024)
        return result

    except Exception as e:
        logger.error("[otimizar_imagem] Erro: %s", e, exc_info=True)
        # Devolve o arquivo original sem processamento
        arquivo.seek(0)
        return arquivo


def gerar_miniatura(arquivo, tamanho=(150, 150), quality=75):
    """
    Gera uma miniatura quadrada recortada do centro.
    Recebe um file-like object, retorna um ContentFile ou None.
    """
    try:
        arquivo.seek(0)
        img = Image.open(arquivo)

        if img.mode not in ('RGB',):
            img = img.convert('RGB')

        # Crop central + redimensionamento
        thumb = ImageOps.fit(img, tamanho, Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        thumb.save(buf, format='JPEG', quality=quality, optimize=True)
        buf.seek(0)

        nome_original = getattr(arquivo, 'name', 'miniatura')
        base = os.path.splitext(os.path.basename(nome_original))[0]
        result = ContentFile(buf.read(), name=f"{base}_thumb.jpg")

        logger.info("[gerar_miniatura] OK — %dx%d", *tamanho)
        return result

    except Exception as e:
        logger.error("[gerar_miniatura] Erro: %s", e, exc_info=True)
        return None
