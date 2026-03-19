# 📱 SÍNTESE DO PROJETO ALLMÉDIAS PWA

## 🎯 **VISÃO GERAL**

Sistema de **armazenamento e gestão de mídias pessoais** com funcionalidades de **anotações inteligentes** e **compartilhamento entre usuários**. 

**Migração:** Flutter/Dart + Django → **Django Puro + PWA**

---

## 🏗️ **ARQUITETURA**

### **Stack Tecnológica**
- **Backend**: Django 6.x
- **Frontend**: Templates HTML + Bootstrap 5 + JavaScript
- **PWA**: Manifest + Service Worker
- **Banco Dev**: SQLite
- **Banco Prod**: PostgreSQL (Railway via DATABASE_URL)
- **Storage**: Wasabi S3 (prod) / Local (dev)
- **Autenticação**: Django Sessions (substitui JWT)

### **Filosofia de Desenvolvimento**
- ✅ **Menos camadas**: Navegador → Django → Banco/S3
- ✅ **PWA nativo**: Site instalável como app
- ✅ **Mobile-first**: Design responsivo, toque otimizado
- ✅ **Simplicidade**: Modelos limpos, menos relacionamentos

---

## 📱 **FUNCIONALIDADES PRINCIPAIS**

### **1. 📚 Minhas Mídias**
**Descrição:** Biblioteca pessoal de arquivos com organização inteligente

**Recursos:**
- Upload de fotos, documentos, vídeos, áudios
- Armazenamento seguro (Wasabi S3)
- Otimização automática de imagens (estilo Google Fotos)
- Sistema de tags para busca
- Favoritos integrados (campo boolean)
- Filtros por tipo de mídia
- Visualização responsiva com thumbnails

**Metadados:**
- Descrição personalizada
- Tags (separadas por vírgula)
- Tipo de mídia (foto, documento, pdf, video, audio)
- Data de upload automática
- Tamanho do arquivo
- Status de upload (fila, processando, concluído, erro)

### **2. 🔄 Conversor de Mídias**
**Descrição:** Transformação automática de arquivos

**Conversões Suportadas:**
- **Imagem → PDF**: Fotos individuais ou múltiplas em um PDF
- **Documento → PDF**: TXT, DOC, DOCX para PDF
- **Processamento em fila**: Sistema assíncrono para arquivos grandes

**Fluxo:**
1. Usuário seleciona arquivo(s)
2. Sistema adiciona à fila de processamento
3. Conversão automática em background
4. Notificação quando concluído
5. Download do arquivo convertido

### **3. 📝 Anota Ai+ (Agenda Inteligente)**
**Descrição:** Sistema de anotações com tipos especializados

**Modalidades:**

#### **📄 Texto Livre**
- Anotações simples estilo notepad
- Formatação básica preservada
- Busca por conteúdo

#### **📋 Lista Numerada** 
- Itens ordenados (1, 2, 3...)
- Reordenação automática
- Adição/remoção dinâmica

#### **✅ Checklist**
- Itens com checkbox (✅/❌)
- Marcação de concluído/pendente
- Progresso visual da lista
- Reativação de itens

#### **💳 PIX**
- Dados bancários estruturados:
  - Nome do PIX
  - Chave PIX (CPF, email, telefone, aleatória)
  - Favorecido
  - Banco
- Cópia rápida de dados
- Compartilhamento seguro

**Recursos Globais:**
- Sistema de favoritos (boolean)
- Busca em todas as anotações
- Histórico por data de criação
- Exportação individual

### **4. ↔️ Enviar e Receber Mídias**
**Descrição:** Compartilhamento seguro entre usuários

**Funcionalidades:**
- Envio de mídias para usuários por email
- Compartilhamento de anotações específicas
- Histórico completo de transferências
- Controle de acesso por usuário
- Notificações de recebimento

**Fluxo de Compartilhamento:**
1. Usuário seleciona item (mídia ou anotação)
2. Informa email do destinatário
3. Sistema verifica se destinatário existe
4. Cria cópia do item para o destinatário
5. Registra transferência no histórico
6. Notifica ambos os usuários

---

## 🗄️ **ESTRUTURA DE DADOS OTIMIZADA**

### **📊 Models Principais**

