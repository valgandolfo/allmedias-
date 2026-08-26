from django.db import models
from django.contrib.auth.models import User


class Mensagem(models.Model):
    """Mensagens WhatsApp agendadas ou imediatas via Evolution API."""

    OCORRENCIA_CHOICES = [
        ('agora',   'Agora'),
        ('unico',   'Enviar no dia/hora acima'),
        ('todo_dia', 'Todo dia'),
        ('semanal',  'Uma vez na semana'),
        ('mensal',   'Uma vez no mês'),
    ]

    usuario       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens', verbose_name='Usuário')
    men_telefone  = models.CharField(max_length=20,  db_column='MEN_TELEFONE', verbose_name='Telefone do Contato')
    men_nome      = models.CharField(max_length=100, db_column='MEN_NOME',     verbose_name='Nome do Contato')
    men_dat       = models.DateField(               db_column='MEN_DAT',      verbose_name='Data Agendada')
    men_hora      = models.TimeField(               db_column='MEN_HORA',     verbose_name='Hora Agendada')
    men_ocorrencia= models.CharField(max_length=20, db_column='MEN_OCORRENCIA', choices=OCORRENCIA_CHOICES, verbose_name='Ocorrência')
    men_mensagem  = models.CharField(max_length=150, db_column='MEN_MENSAGEM', verbose_name='Mensagem')
    men_status    = models.BooleanField(default=False, db_column='MEN_STATUS', verbose_name='Enviado')
    ultimo_disparo= models.DateTimeField(null=True, blank=True, db_column='MEN_ULTIMO_DISPARO', verbose_name='Último Disparo')
    criado_em     = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'TBMENSAGEM'
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.men_nome} | {self.men_dat} {self.men_hora} | {'✅' if self.men_status else '⏳'}"
