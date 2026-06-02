FROM python:3.10-slim

# Evita que o Python grave arquivos .pyc no disco
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que os prints no terminal não sofram buffer
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema que o Python pode precisar
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo o código do projeto para a pasta de trabalho
COPY . /app/

# Expõe a porta (útil localmente, a Railway ignora e usa a dela)
EXPOSE 8000

# O botão de ligar! Comando que a Railway vai executar no final:
# Ele faz as migrações no banco e liga o Gunicorn (servidor de produção)
CMD bash -c "python manage.py migrate && gunicorn pro_newmedia.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
