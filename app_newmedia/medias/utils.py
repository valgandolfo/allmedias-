"""
Utilitários de mídia - NewMedia PWA
"""
import io
import os
import logging
from PIL import Image
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def otimizar_imagem(arquivo, max_width=1280, max_height=1280, quality=75):
    """
    Reduz o tamanho de uma imagem antes de enviá-la ao storage.
    - Redimensiona proporcionalmente se passar de max_width x max_height
    - Converte para JPEG quality=75
    - Retorna um ContentFile pronto para o FileField
    """
    try:
        if hasattr(arquivo, 'seek'):
            try:
                arquivo.seek(0)
            except Exception:
                pass

        img = Image.open(arquivo)
        filename = getattr(arquivo, 'name', 'imagem.jpg')
        base_name = os.path.splitext(filename)[0]

        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
            logger.info(f"Redimensionando imagem {width}x{height} → {new_size[0]}x{new_size[1]}")
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        novo_nome = f"{base_name}.jpg"
        novo_arquivo = ContentFile(buffer.read(), name=novo_nome)

        old_kb = (arquivo.size / 1024) if hasattr(arquivo, 'size') and arquivo.size else 0
        new_kb = novo_arquivo.size / 1024
        if old_kb:
            economia = ((old_kb - new_kb) / old_kb) * 100
            logger.info(f"Imagem otimizada: {old_kb:.1f}KB → {new_kb:.1f}KB ({economia:.1f}% menor)")

        return novo_arquivo

    except Exception as e:
        logger.error(f"Erro ao otimizar imagem: {e}")
        return arquivo

def gerar_miniatura(arquivo, size=(150, 150), quality=75):
    """
    Gera uma miniatura quadrada para listas rápidas.
    - Usa ImageOps.fit para recortar do centro.
    - Converte para JPEG e retorna ContentFile.
    """
    try:
        from PIL import ImageOps
        
        if hasattr(arquivo, 'seek'):
            arquivo.seek(0)

        img = Image.open(arquivo)
        filename = getattr(arquivo, 'name', 'miniatura.jpg')
        base_name = os.path.splitext(filename)[0]

        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # fit recorta e redimensiona mantendo proporção (crop central)
        thumb = ImageOps.fit(img, size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        thumb.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        novo_nome = f"{base_name}_thumb.jpg"
        logger.info(f"Miniatura gerada com sucesso: {novo_nome} ({size[0]}x{size[1]})")
        
        return ContentFile(buffer.read(), name=novo_nome)

    except Exception as e:
        logger.error(f"Erro ao gerar miniatura: {e}")
        return None
