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

# Coleta os arquivos estáticos durante o build forçando modo produção para gerar o manifesto
RUN DJANGO_DEBUG=False DATABASE_URL="mysql://dummy:dummy@localhost/dummy" python manage.py collectstatic --noinput

# Entrypoint unificado: decide se roda gunicorn (web) ou o cron
# baseado na variável de ambiente SERVICE_TYPE
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
