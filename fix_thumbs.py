import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
django.setup()

from app_newmedia.medias.models import Midia
from app_newmedia.medias.utils import gerar_miniatura

print("Fixing thumbnails...")
midias = Midia.objects.all()
count = 0
for m in midias:
    if m.is_imagem and not m.miniatura and m.arquivo:
        try:
            print(f"Generating thumb for: {m.pk} - {m.arquivo.name}")
            thumb = gerar_miniatura(m.arquivo.file)
            if thumb:
                m.miniatura = thumb
                m.save(update_fields=['miniatura'])
                count += 1
                print("Thumb created!")
        except Exception as e:
            print(f"Error {m.pk}: {e}")
print(f"Generated {count} thumbnails.")
