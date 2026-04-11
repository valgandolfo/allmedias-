import re
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_newmedia.settings')
import django
django.setup()

from app_newmedia.medias.models import Midia
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

user, _ = User.objects.get_or_create(username='test_upload', defaults={'email': 'test@test.com'})

with open("allmedias.png", "rb") as f:
    fake_file = SimpleUploadedFile("allmedias.png", f.read(), content_type="image/png")

m = Midia(descricao="Teste Via Script", tipo="foto", usuario=user, arquivo=fake_file)
m.save()
print("Arquivo Name:", m.arquivo.name)
print("Arquivo URL:", m.arquivo.url)
print("Miniatura Name:", m.miniatura.name if m.miniatura else None)
