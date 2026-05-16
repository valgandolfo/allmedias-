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

    tipo_transacao = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de Transação (PIX/COMPRA)'
    )

    cartao_final = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Final do Cartão'
    )

    origem = models.CharField(
        max_length=20,
        choices=[('NOTIFICACAO', 'Notificação'), ('EMAIL', 'E-mail')],
        default='NOTIFICACAO',
        verbose_name='Origem dos dados'
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
            'estabelecimento': 'NÃO IDENTIFICADO',
            'instituicao': '',
            'data': None,
            'hora': None,
            'tipo_transacao': 'PIX' if re.search(r'pix', texto_completo, re.IGNORECASE) else 'COMPRA',
            'cartao_final': '',
        }

        if not texto_completo:
            return resultado

        # 1. Extrair valor monetário
        # Prioridade 1: Símbolo de moeda explícito (ex: R$ 10,00)
        match_valor = re.search(
            r'(?:R\$|RS|\$|€|BRL)\s*(\d{1,3}(?:[.\d]{3})*[,.]\d{2}|\d+[,.]\d{2}|\d+)',
            texto_completo,
            re.IGNORECASE
        )
        # Prioridade 2: Palavras chave seguidas de valor decimal (ex: valor 10,00)
        if not match_valor:
            match_valor = re.search(
                r'(?:valor|de)\s+(\d{1,3}(?:[.\d]{3})*[,.]\d{2}|\d+[,.]\d{2})',
                texto_completo,
                re.IGNORECASE
            )
        # Prioridade 3: Qualquer número com 2 casas decimais que não pareça hora/data (ex: 10,00)
        if not match_valor:
            match_valor = re.search(
                r'(?<!\d:)(\d{1,3}(?:[.\d]{3})*[,.]\d{2}|\d+[,.]\d{2})',
                texto_completo,
                re.IGNORECASE
            )
        if match_valor:
            v_str = match_valor.group(1)
            # Lógica para tratar separadores:
            # Se tem vírgula e ponto (1.234,56), remove ponto e troca vírgula por ponto
            if ',' in v_str and '.' in v_str:
                v_str = v_str.replace('.', '').replace(',', '.')
            # Se tem apenas vírgula (1234,56), troca por ponto
            elif ',' in v_str:
                v_str = v_str.replace(',', '.')
            # Se tem apenas ponto e parece ser decimal (ex: 123.45 e não 1.234)
            # Geralmente se tem 3 dígitos após o ponto, é milhar. Se tem 2, é decimal.
            elif '.' in v_str:
                partes = v_str.split('.')
                if len(partes[-1]) != 2: # Provavelmente milhar: 1.234
                    v_str = v_str.replace('.', '')
            
            try:
                resultado['valor'] = float(v_str)
            except ValueError:
                pass

        # 2. Extrair Final do Cartão
        match_cartao = re.search(r'(?:cartão|final)\s+(?:final\s+)?(\d{4})', texto_completo, re.IGNORECASE)
        if match_cartao:
            resultado['cartao_final'] = match_cartao.group(1)

        # 3. Estabelecimento/Instituição Simplificado
        # Como o usuário pediu para simplificar, usaremos o app_origem no view
        # e aqui não precisamos tentar adivinhar nomes malucos.
        resultado['estabelecimento'] = ''

        # 6. Extrair Data e Hora (se houver no texto, ex: 21/04 às 14:30)
        match_data = re.search(r'(\d{2}/\d{2}(?:/\d{4})?)', texto_completo)
        if match_data:
            from datetime import datetime
            try:
                data_str = match_data.group(1)
                if len(data_str) == 5: # dd/mm
                    data_str += f"/{datetime.now().year}"
                resultado['data'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except: pass

        match_hora = re.search(r'(\d{2}:\d{2}(?::\d{2})?)', texto_completo)
        if match_hora:
            from datetime import datetime
            try:
                resultado['hora'] = datetime.strptime(match_hora.group(1), '%H:%M').time()
            except: pass
        return resultado

    @staticmethod
    def parse_email(subject, body_text):
        """
        Parser especializado para corpos de e-mail (geralmente mais longos que notificações).
        Tenta extrair os dados usando a lógica de texto, mas com limpeza adicional.
        """
        # Combina assunto e corpo para busca
        texto_para_busca = f"{subject}\n{body_text}"
        
        # Limpeza básica de excesso de espaços e quebras de linha
        texto_para_busca = re.sub(r'\s+', ' ', texto_para_busca)
        
        # Chama o parser base (que já melhoramos para ser robusto)
        resultado = NotificacaoCompra.parse_notificacao(texto_para_busca)
        
        # Ajustes específicos para e-mail se necessário
        # Ex: Se o assunto contiver o nome do banco
        if not resultado['instituicao']:
            match_banco = re.search(r'(Nubank|Itaú|Bradesco|Santander|Inter|C6|Caixa|BB|Mercado Pago)', subject, re.IGNORECASE)
            if match_banco:
                resultado['instituicao'] = match_banco.group(1).upper()
                
        return resultado
