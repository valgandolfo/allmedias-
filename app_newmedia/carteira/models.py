"""
Model de notificações de compras capturadas via MacroDroid
"""
import re
from django.db import models
from django.contrib.auth.models import User


class NotificacaoCompra(models.Model):
    """
    Armazena compras capturadas de notificações (Google Wallet, bancos, etc.)
    O MacroDroid envia o texto completo da notificação, o backend faz o parse.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificacoes_compra',
        verbose_name='Usuário'
    )

    # Dados brutos da notificação
    texto_completo = models.TextField(
        verbose_name='Texto completo da notificação'
    )

    app_origem = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='App de origem (Google Wallet, Nubank, etc.)'
    )

    # Campos extraídos via parse
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor da compra'
    )

    estabelecimento = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Estabelecimento/Local'
    )

    data_compra = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data da compra'
    )

    hora_compra = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora da compra'
    )

    # Metadados
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de criação'
    )

    class Meta:
        db_table = 'notificacao_compra'
        verbose_name = 'Notificação de Compra'
        verbose_name_plural = 'Notificações de Compras'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.estabelecimento or 'Compra'} - R$ {self.valor or '???'}"

    @staticmethod
    def parse_notificacao(texto_completo):
        """
        Extrai valor, estabelecimento, data e hora do texto da notificação.
        Usado pela view API antes de salvar.
        """
        resultado = {
            'valor': None,
            'estabelecimento': '',
            'data': None,
            'hora': None,
        }

        # Extrair valor monetário (R$ 45,90 ou 45.90)
        match_valor = re.search(
            r'[R$€$]?\s*([\d]{1,3}(?:[.\d]{3})*[,.]\d{2})',
            texto_completo
        )
        if match_valor:
            valor_str = match_valor.group(1).replace('.', '').replace(',', '.')
            try:
                resultado['valor'] = float(valor_str)
            except ValueError:
                pass

        # Padrões comuns de notificação de compra
        # "Compra de R$ 45,90 em Mercado Livre"
        match_estab = re.search(
            r'(?:em|na|no|estabelecimento)\s+([A-ZÀ][\w\s&.\-]{2,50})',
            texto_completo
        )
        if match_estab:
            resultado['estabelecimento'] = match_estab.group(1).strip()

        # Se não encontrou por "em", tenta extrair o nome mais relevante
        if not resultado['estabelecimento']:
            match_estab2 = re.search(
                r'(?:(?:compra|pagamento|débito).*?)[A-ZÀ][A-ZÀ\w\s&.\-]{5,40}',
                texto_completo
            )
            if match_estab2:
                resultado['estabelecimento'] = match_estab2.group(0).strip()

        return resultado
