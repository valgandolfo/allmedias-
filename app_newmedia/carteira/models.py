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
            'estabelecimento': 'Não identificado',
            'instituicao': '',
            'data': None,
            'hora': None,
            'tipo_transacao': 'COMPRA',
            'cartao_final': '',
        }

        # 1. Extrair valor monetário
        match_valor = re.search(
            r'(?:R\$|\$|€)?\s*([\d]{1,3}(?:[.\d]{3})*[,.]\d{2})',
            texto_completo,
            re.IGNORECASE
        )
        if match_valor:
            valor_str = match_valor.group(1).replace('.', '').replace(',', '.')
            try:
                resultado['valor'] = float(valor_str)
            except ValueError:
                pass

        # 2. Identificar Tipo de Transação (PIX ou COMPRA)
        if re.search(r'pix', texto_completo, re.IGNORECASE):
            resultado['tipo_transacao'] = 'PIX'
        elif re.search(r'compra', texto_completo, re.IGNORECASE):
            resultado['tipo_transacao'] = 'COMPRA'

        # 3. Extrair Final do Cartão
        match_cartao = re.search(r'(?:cartão|final)\s+(?:final\s+)?(\d{4})', texto_completo, re.IGNORECASE)
        if match_cartao:
            resultado['cartao_final'] = match_cartao.group(1)

        # 4. Extrair Estabelecimento ou Remetente
        # Tentamos primeiro o padrão "em [Estabelecimento]" que costuma vir no final
        # Excluímos padrões que pareçam data ou cartão
        matches_estab = re.findall(
            r'(?:em|na|no|de|para|estabelecimento)\s+([A-ZÀ][\w\s&.\-]{2,50})',
            texto_completo,
            re.IGNORECASE
        )
        
        if matches_estab:
            # Filtramos candidatos que são claramente cartões ou datas
            candidatos = []
            for m in matches_estab:
                m_clean = m.strip()
                # Remove "em/às [Data/Hora]" do final se estiver grudado no nome
                # Ex: "João Silva em 23/04/26" -> "João Silva"
                m_clean = re.split(r'\s+(?:em|na|no|de|para|às)\s+\d', m_clean, flags=re.IGNORECASE)[0]
                
                if re.search(r'cartão|final|^\d{2}/\d{2}', m_clean, re.IGNORECASE):
                    continue
                candidatos.append(m_clean)
            
            if candidatos:
                # Pegamos o último candidato válido, que geralmente é o estabelecimento real
                resultado['estabelecimento'] = candidatos[-1]
            else:
                resultado['estabelecimento'] = matches_estab[-1].strip()

        # 5. Extrair Instituição Bancária (se estiver no texto)
        match_banco = re.search(
            r'(?:no|pelo|via)\s+(Nubank|Itaú|Bradesco|Santander|Inter|C6|Caixa|BB|Banco do Brasil)',
            texto_completo,
            re.IGNORECASE
        )
        if match_banco:
            resultado['instituicao'] = match_banco.group(1).strip()

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
