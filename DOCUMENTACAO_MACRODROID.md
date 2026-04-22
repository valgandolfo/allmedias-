# Status da Integração: Carteira & MacroDroid (CONCLUÍDO)

Este documento registra a configuração final funcional da integração entre o AllMedias e o MacroDroid via dispositivo Xiaomi.

## 1. O que foi feito e validado
- **Criação Segura de Tokens:** O sistema gera um `api_token` único por usuário para autenticação de background.
- **Webhook Recebedor:** Localizado em `https://igeracao.com.br/carteira/api/notificacao/`.
- **Parsing Inteligente:** O sistema agora identifica:
  - Valores monetários (R$, $, €, etc).
  - Estabelecimentos e remetentes de PIX (usando preposições "em", "no", "de", "para").
- **Compatibilidade Xiaomi/MIUI:** Ajustes de permissões realizados com sucesso.

## 2. Configuração Final do MacroDroid
Para garantir o funcionamento, a macro deve seguir estes parâmetros:

- **Gatilho:** Notificação Recebida.
  - **Apps:** Bancos (Nubank, Inter, etc) e Google Wallet.
  - **Filtro de Texto:** `PIX|Compra|recebido|transferência` (Regex).
- **Ação:** Requisição HTTP (POST).
  - **URL:** `https://igeracao.com.br/carteira/api/notificacao/` (Obrigatório a barra no final).
  - **Tipo de Conteúdo:** `application/x-www-form-urlencoded`.
  - **Parâmetros:**
    - `texto` : `{not_title} - {not_ticker}` (ou `[not_title]` dependendo da versão).
    - `app` : `{not_app_name}` (ou `[not_app_name]`).
    - `user_token` : `SEU_TOKEN_COPIADO_DO_SITE` (Texto puro).

## 3. Checklist de Manutenção (Xiaomi/HyperOS)
Se o sistema parar de receber notificações, verifique:
1. **Acesso a Notificações:** (Configurações > Acesso a Notificações). Se necessário, desative e ative o MacroDroid novamente.
2. **Início Automático:** Deve estar **ATIVO** para o MacroDroid.
3. **Economia de Bateria:** Deve estar em **"Nenhuma Restrição"**.
4. **Log do Sistema:** No MacroDroid, verifique se aparece `HTTP response code: 200` nas novas entradas.

## 4. Testes realizados
- [x] Teste via CURL (Servidor OK).
- [x] Teste manual via MacroDroid (Conexão OK).
- [x] Teste real via Gatilho de Notificação (Gatilho OK).
