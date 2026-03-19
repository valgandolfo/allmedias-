#!/bin/bash

# ==============================================================================
# SCRIPT DE INICIALIZAÇÃO DO PROJETO ALLMÉDIAS PWA
# ==============================================================================
# Descrição: Configura ambiente, instala dependências e inicia o servidor Django
# Autor: AllMedias Team
# Data: $(date +%Y-%m-%d)
# ==============================================================================

set -e  # Parar execução se algum comando falhar

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner do projeto
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                     📱 ALLMÉDIAS PWA 📱                          ║"
echo "║                                                                  ║"
echo "║  Sistema de Gestão de Mídias Pessoais                          ║"
echo "║  Django + PWA + Bootstrap 5                                     ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    log_error "Arquivo manage.py não encontrado!"
    log_error "Execute este script na pasta raiz do projeto Django."
    exit 1
fi

log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 não está instalado!"
    log_error "Instale o Python 3.8+ antes de continuar."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
log_success "Python $PYTHON_VERSION encontrado ✓"

# Verificar/Criar ambiente virtual
if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
    log_success "Ambiente virtual criado ✓"
else
    log_info "Ambiente virtual já existe ✓"
fi

# Ativar ambiente virtual
log_info "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se a ativação funcionou
if [ -z "$VIRTUAL_ENV" ]; then
    log_error "Falha ao ativar o ambiente virtual!"
    exit 1
fi

log_success "Ambiente virtual ativado ✓"
log_info "Ambiente: $VIRTUAL_ENV"

# Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip --quiet

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    log_warning "requirements.txt não encontrado!"
    log_info "Criando requirements.txt básico..."
    cat > requirements.txt << EOF
Django>=6.0.0
django-storages[s3]>=1.14.0
boto3>=1.34.0
Pillow>=10.0.0
python-decouple>=3.8
reportlab>=4.0.0
whitenoise>=6.6.0
EOF
    log_success "requirements.txt criado ✓"
fi

# Instalar dependências
log_info "Instalando dependências do requirements.txt..."
pip install -r requirements.txt --quiet
log_success "Dependências instaladas ✓"

# Verificar se existe .env.example
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    log_info "Arquivo .env não encontrado."
    log_info "Copiando .env.example para .env..."
    cp .env.example .env
    log_warning "Configure o arquivo .env com suas credenciais!"
    log_info "Editando .env..."
    sleep 2
fi

# Verificar migrações pendentes
log_info "Verificando banco de dados..."

# Aplicar migrações se necessário
if [ ! -f "db.sqlite3" ]; then
    log_info "Banco de dados não existe. Criando..."
    python manage.py makemigrations
    python manage.py migrate
    log_success "Banco de dados criado ✓"
else
    log_info "Aplicando migrações..."
    python manage.py makemigrations --dry-run --verbosity=0 > /dev/null
    if [ $? -eq 0 ]; then
        python manage.py makemigrations
        python manage.py migrate
        log_success "Migrações aplicadas ✓"
    else
        log_info "Nenhuma migração pendente ✓"
    fi
fi

# Verificar se existe superusuário
log_info "Verificando usuário administrador..."
ADMIN_EXISTS=$(python manage.py shell -c "
from django.contrib.auth.models import User
print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')
" 2>/dev/null)

if [ "$ADMIN_EXISTS" = "no" ]; then
    log_warning "Nenhum superusuário encontrado!"
    echo ""
    echo -e "${YELLOW}Deseja criar um superusuário agora? (s/n):${NC}"
    read -r create_admin
    if [[ $create_admin =~ ^[Ss]$ ]]; then
        python manage.py createsuperuser
        log_success "Superusuário criado ✓"
    else
        log_info "Você pode criar um superusuário depois com: python manage.py createsuperuser"
    fi
else
    log_success "Superusuário já existe ✓"
fi

# Coletar arquivos estáticos (se necessário)
if [ -d "static" ] || [ -f "pro_newmedia/settings.py" ]; then
    log_info "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --clear --verbosity=0
    log_success "Arquivos estáticos coletados ✓"
fi

# Liberar porta 8000 se necessário e fixar nela
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Porta 8000 em uso. Liberando..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 1
    log_success "Porta 8000 liberada ✓"
fi
PORT=8000

# Informações finais
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🚀 PROJETO PRONTO! 🚀                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_success "Configuração concluída com sucesso!"
echo ""
log_info "📱 Aplicação: AllMedias PWA"
log_info "🌐 URL Local: http://127.0.0.1:$PORT"
log_info "🔧 Admin: http://127.0.0.1:$PORT/admin"
log_info "📁 Projeto: $(pwd)"
echo ""

# Iniciar servidor Django
log_info "Iniciando servidor Django na porta $PORT..."
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}║  Pressione Ctrl+C para parar o servidor                         ║${NC}"
echo -e "${BLUE}║  Acesse: http://127.0.0.1:$PORT                                 ║${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Executar servidor
python manage.py runserver 127.0.0.1:$PORT

# Cleanup quando o script terminar
echo ""
log_info "Servidor parado."
log_info "Para reiniciar: ./iniciar_projeto.sh"
echo ""
log_success "Obrigado por usar AllMedias PWA! 👋"