#### **TBMIDEAS (Mídias)**
```python
class TBMIDEAS(models.Model):
    MID_ID = models.AutoField(primary_key=True)
    MID_descricao = models.CharField(max_length=100, verbose_name='Descrição')
    MID_tipo_midia = models.CharField(max_length=50, choices=TIPO_CHOICES)
    MID_arquivo = models.FileField(upload_to=user_media_path)
    MID_tags = models.CharField(max_length=500, blank=True, verbose_name='Tags')
    MID_data_upload = models.DateTimeField(auto_now_add=True)
    MID_tamanho = models.CharField(max_length=50, blank=True)
    MID_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='concluido')
    MID_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    MID_favorito = models.BooleanField(default=False)  # ← NOVO: substitui TBFAVORITOS
```

#### **TBANOTAAI (Anotações)**
```python
class TBANOTAAI(models.Model):
    ANO_ID = models.AutoField(primary_key=True)
    ANO_titulo_texto = models.CharField(max_length=100, verbose_name='Título')
    ANO_tipo_texto = models.CharField(max_length=20)  # texto, lista_numerada, checklist, pix
    ANO_texto = models.TextField(blank=True, verbose_name='Conteúdo')
    ANO_data_cadastro = models.DateTimeField(auto_now_add=True)
    ANO_favorito = models.BooleanField(default=False)
    ANO_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Campos específicos para PIX
    ANO_pix_nome = models.CharField(max_length=200, blank=True, null=True)
    ANO_pix_chave = models.CharField(max_length=200, blank=True, null=True)
    ANO_pix_favorecido = models.CharField(max_length=200, blank=True, null=True)
    ANO_pix_banco = models.CharField(max_length=100, blank=True, null=True)
```

#### **TBITEM_ANOTAAI (Itens de Lista/Checklist)**
```python
class TBITEM_ANOTAAI(models.Model):
    ITE_ID = models.AutoField(primary_key=True)
    ITE_ANOTAI_anotacao = models.ForeignKey(TBANOTAAI, on_delete=models.CASCADE)
    ITE_ANOTAI_descricao = models.CharField(max_length=500, verbose_name='Descrição do Item')
    ITE_ANOTAI_linha = models.IntegerField(verbose_name='Ordem')
    ITE_ANOTAI_concluido = models.BooleanField(default=False, verbose_name='Concluído')
```

#### **TBTRANSFERENCIA (Histórico de Compartilhamentos)**
```python
class TBTRANSFERENCIA(models.Model):
    TRF_ID = models.AutoField(primary_key=True)
    TRF_usuario_origem = models.ForeignKey(User, related_name='transferencias_enviadas')
    TRF_usuario_destino = models.ForeignKey(User, related_name='transferencias_recebidas')
    TRF_item_tipo = models.CharField(max_length=20)  # 'midia' ou 'anotacao'
    TRF_item_id = models.IntegerField(verbose_name='ID do Item')
    TRF_data_transferencia = models.DateTimeField(auto_now_add=True)
    TRF_observacao = models.CharField(max_length=200, blank=True)
```

### **🔧 User Model Estendido**
```python
# Adicionar ao model User padrão do Django via profile ou campos personalizados
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # PIX pessoal do usuário
    pix_nome = models.CharField(max_length=200, blank=True)
    pix_chave = models.CharField(max_length=200, blank=True)
    pix_favorecido = models.CharField(max_length=200, blank=True)
    pix_banco = models.CharField(max_length=100, blank=True)
    
    # Controle de acesso (se necessário)
    dias_acesso = models.IntegerField(default=365)
    data_expiracao = models.DateTimeField(blank=True, null=True)
```

### **🗑️ Models Eliminados (Simplificação)**

#### **~~TBFAVORITOS~~** → **REMOVIDO**
**Justificativa:** Substituído por campos boolean nos próprios models
- Performance melhor (sem JOINs)
- Código mais simples
- Menos queries no banco

#### **~~TBPERFIL~~** → **INTEGRADO ao User**
**Justificativa:** Aproveitar Django padrão + UserProfile
- Menos relacionamentos
- Autenticação mais direta
- Facilita permissions

---

## 🔐 **SISTEMA de AUTENTICAÇÃO**

### **Migração: JWT → Django Sessions**

**Antes (Flutter):**
```
Flutter App → JWT Token → Django API → WebView
```

