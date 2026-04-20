# Status da Integração: Carteira & MacroDroid

Este documento registra o estado atual do desenvolvimento do módulo "Carteira" do AllMedias e sua integração com o aplicativo MacroDroid, permitindo que retomemos o trabalho no futuro exatamente de onde paramos.

## 1. O que foi feito e está funcionando (Backend/Frontend)
- **Criação Segura de Tokens:** O sistema agora gera automaticamente um `api_token` único (usando criptografia `secrets` do Python) para cada usuário. Este token substitui o sistema de login padrão (sessão/cookies) para rotas de API em background.
- **Webhook Recebedor (`carteira/api/notificacao/`):** A view foi configurada com `@csrf_exempt` para receber as requisições de servidores e aparelhos externos.
- **Suporte a Form-Data:** O Webhook foi otimizado para receber dados via `application/x-www-form-urlencoded` em vez de JSON puro. Isso resolve o problema de caracteres especiais (aspas, quebras de linha) que vêm nas notificações dos bancos e quebravam o MacroDroid.
- **UI (Interface):** 
  - O link estático da Carteira foi removido do rodapé global (footer).
  - O acesso à Carteira foi redirecionado para o "Card" (Dashboard) da Tela Inicial.
  - Foi criado um Modal inteligente na tela da Carteira que puxa automaticamente o Token do usuário e exibe instruções de integração.

## 2. Testes de Produção Realizados
Foi disparada uma requisição HTTP via console direto para o servidor de produção no Railway:
`curl -X POST https://igeracao.com.br/carteira/api/notificacao/ ...`

**Resultado:** Sucesso (Código 200). O servidor processou, identificou a conta corretamente e inseriu a notificação "fake" no banco de dados. Isso **prova** que não há bloqueios de rede no Railway ou erros de código no Django.

## 3. Pendências / Próximos Passos (Onde paramos)

O gargalo atual encontra-se exclusivamente no ambiente físico do celular (Xiaomi / MacroDroid). O sinal de disparo do celular não está conseguindo "sair" do aparelho em direção à nuvem.

**Para a próxima sessão, devemos investigar os bloqueios do Android:**
1. **Restrições da MIUI/HyperOS:** Garantir que o MacroDroid tenha permissão irrestrita de rodar em segundo plano e acessar dados móveis/wi-fi em background.
2. **Revisão Visual do MacroDroid:** Verificar se as variáveis estão inseridas na aba de **"Parâmetros"** da Requisição HTTP (e se a aba Cabeçalhos está vazia).
3. **Erros de Digitação Invisíveis:** Refazer a requisição no MacroDroid do zero para limpar possíveis espaços em branco invisíveis inseridos pelo teclado mobile na URL ou no nome do parâmetro (`user_token`).

## 4. Configuração Padrão do MacroDroid (Resumo)
- **Gatilho:** Notificações de Bancos selecionados (Nubank, Itaú, etc) com a Regex `PIX|Compra`.
- **Ação:** Requisição HTTP.
- **URL:** `https://igeracao.com.br/carteira/api/notificacao/`
- **Método:** `POST`
- **Tipo de Conteúdo:** `application/x-www-form-urlencoded`
- **Parâmetros (Form Data):**
  - `texto` : `[not_title] - [not_ticker]`
  - `app` : `[not_app_name]`
  - `user_token` : `TOKEN_COPIADO_DO_SITE` (Sem colchetes ou aspas).
