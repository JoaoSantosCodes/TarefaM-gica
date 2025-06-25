#!/bin/bash
# Template de Backup e Rollback para TarefaMágica
# Ajuste os caminhos e comandos conforme seu ambiente

BACKUP_DIR="/caminho/para/backups"
APP_DIR="/caminho/para/app"
DATA_DIR="/caminho/para/dados"

# Backup automático
backup() {
    echo "[Backup] Iniciando backup do app e dados..."
    mkdir -p "$BACKUP_DIR"
    tar czf "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz" "$APP_DIR" "$DATA_DIR"
    echo "[Backup] Backup concluído em $BACKUP_DIR"
}

# Rollback para o backup mais recente
rollback() {
    echo "[Rollback] Procurando backup mais recente..."
    LAST_BACKUP=$(ls -t $BACKUP_DIR/backup_*.tar.gz | head -1)
    if [ -z "$LAST_BACKUP" ]; then
        echo "[Rollback] Nenhum backup encontrado!"
        exit 1
    fi
    echo "[Rollback] Restaurando backup: $LAST_BACKUP"
    tar xzf "$LAST_BACKUP" -C /
    echo "[Rollback] Rollback concluído."
}

case "$1" in
    backup)
        backup
        ;;
    rollback)
        rollback
        ;;
    *)
        echo "Uso: $0 {backup|rollback}"
        ;;
esac 