**Depois (PWA):**
```
Navegador → Django Sessions → Templates HTML
```

### **Fluxo de Autenticação**

#### **1. Registro de Usuário**
- Formulário: Nome, Email, Senha, Confirmar Senha
- Validação de email único
- Criação automática de UserProfile
- Redirect para login

#### **2. Login**
- Email + Senha (validação Django padrão)
- Sessão automática criada
- Redirect para home logada
- Opção "Lembrar-me" (extend session)

#### **3. Recuperação de Senha**
- Email de reset com token temporal
- Formulário de nova senha
- Invalidação de sessões existentes

#### **4. Logout**
- Destroy session
- Redirect para página de login
- Clear de caches PWA se necessário

---

## 📱 **PWA (Progressive Web App)**

### **Componentes Técnicos**

#### **Manifest (`static/manifest.webmanifest`)**
```json
{
  "name": "AllMedias",
  "short_name": "AllMedias",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0d6efd",
  "theme_color": "#0d6efd",
  "icons": [
    {
      "src": "/static/img/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/img/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### **Service Worker (`static/service-worker.js`)**
- Cache de assets estáticos (CSS, JS, imagens)
- Cache de templates principais (home, login)
- Estratégia cache-first para performance
- Fallback offline básico

#### **Instalação Mobile**
- Banner "Adicionar à tela inicial"
- Ícone do app na home screen
- Splash screen automática
- Experiência fullscreen (sem barra do navegador)

---

## 🎨 **DESIGN SYSTEM**

### **Cores Principais**
```css
:root {
  --primary-color: #0d6efd;      /* Azul Bootstrap */
  --bg-color: #f8f9fa;          /* Cinza claro */
  --card-color: #ffffff;        /* Branco */
  --text-color: #212529;        /* Preto suave */
  --muted-color: #6c757d;       /* Cinza médio */
  --success-color: #198754;     /* Verde */
  --warning-color: #ffc107;     /* Amarelo */
  --danger-color: #dc3545;      /* Vermelho */
}
```

### **Componentes**
- **Cards**: Border-radius 12px, shadow sutil
- **Botões**: Feedback táctil com animação
- **Icons**: Bootstrap Icons
- **Layout**: Mobile-first, padding 15px
- **Typography**: System fonts (-apple-system, Segoe UI)

### **Responsividade**
- **Mobile**: < 768px (prioritário)
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px (secundário)

---

## 🚀 **ROADMAP DE DESENVOLVIMENTO**

### **📅 Fase 1: Fundação (1-2 semanas)**
#### **Prioridade Crítica**
1. ✅ **Templates base** (já concluído)
2. 🔄 **Sistema de autenticação completo**
   - Login, registro, logout, recuperação de senha
   - UserProfile com foto e PIX
3. 🔄 **Models otimizados**
   - Migrar do projeto antigo
   - Implementar favoritos boolean
   - Testes básicos

#### **Entregáveis Fase 1:**
- Login funcional com sessões Django
- Modelos de dados criados e migrados
- Templates de autenticação responsivos
- Configuração PWA básica

### **📅 Fase 2: Core Features (2-3 semanas)**
#### **Funcionalidades Principais**
1. **Upload de Mídias**
   - Interface drag & drop
   - Integração Wasabi S3
   - Otimização de imagens
   - Sistema de tags

2. **Biblioteca de Mídias**
   - Lista responsiva com filtros
   - Busca por tags e descrição
   - Favoritos toggle
   - Paginação

3. **Anotações Básicas**
   - Texto livre
   - Lista numerada
   - Interface CRUD completa

#### **Entregáveis Fase 2:**
- Upload funcional para S3
- Biblioteca completa de mídias
- Sistema básico de anotações
- Busca e filtros operacionais

### **📅 Fase 3: Features Avançadas (2-3 semanas)**
#### **Funcionalidades Especializadas**
1. **Conversor de Mídias**
   - Imagem para PDF
   - Documento para PDF
   - Fila de processamento
   - Status de conversão

2. **Anotações Avançadas**
   - Checklist interativo
   - PIX estruturado
   - Exportação/importação

3. **Sistema de Compartilhamento**
   - Envio entre usuários
   - Histórico de transferências
   - Notificações

#### **Entregáveis Fase 3:**
- Conversor funcional
- Todos os tipos de anotação
- Sistema de compartilhamento completo
- Histórico e notificações

### **📅 Fase 4: PWA Completo (1-2 semanas)**
#### **Otimizações Finais**
1. **Service Worker Avançado**
   - Cache inteligente
   - Sincronização offline
   - Notificações push

2. **Performance**
   - Lazy loading de imagens
   - Compressão de assets
   - CDN para estáticos

3. **UX Enhancements**
   - Animações fluidas
   - Feedback táctil completo
   - Shortcuts de teclado

#### **Entregáveis Fase 4:**
- PWA instalável e offline-ready
- Performance otimizada
- Experiência de app nativo completa

---

## 🔧 **CONFIGURAÇÕES TÉCNICAS**

### **Ambiente de Desenvolvimento**
```bash
# Estrutura de pastas
/home/joaonote/newmedia/
├── app_newmedia/          # App principal Django
├── pro_newmedia/          # Configurações do projeto
├── templates/             # Templates globais
├── static/               # Assets estáticos
│   ├── css/
│   ├── js/
│   ├── img/
│   ├── manifest.webmanifest
│   └── service-worker.js
├── media/                # Uploads locais (dev)
├── reciclagem/          # Código do projeto antigo
└── requirements.txt
```

### **Variáveis de Ambiente (.env)**
```bash
# Django
DJANGO_SECRET_KEY=sua_chave_secreta_aqui
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Wasabi S3 (Produção)
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_STORAGE_BUCKET_NAME=allmédias-bucket
AWS_S3_ENDPOINT_URL=https://s3.wasabisys.com

