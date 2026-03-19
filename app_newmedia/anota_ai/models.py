from django.db import models
from django.contrib.auth.models import User

class Anotacao(models.Model):
    """
    Model para armazenar anotações do usuário (Texto, Lista, Checklist, PIX)
    """
    TIPO_CHOICES = [
        ('texto', 'Texto'),
        ('lista_numerada', 'Lista Numerada'),
        ('checklist', 'Checklist'),
        ('pix', 'PIX'),
    ]

    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='anotacoes', 
        verbose_name='Usuário'
    )
    titulo = models.CharField(max_length=100, verbose_name='Título')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    texto = models.TextField(blank=True, null=True, verbose_name='Texto')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    favorito = models.BooleanField(default=False, verbose_name='Favorito')
    
    # Campos específicos para PIX
    pix_nome = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nome do PIX')
    pix_chave = models.CharField(max_length=200, blank=True, null=True, verbose_name='Chave PIX')
    pix_favorecido = models.CharField(max_length=200, blank=True, null=True, verbose_name='Favorecido')
    pix_banco = models.CharField(max_length=100, blank=True, null=True, verbose_name='Banco')

    class Meta:
        verbose_name = 'Anotação'
        verbose_name_plural = 'Anotações'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"


class ItemAnotacao(models.Model):
    """
    Itens para anotações do tipo Lista Numerada e Checklist
    """
    anotacao = models.ForeignKey(
        Anotacao, 
        on_delete=models.CASCADE, 
        related_name='itens', 
        verbose_name='Anotação'
    )
    numero = models.IntegerField(verbose_name='Número')
    concluido = models.BooleanField(default=False, verbose_name='Concluído')
    texto = models.TextField(verbose_name='Texto')

    class Meta:
        verbose_name = 'Item de Anotação'
        verbose_name_plural = 'Itens de Anotação'
        ordering = ['numero']

    def __str__(self):
        return f"{self.numero} - {self.texto}"
