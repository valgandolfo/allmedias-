import os
import requests
from datetime import date
from django.core.management.base import BaseCommand
from app_newmedia.calendario.models import Compromisso

class Command(BaseCommand):
    help = 'Envia compromissos do dia para o WhatsApp dos usuários usando Evolution API'

    def handle(self, *args, **kwargs):
        hoje = date.today()
        # Filtra apenas os compromissos do dia atual, ordenados por hora
        compromissos = Compromisso.objects.filter(data=hoje).order_by('hora')
        
        if not compromissos.exists():
            self.stdout.write(self.style.SUCCESS(f'Sem compromissos para hoje ({hoje.strftime("%d/%m/%Y")}).'))
            return
            
        # Agrupar compromissos por usuário
        agrupados = {}
        for c in compromissos:
            if c.usuario not in agrupados:
                agrupados[c.usuario] = []
            agrupados[c.usuario].append(c)
            
        evolution_url = os.environ.get('EVOLUTION_API_URL', '').rstrip('/')
        evolution_token = os.environ.get('EVOLUTION_API_TOKEN', '')
        instance_name = os.environ.get('EVOLUTION_INSTANCE_NAME', '')
        
        if not evolution_url or not evolution_token or not instance_name:
            self.stdout.write(self.style.ERROR('As variáveis EVOLUTION_API_URL, EVOLUTION_API_TOKEN e EVOLUTION_INSTANCE_NAME precisam estar configuradas no seu .env ou Railway.'))
            return
            
        headers = {
            'apikey': evolution_token,
            'Content-Type': 'application/json'
        }
        
        for usuario, lista_comp in agrupados.items():
            try:
                perfil = getattr(usuario, 'profile', None)
                telefone = perfil.telefone if perfil else None
            except Exception:
                telefone = None
                
            if not telefone:
                self.stdout.write(self.style.WARNING(f'Usuário {usuario.username} ignorado: Sem telefone configurado no perfil.'))
                continue
                
            # Limpar formatação do telefone (manter apenas números)
            numero_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Se for um número de celular brasileiro no formato local (ex: 11988887777), adiciona 55 na frente
            if len(numero_limpo) in [10, 11] and not numero_limpo.startswith('55'):
                numero_limpo = '55' + numero_limpo
            
            # Formatar a mensagem do WhatsApp
            linhas = [f"Olá, *{usuario.first_name or usuario.username}*! ☀️", "", "Aqui estão os seus compromissos para o dia de hoje:"]
            for c in lista_comp:
                obs = f" - _{c.observacoes}_" if c.observacoes else ""
                linhas.append(f"⏰ *{c.hora.strftime('%H:%M')}* - {c.titulo}{obs}")
                
            mensagem = "\n".join(linhas)
            
            # Preparar a requisição para a Evolution API (endpoint de enviar texto)
            endpoint = f"{evolution_url}/message/sendText/{instance_name}"
            payload = {
                "number": numero_limpo,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": mensagem
                }
            }
            
            try:
                resp = requests.post(endpoint, json=payload, headers=headers)
                if resp.status_code in [200, 201]:
                    self.stdout.write(self.style.SUCCESS(f'Mensagem enviada com sucesso para {usuario.username} ({numero_limpo}).'))
                else:
                    self.stdout.write(self.style.ERROR(f'Falha ao enviar para {usuario.username} ({numero_limpo}). Código: {resp.status_code}. Resposta: {resp.text}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro de conexão ao enviar para {usuario.username}: {str(e)}'))

