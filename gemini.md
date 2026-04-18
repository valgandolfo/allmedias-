# 📘 Gemini – Visão Geral do Projeto AllMédias

## 🚀 Principais Recursos
- **Gestão de Mídias**: Upload, visualização em mosaico responsivo, otimização automática de imagens e PDFs.
- **OCR Assíncrono**: Extração de palavras‑chave via Tesseract, armazenadas como hashtags.
- **Conversor de Mídias**: Transformação automática de arquivos para PDF com feedback em toast.
- **Anota AI+**: Notas inteligentes com modos Livre, Lista Numerada, Checklist interativo e PIX.
- **Transferência de Mídias**: Envio direto entre usuários com histórico visual.
- **Calendário Interativo**: Grade CSS‑Grid, criação rápida de compromissos, labels coloridas.
- **PWA Nativo**: Instalação como app, service‑worker offline, manifest configurado.

## 📋 Regras de Negócio
- **Privacidade por Usuário**: Cada usuário visualiza apenas seus próprios arquivos, anotações e compromissos.
- **Processamento em Background**: Operações custosas (OCR, conversão) são enfileiradas via **django‑q2**; a UI nunca bloqueia.
- **Armazenamento Seguro**: Dados de produção são armazenados no **Wasabi S3**; ambiente de desenvolvimento usa armazenamento local.
- **Tagging Automático**: Tags geradas a partir de OCR são limitadas às 5 palavras‑chave mais relevantes.
- **Limite de Tamanho**: Uploads são validados contra limites configurados no bucket S3.
- **Calendário**: Cada evento pertence a um único usuário; cores são definidas por hexadecimais para visualização distinta.

## 📄 Páginas Principais (Templates)
| Página | Descrição | Template |
|--------|-----------|----------|
| **Home / Dashboard** | Visão geral de mídias, tarefas e calendário | `templates/base.html` |
| **Lista de Mídias** | Exibição em grid responsivo com filtros | `templates/medias/lista.html` |
| **Detalhe da Mídia** | Visualização individual, download, tags | `templates/medias/detalhes.html` |
| **Anota AI+** | Editor de notas com modos avançados | `templates/anota_ai/detalhes.html` |
| **Calendário** | Grade mensal/ano com modal de criação | `templates/calendario/calendario.html` |
| **Transferência** | Histórico de envios e recebimentos | `templates/transferir/historico.html` |

## 🛠️ Tecnologia Utilizada
- **Backend**: Django 6.x (ORM, Sessions, admin)
- **Frontend**: HTML5, Bootstrap 5, CSS Grid, JavaScript (Fetch API)
- **PWA**: `manifest.webmanifest`, `service‑worker.js`
- **Fila/Background**: django‑q2 (ORM‑based broker)
- **OCR**: Tesseract C++ via `pytesseract`
- **Armazenamento**: Wasabi S3 (prod) / Local FS (dev)
- **Banco de Dados**: SQLite (dev) → MySQL (prod) via Railway
- **Deploy**: Railway (Docker‑free, apt‑file for Tesseract)

## 🎨 Design System
- **Estilo**: Glassmorphism dark‑neon theme (blur, translucidez, sombras suaves).
- **Tipografia**: Google Font **Inter** (peso 400‑600) para legibilidade.
- **Cores Primárias**: 
  - Neon azul `#00f5ff`
  - Neon rosa `#ff00ff`
  - Fundo escuro `hsl(210, 10%, 12%)`
- **Componentes Reutilizáveis**: FAB (Floating Action Button), toast notifications, modal slide‑up, cards com blur.
- **Micro‑animações**: Hover scaling, transição de cores, carregamento de imagens com fade‑in.
- **Responsividade**: Layouts baseados em CSS Grid e Flexbox, breakpoints para mobile‑first.

---
*Este documento serve como referência rápida para desenvolvedores, designers e stakeholders do projeto AllMédias.*
