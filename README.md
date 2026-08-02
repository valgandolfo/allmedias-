# 📱 SÍNTESE DO PROJETO ALLMÉDIAS PWA

## 🎯 **VISÃO GERAL**

Sistema de **armazenamento e gestão de mídias pessoais** com funcionalidades de **anotações inteligentes**, **agendamento de compromissos** e **compartilhamento entre usuários**.

**Arquitetura Base:** Django Puro + PWA (Substituindo fluxo legado em Flutter).

---

## 🏗️ **ARQUITETURA**

### **Stack Tecnológica**
- **Backend**: Django 6.x
- **Frontend**: Templates HTML + Bootstrap 5 + JavaScript (Fetch API / CSS Grid)
- **PWA**: Manifest + Service Worker
- **Tarefas em Background / Fila**: django-q2 (utilizando Redis como broker)
- **Banco Dev**: MySQL (Local / Docker)
- **Banco Prod**: MySQL (Railway via DATABASE_URL)
- **Storage**: Cloudflare (prod) / Local (dev)
- **Infraestrutura**: Docker
- **Autenticação**: Django Sessions

### **Filosofia de Desenvolvimento e UI**
- ✅ **Menos camadas**: Navegador → Django → Banco/S3
- ✅ **PWA nativo**: Site instalável como app na home screen
- ✅ **Assincronicidade e Performace**: Operações custosas são jogadas para fila de processamento sem prender a tela do usuário.
- ✅ **Mobile-first**: Design responsivo (CSS Grid nativo), botões FAB (Floating Action Button), prioridade na usabilidade em telas pequenas.
- ✅ **Arquitetura CRUD-Pai/Filho**: O sistema adota a filosofia DRY (*Don't Repeat Yourself*). Todos os módulos utilizam uma herança central de templates (`templates/crud/lista_base.html` e `detalhes_base.html`). Isso restringe cada módulo a ter **apenas 2 arquivos** HTML de interface (`lista.html` e `detalhes.html`), delegando a renderização interna a variáveis de estado (ex: `acao = criar|editar|deletar`).
- ✅ **View Toggle Dinâmico**: As telas de lista oferecem alternância instantânea entre visualização em Lista e Grid/Cards via troca de classe CSS disparada por JavaScript. A preferência de visualização do usuário é salva no `localStorage` do dispositivo, dispensando consultas ao banco de dados e garantindo persistência imediata e offline por módulo.

---

## 📱 **FUNCIONALIDADES PRINCIPAIS**

### **1. 📚 Minhas Mídias (Central de Arquivos)**
**Descrição:** Biblioteca pessoal de arquivos organizados na nuvem.

**Recursos:**
- Upload de arquivos (fotos, docs, pdfs, audio e video).
- Armazenamento na Storage Cloudflare.
- Otimização automática de imagens.
- Layout de exibição customizado em mosaico responsivo.

### **2. 🔄 Conversor de Mídias**
**Descrição:** Transformação de arquivos automatizada.

**Recursos:**
- Conversão de Imagens e Documentos genéricos → PDF.
- Acompanhamento reativo do processamento.
- Feedback por Notificações Toast no front-end.

### **3. 📝 Anota Ai+ (Caderno Inteligente)**
**Descrição:** Engine de anotações com parser de contexto.

**Modalidades:**
- **Livre**: Texto comum para lembretes.
- **Lista Numerada**: Reconhecimento dinâmico de `1 - item`.
- **Checklist**: Inputs como `[ ]` e `[x]` mapeados como botões clicáveis interativos. Tela própria para riscar itens à mão.
- **PIX**: Armazenamento semi-estruturado (Favorecido, Banco, Chave, Cidade) para compartilhamento ágil.

### **4. ↔️ Transferir Mídias**
**Descrição:** Motor para compartilhamento de dados intra-usuários.

**Recursos:**
- Envio direto de uma mídia ou Anotação via email de destinatário já cadastrado.
- Histórico visual contendo tudo que o usuário já enviou e já recebeu do sistema, detalhando data e tipo.

### **5. 📅 Calendário & Notificações**
**Descrição:** Agenda pessoal interativa via CSS Grid com sistema de automação.

**Recursos:**
- Grade de visualização de fácil navegação (mês e ano livre).
- Modal inferencial rápido: Ao clicar no dia, o modal desliza e permite consultar a lista e adicionar compromissos ali mesmo sem refresh de janela.
- Labels de Evento por cor (ex: azul, verde, vermelho, amarelo) para organização visual.
- Isolamento autoral (cada `User` vê exclusivamente o próprio sub-universo temporal).
- **Integração com WhatsApp:** Disparo de mensagens através de um Cron gerenciado via Redis, baseado nos compromissos agendados.

### **6. 💬 Mensagens WhatsApp**
**Descrição:** Módulo para agendamento e envio avulso de mensagens diretas pelo WhatsApp via Evolution API.

**Recursos:**
- Envio imediato de mensagem via interface (selecionando a ocorrência "Agora").
- Agendamento flexível de rotinas ("Todo dia", "Semanal", "Mensal") delegadas ao serviço de Cron.
- Reenvio instantâneo diretamente pelo menu de contexto da lista.
- Integração visual com status claro de andamento (✅ Enviada / ⏳ Pendente).
- Utiliza a herança padrão de UI (lista_base e detalhes_base).

---

## 🗄️ **ESTRUTURA DE DADOS OTIMIZADA**

A infraestrutura foi compactada. Tabelas legadas redundantes (como "Perfil separado" e "Mapeamento de Favoritos") foram enxugadas.

### **Modelos (Tabelas Principais)**

#### **`app_newmedia.medias.models.Midia` (TBMIDEAS)**
Armazena a raiz dos arquivos, metadados e tamanhos.

#### **`app_newmedia.anota_ai.models.Anotacao` (TBANOTAAI)**
Abraça de forma dinâmica texto, pix e checklist usando campos nulos estendidos e enumeração de Tipo, juntamente aos fragmentos filhos `ItemAnotacao` para as checklists.

#### **`app_newmedia.transferir.models.Transferencia` (TBTRANSFERENCIA)**
Faz a ponte dupla de foreign keys `usuario_origem` e `usuario_destino`.

#### **`app_newmedia.calendario.models.Compromisso` (TBCALENDARIO)**
Entidade recém gerada contendo os metadados fixos:
- `usuario` (FK)
- `data` e `hora`
- `titulo` (Max 50)
- `cor` (Hex de identificação)
- `observacoes` (Texto livre)

#### **`app_newmedia.mensagem.models.Mensagem` (TBMENSAGEM)**
Entidade estruturada para controle de disparos da Evolution API:
- `men_telefone` e `men_nome` (Identificação)
- `men_dat` e `men_hora` (Cronograma de agendamento)
- `men_ocorrencia` (Escolha entre Agora, Todo dia, Semanal, Mensal)
- `men_mensagem` (Conteúdo a ser enviado - Máximo 150 caracteres)
- `men_status` (Flag booleana de controle do Cron e Dashboard)

---

## 🚀 **ROTINAS ASSÍNCRONAS & DEPLOY**

### **Infraestrutura e Hospedagem (Railway VPS)**
O projeto está hospedado em uma VPS na Railway, orquestrado através de **Dockerfile** e operando sob o domínio público **igeracao.com.br**. A infraestrutura em produção conta com 3 serviços, incluindo:
1. Serviço do repositório principal.
2. Serviço secundário de um repositório que interliga o principal ao Redis.

O sistema de correio utiliza o e-mail **Titan integrado com o Gmail via POP**.

### **Background Tasks e Cron (Redis + Django Q2)**
- Diferente de setups antigos, agora o projeto já está configurado com **Redis** e suas devidas credenciais.
- Este repositório Redis gerencia um **Cron** responsável pelo envio de mensagens de notificação via **WhatsApp**.

### **Comportamento PWA**
Os arquivos essenciais que ditam a instalação no ecossistema Android e iOS da Apple via Safari estão atrelados ao projeto em:
- `static/manifest.webmanifest`
- `static/service-worker.js`
- `templates/base.html` (com a tag de meta-theme-color e injeção do Worker).

---

## 📂 **MAPA DO REPOSITÓRIO (DIRECTORY STRUCTURE)**

Esta estrutura ajuda desenvolvedores e agentes de IA a navegarem rapidamente pela base de código.

```text
/home/joaonote/newmedia/
├── app_newmedia/      # Todos os apps/módulos do Django (medias, anota_ai, calendario, transferir)
├── pro_newmedia/      # Configurações core do projeto (settings.py, urls.py, wsgi, asgi)
├── templates/         # Arquivos HTML (Usa filosofia DRY em templates/crud/lista_base.html)
├── static/            # Assets estáticos (CSS, JS customizados, manifest.webmanifest, service-worker.js)
├── scripts/           # Scripts Python e bash auxiliares
├── Dockerfile         # Instruções de build da imagem
├── docker-compose.yml # Orquestração local dos containers (App + Banco + Redis)
├── entrypoint.sh      # Script de inicialização (Roda migrações e sobe o gunicorn/server)
├── manage.py          # Entrypoint padrão do Django
└── .env               # Variáveis de ambiente sensíveis (DB, Redis, Email)
```

---
*Este documento é a base viva oficial e consolidada das descrições operacionais e arquitetônicas do repositório PWA AllMédias, unificando os drafts antigos de idealização.*