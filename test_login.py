import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_newmedia.settings')
django.setup()

c = Client()
response = c.get('/login/')

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("Content Length:", len(response.content))
    print("Includes '<form':", b'<form' in response.content)
else:
    print("Response Content:")
    print(response.content.decode('utf-8')[:500])
