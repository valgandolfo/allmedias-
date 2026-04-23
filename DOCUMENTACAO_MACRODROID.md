# Status da Integração: Carteira & MacroDroid (CONCLUÍDO)

Este documento registra a configuração final funcional da integração entre o AllMedias e o MacroDroid via dispositivo Xiaomi.

## 1. O que foi feito e validado
- **Criação Segura de Tokens:** O sistema gera um `api_token` único por usuário para autenticação de background.
- **Webhook Recebedor:** Localizado em `https://igeracao.com.br/carteira/api/notificacao/`.
- **Parsing Inteligente:** O sistema agora identifica:
  - Valores monetários (R$, $, €, etc).
  - Estabelecimentos e remetentes de PIX (usando preposições "em", "no", "de", "para").
- **Compatibilidade Xiaomi/MIUI:** Ajustes de permissões realizados com sucesso.

## 2. Configuração Final do MacroDroid (Recomendado)
Para evitar problemas com o corpo (body) da requisição, configure a ação **"Requisição HTTP"** usando a URL completa com parâmetros:

- **Ação:** Requisição HTTP.
- **Método:** POST ou GET (o sistema agora aceita ambos).
- **URL:** `https://igeracao.com.br/carteira/api/notificacao/?texto=[not_title] - [notification]&app=[not_app_name]&user_token=SEU_TOKEN_AQUI`
- **Nota:** Substitua `SEU_TOKEN_AQUI` pelo seu token pessoal gerado no site.

**Por que usar assim?** 
Algumas versões do MacroDroid no Android/Xiaomi têm dificuldade em enviar o "Body" da requisição corretamente. Enviando os parâmetros direto na URL (Query String), a integração se torna 100% confiável.

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
