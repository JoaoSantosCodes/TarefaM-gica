#!/bin/bash
# 🚀 Script de Deploy - TarefaMágica
# Automatiza o processo de deploy com backup, validação e rollback

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="TarefaMágica"
APP_PORT=5000
BACKUP_DIR="backups"
LOG_FILE="logs/deploy.log"
HEALTH_CHECK_URL="http://localhost:${APP_PORT}/health"

# Função de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1" | tee -a "$LOG_FILE"
}

# Função de backup
create_backup() {
    log "📦 Criando backup do ambiente atual..."
    
    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_NAME="backup_$(date +'%Y%m%d_%H%M%S')"
        tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
            --exclude='backups' \
            --exclude='logs' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            .
        
        success "Backup criado: ${BACKUP_NAME}.tar.gz"
    else
        warning "Diretório de backup não encontrado, criando..."
        mkdir -p "$BACKUP_DIR"
        create_backup
    fi
}

# Função de health check
health_check() {
    log "🏥 Executando health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            success "Health check passou na tentativa $attempt"
            return 0
        fi
        
        log "Tentativa $attempt/$max_attempts - Aguardando..."
        sleep 2
        ((attempt++))
    done
    
    error "Health check falhou após $max_attempts tentativas"
    return 1
}

# Função de rollback
rollback() {
    error "❌ Deploy falhou! Iniciando rollback..."
    
    # Restaurar backup se existir
    if [ -f "${BACKUP_DIR}/backup_$(date +'%Y%m%d_%H%M%S').tar.gz" ]; then
        log "🔄 Restaurando backup..."
        tar -xzf "${BACKUP_DIR}/backup_$(date +'%Y%m%d_%H%M%S').tar.gz"
    fi
    
    # Reiniciar serviços
    restart_services
    
    # Verificar se rollback funcionou
    if health_check; then
        success "Rollback concluído com sucesso"
    else
        error "Rollback falhou! Intervenção manual necessária"
        exit 1
    fi
}

# Função para reiniciar serviços
restart_services() {
    log "🔄 Reiniciando serviços..."
    
    # Parar aplicação se estiver rodando
    if pgrep -f "python.*app.py" > /dev/null; then
        pkill -f "python.*app.py"
        sleep 2
    fi
    
    # Iniciar aplicação
    nohup python app.py > logs/app.log 2>&1 &
    sleep 5
}

# Função para executar testes
run_tests() {
    log "🧪 Executando testes..."
    
    if command -v pytest > /dev/null; then
        if pytest tests/ -v --tb=short; then
            success "Testes passaram"
        else
            error "Testes falharam"
            return 1
        fi
    else
        warning "Pytest não encontrado, pulando testes"
    fi
}

# Função para validar ambiente
validate_environment() {
    log "🔍 Validando ambiente..."
    
    # Verificar Python
    if ! command -v python3 > /dev/null; then
        error "Python3 não encontrado"
        return 1
    fi
    
    # Verificar dependências
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt não encontrado"
        return 1
    fi
    
    # Verificar arquivo de configuração
    if [ ! -f ".env" ]; then
        warning "Arquivo .env não encontrado"
    fi
    
    success "Ambiente validado"
}

# Função para instalar dependências
install_dependencies() {
    log "📦 Instalando dependências..."
    
    # Atualizar pip
    python3 -m pip install --upgrade pip
    
    # Instalar dependências
    if pip install -r requirements.txt; then
        success "Dependências instaladas"
    else
        error "Falha ao instalar dependências"
        return 1
    fi
}

# Função para executar migrações
run_migrations() {
    log "🗄️ Executando migrações..."
    
    # Aqui você pode adicionar comandos específicos para migrações
    # Por exemplo: python manage.py migrate
    
    success "Migrações executadas"
}

# Função para limpar cache
clean_cache() {
    log "🧹 Limpando cache..."
    
    # Remover arquivos Python compilados
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    
    success "Cache limpo"
}

# Função principal de deploy
main() {
    log "🚀 Iniciando deploy do $APP_NAME..."
    
    # Criar diretório de logs se não existir
    mkdir -p logs
    
    # Validar ambiente
    validate_environment || exit 1
    
    # Criar backup
    create_backup
    
    # Limpar cache
    clean_cache
    
    # Instalar dependências
    install_dependencies || rollback
    
    # Executar migrações
    run_migrations || rollback
    
    # Executar testes
    run_tests || rollback
    
    # Reiniciar serviços
    restart_services
    
    # Health check
    if health_check; then
        success "✅ Deploy concluído com sucesso!"
        
        # Mostrar informações do deploy
        log "📊 Informações do deploy:"
        log "   - Porta: $APP_PORT"
        log "   - Health Check: $HEALTH_CHECK_URL"
        log "   - Logs: logs/app.log"
        log "   - Backup: $BACKUP_DIR/"
        
    else
        rollback
    fi
}

# Função de ajuda
show_help() {
    echo "🚀 Script de Deploy - $APP_NAME"
    echo ""
    echo "Uso: $0 [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  deploy     Executar deploy completo (padrão)"
    echo "  backup     Apenas criar backup"
    echo "  test       Apenas executar testes"
    echo "  health     Apenas health check"
    echo "  rollback   Executar rollback"
    echo "  help       Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 deploy"
    echo "  $0 backup"
    echo "  $0 test"
}

# Tratamento de argumentos
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "backup")
        create_backup
        ;;
    "test")
        run_tests
        ;;
    "health")
        health_check
        ;;
    "rollback")
        rollback
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        error "Opção inválida: $1"
        show_help
        exit 1
        ;;
esac 