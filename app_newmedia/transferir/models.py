from django.db import models
from django.contrib.auth.models import User

class Transferencia(models.Model):
    """
    Model para armazenar transferências de mídias e anotações entre usuários
    """
    TIPO_ITEM_CHOICES = [
        ('media', 'Mídia'),
        ('anotacao', 'Anotação'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    ]

    remetente = models.ForeignKey(
        User, 
        related_name='transferencias_enviadas', 
        on_delete=models.CASCADE,
        verbose_name='Remetente'
    )
    destinatario = models.ForeignKey(
        User, 
        related_name='transferencias_recebidas', 
        on_delete=models.CASCADE,
        verbose_name='Destinatário'
    )
    tipo_item = models.CharField(
        max_length=20, 
        choices=TIPO_ITEM_CHOICES,
        verbose_name='Tipo de Item'
    )
    item_id = models.IntegerField(
        verbose_name='ID do Item'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    subtitulo = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Subtítulo'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    data_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Envio'
    )
    data_resposta = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Data de Resposta'
    )
    observacao = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Observação'
    )

    class Meta:
        verbose_name = 'Transferência'
        verbose_name_plural = 'Transferências'
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_item_display()}) de {self.remetente} para {self.destinatario}"
