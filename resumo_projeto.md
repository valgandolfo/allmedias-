# AllMedias PWA - Especificação do Projeto

## 📋 Visão Geral

O **AllMedias PWA** é uma aplicação web progressiva para gerenciamento pessoal de mídias, anotações e compartilhamento entre usuários. Migração do sistema Flutter/Dart + Django para **Django puro** com PWA.

---

## 🎯 Funcionalidades Principais

### 1. 📚 **Minhas Medias** (Biblioteca Digital)
- **Armazenamento**: Upload para Wasabi S3 (produção) / local (desenvolvimento)  
- **Tipos suportados**: Fotos, documentos, PDFs, vídeos, áudios, textos, emails
- **Identificação**: 
  - Descrição personalizada
  - Tags para busca e categorização
  - Data de criação automática
- **Busca inteligente**: Por descrição, tags, tipo de mídia
- **Status de upload**: Pendente, agendado, concluído, erro

### 2. 🔄 **Converter Medias** (Transformação de Arquivos)
- **Imagem → PDF**: Conversão de fotos/imagens para documento PDF
- **Documento → PDF**: Transformação de TXT, DOC, etc. em PDF
- **Processamento**: Backend Django com bibliotecas de conversão
- **Organização**: Mídia original + versão convertida mantidas

### 3. 📝 **Anota Ai+** (Sistema de Anotações)
Agenda inteligente com três modalidades:

#### **Modalidade Texto Livre**
- Editor de texto simples
- Formatação básica
- Salvar/editar anotações

#### **Modalidade Lista Numerada**
- Itens ordenados automaticamente
- Adicionar/remover/reordenar itens
- Numeração automática

#### **Modalidade Checklist**
- Lista de tarefas com checkbox
- Marcar como concluído/pendente
- Progresso visual das tarefas

### 4. ↔️ **Enviar e Receber Medias** (Compartilhamento Social)
- **Compartilhar anotações**: Entre usuários cadastrados
- **Envio**: Selecionar usuários destinatários
- **Recebimento**: Notificações de novas anotações recebidas
- **Controle**: Histórico de transferências
- **Privacidade**: Apenas usuários autorizados

---

## 🏗️ Arquitetura Técnica

### **Frontend (PWA)**
- **Base**: Django Templates + HTML5/CSS3/JS
- **Framework CSS**: Bootstrap 5 + Bootstrap Icons
- **PWA**: Manifest + Service Worker para instalação mobile
- **Responsivo**: Mobile-first design

### **Backend**
- **Framework**: Django 6.x
- **Banco de dados**: 
  - SQLite (desenvolvimento)
  - PostgreSQL/MySQL via `DATABASE_URL` (produção Railway)
- **Armazenamento**: 
  - Local `media/` (desenvolvimento)  
  - Wasabi S3 (produção)
- **Autenticação**: Sistema Django User + perfis customizados

### **Modelos de Dados Principais**

#### **TBMIDEAS** (Mídias)
- MID_ID: Chave primária
- MID_descricao: Descrição da mídia
- MID_tipo_midia: foto|documento|email|pdf|texto|video|audio|outro
- MID_status: pendente|agendado|concluido|erro
- MID_tamanho: Tamanho do arquivo
- MID_data_criacao: Data automática
- MID_arquivo: Path do arquivo no storage
- MID_tags: Tags separadas por vírgula
- Usuario: FK para User

## TABELA TBANOTAAI
- Título e conteúdo da anotação
- Tipo: texto|lista_numerada|checklist
- Data de criação/modificação
- Usuário proprietário
- Status (privada/compartilhável)

## TABELA TBTRANSFERENCIA (Compartilhamento)
- Remetente (FK User)
- Destinatário (FK User)  
- Conteúdo compartilhado
- Data de envio
- Status (enviado|recebido|lido)





Este documento captura toda a essência do seu projeto! Ele serve como:

1. **Especificação técnica** para desenvolvimento
2. **Roadmap** para implementação por fases  
3. **Documentação** para futuras referências
4. **Guia** para novos desenvolvedores no projeto



