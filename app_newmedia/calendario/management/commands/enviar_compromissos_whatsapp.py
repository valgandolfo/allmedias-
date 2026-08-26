import os
from decouple import config
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from app_newmedia.calendario.models import Compromisso, LogCron


class Command(BaseCommand):
    help = 'Envia lembrete de compromissos para o WhatsApp na antecedência configurada usando Evolution API'

    def handle(self, *args, **kwargs):
        agora = timezone.localtime()
        log_linhas = []  # acumula linhas para gravar no LogCron

        def log(msg):
            self.stdout.write(msg)
            log_linhas.append(msg)

        log(f'[CRON] Executando às {agora.strftime("%Y-%m-%d %H:%M:%S %Z")}')

        # Buscar compromissos até 2 dias à frente (antecedência máxima = 1440 min = 1 dia)
        limite_busca_dias = agora.date() + timedelta(days=2)

        compromissos_pendentes = Compromisso.objects.filter(
            data__lte=limite_busca_dias,
            lembrete_enviado=False
        ).order_by('data', 'hora')

        total_pendentes = compromissos_pendentes.count()
        log(f'[CRON] {total_pendentes} compromisso(s) pendente(s) encontrado(s).')

        # ---------------------------------------------------------------
        # JANELA DE ENVIO (ajustada para cron de 15 minutos):
        # Aumentamos para 16 minutos tanto no futuro quanto no passado.
        # - FUTURO: Garante que o lembrete seja enviado no ciclo ANTERIOR 
        #   à hora exata, para não chegar atrasado.
        # - PASSADO: Se o cron atrasar, ou se o usuário agendar em cima
        #   da hora, o lembrete ainda será capturado na próxima rodada.
        # Como marcamos 'lembrete_enviado=True', não há risco de duplicidade.
        # ---------------------------------------------------------------
        JANELA_FUTURO_MIN = 16       # minuto(s) à frente
        JANELA_PASSADO_MIN = 16      # minuto(s) atrás (tolerância alta para atrasos)
        DESCARTA_APOS_MIN = 60       # marca como enviado se passou mais de 1h sem envio

        compromissos_para_enviar = []

        for c in compromissos_pendentes:
            data_hora_comp = timezone.make_aware(datetime.combine(c.data, c.hora))
            hora_do_lembrete = data_hora_comp - timedelta(minutes=c.antecedencia_minutos)

            log(
                f'  → [{c.titulo}] em {data_hora_comp.strftime("%d/%m %H:%M")} | '
                f'lembrete às {hora_do_lembrete.strftime("%d/%m %H:%M")} | '
                f'antecedência: {c.antecedencia_minutos}min'
            )

            # Compromisso já passou há mais de DESCARTA_APOS_MIN — descartar
            if data_hora_comp < (agora - timedelta(minutes=DESCARTA_APOS_MIN)):
                log(f'     → DESCARTADO (compromisso já expirou há mais de {DESCARTA_APOS_MIN}min)')
                c.lembrete_enviado = True
                c.save()
                continue

            # Verifica se já chegou a hora do lembrete (ou se já passou e ainda não foi enviado)
            if hora_do_lembrete <= (agora + timedelta(minutes=JANELA_FUTURO_MIN)):
                log(f'     → DENTRO DA JANELA — adicionado para envio')
                compromissos_para_enviar.append(c)
            else:
                diff = hora_do_lembrete - agora
                log(f'     → Fora da janela (lembrete em {int(diff.total_seconds() / 60)}min)')

        if not compromissos_para_enviar:
            msg = '[CRON] Sem compromissos na janela atual para notificar.'
            log(self.style.SUCCESS(msg))
            LogCron.objects.create(
                status='sem_compromissos',
                mensagens_enviadas=0,
                detalhes='\n'.join(log_linhas),
            )
            return

        log(f'[CRON] {len(compromissos_para_enviar)} compromisso(s) para enviar agora.')

        # Verificar variáveis de ambiente da Evolution API
        evolution_url = config('EVOLUTION_API_URL', default='').rstrip('/')
        evolution_token = config('EVOLUTION_API_TOKEN', default='')
        instance_name = config('EVOLUTION_INSTANCE_NAME', default='')

        if not evolution_url:
            log(self.style.ERROR('[CRON] ERRO: EVOLUTION_API_URL não configurada.'))
            LogCron.objects.create(status='erro', detalhes='EVOLUTION_API_URL não configurada.')
            return
        if not evolution_token:
            log(self.style.ERROR('[CRON] ERRO: EVOLUTION_API_TOKEN não configurado.'))
            LogCron.objects.create(status='erro', detalhes='EVOLUTION_API_TOKEN não configurado.')
            return
        if not instance_name:
            log(self.style.ERROR('[CRON] ERRO: EVOLUTION_INSTANCE_NAME não configurado.'))
            LogCron.objects.create(status='erro', detalhes='EVOLUTION_INSTANCE_NAME não configurado.')
            return

        log(f'[CRON] Evolution API: {evolution_url} | Instância: {instance_name}')

        mensagens_ok = 0  # contador de mensagens enviadas com sucesso

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
                log(self.style.WARNING(f'[CRON] Erro ao acessar perfil de {usuario.username}: {e}'))
                telefone = None

            if not telefone:
                log(self.style.WARNING(
                    f'[CRON] Usuário {usuario.username} ignorado: sem telefone no perfil.'
                ))
                continue

            # Normalizar número: manter só dígitos e adicionar DDI 55 se necessário
            numero_limpo = ''.join(filter(str.isdigit, telefone))
            if len(numero_limpo) in [10, 11] and not numero_limpo.startswith('55'):
                numero_limpo = '55' + numero_limpo

            log(f'[CRON] Preparando envio para {usuario.username} → {numero_limpo}')

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
                    log(self.style.SUCCESS(
                        f'[CRON] ✅ Mensagem enviada para {usuario.username} ({numero_limpo}).'
                    ))
                    mensagens_ok += 1
                    for c in lista_comp:
                        c.lembrete_enviado = True
                        c.save()
                else:
                    log(self.style.ERROR(
                        f'[CRON] ❌ Falha ao enviar para {usuario.username} ({numero_limpo}). '
                        f'HTTP {resp.status_code}: {resp.text[:300]}'
                    ))
            except requests.Timeout:
                log(self.style.ERROR(
                    f'[CRON] ❌ Timeout ao conectar na Evolution API para {usuario.username}.'
                ))
            except Exception as e:
                log(self.style.ERROR(
                    f'[CRON] ❌ Erro de conexão ao enviar para {usuario.username}: {str(e)}'
                ))

        log('[CRON] Execução concluída.')

        # Salva log no banco
        status_final = 'ok' if mensagens_ok > 0 else 'erro'
        LogCron.objects.create(
            status=status_final,
            mensagens_enviadas=mensagens_ok,
            detalhes='\n'.join(log_linhas),
        )
