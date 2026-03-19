<<<<<<< HEAD
# allmedias-
=======
# 📱 AllMedias PWA

Sistema de gestão de mídias pessoais com funcionalidades de anotações e compartilhamento entre usuários.

## 🚀 Início Rápido

### **Executar o projeto**
```bash
./iniciar_projeto.sh
```

Este script irá:
- ✅ Verificar Python 3.8+
- ✅ Criar/ativar ambiente virtual
- ✅ Instalar dependências
- ✅ Configurar banco de dados
- ✅ Criar superusuário (opcional)
- ✅ Iniciar servidor Django

### **Acessos**
- 🌐 **Aplicação**: http://127.0.0.1:8000
- 🔧 **Admin Django**: http://127.0.0.1:8000/admin

## ⚙️ Configuração

### **1. Ambiente (.env)**
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

### **2. Principais variáveis**
- `DJANGO_SECRET_KEY`: Chave secreta única ([gerar aqui](https://djecrety.ir/))
- `DATABASE_URL`: SQLite (dev) ou PostgreSQL (prod)
- `AWS_*`: Credenciais Wasabi S3 (opcional em dev)
- `EMAIL_*`: SMTP para recuperação de senha

## 🏗️ Stack Tecnológica

- **Backend**: Django 6.x
- **Frontend**: HTML + Bootstrap 5 + JavaScript
- **PWA**: Service Worker + Manifest
- **Storage**: Wasabi S3 / Local
- **Banco**: SQLite (dev) / PostgreSQL (prod)

## 📱 Funcionalidades

### **📚 Minhas Mídias**
- Upload de fotos, documentos, vídeos
- Organização por tags
- Sistema de favoritos
- Otimização automática de imagens

### **🔄 Conversor de Mídias** 
- Imagem → PDF
- Documento → PDF
- Processamento em fila

### **📝 Anota Ai+**
- Texto livre
- Lista numerada  
- Checklist interativo
- PIX estruturado

### **↔️ Compartilhamento**
- Envio entre usuários
- Histórico de transferências
- Controle de acesso

## 🛠️ Comandos Úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor manualmente
python manage.py runserver 127.0.0.1:8000

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell Django
python manage.py shell
```

## 📁 Estrutura do Projeto

```
allmédias/
├── pro_newmedia/          # Configurações Django
├── app_newmedia/          # App principal  
├── templates/             # Templates HTML
├── static/                # CSS, JS, imagens
├── media/                 # Uploads locais
├── venv/                  # Ambiente virtual
├── .env                   # Configurações (criar)
├── .env.example           # Template de configurações
├── requirements.txt       # Dependências Python
├── iniciar_projeto.sh     # Script de inicialização
└── README.md             # Esta documentação
```

## 📋 Documentação Completa

Consulte `SINTESE_PROJETO_ALLMÉDIAS.md` para documentação técnica detalhada.

## 🚀 Deploy (Railway)

1. Configure variáveis de ambiente no Railway
2. Conecte repositório Git
3. Railway detecta Django automaticamente
4. Configure `DATABASE_URL` e `AWS_*` para produção

---

**Versão**: 1.0  
**Migração**: Flutter → Django PWA  
**Autor**: AllMedias Team# allmedias-
>>>>>>> 6ae5f7b (first commit)
