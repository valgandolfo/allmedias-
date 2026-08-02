#!/bin/bash
# Entrypoint unificado: usa a variável SERVICE_TYPE para decidir o que rodar.
# - Serviço web:  SERVICE_TYPE não definida (ou "web")  → gunicorn
# - Serviço cron: SERVICE_TYPE=cron                     → loop a cada 5 minutos

PORT="${PORT:-8000}"
if [ "$SERVICE_TYPE" = "cron" ]; then
    echo "[entrypoint] Modo CRON — iniciando loop de lembretes WhatsApp (a cada 5 minutos)"
    while true; do
        echo "[cron-loop] Disparando enviar_compromissos_whatsapp às $(date '+%Y-%m-%d %H:%M:%S')"
        python manage.py enviar_compromissos_whatsapp
        echo "[cron-loop] Aguardando 300 segundos..."
        sleep 300
    done
else
    echo "[entrypoint] Modo WEB — iniciando Gunicorn na porta $PORT"
    exec gunicorn pro_newmedia.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4
fi
