import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
from app_newmedia.conversor.views import _converter_arquivo_para_pdf

m = Midia.objects.filter(tipo='foto').exclude(arquivo='').last()
if m:
    print(f"Midia: {m.id} - {m.arquivo.name}")
    try:
        pdf_bytes = _converter_arquivo_para_pdf(m.arquivo)
        print(f"Gerou bytes de PDF. Tamanho: {len(pdf_bytes)}")
        print("Cabecalho PDF:", pdf_bytes[:20])
    except Exception as e:
        print("Erro na conversao:", e)
else:
    print("Nenhuma foto")
