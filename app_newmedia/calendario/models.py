from django.db import models
from django.contrib.auth.models import User

class Compromisso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compromissos')
    data = models.DateField(db_column='CAL_DATA', verbose_name='Data')
    hora = models.TimeField(db_column='CAL_HORA', verbose_name='Hora')
    titulo = models.CharField(max_length=50, db_column='CAL_COMPROMISSO', verbose_name='Compromisso')
    cor = models.CharField(max_length=15, db_column='CAL_COR', verbose_name='Cor', default='#7C8EE0')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        db_table = 'TBCALENDARIO'
        verbose_name_plural = 'Compromissos'
        ordering = ['data', 'hora']

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} {self.hora.strftime('%H:%M')} - {self.titulo}"
