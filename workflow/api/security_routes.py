"""
Rotas da API para Monitoramento de Segurança - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import os
import json

from ..security.security_monitoring import (
    SecurityMonitoring, SecurityAlert, AlertLevel, AlertType
)
from ..security.rate_limiting import rate_limiter, RateLimitType
from ..security.security_headers import security_headers
from ..security.ssl_validation import ssl_validator
from ..security.input_validation import InputValidation

# Configuração do blueprint
security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# Instância do monitoramento de segurança
security_monitoring = SecurityMonitoring()

@security_bp.route('/monitor/login', methods=['POST'])
def monitor_login():
    """
    Monitora tentativa de login
    
    Body:
        user_id: str
        ip_address: str
        success: bool
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'ip_address' not in data or 'success' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id, ip_address e success são obrigatórios'
            }), 400
            
        user_id = data['user_id']
        ip_address = data['ip_address']
        success = data['success']
        
        # Monitora tentativa de login
        security_monitoring.monitor_login_attempt(user_id, ip_address, success)
        
        return jsonify({
            'success': True,
            'message': 'Tentativa de login monitorada com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao monitorar login: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/monitor/data-access', methods=['POST'])
def monitor_data_access():
    """
    Monitora acesso a dados
    
    Body:
        user_id: str
        resource: str
        action: str
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'resource' not in data or 'action' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id, resource e action são obrigatórios'
            }), 400
            
        user_id = data['user_id']
        resource = data['resource']
        action = data['action']
        
        # Monitora acesso a dados
        security_monitoring.monitor_data_access(user_id, resource, action)
        
        return jsonify({
            'success': True,
            'message': 'Acesso a dados monitorado com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao monitorar acesso a dados: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/monitor/financial', methods=['POST'])
def monitor_financial():
    """
    Monitora atividade financeira
    
    Body:
        user_id: str
        amount: float
        transaction_type: str
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'amount' not in data or 'transaction_type' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id, amount e transaction_type são obrigatórios'
            }), 400
            
        user_id = data['user_id']
        amount = float(data['amount'])
        transaction_type = data['transaction_type']
        
        # Monitora atividade financeira
        security_monitoring.monitor_financial_activity(user_id, amount, transaction_type)
        
        return jsonify({
            'success': True,
            'message': 'Atividade financeira monitorada com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao monitorar atividade financeira: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/dashboard', methods=['GET'])
def get_security_dashboard():
    """
    Obtém dados do dashboard de segurança
    
    Query params:
        days: int (padrão: 7)
    """
    try:
        days = int(request.args.get('days', 7))
        
        dashboard_data = security_monitoring.get_security_dashboard_data(days)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Obtém alertas de segurança
    
    Query params:
        level: str (opcional)
        resolved: bool (opcional)
        days: int (padrão: 30)
    """
    try:
        level = request.args.get('level')
        resolved = request.args.get('resolved')
        days = int(request.args.get('days', 30))
        
        # Filtra alertas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        alerts = security_monitoring._get_alerts_in_period(start_date, end_date)
        
        # Aplica filtros
        if level:
            alerts = [a for a in alerts if a.level.value == level]
            
        if resolved is not None:
            resolved_bool = resolved.lower() == 'true'
            alerts = [a for a in alerts if a.resolved == resolved_bool]
            
        return jsonify({
            'success': True,
            'alerts': [
                {
                    'alert_id': alert.alert_id,
                    'alert_type': alert.alert_type.value,
                    'level': alert.level.value,
                    'user_id': alert.user_id,
                    'ip_address': alert.ip_address,
                    'description': alert.description,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved,
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                    'resolved_by': alert.resolved_by,
                    'details': alert.details
                }
                for alert in alerts
            ]
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter alertas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id: str):
    """
    Marca alerta como resolvido
    
    Body:
        resolved_by: str
    """
    try:
        data = request.get_json()
        resolved_by = data.get('resolved_by', 'system') if data else 'system'
        
        # Busca alerta
        alerts_dir = security_monitoring.storage_path + "/alerts"
        alert_file = f"{alerts_dir}/{alert_id}.json"
        
        if not os.path.exists(alert_file):
            return jsonify({
                'success': False,
                'error': 'Alerta não encontrado'
            }), 404
            
        # Atualiza alerta
        with open(alert_file, 'r', encoding='utf-8') as f:
            alert_data = json.load(f)
            
        alert_data['resolved'] = True
        alert_data['resolved_at'] = datetime.utcnow().isoformat()
        alert_data['resolved_by'] = resolved_by
        
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, indent=2)
            
        return jsonify({
            'success': True,
            'message': f'Alerta {alert_id} marcado como resolvido'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao resolver alerta: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/blacklist', methods=['GET'])
def get_blacklist():
    """
    Obtém lista de IPs na blacklist
    """
    try:
        blacklist_file = security_monitoring.storage_path + "/blacklist/ips.json"
        
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
        else:
            blacklist = []
            
        return jsonify({
            'success': True,
            'blacklist': blacklist
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter blacklist: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/blacklist', methods=['POST'])
def add_to_blacklist():
    """
    Adiciona IP à blacklist
    
    Body:
        ip_address: str
    """
    try:
        data = request.get_json()
        
        if not data or 'ip_address' not in data:
            return jsonify({
                'success': False,
                'error': 'ip_address é obrigatório'
            }), 400
            
        ip_address = data['ip_address']
        
        # Adiciona à blacklist
        security_monitoring._add_to_blacklist(ip_address)
        
        return jsonify({
            'success': True,
            'message': f'IP {ip_address} adicionado à blacklist'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao adicionar IP à blacklist: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/blacklist/<ip_address>', methods=['DELETE'])
def remove_from_blacklist(ip_address: str):
    """
    Remove IP da blacklist
    """
    try:
        blacklist_file = security_monitoring.storage_path + "/blacklist/ips.json"
        
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
                
            if ip_address in blacklist:
                blacklist.remove(ip_address)
                
                with open(blacklist_file, 'w', encoding='utf-8') as f:
                    json.dump(blacklist, f, indent=2)
                    
                return jsonify({
                    'success': True,
                    'message': f'IP {ip_address} removido da blacklist'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'IP não encontrado na blacklist'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Blacklist não encontrada'
            }), 404
            
    except Exception as e:
        logging.error(f"Erro ao remover IP da blacklist: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Obtém métricas de segurança
    
    Query params:
        metric_name: str (opcional)
        days: int (padrão: 7)
    """
    try:
        metric_name = request.args.get('metric_name')
        days = int(request.args.get('days', 7))
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        metrics = security_monitoring._get_metrics_in_period(start_date, end_date)
        
        # Filtra por nome da métrica se especificado
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
            
        return jsonify({
            'success': True,
            'metrics': [
                {
                    'metric_id': metric.metric_id,
                    'metric_name': metric.metric_name,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'user_id': metric.user_id,
                    'context': metric.context
                }
                for metric in metrics
            ]
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/status', methods=['GET'])
def get_security_status():
    """
    Obtém status do sistema de segurança
    """
    try:
        # Obtém estatísticas dos últimos 24 horas
        dashboard_data = security_monitoring.get_security_dashboard_data(1)
        stats = dashboard_data.get('statistics', {})
        
        # Determina status geral
        if stats.get('critical_alerts', 0) > 0:
            status = 'critical'
        elif stats.get('high_alerts', 0) > 5:
            status = 'warning'
        elif stats.get('unresolved_alerts', 0) > 10:
            status = 'attention'
        else:
            status = 'normal'
            
        return jsonify({
            'success': True,
            'status': {
                'overall': status,
                'monitoring_active': security_monitoring.monitoring_active,
                'last_check': datetime.utcnow().isoformat(),
                'statistics': stats
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/rate-limit/check', methods=['POST'])
def check_rate_limit():
    """
    Verifica rate limit para uma ação
    
    Body:
        identifier: str
        limit_type: str
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados obrigatórios não fornecidos'
            }), 400
            
        # Validação dos campos obrigatórios
        required_fields = ['identifier', 'limit_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Sanitização dos dados
        identifier = InputValidation.sanitize_string(data['identifier'], max_length=200)
        limit_type_str = InputValidation.sanitize_string(data['limit_type'], max_length=50)
        
        # Validação do tipo de limite
        try:
            limit_type = RateLimitType(limit_type_str)
        except ValueError:
            allowed_types = [lt.value for lt in RateLimitType]
            return jsonify({
                'success': False,
                'error': f'Tipo de limite inválido. Tipos permitidos: {", ".join(allowed_types)}'
            }), 400
        
        # Verifica rate limit
        allowed, message = rate_limiter.check_rate_limit(identifier, limit_type)
        
        return jsonify({
            'success': True,
            'allowed': allowed,
            'message': message,
            'identifier': identifier,
            'limit_type': limit_type.value
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao verificar rate limit: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/rate-limit/status/<identifier>/<limit_type>', methods=['GET'])
def get_rate_limit_status(identifier: str, limit_type: str):
    """
    Obtém status do rate limit para um identificador
    
    Args:
        identifier: Identificador único
        limit_type: Tipo de limite
    """
    try:
        # Sanitização dos parâmetros
        identifier = InputValidation.sanitize_string(identifier, max_length=200)
        limit_type_str = InputValidation.sanitize_string(limit_type, max_length=50)
        
        # Validação do tipo de limite
        try:
            limit_type_enum = RateLimitType(limit_type_str)
        except ValueError:
            allowed_types = [lt.value for lt in RateLimitType]
            return jsonify({
                'success': False,
                'error': f'Tipo de limite inválido. Tipos permitidos: {", ".join(allowed_types)}'
            }), 400
        
        # Obtém status
        status = rate_limiter.get_status(identifier, limit_type_enum)
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter status do rate limit: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/rate-limit/reset', methods=['POST'])
def reset_rate_limit():
    """
    Reseta rate limit para um identificador
    
    Body:
        identifier: str
        limit_type: str (opcional)
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'identifier' not in data:
            return jsonify({
                'success': False,
                'error': 'identifier é obrigatório'
            }), 400
        
        # Sanitização dos dados
        identifier = InputValidation.sanitize_string(data['identifier'], max_length=200)
        limit_type_str = InputValidation.sanitize_string(data.get('limit_type', ''), max_length=50)
        
        # Validação do tipo de limite (se fornecido)
        limit_type = None
        if limit_type_str:
            try:
                limit_type = RateLimitType(limit_type_str)
            except ValueError:
                allowed_types = [lt.value for lt in RateLimitType]
                return jsonify({
                    'success': False,
                    'error': f'Tipo de limite inválido. Tipos permitidos: {", ".join(allowed_types)}'
                }), 400
        
        # Reseta rate limit
        rate_limiter.reset_limits(identifier, limit_type)
        
        return jsonify({
            'success': True,
            'message': f'Rate limit resetado para {identifier}',
            'identifier': identifier,
            'limit_type': limit_type.value if limit_type else 'all'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao resetar rate limit: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/rate-limit/statistics', methods=['GET'])
def get_rate_limit_statistics():
    """
    Obtém estatísticas do sistema de rate limiting
    """
    try:
        statistics = rate_limiter.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/ssl/validate', methods=['POST'])
def validate_ssl_certificate():
    """
    Valida certificado SSL de um hostname
    
    Body:
        hostname: str
        port: int (opcional, padrão: 443)
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'hostname' not in data:
            return jsonify({
                'success': False,
                'error': 'hostname é obrigatório'
            }), 400
        
        # Sanitização dos dados
        hostname = InputValidation.sanitize_string(data['hostname'], max_length=255)
        port = InputValidation.sanitize_int(data.get('port', 443), min_value=1, max_value=65535)
        
        # Valida certificado
        cert_info = ssl_validator.get_certificate_info(hostname, port)
        
        return jsonify({
            'success': True,
            'certificate': cert_info
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao validar certificado SSL: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/ssl/health', methods=['GET'])
def check_ssl_health():
    """
    Verifica saúde dos certificados SSL dos domínios confiáveis
    """
    try:
        health_report = ssl_validator.check_certificate_health()
        
        return jsonify({
            'success': True,
            'health_report': health_report
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao verificar saúde SSL: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/ssl/secure-request', methods=['POST'])
def make_secure_request():
    """
    Faz requisição HTTP segura com validação SSL
    
    Body:
        url: str
        method: str (opcional, padrão: GET)
        headers: dict (opcional)
        data: dict (opcional)
        timeout: int (opcional, padrão: 30)
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'url é obrigatória'
            }), 400
        
        # Sanitização dos dados
        url = InputValidation.sanitize_string(data['url'], max_length=2000)
        method = InputValidation.sanitize_string(data.get('method', 'GET'), max_length=10).upper()
        timeout = InputValidation.sanitize_int(data.get('timeout', 30), min_value=1, max_value=300)
        
        # Validação do método HTTP
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method not in allowed_methods:
            return jsonify({
                'success': False,
                'error': f'Método HTTP inválido. Métodos permitidos: {", ".join(allowed_methods)}'
            }), 400
        
        # Sanitização dos headers (se fornecidos)
        headers = None
        if 'headers' in data and isinstance(data['headers'], dict):
            headers = {}
            for key, value in data['headers'].items():
                sanitized_key = InputValidation.sanitize_string(key, max_length=100)
                sanitized_value = InputValidation.sanitize_string(str(value), max_length=1000)
                headers[sanitized_key] = sanitized_value
        
        # Sanitização dos dados (se fornecidos)
        request_data = None
        if 'data' in data and isinstance(data['data'], dict):
            request_data = {}
            for key, value in data['data'].items():
                sanitized_key = InputValidation.sanitize_string(key, max_length=100)
                if isinstance(value, (str, int, float, bool)):
                    request_data[sanitized_key] = value
                else:
                    request_data[sanitized_key] = InputValidation.sanitize_string(str(value), max_length=1000)
        
        # Faz requisição segura
        success, response, errors = ssl_validator.make_secure_request(
            url=url,
            method=method,
            headers=headers,
            data=request_data,
            timeout=timeout
        )
        
        if success and response:
            return jsonify({
                'success': True,
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content': response.text[:1000] if response.text else None,
                    'url': response.url
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Falha na requisição segura',
                'errors': errors
            }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao fazer requisição segura: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/ssl/validate-webhook', methods=['POST'])
def validate_webhook_url():
    """
    Valida URL de webhook para uso seguro
    
    Body:
        url: str
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'url é obrigatória'
            }), 400
        
        # Sanitização dos dados
        url = InputValidation.sanitize_string(data['url'], max_length=2000)
        
        # Valida webhook
        is_valid, errors = ssl_validator.validate_webhook_url(url)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'errors': errors,
            'url': url
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao validar webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/headers/report', methods=['GET'])
def get_security_headers_report():
    """
    Obtém relatório de headers de segurança
    """
    try:
        report = security_headers.get_security_report()
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter relatório de headers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@security_bp.route('/headers/test', methods=['GET'])
def test_security_headers():
    """
    Endpoint de teste para verificar headers de segurança
    """
    try:
        response = jsonify({
            'success': True,
            'message': 'Headers de segurança aplicados com sucesso',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Aplica headers de segurança
        response = security_headers.add_security_headers(response)
        response = security_headers.add_cache_headers(response, 'no-cache')
        
        return response, 200
        
    except Exception as e:
        logging.error(f"Erro ao testar headers de segurança: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500 