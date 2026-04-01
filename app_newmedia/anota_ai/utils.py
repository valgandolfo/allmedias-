import crcmod
import re
import unicodedata

def remove_acentos(texto):
    """Remove acentos e caracteres especiais, mantendo o padrão do Pix"""
    if not texto: return ""
    texto = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8')
    # Remover tudo exceto letras, números e espaços
    texto = re.sub(r'[^a-zA-Z0-9 ]', '', texto)
    return texto[:25] # Limitar tamanho conforme especificação EMV

def format_emv_str(id_str, value):
    """Formata valor com ID de tag e comprimento de 2 dígitos"""
    value = str(value)
    return f"{id_str}{len(value):02d}{value}"

def calcular_crc16(payload):
    """Calcula o CRC16-CCITT do payload Pix"""
    # Adicionar o identificador do CRC16 no final do payload ("6304")
    payload = payload + "6304"
    crc16_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)
    crc = crc16_func(payload.encode('utf-8'))
    return f"{crc:04X}"

def gerar_payload_pix(chave, nome, cidade, valor=None, txid='***'):
    """Gera string do Pix Copia e Cola"""
    if not chave or not nome or not cidade:
        return ""

    # Normalizar campos
    chave = chave.strip()
    nome = remove_acentos(nome.upper())
    cidade = remove_acentos(cidade.upper())
    txid = txid.upper().strip() if txid else '***'
    
    # Payload Format Indicator (ID 00)
    payload = format_emv_str('00', '01')
    
    # Merchant Account Information - GUI (ID 26, sub-ID 00) e Chave (Sub-ID 01)
    merchant_gui = format_emv_str('00', 'br.gov.bcb.pix')
    merchant_chave = format_emv_str('01', chave)
    merchant_account = format_emv_str('26', merchant_gui + merchant_chave)
    payload += merchant_account
    
    # Merchant Category Code (ID 52) - 0000
    payload += format_emv_str('52', '0000')
    
    # Transaction Currency (ID 53) - 986 para BRL
    payload += format_emv_str('53', '986')
    
    # Transaction Amount (ID 54) - opcional
    if valor and float(valor) > 0:
        valor_str = f"{float(valor):.2f}"
        payload += format_emv_str('54', valor_str)
        
    # Country Code (ID 58) - BR
    payload += format_emv_str('58', 'BR')
    
    # Merchant Name (ID 59)
    payload += format_emv_str('59', nome)
    
    # Merchant City (ID 60)
    payload += format_emv_str('60', cidade)
    
    # Additional Data Field Template (ID 62, sub-ID 05 para txid)
    additional_data = format_emv_str('05', txid)
    payload += format_emv_str('62', additional_data)
    
    # CRC16 (ID 63, length 04) será calculado e tem tamanho 4 caracteres
    crc16 = calcular_crc16(payload)
    return payload + "6304" + crc16
