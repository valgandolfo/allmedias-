import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
from django.core.files.uploadedfile import SimpleUploadedFile
from app_newmedia.conversor.views import _converter_arquivo_para_pdf

# Find a good Midia (that doesn't have the 1Bat prefix and is an image)
m = Midia.objects.filter(tipo='foto').exclude(arquivo__startswith='1Bat').last()
if m:
    print(f"Midia selecionada: {m.id} - {m.arquivo.name}")
    try:
        # Read the file
        bytes_data = _converter_arquivo_para_pdf(m.arquivo)
        print("Conversao ocorreu bem. Tamanho do PDF:", len(bytes_data))
        if len(bytes_data) < 200:
            print("Conteudo pequeno:", bytes_data)
        else:
            print("Comeco do PDF:", bytes_data[:50])
    except Exception as e:
        print("Erro Exception:", e)
else:
    print("Sem midias de foto disponiveis no Wasabi.")
