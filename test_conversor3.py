import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
from app_newmedia.conversor.views import _converter_arquivo_para_pdf
from django.core.files.base import ContentFile

# Mock an image in memory
pdf_bytes = _converter_arquivo_para_pdf(ContentFile(b"Hello world test!", name="test.txt"))
print("Tamanho do PDF de texto:", len(pdf_bytes))
print(pdf_bytes[:50])

from PIL import Image
import io
img = Image.new('RGB', (60, 30), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()

pdf_bytes2 = _converter_arquivo_para_pdf(ContentFile(img_bytes, name="test.jpg"))
print("Tamanho do PDF de imagem:", len(pdf_bytes2))
print(pdf_bytes2[:50])
