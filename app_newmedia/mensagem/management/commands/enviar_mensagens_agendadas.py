import os
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from app_newmedia.mensagem.models import Mensagem
from app_newmedia.mensagem.views import _enviar_whatsapp


class Command(BaseCommand):
    help = 'Processa fila de mensagens agendadas e envia via Evolution API'

    def handle(self, *args, **kwargs):
        agora = timezone.localtime()
        hoje = agora.date()
        self.stdout.write(f'[MENSAGEM-CRON] Iniciando execução às {agora.strftime("%Y-%m-%d %H:%M:%S %Z")}')

        # 1. Resetar mensagens recorrentes que já foram enviadas
        # Se virou o dia (men_dat < hoje), avançamos a data e voltamos o status para Pendente
        import calendar
        recorrentes_enviadas = Mensagem.objects.filter(
            men_status=True,
            men_ocorrencia__in=['todo_dia', 'semanal', 'mensal'],
            men_dat__lt=hoje
        )
        
        if recorrentes_enviadas.exists():
            self.stdout.write(f'[MENSAGEM-CRON] Resetando {recorrentes_enviadas.count()} mensagem(ns) recorrente(s)...')
            for m in recorrentes_enviadas:
                nova_data = m.men_dat
                while nova_data < hoje:
                    if m.men_ocorrencia == 'todo_dia':
                        nova_data += timedelta(days=1)
                    elif m.men_ocorrencia == 'semanal':
                        nova_data += timedelta(days=7)
                    elif m.men_ocorrencia == 'mensal':
                        mes = nova_data.month + 1
                        ano = nova_data.year
                        if mes > 12:
                            mes = 1
                            ano += 1
                        dia = min(nova_data.day, calendar.monthrange(ano, mes)[1])
                        nova_data = nova_data.replace(year=ano, month=mes, day=dia)
                
                m.men_dat = nova_data
                m.men_status = False
                m.save(update_fields=['men_dat', 'men_status'])
                self.stdout.write(f'  → [{m.men_nome}] Reprogramada para {m.men_dat.strftime("%d/%m/%Y")}')

        # Janela de envio idêntica ao cron de calendário
        JANELA_FUTURO_MIN = 16
        JANELA_PASSADO_MIN = 16
        DESCARTA_APOS_MIN = 60

        # 2. Busca mensagens pendentes (incluindo as recorrentes que acabaram de ser resetadas)
        mensagens_pendentes = Mensagem.objects.filter(
            men_status=False,
            men_ocorrencia__in=['unico', 'todo_dia', 'semanal', 'mensal']
        ).order_by('men_dat', 'men_hora')

        total = mensagens_pendentes.count()
        self.stdout.write(f'[MENSAGEM-CRON] Encontradas {total} mensagem(ns) pendente(s).')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('[MENSAGEM-CRON] Nenhuma mensagem agendada para enviar. Encerrando.'))
            return

        mensagens_para_enviar = []

        for m in mensagens_pendentes:
            data_avaliacao = m.men_dat

            # Se a mensagem está atrasada (data no passado) mas é recorrente,
            # o usuário quer que a data seja ignorada e avaliada como hoje.
            if data_avaliacao < hoje and m.men_ocorrencia in ['todo_dia', 'semanal', 'mensal']:
                if m.men_ocorrencia == 'todo_dia':
                    data_avaliacao = hoje
                elif m.men_ocorrencia == 'semanal' and data_avaliacao.weekday() == hoje.weekday():
                    data_avaliacao = hoje
                elif m.men_ocorrencia == 'mensal' and data_avaliacao.day == hoje.day:
                    data_avaliacao = hoje

            data_hora_envio = timezone.make_aware(datetime.combine(data_avaliacao, m.men_hora))
            
            self.stdout.write(
                f'  → [{m.men_nome}] Avaliando agendamento para {data_hora_envio.strftime("%d/%m %H:%M")} (Original: {m.men_dat.strftime("%d/%m")})'
            )

            if data_hora_envio < (agora - timedelta(minutes=DESCARTA_APOS_MIN)):
                self.stdout.write(f'     → DESCARTADA (Data expirou há mais de {DESCARTA_APOS_MIN}min)')
                m.men_status = True
                m.save(update_fields=['men_status'])
                continue

            dentro_da_janela = (
                data_hora_envio <= (agora + timedelta(minutes=JANELA_FUTURO_MIN)) and
                data_hora_envio >= (agora - timedelta(minutes=JANELA_PASSADO_MIN))
            )

            if dentro_da_janela:
                self.stdout.write(f'     → DENTRO DA JANELA — Adicionada para envio')
                mensagens_para_enviar.append(m)
            else:
                diff = data_hora_envio - agora
                self.stdout.write(f'     → Fora da janela (envio em {int(diff.total_seconds() / 60)}min)')

        if not mensagens_para_enviar:
            self.stdout.write(self.style.SUCCESS('[MENSAGEM-CRON] Nenhuma mensagem está dentro da janela de envio atual.'))
            return

        self.stdout.write(f'[MENSAGEM-CRON] Processando envio de {len(mensagens_para_enviar)} mensagem(ns)...')

        for m in mensagens_para_enviar:
            self.stdout.write(f'[MENSAGEM-CRON] Disparando para {m.men_nome} ({m.men_telefone})')
            resultado = _enviar_whatsapp(m.men_telefone, m.men_mensagem)
            
            if resultado['sucesso']:
                self.stdout.write(self.style.SUCCESS(f'[MENSAGEM-CRON] ✅ Sucesso! ({m.men_nome})'))
                m.men_status = True
                m.save(update_fields=['men_status'])
            else:
                self.stdout.write(self.style.ERROR(f'[MENSAGEM-CRON] ❌ Falha ({m.men_nome}): {resultado["erro"]}'))

        self.stdout.write('[MENSAGEM-CRON] Execução concluída.')
