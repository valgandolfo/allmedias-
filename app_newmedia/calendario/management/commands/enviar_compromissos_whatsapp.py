import os
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from app_newmedia.calendario.models import Compromisso


class Command(BaseCommand):
    help = 'Envia lembrete de compromissos para o WhatsApp na antecedência configurada usando Evolution API'

    def handle(self, *args, **kwargs):
        agora = timezone.localtime()
        self.stdout.write(f'[CRON] Executando às {agora.strftime("%Y-%m-%d %H:%M:%S %Z")}')

        # Buscar compromissos até 2 dias à frente (antecedência máxima = 1440 min = 1 dia)
        limite_busca_dias = agora.date() + timedelta(days=2)

        compromissos_pendentes = Compromisso.objects.filter(
            data__lte=limite_busca_dias,
            lembrete_enviado=False
        ).order_by('data', 'hora')

        total_pendentes = compromissos_pendentes.count()
        self.stdout.write(f'[CRON] {total_pendentes} compromisso(s) pendente(s) encontrado(s).')

        # ---------------------------------------------------------------
        # JANELA DE ENVIO (ajustada para cron de */5 * * * * — a cada 5 minutos):
        #   - Limite SUPERIOR: olha até 5 minutos à frente para não perder o próximo tick
        #   - Limite INFERIOR: tolera até 5 minutos de atraso na execução do cron
        #
        # Isso garante que cada lembrete seja enviado exatamente uma vez,
        # mesmo que o cron atrase ou rode levemente adiantado.
        # ---------------------------------------------------------------
        JANELA_FUTURO_MIN = 5        # minuto(s) à frente (1 ciclo do cron)
        JANELA_PASSADO_MIN = 5       # minuto(s) atrás (tolerância a atrasos)
        DESCARTA_APOS_MIN = 30       # marca como enviado se passou mais de 30min sem envio

        compromissos_para_enviar = []

        for c in compromissos_pendentes:
            data_hora_comp = timezone.make_aware(datetime.combine(c.data, c.hora))
            hora_do_lembrete = data_hora_comp - timedelta(minutes=c.antecedencia_minutos)

            self.stdout.write(
                f'  → [{c.titulo}] em {data_hora_comp.strftime("%d/%m %H:%M")} | '
                f'lembrete às {hora_do_lembrete.strftime("%d/%m %H:%M")} | '
                f'antecedência: {c.antecedencia_minutos}min'
            )

            # Compromisso já passou há mais de DESCARTA_APOS_MIN — descartar
            if data_hora_comp < (agora - timedelta(minutes=DESCARTA_APOS_MIN)):
                self.stdout.write(f'     → DESCARTADO (compromisso já expirou há mais de {DESCARTA_APOS_MIN}min)')
                c.lembrete_enviado = True
                c.save()
                continue

            # Verifica se está dentro da janela de envio (passado próximo + futuro imediato)
            dentro_da_janela = (
                hora_do_lembrete <= (agora + timedelta(minutes=JANELA_FUTURO_MIN)) and
                hora_do_lembrete >= (agora - timedelta(minutes=JANELA_PASSADO_MIN))
            )

            if dentro_da_janela:
                self.stdout.write(f'     → DENTRO DA JANELA — adicionado para envio')
                compromissos_para_enviar.append(c)
            else:
                diff = hora_do_lembrete - agora
                self.stdout.write(f'     → Fora da janela (lembrete em {int(diff.total_seconds() / 60)}min)')

        if not compromissos_para_enviar:
            self.stdout.write(self.style.SUCCESS('[CRON] Sem compromissos na janela atual para notificar.'))
            return

        self.stdout.write(f'[CRON] {len(compromissos_para_enviar)} compromisso(s) para enviar agora.')

        # Verificar variáveis de ambiente da Evolution API
        evolution_url = os.environ.get('EVOLUTION_API_URL', '').rstrip('/')
        evolution_token = os.environ.get('EVOLUTION_API_TOKEN', '')
        instance_name = os.environ.get('EVOLUTION_INSTANCE_NAME', '')

        if not evolution_url:
            self.stdout.write(self.style.ERROR('[CRON] ERRO: EVOLUTION_API_URL não configurada.'))
            return
        if not evolution_token:
            self.stdout.write(self.style.ERROR('[CRON] ERRO: EVOLUTION_API_TOKEN não configurado.'))
            return
        if not instance_name:
            self.stdout.write(self.style.ERROR('[CRON] ERRO: EVOLUTION_INSTANCE_NAME não configurado.'))
            return

        self.stdout.write(f'[CRON] Evolution API: {evolution_url} | Instância: {instance_name}')

        headers = {
            'apikey': evolution_token,
            'Content-Type': 'application/json'
        }

        # Agrupar compromissos por usuário
        agrupados = {}
        for c in compromissos_para_enviar:
            if c.usuario not in agrupados:
                agrupados[c.usuario] = []
            agrupados[c.usuario].append(c)

        for usuario, lista_comp in agrupados.items():
            # Recuperar telefone do perfil
            try:
                perfil = getattr(usuario, 'profile', None)
                telefone = perfil.telefone if perfil else None
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'[CRON] Erro ao acessar perfil de {usuario.username}: {e}'))
                telefone = None

            if not telefone:
                self.stdout.write(self.style.WARNING(
                    f'[CRON] Usuário {usuario.username} ignorado: sem telefone no perfil.'
                ))
                continue

            # Normalizar número: manter só dígitos e adicionar DDI 55 se necessário
            numero_limpo = ''.join(filter(str.isdigit, telefone))
            if len(numero_limpo) in [10, 11] and not numero_limpo.startswith('55'):
                numero_limpo = '55' + numero_limpo

            self.stdout.write(f'[CRON] Preparando envio para {usuario.username} → {numero_limpo}')

            # Montar mensagem
            saudacao = f"Olá, *{usuario.first_name or usuario.username}*! ☀️"
            if len(lista_comp) == 1:
                intro = "Lembrete: Você tem um compromisso em breve:"
            else:
                intro = "Lembrete: Você tem compromissos em breve:"

            linhas = [saudacao, "", intro]
            for c in lista_comp:
                obs = f" - _{c.observacoes}_" if c.observacoes else ""
                linhas.append(f"⏰ *{c.hora.strftime('%H:%M')}* - {c.titulo}{obs}")

            mensagem = "\n".join(linhas)

            # Enviar via Evolution API
            endpoint = f"{evolution_url}/message/sendText/{instance_name}"
            payload = {"number": numero_limpo, "text": mensagem}

            try:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=15)
                if resp.status_code in [200, 201]:
                    self.stdout.write(self.style.SUCCESS(
                        f'[CRON] ✅ Mensagem enviada para {usuario.username} ({numero_limpo}).'
                    ))
                    for c in lista_comp:
                        c.lembrete_enviado = True
                        c.save()
                else:
                    self.stdout.write(self.style.ERROR(
                        f'[CRON] ❌ Falha ao enviar para {usuario.username} ({numero_limpo}). '
                        f'HTTP {resp.status_code}: {resp.text[:300]}'
                    ))
            except requests.Timeout:
                self.stdout.write(self.style.ERROR(
                    f'[CRON] ❌ Timeout ao conectar na Evolution API para {usuario.username}.'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'[CRON] ❌ Erro de conexão ao enviar para {usuario.username}: {str(e)}'
                ))

        self.stdout.write('[CRON] Execução concluída.')
