import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
from django.test import RequestFactory
from app_newmedia.conversor.views import _converter_arquivo_para_pdf

m = Midia.objects.filter(tipo='foto').exclude(arquivo='').last()
if m:
    print(f"Midia ID: {m.id}, Nome: {m.arquivo.name}")
    try:
        bytes_data = _converter_arquivo_para_pdf(m.arquivo)
        print("Tamanho do PDF gerado:", len(bytes_data))
        print("Inicio dos bytes:", bytes_data[:50])
    except Exception as e:
        print("Erro Exception:", e)
else:
    print("Sem midia.")
