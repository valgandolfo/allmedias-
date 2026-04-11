from PIL import Image
import io
from django.core.files.base import ContentFile

# create a 1x1 image
img = Image.new('RGB', (1, 1))
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)
novo_arquivo = ContentFile(buf.read(), name="test.jpg")

print("Before miniatura, size:", len(novo_arquivo.read()))
novo_arquivo.seek(0)

# Simulate miniatura
img2 = Image.open(novo_arquivo)
print("Miniatura gerada, size img2:", img2.size)

# Simulate GoogleDriveStorage._save
print("Has seek:", hasattr(novo_arquivo, 'seek'))
novo_arquivo.seek(0)
print("After pointer reset, read size:", len(novo_arquivo.read()))

