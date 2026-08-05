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
        self.stdout.write(f'[MENSAGEM-CRON] Iniciando execução às {agora.strftime("%Y-%m-%d %H:%M:%S %Z")}')

        # Janela de envio idêntica ao cron de calendário
        JANELA_FUTURO_MIN = 16
        JANELA_PASSADO_MIN = 16
        DESCARTA_APOS_MIN = 60

        # Busca apenas mensagens que não foram enviadas e cuja ocorrência é 'unico'
        # (Futuramente podemos adicionar regras aqui para 'todo_dia', etc)
        mensagens_pendentes = Mensagem.objects.filter(
            men_status=False,
            men_ocorrencia='unico'
        ).order_by('men_dat', 'men_hora')

        total = mensagens_pendentes.count()
        self.stdout.write(f'[MENSAGEM-CRON] Encontradas {total} mensagem(ns) pendente(s).')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('[MENSAGEM-CRON] Nenhuma mensagem agendada para enviar. Encerrando.'))
            return

        mensagens_para_enviar = []

        for m in mensagens_pendentes:
            data_hora_envio = timezone.make_aware(datetime.combine(m.men_dat, m.men_hora))
            
            self.stdout.write(
                f'  → [{m.men_nome}] Agendado para {data_hora_envio.strftime("%d/%m %H:%M")}'
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
