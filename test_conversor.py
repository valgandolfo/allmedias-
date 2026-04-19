import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
m = Midia.objects.filter(tipo='foto').exclude(arquivo='').first()
if m:
    print(f"Midia: {m.id} - {m.arquivo.name}")
    try:
        m.arquivo.open('rb')
        bytes_data = m.arquivo.read()
        m.arquivo.close()
        print(f"Bytes lidos: {len(bytes_data)}")
        if len(bytes_data) < 1000:
            print("Conteudo pequeno:", bytes_data)
    except Exception as e:
        print("Erro:", e)
else:
    print("Nenhuma foto encontrada")