# Email (para recuperação de senha)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
```

### **Dependências Principais (requirements.txt)**
```txt
Django>=6.0.0
django-storages[s3]>=1.14.0
boto3>=1.34.0
Pillow>=10.0.0  # Para processamento de imagens
python-decouple>=3.8  # Para .env
reportlab>=4.0.0  # Para geração de PDF
whitenoise>=6.6.0  # Para static files em produção
```

---

## 📈 **MÉTRICAS DE SUCESSO**

### **Performance**
- **Tempo de carregamento**: < 3s (first paint)
- **Upload de mídia**: Progresso visual em tempo real
- **Busca**: Resultados < 500ms
- **PWA Score**: 90+ no Lighthouse

### **UX (User Experience)**
- **Mobile-first**: Design otimizado para toque
- **Offline básico**: Cache de páginas principais
- **Feedback visual**: Animações de carregamento
- **Acessibilidade**: WCAG 2.1 AA compliance

### **Funcionalidade**
- **Todos os 4 módulos** operacionais
- **Upload simultâneo** de múltiplos arquivos
- **Compartilhamento** entre usuários eficiente
- **Favoritos e busca** responsivos

---

## 💡 **DECISÕES ARQUITETURAIS**

### **✅ Simplificações Aprovadas**
1. **Favoritos Boolean**: Eliminar TBFAVORITOS
2. **User Profile**: Integrar TBPERFIL ao Django User
3. **Sessions vs JWT**: Mais simples para PWA
4. **Templates vs SPA**: Melhor SEO e performance inicial

### **🎯 Benefícios Alcançados**
- **Menos complexidade** no banco de dados
- **Queries mais eficientes** (menos JOINs)
- **Desenvolvimento mais rápido**
- **Manutenção facilitada**
- **Deploy mais simples**

---

## 🎉 **PRÓXIMOS PASSOS IMEDIATOS**

1. **Implementar sistema de login completo**
   - Views de autenticação
   - Templates responsivos  
   - Validações e segurança

2. **Migrar models do projeto antigo**
   - Adaptar com as simplificações
   - Criar migrations
   - Testes unitários básicos

3. **Criar views principais**
   - Home logada
   - Upload de mídia
   - Lista de mídias
   - CRUD de anotações

4. **Configurar storage S3**
   - Wasabi em produção
   - Fallback local em dev
   - Otimização de imagens

---

*Este documento serve como referência completa para o desenvolvimento do AllMedias PWA. Todas as decisões técnicas e de produto estão consolidadas aqui para consulta durante o desenvolvimento.*

**Versão:** 1.0  
**Data:** {{ data_atual }}  
**Status:** Aprovado para desenvolvimento