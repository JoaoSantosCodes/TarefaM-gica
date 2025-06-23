# 🚀 Guia de Deploy - TarefaMágica

## 📋 Visão Geral

O TarefaMágica é um sistema automatizado de workflow com foco em segurança, consentimento parental e integração Android, seguindo as diretrizes da LGPD.

## 🏗️ Arquitetura

### Componentes Principais

```
TarefaMágica/
├── workflow/                 # Backend Python
│   ├── api/                 # Rotas da API REST
│   ├── security/            # Módulos de segurança
│   ├── backup/              # Sistema de backup
│   ├── financial/           # Integração PIX
│   └── config/              # Configurações
├── docs/                    # Documentação
├── checklists/              # Checklists de validação
├── tests/                   # Testes automatizados
└── deployment/              # Scripts de deploy
```

### Stack Tecnológica

- **Backend:** Python 3.11+ com Flask
- **Segurança:** Cryptography, PyOTP, JWT
- **Banco:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Monitoramento:** Logs estruturados + métricas
- **CI/CD:** GitHub Actions
- **Backup:** Sistema automático com retenção

## 🔧 Ambientes

### Desenvolvimento (Local)
- **URL:** http://localhost:5000
- **Banco:** SQLite
- **Logs:** Console + arquivo
- **Backup:** Local

### Staging
- **URL:** https://staging.tarefamagica.com
- **Banco:** PostgreSQL
- **Logs:** Centralizados
- **Backup:** Automático diário

### Produção
- **URL:** https://tarefamagica.com
- **Banco:** PostgreSQL (cluster)
- **Logs:** Centralizados + monitoramento
- **Backup:** Automático + redundância

## 🚀 Deploy Automatizado

### Pré-requisitos

```bash
# Dependências do sistema
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install postgresql postgresql-contrib
sudo apt install nginx certbot python3-certbot-nginx

# Dependências Python
pip install -r requirements.txt
```

### Variáveis de Ambiente

Crie arquivo `.env`:

```env
# Configurações da Aplicação
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost/tarefamagica

# Segurança
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key-32-chars

# PIX Integration
PIX_MERCHANT_ID=your-merchant-id
PIX_API_KEY=your-pix-api-key
PIX_ENVIRONMENT=production

# Backup
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=02:00

# Monitoramento
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

### Script de Deploy

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando deploy do TarefaMágica..."

# 1. Backup do ambiente atual
echo "📦 Criando backup..."
python workflow/backup/automated_backup.py

# 2. Pull das mudanças
echo "📥 Atualizando código..."
git pull origin main

# 3. Instalar dependências
echo "📦 Instalando dependências..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Executar migrações
echo "🗄️ Executando migrações..."
python -c "from workflow.database import init_db; init_db()"

# 5. Executar testes
echo "🧪 Executando testes..."
pytest tests/ --cov=workflow

# 6. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart tarefamagica
sudo systemctl restart nginx

# 7. Health check
echo "🏥 Verificando saúde..."
sleep 10
curl -f http://localhost:5000/health || exit 1

echo "✅ Deploy concluído com sucesso!"
```

### Rollback Automatizado

```bash
#!/bin/bash
# rollback.sh

set -e

echo "🔄 Iniciando rollback..."

# 1. Identificar versão anterior
PREVIOUS_VERSION=$(git log --oneline -2 | tail -1 | cut -d' ' -f1)

# 2. Restaurar código
echo "📥 Restaurando versão anterior..."
git reset --hard $PREVIOUS_VERSION

# 3. Restaurar backup se necessário
if [ "$1" = "--with-backup" ]; then
    echo "📦 Restaurando backup..."
    python workflow/backup/automated_backup.py --restore-latest
fi

# 4. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart tarefamagica

# 5. Health check
echo "🏥 Verificando saúde..."
sleep 10
curl -f http://localhost:5000/health || exit 1

echo "✅ Rollback concluído com sucesso!"
```

## 🔒 Configuração de Segurança

### SSL/TLS
```bash
# Gerar certificado SSL
sudo certbot --nginx -d tarefamagica.com -d www.tarefamagica.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall
```bash
# Configurar UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/tarefamagica
server {
    listen 80;
    server_name tarefamagica.com www.tarefamagica.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tarefamagica.com www.tarefamagica.com;

    ssl_certificate /etc/letsencrypt/live/tarefamagica.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tarefamagica.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoramento

### Health Check Endpoints
- `GET /health` - Status geral da aplicação
- `GET /api/backup/health` - Status do sistema de backup
- `GET /api/security/health` - Status dos módulos de segurança

### Logs
```bash
# Logs da aplicação
sudo journalctl -u tarefamagica -f

# Logs de backup
tail -f logs/backup.log

# Logs de segurança
tail -f logs/security.log
```

### Métricas
```bash
# Verificar métricas de backup
curl http://localhost:5000/api/backup/metrics

# Verificar alertas
curl http://localhost:5000/api/backup/alerts
```

## 🔄 CI/CD Pipeline

### Workflow GitHub Actions
O pipeline automatizado inclui:

1. **Segurança:** Análise com Bandit e Safety
2. **Testes:** Unitários e cobertura
3. **Qualidade:** Lint, formatação, type checking
4. **Validação:** Checklist de segurança
5. **Build:** Criação do pacote
6. **Deploy:** Staging (develop) e Produção (main)
7. **Notificações:** Sucesso/falha

### Triggers
- **Push para `main`:** Deploy automático para produção
- **Push para `develop`:** Deploy automático para staging
- **Pull Request:** Validação completa sem deploy

## 🚨 Incident Response

### Procedimento de Emergência

1. **Identificação**
   ```bash
   # Verificar logs
   sudo journalctl -u tarefamagica --since "10 minutes ago"
   
   # Verificar saúde
   curl -f http://localhost:5000/health
   ```

2. **Contenção**
   ```bash
   # Parar aplicação se necessário
   sudo systemctl stop tarefamagica
   
   # Ativar modo de manutenção
   echo "MAINTENANCE_MODE=true" >> .env
   ```

3. **Eradicação**
   ```bash
   # Executar rollback se necessário
   ./rollback.sh
   
   # Verificar integridade
   python workflow/security/data_integrity.py --verify-all
   ```

4. **Recuperação**
   ```bash
   # Reiniciar serviços
   sudo systemctl start tarefamagica
   
   # Verificar saúde
   curl -f http://localhost:5000/health
   ```

## 📋 Checklist de Deploy

### Pré-deploy
- [ ] Testes passando localmente
- [ ] Checklist de segurança validado
- [ ] Backup do ambiente atual
- [ ] Variáveis de ambiente configuradas
- [ ] Certificados SSL válidos

### Deploy
- [ ] Pipeline CI/CD executado com sucesso
- [ ] Migrações aplicadas
- [ ] Serviços reiniciados
- [ ] Health check passando
- [ ] Logs sem erros críticos

### Pós-deploy
- [ ] Funcionalidades críticas testadas
- [ ] Métricas de performance normais
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Equipe notificada

## 📞 Contatos de Emergência

- **DevOps:** [email@tarefamagica.com]
- **Segurança:** [security@tarefamagica.com]
- **Suporte:** [support@tarefamagica.com]

---

**📅 Última Atualização:** $(date)
**👤 Responsável:** DevOps Team
**🎯 Versão:** 1.0.0 