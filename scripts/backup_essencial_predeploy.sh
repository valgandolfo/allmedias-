#!/usr/bin/env bash
set -euo pipefail

# Backup essencial para pré-deploy:
# - .env (config local/sensível)
# - db.sqlite3 (dados locais)
# - media/ (uploads locais)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_NAME="backup_essencial_predeploy_${TIMESTAMP}.tar.gz"
TMP_DIR="$(mktemp -d)"
DRY_RUN="${1:-}"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$BACKUP_DIR"

echo "Iniciando backup essencial em: $ROOT_DIR"
echo "Destino: $BACKUP_DIR/$BACKUP_NAME"

copied_any=false

copy_item_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -e "$src" ]; then
    copied_any=true
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
    echo " - Incluido: ${src#$ROOT_DIR/}"
  else
    echo " - Nao encontrado (ignorado): ${src#$ROOT_DIR/}"
  fi
}

copy_item_if_exists "$ROOT_DIR/.env" "$TMP_DIR/.env"
copy_item_if_exists "$ROOT_DIR/db.sqlite3" "$TMP_DIR/db.sqlite3"
copy_item_if_exists "$ROOT_DIR/media" "$TMP_DIR/media"

if [ "$copied_any" = false ]; then
  echo "Nenhum item essencial encontrado. Backup nao criado."
  exit 1
fi

MANIFEST="$TMP_DIR/manifest_backup.txt"
{
  echo "Backup essencial pre-deploy"
  echo "Data: $(date -Iseconds)"
  echo "Projeto: $ROOT_DIR"
  echo
  echo "Conteudo:"
  [ -f "$TMP_DIR/.env" ] && echo "- .env"
  [ -f "$TMP_DIR/db.sqlite3" ] && echo "- db.sqlite3"
  [ -d "$TMP_DIR/media" ] && echo "- media/"
  echo
  echo "Tamanhos:"
  [ -f "$TMP_DIR/.env" ] && du -h "$TMP_DIR/.env" | awk '{print "- .env: "$1}'
  [ -f "$TMP_DIR/db.sqlite3" ] && du -h "$TMP_DIR/db.sqlite3" | awk '{print "- db.sqlite3: "$1}'
  [ -d "$TMP_DIR/media" ] && du -sh "$TMP_DIR/media" | awk '{print "- media/: "$1}'
} > "$MANIFEST"

if [ "$DRY_RUN" = "--dry-run" ]; then
  echo
  echo "Dry-run concluido. Nenhum arquivo .tar.gz foi gerado."
  echo "Itens elegiveis listados acima."
  exit 0
fi

tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$TMP_DIR" .
echo
echo "Backup criado com sucesso:"
echo "  $BACKUP_DIR/$BACKUP_NAME"
echo
echo "Para restaurar rapidamente:"
echo "  tar -xzf \"$BACKUP_DIR/$BACKUP_NAME\" -C \"$ROOT_DIR\""
