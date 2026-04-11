import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_newmedia.settings')
django.setup()
from app_newmedia.medias.utils import otimizar_imagem, gerar_miniatura
from django.core.files.uploadedfile import SimpleUploadedFile

with open("allmedias.png", "rb") as f:
    fake_file = SimpleUploadedFile("allmedias.png", f.read(), content_type="image/png")

print("Chamando otimizar_imagem...")
opt = otimizar_imagem(fake_file)
print("Opt size:", opt.size)

print("Chamando gerar_miniatura...")
try:
    thumb = gerar_miniatura(opt)
    print("Thumb size:", thumb.size if thumb else None)
except Exception as e:
    import traceback
    traceback.print_exc()
