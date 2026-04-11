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
- **Banco Dev**: SQLite
- **Banco Prod**: MYSQL (Railway via DATABASE_URL)
- **Storage**: Wasabi S3 (prod) / Local (dev)
- **Autenticação**: Django Sessions

### **Filosofia de Desenvolvimento**
- ✅ **Menos camadas**: Navegador → Django → Banco/S3
- ✅ **PWA nativo**: Site instalável como app na home screen
- ✅ **Mobile-first**: Design responsivo (CSS Grid nativo), botões FAB (Floating Action Button), prioridade na usabilidade em telas pequenas.

---

## 📱 **FUNCIONALIDADES PRINCIPAIS**

### **1. 📚 Minhas Mídias (Central de Arquivos)**
**Descrição:** Biblioteca pessoal de arquivos organizados na nuvem.

**Recursos:**
- Upload de arquivos (fotos, docs, pdfs, audio e video).
- Armazenamento em Wasabi S3.
- Tags manuais para organização.
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

### **5. 📅 Calendário**
**Descrição:** Agenda pessoal interativa via CSS Grid.

**Recursos:**
- Grade de visualização de fácil navegação (mês e ano livre).
- Modal inferencial rápido: Ao clicar no dia, o modal desliza e permite consultar a lista e adicionar compromissos ali mesmo sem refresh de janela.
- Labels de Evento por cor (ex: azul, verde, vermelho, amarelo) para organização visual.
- Isolamento autoral (cada `User` vê exclusivamente o próprio sub-universo temporal).

---

## 🗄️ **ESTRUTURA DE DADOS OTIMIZADA**

A infraestrutura foi compactada. Tabelas legadas redundantes (como "Perfil separado" e "Mapeamento de Favoritos") foram enxugadas.

### **Modelos (Tabelas Principais)**

#### **`app_newmedia.medias.models.Midia` (TBMIDEAS)**
Armazena a raiz dos arquivos, metadados e tamanhos. Tags são adicionadas manualmente pelos usuários.

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

---

## 🚀 **ROTINAS ASSÍNCRONAS & DEPLOY**

### **Requisitos de Build (Railway)**
Para garantir que as integrações funcionem sem quebrar no ambiente Linux Serverless da Railway, não há dependências específicas de sistema além das padrão do Python/Django.

### **Comportamento PWA**
Os arquivos essenciais que ditam a instalação no ecossistema Android e iOS da Apple via Safari estão atrelados ao projeto em:
- `static/manifest.webmanifest`
- `static/service-worker.js`
- `templates/base.html` (com a tag de meta-theme-color e injeção do Worker).

---
*Este documento é a base viva oficial e consolidada das descrições operacionais e arquitetônicas do repositório PWA AllMédias, unificando os drafts antigos de idealização.*