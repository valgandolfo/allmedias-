#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS_FILE="$ROOT_DIR/pro_newmedia/settings.py"
REQUIREMENTS_FILE="$ROOT_DIR/requirements.txt"
ENV_FILE="$ROOT_DIR/.env"

ok_count=0
warn_count=0
fail_count=0

ok() {
  ok_count=$((ok_count + 1))
  echo "[OK] $1"
}

warn() {
  warn_count=$((warn_count + 1))
  echo "[AVISO] $1"
}

fail() {
  fail_count=$((fail_count + 1))
  echo "[FALTA] $1"
}

has_in_file() {
  local pattern="$1"
  local file="$2"
  grep -Eq "$pattern" "$file"
}

echo "Verificacao pre-deploy Railway"
echo "Projeto: $ROOT_DIR"
echo

# Arquivos basicos
[ -f "$ROOT_DIR/manage.py" ] && ok "manage.py encontrado" || fail "manage.py nao encontrado"
[ -f "$SETTINGS_FILE" ] && ok "settings.py encontrado" || fail "pro_newmedia/settings.py nao encontrado"
[ -f "$REQUIREMENTS_FILE" ] && ok "requirements.txt encontrado" || fail "requirements.txt nao encontrado"
[ -f "$ENV_FILE" ] && ok ".env encontrado (uso local)" || warn ".env nao encontrado"

# Dependencias recomendadas para Railway/Django
if [ -f "$REQUIREMENTS_FILE" ]; then
  has_in_file "^[[:space:]]*gunicorn([<>=].*)?$" "$REQUIREMENTS_FILE" \
    && ok "gunicorn presente em requirements.txt" \
    || fail "gunicorn ausente em requirements.txt (necessario para subir web service)"

  has_in_file "whitenoise" "$REQUIREMENTS_FILE" \
    && ok "whitenoise presente em requirements.txt" \
    || warn "whitenoise ausente (recomendado para servir static em producao)"
fi

# Middleware static em producao
if [ -f "$SETTINGS_FILE" ]; then
  has_in_file "WhiteNoiseMiddleware" "$SETTINGS_FILE" \
    && ok "WhiteNoiseMiddleware configurado" \
    || warn "WhiteNoiseMiddleware nao encontrado no MIDDLEWARE"

  has_in_file "CSRF_TRUSTED_ORIGINS" "$SETTINGS_FILE" \
    && ok "CSRF_TRUSTED_ORIGINS configurado" \
    || warn "CSRF_TRUSTED_ORIGINS nao configurado em settings.py"

  # Seu parser atual de DATABASE_URL cobre mysql/mysql2, nao postgres
  if has_in_file "\"mysql\"" "$SETTINGS_FILE" && ! has_in_file "postgres|postgresql|psql" "$SETTINGS_FILE"; then
    warn "Parser de DATABASE_URL no settings parece aceitar apenas MySQL; Railway comum usa PostgreSQL"
  fi
fi

# Variaveis de ambiente minimas
if [ -f "$ENV_FILE" ]; then
  has_in_file "^DJANGO_SECRET_KEY=" "$ENV_FILE" && ok "DJANGO_SECRET_KEY definido no .env" || fail "DJANGO_SECRET_KEY ausente no .env"
  has_in_file "^DJANGO_DEBUG=" "$ENV_FILE" && ok "DJANGO_DEBUG definido no .env" || warn "DJANGO_DEBUG ausente no .env"
  has_in_file "^DJANGO_ALLOWED_HOSTS=" "$ENV_FILE" && ok "DJANGO_ALLOWED_HOSTS definido no .env" || fail "DJANGO_ALLOWED_HOSTS ausente no .env"
  has_in_file "^DATABASE_URL=" "$ENV_FILE" && ok "DATABASE_URL definido no .env" || fail "DATABASE_URL ausente no .env"
fi

echo
echo "Resumo:"
echo "  OK: $ok_count"
echo "  Avisos: $warn_count"
echo "  Faltas: $fail_count"
echo

if [ "$fail_count" -gt 0 ]; then
  echo "Status: REPROVADO (ha itens obrigatorios faltando)"
  exit 1
fi

if [ "$warn_count" -gt 0 ]; then
  echo "Status: APROVADO COM ALERTAS"
  exit 0
fi

echo "Status: PRONTO PARA DEPLOY"
