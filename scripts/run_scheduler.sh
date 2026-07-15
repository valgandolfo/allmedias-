#!/bin/bash
# Loop infinito: executa o comando a cada 30 segundos
# Use este script como Start Command de um serviço Worker no Railway
echo "=== Iniciando scheduler de compromissos ==="
while true; do
    python manage.py enviar_compromissos_whatsapp
    sleep 30
done
