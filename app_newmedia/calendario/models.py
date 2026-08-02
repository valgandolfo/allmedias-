from django.db import models
from django.contrib.auth.models import User

class Compromisso(models.Model):
    OPCOES_ANTECEDENCIA = [
        (0, 'Na hora do compromisso'),
        (15, '15 minutos antes'),
        (30, '30 minutos antes'),
        (60, '1 hora antes'),
        (120, '2 horas antes'),
        (1440, '1 dia antes'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compromissos')
    data = models.DateField(db_column='CAL_DATA', verbose_name='Data')
    hora = models.TimeField(db_column='CAL_HORA', verbose_name='Hora')
    titulo = models.CharField(max_length=50, db_column='CAL_COMPROMISSO', verbose_name='Compromisso')
    cor = models.CharField(max_length=15, db_column='CAL_COR', verbose_name='Cor', default='#7C8EE0')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    antecedencia_minutos = models.IntegerField(
        choices=OPCOES_ANTECEDENCIA, 
        default=120, 
        verbose_name='Avisar com antecedência de'
    )
    lembrete_enviado = models.BooleanField(default=False, verbose_name='Lembrete Enviado')

    class Meta:
        db_table = 'TBCALENDARIO'
        verbose_name_plural = 'Compromissos'
        ordering = ['data', 'hora']

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} {self.hora.strftime('%H:%M')} - {self.titulo}"


class LogCron(models.Model):
    """Registro de cada execução do cron de WhatsApp para auditoria no Admin."""

    STATUS_CHOICES = [
        ('ok', '✅ Enviado'),
        ('sem_compromissos', '💭 Sem compromissos na janela'),
        ('erro', '❌ Erro'),
    ]

    executado_em = models.DateTimeField(auto_now_add=True, verbose_name='Executado em')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Status')
    mensagens_enviadas = models.IntegerField(default=0, verbose_name='Mensagens enviadas')
    detalhes = models.TextField(blank=True, verbose_name='Detalhes / Log')

    class Meta:
        db_table = 'TBLOGCRON'
        verbose_name = 'Log do Cron'
        verbose_name_plural = 'Logs do Cron (WhatsApp)'
        ordering = ['-executado_em']

    def __str__(self):
        return f"{self.executado_em.strftime('%d/%m/%Y %H:%M')} — {self.get_status_display()} ({self.mensagens_enviadas} msg)"
