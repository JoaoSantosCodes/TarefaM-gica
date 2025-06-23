"""
Rotas da API para Sistema de Auditoria - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from ..security.audit_system import (
    AuditSystem, AuditEvent, AuditQuery, AuditCategory, AuditAction, AuditLevel
)

# Configuração do blueprint
audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

# Instância do sistema de auditoria
audit_system = AuditSystem()

@audit_bp.route('/events', methods=['GET'])
def get_audit_events():
    """
    Obtém eventos de auditoria
    
    Query params:
        start_date: str (ISO format)
        end_date: str (ISO format)
        user_id: str (opcional)
        category: str (opcional)
        action: str (opcional)
        level: str (opcional)
        success: bool (opcional)
        resource_id: str (opcional)
        ip_address: str (opcional)
        limit: int (padrão: 1000)
        offset: int (padrão: 0)
    """
    try:
        # Parâmetros de data
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            
        # Parâmetros de filtro
        user_id = request.args.get('user_id')
        category_str = request.args.get('category')
        action_str = request.args.get('action')
        level_str = request.args.get('level')
        success_str = request.args.get('success')
        resource_id = request.args.get('resource_id')
        ip_address = request.args.get('ip_address')
        
        # Parâmetros de paginação
        limit = int(request.args.get('limit', 1000))
        offset = int(request.args.get('offset', 0))
        
        # Converte strings para enums
        category = None
        if category_str:
            try:
                category = AuditCategory(category_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Categoria inválida: {category_str}'
                }), 400
                
        action = None
        if action_str:
            try:
                action = AuditAction(action_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Ação inválida: {action_str}'
                }), 400
                
        level = None
        if level_str:
            try:
                level = AuditLevel(level_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Nível inválido: {level_str}'
                }), 400
                
        success = None
        if success_str:
            success = success_str.lower() == 'true'
            
        # Cria query
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            category=category,
            action=action,
            level=level,
            success=success,
            resource_id=resource_id,
            ip_address=ip_address,
            limit=limit,
            offset=offset
        )
        
        # Executa consulta
        events = audit_system.query_events(query)
        
        return jsonify({
            'success': True,
            'events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'user_id': event.user_id,
                    'session_id': event.session_id,
                    'ip_address': event.ip_address,
                    'user_agent': event.user_agent,
                    'category': event.category.value,
                    'action': event.action.value,
                    'level': event.level.value,
                    'description': event.description,
                    'details': event.details,
                    'resource_id': event.resource_id,
                    'resource_type': event.resource_type,
                    'success': event.success,
                    'duration_ms': event.duration_ms,
                    'error_message': event.error_message
                }
                for event in events
            ],
            'total_count': len(events)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Parâmetro inválido: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter eventos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/reports', methods=['POST'])
def generate_audit_report():
    """
    Gera relatório de auditoria
    
    Body:
        start_date: str (ISO format)
        end_date: str (ISO format)
        report_type: str (summary, user_activity, security_events, financial_audit)
    """
    try:
        data = request.get_json()
        
        if not data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({
                'success': False,
                'error': 'start_date e end_date são obrigatórios'
            }), 400
            
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        report_type = data.get('report_type', 'summary')
        
        # Valida tipo de relatório
        valid_types = ['summary', 'user_activity', 'security_events', 'financial_audit']
        if report_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Tipo de relatório inválido: {report_type}'
            }), 400
            
        # Gera relatório
        report = audit_system.generate_audit_report(start_date, end_date, report_type)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Data inválida: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/categories', methods=['GET'])
def get_audit_categories():
    """
    Obtém categorias de auditoria disponíveis
    """
    try:
        categories = [
            {
                'value': category.value,
                'name': category.name,
                'description': _get_category_description(category)
            }
            for category in AuditCategory
        ]
        
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter categorias: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/actions', methods=['GET'])
def get_audit_actions():
    """
    Obtém ações de auditoria disponíveis
    """
    try:
        actions = [
            {
                'value': action.value,
                'name': action.name,
                'category': _get_action_category(action),
                'description': _get_action_description(action)
            }
            for action in AuditAction
        ]
        
        return jsonify({
            'success': True,
            'actions': actions
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter ações: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/levels', methods=['GET'])
def get_audit_levels():
    """
    Obtém níveis de auditoria disponíveis
    """
    try:
        levels = [
            {
                'value': level.value,
                'name': level.name,
                'description': _get_level_description(level)
            }
            for level in AuditLevel
        ]
        
        return jsonify({
            'success': True,
            'levels': levels
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter níveis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/statistics', methods=['GET'])
def get_audit_statistics():
    """
    Obtém estatísticas de auditoria
    
    Query params:
        days: int (padrão: 30)
    """
    try:
        days = int(request.args.get('days', 30))
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Gera relatório resumido
        report = audit_system.generate_audit_report(start_date, end_date, 'summary')
        
        return jsonify({
            'success': True,
            'statistics': report.get('statistics', {}),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/user-activity/<user_id>', methods=['GET'])
def get_user_activity(user_id: str):
    """
    Obtém atividade de um usuário específico
    
    Query params:
        days: int (padrão: 30)
    """
    try:
        days = int(request.args.get('days', 30))
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Cria query para usuário específico
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            limit=10000
        )
        
        events = audit_system.query_events(query)
        
        # Agrupa por categoria e ação
        activity_summary = {}
        for event in events:
            category = event.category.value
            action = event.action.value
            
            if category not in activity_summary:
                activity_summary[category] = {}
                
            if action not in activity_summary[category]:
                activity_summary[category][action] = {
                    'count': 0,
                    'successful': 0,
                    'failed': 0,
                    'last_occurrence': None
                }
                
            activity_summary[category][action]['count'] += 1
            if event.success:
                activity_summary[category][action]['successful'] += 1
            else:
                activity_summary[category][action]['failed'] += 1
                
            if not activity_summary[category][action]['last_occurrence'] or event.timestamp > activity_summary[category][action]['last_occurrence']:
                activity_summary[category][action]['last_occurrence'] = event.timestamp.isoformat()
                
        return jsonify({
            'success': True,
            'user_id': user_id,
            'activity_summary': activity_summary,
            'total_events': len(events),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter atividade do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/cleanup', methods=['POST'])
def cleanup_old_events():
    """
    Remove eventos antigos
    """
    try:
        removed_count = audit_system.cleanup_old_events()
        
        return jsonify({
            'success': True,
            'message': f'{removed_count} eventos antigos removidos',
            'removed_count': removed_count
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao limpar eventos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@audit_bp.route('/status', methods=['GET'])
def get_audit_status():
    """
    Obtém status do sistema de auditoria
    """
    try:
        # Obtém estatísticas dos últimos 24 horas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        
        query = AuditQuery(start_date=start_date, end_date=end_date, limit=10000)
        recent_events = audit_system.query_events(query)
        
        # Calcula estatísticas
        total_events = len(recent_events)
        error_events = len([e for e in recent_events if e.level in [AuditLevel.ERROR, AuditLevel.CRITICAL]])
        security_events = len([e for e in recent_events if e.category == AuditCategory.SECURITY])
        
        return jsonify({
            'success': True,
            'status': {
                'processor_active': audit_system.processor_active,
                'last_24h': {
                    'total_events': total_events,
                    'error_events': error_events,
                    'security_events': security_events
                },
                'last_check': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

def _get_category_description(category: AuditCategory) -> str:
    """Retorna descrição da categoria"""
    descriptions = {
        AuditCategory.AUTHENTICATION: "Eventos relacionados à autenticação de usuários",
        AuditCategory.AUTHORIZATION: "Eventos relacionados à autorização e permissões",
        AuditCategory.DATA_ACCESS: "Eventos relacionados ao acesso a dados",
        AuditCategory.FINANCIAL: "Eventos relacionados a transações financeiras",
        AuditCategory.CONSENT: "Eventos relacionados ao consentimento parental",
        AuditCategory.SECURITY: "Eventos relacionados à segurança do sistema",
        AuditCategory.SYSTEM: "Eventos relacionados ao sistema",
        AuditCategory.USER_MANAGEMENT: "Eventos relacionados ao gerenciamento de usuários",
        AuditCategory.CONFIGURATION: "Eventos relacionados à configuração do sistema"
    }
    return descriptions.get(category, "Sem descrição")

def _get_action_description(action: AuditAction) -> str:
    """Retorna descrição da ação"""
    descriptions = {
        AuditAction.LOGIN: "Login de usuário",
        AuditAction.LOGOUT: "Logout de usuário",
        AuditAction.LOGIN_FAILED: "Tentativa de login falhou",
        AuditAction.PASSWORD_CHANGE: "Alteração de senha",
        AuditAction.PASSWORD_RESET: "Reset de senha",
        AuditAction.TWO_FACTOR_ENABLE: "2FA habilitado",
        AuditAction.TWO_FACTOR_DISABLE: "2FA desabilitado",
        AuditAction.PERMISSION_GRANTED: "Permissão concedida",
        AuditAction.PERMISSION_REVOKED: "Permissão revogada",
        AuditAction.ROLE_CHANGED: "Role alterado",
        AuditAction.ACCESS_DENIED: "Acesso negado",
        AuditAction.DATA_READ: "Leitura de dados",
        AuditAction.DATA_WRITE: "Escrita de dados",
        AuditAction.DATA_DELETE: "Exclusão de dados",
        AuditAction.DATA_EXPORT: "Exportação de dados",
        AuditAction.DATA_IMPORT: "Importação de dados",
        AuditAction.TRANSACTION_CREATED: "Transação criada",
        AuditAction.TRANSACTION_APPROVED: "Transação aprovada",
        AuditAction.TRANSACTION_REJECTED: "Transação rejeitada",
        AuditAction.PAYMENT_PROCESSED: "Pagamento processado",
        AuditAction.CONSENT_GIVEN: "Consentimento dado",
        AuditAction.CONSENT_WITHDRAWN: "Consentimento retirado",
        AuditAction.CONSENT_UPDATED: "Consentimento atualizado",
        AuditAction.CONSENT_EXPIRED: "Consentimento expirado",
        AuditAction.SECURITY_ALERT: "Alerta de segurança",
        AuditAction.SUSPICIOUS_ACTIVITY: "Atividade suspeita",
        AuditAction.IP_BLOCKED: "IP bloqueado",
        AuditAction.RATE_LIMIT_EXCEEDED: "Limite de taxa excedido",
        AuditAction.SYSTEM_STARTUP: "Sistema iniciado",
        AuditAction.SYSTEM_SHUTDOWN: "Sistema desligado",
        AuditAction.CONFIGURATION_CHANGED: "Configuração alterada",
        AuditAction.BACKUP_CREATED: "Backup criado",
        AuditAction.BACKUP_RESTORED: "Backup restaurado",
        AuditAction.USER_CREATED: "Usuário criado",
        AuditAction.USER_UPDATED: "Usuário atualizado",
        AuditAction.USER_DELETED: "Usuário deletado",
        AuditAction.USER_ACTIVATED: "Usuário ativado",
        AuditAction.USER_DEACTIVATED: "Usuário desativado"
    }
    return descriptions.get(action, "Sem descrição")

def _get_action_category(action: AuditAction) -> str:
    """Retorna categoria da ação"""
    category_mapping = {
        # Autenticação
        AuditAction.LOGIN: AuditCategory.AUTHENTICATION,
        AuditAction.LOGOUT: AuditCategory.AUTHENTICATION,
        AuditAction.LOGIN_FAILED: AuditCategory.AUTHENTICATION,
        AuditAction.PASSWORD_CHANGE: AuditCategory.AUTHENTICATION,
        AuditAction.PASSWORD_RESET: AuditCategory.AUTHENTICATION,
        AuditAction.TWO_FACTOR_ENABLE: AuditCategory.AUTHENTICATION,
        AuditAction.TWO_FACTOR_DISABLE: AuditCategory.AUTHENTICATION,
        
        # Autorização
        AuditAction.PERMISSION_GRANTED: AuditCategory.AUTHORIZATION,
        AuditAction.PERMISSION_REVOKED: AuditCategory.AUTHORIZATION,
        AuditAction.ROLE_CHANGED: AuditCategory.AUTHORIZATION,
        AuditAction.ACCESS_DENIED: AuditCategory.AUTHORIZATION,
        
        # Acesso a dados
        AuditAction.DATA_READ: AuditCategory.DATA_ACCESS,
        AuditAction.DATA_WRITE: AuditCategory.DATA_ACCESS,
        AuditAction.DATA_DELETE: AuditCategory.DATA_ACCESS,
        AuditAction.DATA_EXPORT: AuditCategory.DATA_ACCESS,
        AuditAction.DATA_IMPORT: AuditCategory.DATA_ACCESS,
        
        # Financeiro
        AuditAction.TRANSACTION_CREATED: AuditCategory.FINANCIAL,
        AuditAction.TRANSACTION_APPROVED: AuditCategory.FINANCIAL,
        AuditAction.TRANSACTION_REJECTED: AuditCategory.FINANCIAL,
        AuditAction.PAYMENT_PROCESSED: AuditCategory.FINANCIAL,
        
        # Consentimento
        AuditAction.CONSENT_GIVEN: AuditCategory.CONSENT,
        AuditAction.CONSENT_WITHDRAWN: AuditCategory.CONSENT,
        AuditAction.CONSENT_UPDATED: AuditCategory.CONSENT,
        AuditAction.CONSENT_EXPIRED: AuditCategory.CONSENT,
        
        # Segurança
        AuditAction.SECURITY_ALERT: AuditCategory.SECURITY,
        AuditAction.SUSPICIOUS_ACTIVITY: AuditCategory.SECURITY,
        AuditAction.IP_BLOCKED: AuditCategory.SECURITY,
        AuditAction.RATE_LIMIT_EXCEEDED: AuditCategory.SECURITY,
        
        # Sistema
        AuditAction.SYSTEM_STARTUP: AuditCategory.SYSTEM,
        AuditAction.SYSTEM_SHUTDOWN: AuditCategory.SYSTEM,
        AuditAction.CONFIGURATION_CHANGED: AuditCategory.CONFIGURATION,
        AuditAction.BACKUP_CREATED: AuditCategory.SYSTEM,
        AuditAction.BACKUP_RESTORED: AuditCategory.SYSTEM,
        
        # Gerenciamento de usuários
        AuditAction.USER_CREATED: AuditCategory.USER_MANAGEMENT,
        AuditAction.USER_UPDATED: AuditCategory.USER_MANAGEMENT,
        AuditAction.USER_DELETED: AuditCategory.USER_MANAGEMENT,
        AuditAction.USER_ACTIVATED: AuditCategory.USER_MANAGEMENT,
        AuditAction.USER_DEACTIVATED: AuditCategory.USER_MANAGEMENT
    }
    
    category = category_mapping.get(action)
    return category.value if category else "unknown"

def _get_level_description(level: AuditLevel) -> str:
    """Retorna descrição do nível"""
    descriptions = {
        AuditLevel.DEBUG: "Informações de debug",
        AuditLevel.INFO: "Informações gerais",
        AuditLevel.WARNING: "Avisos",
        AuditLevel.ERROR: "Erros",
        AuditLevel.CRITICAL: "Eventos críticos"
    }
    return descriptions.get(level, "Sem descrição") 