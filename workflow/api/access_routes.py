"""
Rotas da API para Controle de Acesso - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, List
import logging

from ..security.access_control import (
    AccessControl, UserRole, Permission, User, AccessLog
)

# Configuração do blueprint
access_bp = Blueprint('access', __name__, url_prefix='/api/access')

# Instância do controle de acesso
access_control = AccessControl()

@access_bp.route('/users', methods=['POST'])
def create_user():
    """
    Cria um novo usuário
    
    Body:
        user_id: str
        role: str (child, parent, admin, moderator)
        parent_id: str (opcional)
        child_id: str (opcional)
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'role' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id e role são obrigatórios'
            }), 400
            
        user_id = data['user_id']
        role_str = data['role']
        parent_id = data.get('parent_id')
        child_id = data.get('child_id')
        
        # Valida role
        try:
            role = UserRole(role_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Role inválido: {role_str}'
            }), 400
            
        # Cria usuário
        user = access_control.create_user(
            user_id=user_id,
            role=role,
            parent_id=parent_id,
            child_id=child_id
        )
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'role': user.role.value,
                'parent_id': user.parent_id,
                'child_id': user.child_id,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active,
                'permissions': [p.value for p in user.permissions]
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao criar usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id: str):
    """
    Obtém informações de um usuário
    """
    try:
        user = access_control._load_user(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
            
        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'role': user.role.value,
                'parent_id': user.parent_id,
                'child_id': user.child_id,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'permissions': [p.value for p in user.permissions]
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/users/<user_id>/permissions', methods=['GET'])
def get_user_permissions(user_id: str):
    """
    Obtém permissões de um usuário
    """
    try:
        permissions = access_control.get_user_permissions(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'permissions': [p.value for p in permissions]
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter permissões: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/users/<user_id>/permissions', methods=['POST'])
def grant_permission(user_id: str):
    """
    Concede permissão a um usuário
    
    Body:
        permission: str
    """
    try:
        data = request.get_json()
        
        if not data or 'permission' not in data:
            return jsonify({
                'success': False,
                'error': 'permission é obrigatório'
            }), 400
            
        permission_str = data['permission']
        
        # Valida permissão
        try:
            permission = Permission(permission_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Permissão inválida: {permission_str}'
            }), 400
            
        # Concede permissão
        success = access_control.grant_permission(user_id, permission)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
            
        return jsonify({
            'success': True,
            'message': f'Permissão {permission.value} concedida com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao conceder permissão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/users/<user_id>/permissions', methods=['DELETE'])
def revoke_permission(user_id: str):
    """
    Revoga permissão de um usuário
    
    Body:
        permission: str
    """
    try:
        data = request.get_json()
        
        if not data or 'permission' not in data:
            return jsonify({
                'success': False,
                'error': 'permission é obrigatório'
            }), 400
            
        permission_str = data['permission']
        
        # Valida permissão
        try:
            permission = Permission(permission_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Permissão inválida: {permission_str}'
            }), 400
            
        # Revoga permissão
        success = access_control.revoke_permission(user_id, permission)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
            
        return jsonify({
            'success': True,
            'message': f'Permissão {permission.value} revogada com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao revogar permissão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/users/<user_id>/deactivate', methods=['POST'])
def deactivate_user(user_id: str):
    """
    Desativa um usuário
    """
    try:
        success = access_control.deactivate_user(user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
            
        return jsonify({
            'success': True,
            'message': f'Usuário {user_id} desativado com sucesso'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao desativar usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/check', methods=['POST'])
def check_permission():
    """
    Verifica se usuário tem permissão
    
    Body:
        user_id: str
        permission: str
        resource_id: str (opcional)
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'permission' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id e permission são obrigatórios'
            }), 400
            
        user_id = data['user_id']
        permission_str = data['permission']
        resource_id = data.get('resource_id')
        
        # Valida permissão
        try:
            permission = Permission(permission_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Permissão inválida: {permission_str}'
            }), 400
            
        # Verifica permissão
        has_permission = access_control.check_permission(
            user_id=user_id,
            permission=permission,
            resource_id=resource_id
        )
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'permission': permission.value,
            'resource_id': resource_id,
            'has_permission': has_permission
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao verificar permissão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/logs', methods=['GET'])
def get_access_logs():
    """
    Obtém logs de acesso
    
    Query params:
        user_id: str (opcional)
        days: int (padrão: 30)
    """
    try:
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 30))
        
        logs = access_control.get_access_logs(
            user_id=user_id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'logs': [
                {
                    'log_id': log.log_id,
                    'user_id': log.user_id,
                    'action': log.action,
                    'resource': log.resource,
                    'timestamp': log.timestamp.isoformat(),
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'success': log.success,
                    'details': log.details
                }
                for log in logs
            ]
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'days deve ser um número inteiro'
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/roles', methods=['GET'])
def get_roles():
    """
    Obtém lista de roles disponíveis
    """
    try:
        roles = [
            {
                'role': role.value,
                'name': role.name,
                'permissions': [p.value for p in access_control.role_permissions.get(role, set())]
            }
            for role in UserRole
        ]
        
        return jsonify({
            'success': True,
            'roles': roles
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter roles: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@access_bp.route('/permissions', methods=['GET'])
def get_permissions():
    """
    Obtém lista de permissões disponíveis
    """
    try:
        permissions = [
            {
                'permission': permission.value,
                'name': permission.name,
                'description': _get_permission_description(permission)
            }
            for permission in Permission
        ]
        
        return jsonify({
            'success': True,
            'permissions': permissions
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter permissões: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

def _get_permission_description(permission: Permission) -> str:
    """Retorna descrição da permissão"""
    descriptions = {
        Permission.READ_OWN_DATA: "Ler dados próprios",
        Permission.WRITE_OWN_DATA: "Escrever dados próprios",
        Permission.READ_CHILD_DATA: "Ler dados da criança",
        Permission.WRITE_CHILD_DATA: "Escrever dados da criança",
        Permission.CREATE_TRANSACTION: "Criar transação",
        Permission.APPROVE_TRANSACTION: "Aprovar transação",
        Permission.VIEW_TRANSACTION_HISTORY: "Ver histórico de transações",
        Permission.MANAGE_CONSENT: "Gerenciar consentimento",
        Permission.VIEW_CONSENT_HISTORY: "Ver histórico de consentimento",
        Permission.MANAGE_USERS: "Gerenciar usuários",
        Permission.VIEW_LOGS: "Ver logs do sistema",
        Permission.MANAGE_SYSTEM: "Gerenciar sistema"
    }
    
    return descriptions.get(permission, "Sem descrição") 