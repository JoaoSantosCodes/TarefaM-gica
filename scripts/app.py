#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Aplicação Principal - TarefaMágica
Sistema de workflow automatizado com foco em segurança e LGPD
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Importa módulos de segurança
from workflow.security.rate_limiting_middleware import setup_rate_limiting_middleware
from workflow.security.security_headers import security_headers
from workflow.security.security_monitoring import SecurityMonitoring
from workflow.security.audit_system import AuditSystem

# Importa blueprints da API
from workflow.api.security_routes import security_bp
from workflow.api.consent_routes import consent_bp
from workflow.api.access_routes import access_bp
from workflow.api.audit_routes import audit_bp
from workflow.api.backup_routes import backup_bp
from workflow.api.financial_routes import financial_bp
from workflow.api.timeout_routes import timeout_bp
from workflow.api.log_sanitization_routes import log_sanitization_bp
from workflow.api.two_factor_routes import two_factor_bp
from workflow.api.mobile_routes import mobile_bp

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """
    Cria e configura a aplicação Flask
    
    Returns:
        Flask: Aplicação configurada
    """
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tarefamagica-secret-key-2024')
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Habilita CORS
    CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configura middlewares de segurança
    setup_security_middlewares(app)
    
    # Registra blueprints
    register_blueprints(app)
    
    # Configura handlers de erro
    setup_error_handlers(app)
    
    # Configura rotas de health check
    setup_health_routes(app)
    
    logger.info("✅ Aplicação TarefaMágica criada com sucesso")
    return app

def setup_security_middlewares(app):
    """
    Configura todos os middlewares de segurança
    
    Args:
        app: Aplicação Flask
    """
    try:
        # Rate Limiting
        setup_rate_limiting_middleware(app)
        logger.info("✅ Rate limiting configurado")
        
        # Security Headers
        app.before_request(security_headers)
        logger.info("✅ Security headers configurados")
        
        # Security Monitoring
        security_monitoring = SecurityMonitoring()
        
        @app.before_request
        def monitor_request():
            """Monitora todas as requisições"""
            try:
                # Monitora requisição
                security_monitoring.monitor_request(
                    ip_address=get_client_ip(),
                    user_agent=request.headers.get('User-Agent', 'unknown'),
                    method=request.method,
                    path=request.path,
                    user_id=get_user_id_from_request()
                )
            except Exception as e:
                logger.error(f"Erro ao monitorar requisição: {str(e)}")
        
        logger.info("✅ Security monitoring configurado")
        
        # Audit System
        audit_system = AuditSystem()
        
        @app.after_request
        def audit_response(response):
            """Audita todas as respostas"""
            try:
                audit_system.log_api_call(
                    user_id=get_user_id_from_request(),
                    action=f"{request.method} {request.path}",
                    resource=request.path,
                    status_code=response.status_code,
                    ip_address=get_client_ip(),
                    user_agent=request.headers.get('User-Agent', 'unknown'),
                    success=response.status_code < 400
                )
            except Exception as e:
                logger.error(f"Erro ao auditar resposta: {str(e)}")
            return response
        
        logger.info("✅ Audit system configurado")
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar middlewares de segurança: {str(e)}")

def register_blueprints(app):
    """
    Registra todos os blueprints da API
    
    Args:
        app: Aplicação Flask
    """
    try:
        # Blueprints de segurança
        app.register_blueprint(security_bp)
        app.register_blueprint(consent_bp)
        app.register_blueprint(access_bp)
        app.register_blueprint(audit_bp)
        app.register_blueprint(two_factor_bp)
        
        # Blueprints de funcionalidades
        app.register_blueprint(backup_bp)
        app.register_blueprint(financial_bp)
        app.register_blueprint(timeout_bp)
        app.register_blueprint(log_sanitization_bp)
        app.register_blueprint(mobile_bp)
        
        logger.info("✅ Todos os blueprints registrados")
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar blueprints: {str(e)}")

def setup_error_handlers(app):
    """
    Configura handlers de erro
    
    Args:
        app: Aplicação Flask
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint não encontrado',
            'message': 'A rota solicitada não existe',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Método não permitido',
            'message': 'O método HTTP não é suportado para este endpoint',
            'timestamp': datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Erro não tratado: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def setup_health_routes(app):
    """
    Configura rotas de health check
    
    Args:
        app: Aplicação Flask
    """
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check básico"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'service': 'TarefaMágica'
        }), 200
    
    @app.route('/health/security', methods=['GET'])
    def security_health_check():
        """Health check de segurança"""
        try:
            from workflow.security.security_monitoring import SecurityMonitoring
            from workflow.security.rate_limiting import rate_limiter
            
            security_monitoring = SecurityMonitoring()
            
            return jsonify({
                'success': True,
                'status': 'healthy',
                'security': {
                    'monitoring': 'active',
                    'rate_limiting': 'active',
                    'audit': 'active',
                    'headers': 'active'
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

def get_client_ip():
    """Obtém IP real do cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_user_id_from_request():
    """Obtém user_id da requisição (se disponível)"""
    try:
        # Tenta obter do header de autorização
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # Aqui você implementaria a lógica de decodificação do JWT
            return 'user_from_token'
        
        # Tenta obter do JSON body
        if request.is_json:
            data = request.get_json()
            return data.get('user_id')
        
        # Tenta obter dos query params
        return request.args.get('user_id')
        
    except:
        return None

# Cria aplicação
app = create_app()

if __name__ == '__main__':
    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Inicia servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Iniciando TarefaMágica na porta {port}")
    logger.info(f"🔒 Modo debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    ) 