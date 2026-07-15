#!/bin/bash
# Entrypoint unificado: usa a variável SERVICE_TYPE para decidir o que rodar.
# - Serviço web:  SERVICE_TYPE não definida (ou "web")  → gunicorn
# - Serviço cron: SERVICE_TYPE=cron                     → management command

if [ "$SERVICE_TYPE" = "cron" ]; then
    echo "[entrypoint] Modo CRON — executando enviar_compromissos_whatsapp"
    exec python manage.py enviar_compromissos_whatsapp
else
    echo "[entrypoint] Modo WEB — iniciando Gunicorn"
    exec gunicorn pro_newmedia.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4
fi
