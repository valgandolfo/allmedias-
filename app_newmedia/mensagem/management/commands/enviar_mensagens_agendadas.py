import os
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
import datetime as dt_module
from django.core.management.base import BaseCommand
from app_newmedia.mensagem.models import Mensagem
from app_newmedia.mensagem.views import _enviar_whatsapp

def get_target_day_of_month(data_original, hoje):
    """Retorna o dia alvo no mês/ano atual com base no dia original, respeitando os limites do mês."""
    _, last_day = calendar.monthrange(hoje.year, hoje.month)
    return min(data_original.day, last_day)

def is_feriado_nacional_ou_santo(data):
    """Verifica se é feriado nacional fixo ou dia santo universal (Sexta Santa, Corpus Christi)."""
    ano = data.year
    mes = data.month
    dia = data.day

    feriados_fixos = [
        (1, 1),   # Ano novo
        (4, 21),  # Tiradentes
        (5, 1),   # Dia do Trabalho
        (9, 7),   # Independência
        (10, 12), # Nossa Senhora Aparecida
        (11, 2),  # Finados
        (11, 15), # Proclamação da República
        (12, 25), # Natal
    ]
    if (mes, dia) in feriados_fixos:
        return True

    # Calcula Páscoa (Algoritmo de Meeus/Jones/Butcher)
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    mes_pascoa = (h + L - 7 * m + 114) // 31
    dia_pascoa = ((h + L - 7 * m + 114) % 31) + 1
    pascoa = dt_module.date(ano, mes_pascoa, dia_pascoa)

    sexta_santa = pascoa - timedelta(days=2)
    corpus_christi = pascoa + timedelta(days=60)

    if data == sexta_santa or data == corpus_christi:
        return True

    return False

class Command(BaseCommand):
    help = 'Processa fila de mensagens agendadas e envia via Evolution API, respeitando o último disparo.'

    def handle(self, *args, **kwargs):
        agora_servidor = timezone.localtime()
        self.stdout.write(f'[MENSAGEM-CRON] Iniciando execução às {agora_servidor.strftime("%Y-%m-%d %H:%M:%S %Z")}')

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
            # Puxa o fuso horário do perfil (se existir), senão usa SP
            fuso_str = 'America/Sao_Paulo'
            if hasattr(m.usuario, 'profile') and getattr(m.usuario.profile, 'fuso_horario', None):
                fuso_str = m.usuario.profile.fuso_horario
            
            try:
                import zoneinfo
                fuso = zoneinfo.ZoneInfo(fuso_str)
            except Exception:
                fuso = None # Fallback pro default do django
                
            agora_usuario = timezone.localtime(timezone.now(), timezone=fuso) if fuso else timezone.localtime()
            hoje_usuario = agora_usuario.date()

            # 1. Se for 'unico' e já estiver enviada, ignora.
            if m.men_ocorrencia == 'unico' and m.men_status:
                continue

            data_original = m.men_dat
            hora_original = m.men_hora

            # 2. Verifica se HOJE é um dia válido de disparo para essa mensagem no fuso local do usuário
            dia_de_disparo = False
            
            if m.men_ocorrencia == 'unico':
                if hoje_usuario == data_original:
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'todo_dia':
                if hoje_usuario >= data_original:
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'semanal':
                if hoje_usuario >= data_original and hoje_usuario.weekday() == data_original.weekday():
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'mensal':
                if hoje_usuario >= data_original and hoje_usuario.day == get_target_day_of_month(data_original, hoje_usuario):
                    dia_de_disparo = True
            elif m.men_ocorrencia == 'dias_uteis':
                if hoje_usuario >= data_original:
                    if hoje_usuario.weekday() < 5 and not is_feriado_nacional_ou_santo(hoje_usuario):
                        dia_de_disparo = True

            if not dia_de_disparo:
                continue

            # 3. Monta a data/hora alvo de envio para o HOJE do usuário e converte para timezone aware com o fuso dele
            if fuso:
                alvo_hoje = timezone.make_aware(datetime.combine(hoje_usuario, hora_original), timezone=fuso)
            else:
                alvo_hoje = timezone.make_aware(datetime.combine(hoje_usuario, hora_original))
            
            # 4. Verifica se a mensagem já foi disparada HOJE usando 'ultimo_disparo'
            ja_disparou_hoje = False
            if m.ultimo_disparo:
                # Converte o último disparo para a timezone do usuário
                if fuso:
                    ultimo_local = timezone.localtime(m.ultimo_disparo, timezone=fuso)
                else:
                    ultimo_local = timezone.localtime(m.ultimo_disparo)
                    
                if ultimo_local.date() == hoje_usuario:
                    ja_disparou_hoje = True

            if ja_disparou_hoje:
                continue
                
            self.stdout.write(
                f'  → [{m.men_nome}] Avaliando alvo {alvo_hoje.strftime("%d/%m %H:%M %Z")} (Original: {m.men_dat.strftime("%d/%m")})'
            )

            # 5. Verifica as janelas de envio / descarte usando o "agora" (o agora_usuario e alvo_hoje estão com fuso, então podemos subtrair com segurança no tempo absoluto)
            diff_minutos = (timezone.now() - alvo_hoje).total_seconds() / 60
            
            # Se o horário alvo passou há mais de 60 minutos, consideramos expirada (DESCARTADA).
            if diff_minutos > DESCARTA_APOS_MIN:
                self.stdout.write(f'     → DESCARTADA para hoje (Expirou há mais de {int(diff_minutos)}min)')
                m.ultimo_disparo = timezone.now()
                if m.men_ocorrencia == 'unico':
                    m.men_status = True
                m.save(update_fields=['ultimo_disparo', 'men_status'])
                continue

            # O horário já chegou ou estamos nos 16 minutos de antecedência?
            if alvo_hoje <= timezone.now() + timedelta(minutes=JANELA_FUTURO_MIN):
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
                m.ultimo_disparo = timezone.now()
                if m.men_ocorrencia == 'unico':
                    m.men_status = True
                m.save(update_fields=['ultimo_disparo', 'men_status'])
            else:
                self.stdout.write(self.style.ERROR(f'[MENSAGEM-CRON] ❌ Falha ({m.men_nome}): {resultado["erro"]}'))

        self.stdout.write('[MENSAGEM-CRON] Execução concluída.')
