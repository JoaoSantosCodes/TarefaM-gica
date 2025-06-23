"""
Rotas da API para Configuração de Timeout - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import uuid

from ..security.timeout_config import timeout_manager, TimeoutType, TimeoutLevel, TimeoutConfig
from ..security.input_validation import InputValidation

# Configuração do blueprint
timeout_bp = Blueprint('timeout', __name__, url_prefix='/api/timeout')

@timeout_bp.route('/session/create', methods=['POST'])
def create_session():
    """
    Cria uma nova sessão com timeout
    
    Body:
        user_id: str - ID do usuário
        timeout_type: str - Tipo de timeout (session, connection, request, etc.)
        level: str (opcional) - Nível de timeout (short, medium, long)
        metadata: dict (opcional) - Metadados adicionais
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'user_id' not in data or 'timeout_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Campos user_id e timeout_type são obrigatórios'
            }), 400
        
        # Sanitização dos dados
        user_id = InputValidation.sanitize_string(data['user_id'], max_length=100)
        timeout_type_str = InputValidation.sanitize_string(data['timeout_type'], max_length=50)
        level_str = InputValidation.sanitize_string(data.get('level', 'medium'), max_length=20)
        metadata = data.get('metadata', {})
        
        # Validação do tipo de timeout
        try:
            timeout_type = TimeoutType(timeout_type_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Tipo de timeout inválido. Tipos válidos: {", ".join([t.value for t in TimeoutType])}'
            }), 400
        
        # Validação do nível
        try:
            level = TimeoutLevel(level_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Nível de timeout inválido. Níveis válidos: {", ".join([l.value for l in TimeoutLevel])}'
            }), 400
        
        # Gera ID único da sessão
        session_id = str(uuid.uuid4())
        
        # Cria sessão
        session = timeout_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            timeout_type=timeout_type,
            level=level,
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'timeout_type': session.timeout_type.value,
                'level': session.level.value,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'extensions_used': session.extensions_used,
                'max_extensions': session.max_extensions,
                'auto_extend': session.auto_extend,
                'metadata': session.metadata
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao criar sessão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """
    Obtém informações de uma sessão
    
    Args:
        session_id: ID da sessão
    """
    try:
        # Sanitização do ID da sessão
        session_id = InputValidation.sanitize_string(session_id, max_length=100)
        
        # Obtém sessão
        session = timeout_manager.get_session(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada ou expirada'
            }), 404
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'timeout_type': session.timeout_type.value,
                'level': session.level.value,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'extensions_used': session.extensions_used,
                'max_extensions': session.max_extensions,
                'auto_extend': session.auto_extend,
                'metadata': session.metadata,
                'time_remaining': int((session.expires_at - datetime.utcnow()).total_seconds())
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter sessão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/session/<session_id>/extend', methods=['POST'])
def extend_session(session_id: str):
    """
    Estende uma sessão
    
    Args:
        session_id: ID da sessão
        
    Body:
        duration_seconds: int (opcional) - Duração adicional em segundos
    """
    try:
        data = request.get_json() or {}
        
        # Sanitização dos dados
        session_id = InputValidation.sanitize_string(session_id, max_length=100)
        duration_seconds = InputValidation.validate_integer(data.get('duration_seconds'), min_value=1, max_value=86400)
        
        # Estende sessão
        success = timeout_manager.extend_session(session_id, duration_seconds)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Não foi possível estender a sessão'
            }), 400
        
        # Obtém sessão atualizada
        session = timeout_manager.get_session(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Sessão estendida com sucesso',
            'session': {
                'session_id': session.session_id,
                'expires_at': session.expires_at.isoformat(),
                'extensions_used': session.extensions_used,
                'max_extensions': session.max_extensions,
                'time_remaining': int((session.expires_at - datetime.utcnow()).total_seconds())
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao estender sessão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/session/<session_id>/activity', methods=['POST'])
def update_activity(session_id: str):
    """
    Atualiza atividade de uma sessão
    
    Args:
        session_id: ID da sessão
    """
    try:
        # Sanitização do ID da sessão
        session_id = InputValidation.sanitize_string(session_id, max_length=100)
        
        # Atualiza atividade
        success = timeout_manager.update_activity(session_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Atividade atualizada com sucesso'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao atualizar atividade: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/session/<session_id>', methods=['DELETE'])
def remove_session(session_id: str):
    """
    Remove uma sessão
    
    Args:
        session_id: ID da sessão
    """
    try:
        # Sanitização do ID da sessão
        session_id = InputValidation.sanitize_string(session_id, max_length=100)
        
        # Remove sessão
        success = timeout_manager.remove_session(session_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Sessão removida com sucesso'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao remover sessão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/user/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id: str):
    """
    Obtém todas as sessões de um usuário
    
    Args:
        user_id: ID do usuário
    """
    try:
        # Sanitização do ID do usuário
        user_id = InputValidation.sanitize_string(user_id, max_length=100)
        
        # Obtém sessões do usuário
        sessions = timeout_manager.get_user_sessions(user_id)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'timeout_type': session.timeout_type.value,
                'level': session.level.value,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'extensions_used': session.extensions_used,
                'max_extensions': session.max_extensions,
                'auto_extend': session.auto_extend,
                'time_remaining': int((session.expires_at - datetime.utcnow()).total_seconds())
            })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter sessões do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/type/<timeout_type>/sessions', methods=['GET'])
def get_sessions_by_type(timeout_type: str):
    """
    Obtém sessões por tipo
    
    Args:
        timeout_type: Tipo de timeout
    """
    try:
        # Sanitização do tipo de timeout
        timeout_type_str = InputValidation.sanitize_string(timeout_type, max_length=50)
        
        # Validação do tipo
        try:
            timeout_type_enum = TimeoutType(timeout_type_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Tipo de timeout inválido. Tipos válidos: {", ".join([t.value for t in TimeoutType])}'
            }), 400
        
        # Obtém sessões por tipo
        sessions = timeout_manager.get_sessions_by_type(timeout_type_enum)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'user_id': session.user_id,
                'level': session.level.value,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'extensions_used': session.extensions_used,
                'max_extensions': session.max_extensions,
                'time_remaining': int((session.expires_at - datetime.utcnow()).total_seconds())
            })
        
        return jsonify({
            'success': True,
            'timeout_type': timeout_type_str,
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter sessões por tipo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/config', methods=['GET'])
def get_configs():
    """
    Obtém todas as configurações de timeout
    """
    try:
        configs = timeout_manager.get_all_configs()
        
        configs_data = {}
        for timeout_type, levels in configs.items():
            configs_data[timeout_type.value] = {}
            for level, config in levels.items():
                configs_data[timeout_type.value][level.value] = {
                    'duration_seconds': config.duration_seconds,
                    'description': config.description,
                    'auto_extend': config.auto_extend,
                    'max_extensions': config.max_extensions,
                    'warning_before_expiry': config.warning_before_expiry,
                    'cleanup_interval': config.cleanup_interval
                }
        
        return jsonify({
            'success': True,
            'configurations': configs_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter configurações: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/config', methods=['POST'])
def update_config():
    """
    Atualiza configuração de timeout
    
    Body:
        timeout_type: str - Tipo de timeout
        level: str - Nível de timeout
        duration_seconds: int - Duração em segundos
        description: str - Descrição
        auto_extend: bool (opcional) - Auto-extensão
        max_extensions: int (opcional) - Máximo de extensões
        warning_before_expiry: int (opcional) - Aviso antes da expiração
        cleanup_interval: int (opcional) - Intervalo de limpeza
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        required_fields = ['timeout_type', 'level', 'duration_seconds', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Sanitização dos dados
        timeout_type_str = InputValidation.sanitize_string(data['timeout_type'], max_length=50)
        level_str = InputValidation.sanitize_string(data['level'], max_length=20)
        duration_seconds = InputValidation.validate_integer(data['duration_seconds'], min_value=1, max_value=86400)
        description = InputValidation.sanitize_string(data['description'], max_length=500)
        auto_extend = InputValidation.validate_boolean(data.get('auto_extend', False))
        max_extensions = InputValidation.validate_integer(data.get('max_extensions', 0), min_value=0, max_value=100)
        warning_before_expiry = InputValidation.validate_integer(data.get('warning_before_expiry', 300), min_value=0, max_value=3600)
        cleanup_interval = InputValidation.validate_integer(data.get('cleanup_interval', 3600), min_value=60, max_value=86400)
        
        # Validação do tipo
        try:
            timeout_type = TimeoutType(timeout_type_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Tipo de timeout inválido. Tipos válidos: {", ".join([t.value for t in TimeoutType])}'
            }), 400
        
        # Validação do nível
        try:
            level = TimeoutLevel(level_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Nível de timeout inválido. Níveis válidos: {", ".join([l.value for l in TimeoutLevel])}'
            }), 400
        
        # Cria nova configuração
        config = TimeoutConfig(
            timeout_type=timeout_type,
            level=level,
            duration_seconds=duration_seconds,
            description=description,
            auto_extend=auto_extend,
            max_extensions=max_extensions,
            warning_before_expiry=warning_before_expiry,
            cleanup_interval=cleanup_interval
        )
        
        # Atualiza configuração
        timeout_manager.update_config(timeout_type, level, config)
        
        return jsonify({
            'success': True,
            'message': f'Configuração {timeout_type.value}.{level.value} atualizada com sucesso',
            'config': {
                'timeout_type': config.timeout_type.value,
                'level': config.level.value,
                'duration_seconds': config.duration_seconds,
                'description': config.description,
                'auto_extend': config.auto_extend,
                'max_extensions': config.max_extensions,
                'warning_before_expiry': config.warning_before_expiry,
                'cleanup_interval': config.cleanup_interval
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao atualizar configuração: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/cleanup', methods=['POST'])
def cleanup_sessions():
    """
    Remove sessões expiradas manualmente
    """
    try:
        removed_count = timeout_manager.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'message': f'{removed_count} sessões expiradas removidas',
            'removed_count': removed_count
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao limpar sessões: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@timeout_bp.route('/stats', methods=['GET'])
def get_statistics():
    """
    Obtém estatísticas do sistema de timeout
    """
    try:
        stats = timeout_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500 