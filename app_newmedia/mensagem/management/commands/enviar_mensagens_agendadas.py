import os
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from app_newmedia.mensagem.models import Mensagem
from app_newmedia.mensagem.views import _enviar_whatsapp

def get_target_day_of_month(data_original, hoje):
    """Retorna o dia alvo no mês/ano atual com base no dia original, respeitando os limites do mês."""
    _, last_day = calendar.monthrange(hoje.year, hoje.month)
    return min(data_original.day, last_day)

class Command(BaseCommand):
    help = 'Processa fila de mensagens agendadas e envia via Evolution API, respeitando o último disparo.'

    def handle(self, *args, **kwargs):
        agora = timezone.localtime()
        hoje = agora.date()
        self.stdout.write(f'[MENSAGEM-CRON] Iniciando execução às {agora.strftime("%Y-%m-%d %H:%M:%S %Z")}')

        JANELA_FUTURO_MIN = 16
        DESCARTA_APOS_MIN = 60

        # Busca todas as mensagens que não são "agora". As que são 'unico' enviadas são filtradas abaixo.
        mensagens_ativas = Mensagem.objects.exclude(men_ocorrencia='agora')
        total = mensagens_ativas.count()
        self.stdout.write(f'[MENSAGEM-CRON] Avaliando {total} mensagem(ns) agendada(s).')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('[MENSAGEM-CRON] Nenhuma mensagem agendada. Encerrando.'))
            return

        mensagens_para_enviar = []

        for m in mensagens_ativas:
            # 1. Se for 'unico' e já estiver enviada, ignora.
            if m.men_ocorrencia == 'unico' and m.men_status:
                continue

            data_original = m.men_dat
            hora_original = m.men_hora

            # 2. Verifica se HOJE é um dia válido de disparo para essa mensagem
            dia_de_disparo = False
            
            if m.men_ocorrencia == 'unico':
                if hoje == data_original:
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'todo_dia':
                if hoje >= data_original:
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'semanal':
                if hoje >= data_original and hoje.weekday() == data_original.weekday():
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'mensal':
                if hoje >= data_original and hoje.day == get_target_day_of_month(data_original, hoje):
                    dia_de_disparo = True

            if not dia_de_disparo:
                continue

            # 3. Monta a data/hora alvo de envio para HOJE
            alvo_hoje = timezone.make_aware(datetime.combine(hoje, hora_original))
            
            # 4. Verifica se a mensagem já foi disparada HOJE usando 'ultimo_disparo'
            ja_disparou_hoje = False
            if m.ultimo_disparo:
                ultimo_local = timezone.localtime(m.ultimo_disparo)
                if ultimo_local.date() == hoje:
                    ja_disparou_hoje = True

            if ja_disparou_hoje:
                continue
                
            self.stdout.write(
                f'  → [{m.men_nome}] Avaliando alvo {alvo_hoje.strftime("%d/%m %H:%M")} (Original: {m.men_dat.strftime("%d/%m")})'
            )

            # 5. Verifica as janelas de envio / descarte
            diff_minutos = (agora - alvo_hoje).total_seconds() / 60
            
            # Se o horário alvo passou há mais de 60 minutos, consideramos expirada (DESCARTADA).
            # Para não tentar enviar novamente hoje, marcamos 'ultimo_disparo = agora'.
            if diff_minutos > DESCARTA_APOS_MIN:
                self.stdout.write(f'     → DESCARTADA para hoje (Expirou há mais de {int(diff_minutos)}min)')
                m.ultimo_disparo = agora
                if m.men_ocorrencia == 'unico':
                    m.men_status = True
                m.save(update_fields=['ultimo_disparo', 'men_status'])
                continue

            # O horário já chegou ou estamos nos 16 minutos de antecedência?
            if alvo_hoje <= agora + timedelta(minutes=JANELA_FUTURO_MIN):
                self.stdout.write(f'     → DENTRO DA JANELA — Adicionada para envio')
                mensagens_para_enviar.append((m, alvo_hoje))
            else:
                self.stdout.write(f'     → Fora da janela (envio em {int(-diff_minutos)}min)')

        if not mensagens_para_enviar:
            self.stdout.write(self.style.SUCCESS('[MENSAGEM-CRON] Nenhuma mensagem está dentro da janela de envio atual.'))
            return

        self.stdout.write(f'[MENSAGEM-CRON] Processando envio de {len(mensagens_para_enviar)} mensagem(ns)...')

        for m, alvo_hoje in mensagens_para_enviar:
            self.stdout.write(f'[MENSAGEM-CRON] Disparando para {m.men_nome} ({m.men_telefone})')
            resultado = _enviar_whatsapp(m.men_telefone, m.men_mensagem)
            
            if resultado['sucesso']:
                self.stdout.write(self.style.SUCCESS(f'[MENSAGEM-CRON] ✅ Sucesso! ({m.men_nome})'))
                m.ultimo_disparo = agora
                if m.men_ocorrencia == 'unico':
                    m.men_status = True
                m.save(update_fields=['ultimo_disparo', 'men_status'])
            else:
                self.stdout.write(self.style.ERROR(f'[MENSAGEM-CRON] ❌ Falha ({m.men_nome}): {resultado["erro"]}'))

        self.stdout.write('[MENSAGEM-CRON] Execução concluída.')
