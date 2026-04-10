import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_newmedia.settings')
django.setup()

from app_newmedia.medias.models import Midia
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

user, _ = User.objects.get_or_create(username='test_upload', defaults={'email': 'test@test.com'})

print("Fazendo upload da foto...")
with open("allmedias.png", "rb") as f:
    fake_file = SimpleUploadedFile("allmedias.png", f.read(), content_type="image/png")

m = Midia(descricao="Teste Via Script", tipo="foto", usuario=user, arquivo=fake_file)
m.save()
print("Salvo com sucesso!")
