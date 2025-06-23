"""
Rotas da API para Gerenciamento de Consentimento - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, List
import logging

from ..security.parental_consent import ParentalConsent
from ..security.input_validation import InputValidation

# Configuração do blueprint
consent_bp = Blueprint('consent', __name__, url_prefix='/api/consent')

# Instância do sistema de consentimento
consent_system = ParentalConsent()

@consent_bp.route('/create', methods=['POST'])
def create_consent():
    """
    Cria novo consentimento parental
    
    Body:
        parent_id: str
        child_id: str
        consent_type: str
        description: str
        expires_at: str (opcional)
    """
    try:
        data = request.get_json()
        
        # Validação e sanitização dos dados de entrada
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados obrigatórios não fornecidos'
            }), 400
            
        # Validação dos campos obrigatórios
        required_fields = ['parent_id', 'child_id', 'consent_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Sanitização dos dados
        parent_id = InputValidation.sanitize_string(data['parent_id'], max_length=100)
        child_id = InputValidation.sanitize_string(data['child_id'], max_length=100)
        consent_type = InputValidation.sanitize_string(data['consent_type'], max_length=50)
        description = InputValidation.sanitize_string(data['description'], max_length=500)
        
        # Validação de tipos de consentimento permitidos
        allowed_types = ['data_collection', 'financial_transactions', 'location_sharing', 'content_creation']
        if consent_type not in allowed_types:
            return jsonify({
                'success': False,
                'error': f'Tipo de consentimento inválido. Tipos permitidos: {", ".join(allowed_types)}'
            }), 400
        
        # Processamento da data de expiração (opcional)
        expires_at = None
        if 'expires_at' in data and data['expires_at']:
            try:
                expires_at = datetime.fromisoformat(InputValidation.sanitize_string(data['expires_at']))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de data inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        # Cria consentimento
        consent = consent_system.create_consent(
            parent_id=parent_id,
            child_id=child_id,
            consent_type=consent_type,
            description=description,
            expires_at=expires_at
        )
        
        return jsonify({
            'success': True,
            'consent': {
                'consent_id': consent.consent_id,
                'parent_id': consent.parent_id,
                'child_id': consent.child_id,
                'consent_type': consent.consent_type,
                'description': consent.description,
                'status': consent.status.value,
                'created_at': consent.created_at.isoformat(),
                'expires_at': consent.expires_at.isoformat() if consent.expires_at else None
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao criar consentimento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@consent_bp.route('/validate', methods=['POST'])
def validate_consent():
    """
    Valida consentimento existente
    
    Body:
        parent_id: str
        child_id: str
        consent_type: str
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados obrigatórios não fornecidos'
            }), 400
            
        required_fields = ['parent_id', 'child_id', 'consent_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Sanitização dos dados
        parent_id = InputValidation.sanitize_string(data['parent_id'], max_length=100)
        child_id = InputValidation.sanitize_string(data['child_id'], max_length=100)
        consent_type = InputValidation.sanitize_string(data['consent_type'], max_length=50)
        
        # Validação de tipos de consentimento permitidos
        allowed_types = ['data_collection', 'financial_transactions', 'location_sharing', 'content_creation']
        if consent_type not in allowed_types:
            return jsonify({
                'success': False,
                'error': f'Tipo de consentimento inválido. Tipos permitidos: {", ".join(allowed_types)}'
            }), 400
        
        # Valida consentimento
        is_valid = consent_system.validate_consent(parent_id, child_id, consent_type)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'consent_info': {
                'parent_id': parent_id,
                'child_id': child_id,
                'consent_type': consent_type
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao validar consentimento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@consent_bp.route('/revoke', methods=['POST'])
def revoke_consent():
    """
    Revoga consentimento
    
    Body:
        consent_id: str
        reason: str (opcional)
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'consent_id' not in data:
            return jsonify({
                'success': False,
                'error': 'consent_id é obrigatório'
            }), 400
        
        # Sanitização dos dados
        consent_id = InputValidation.sanitize_string(data['consent_id'], max_length=100)
        reason = InputValidation.sanitize_string(data.get('reason', ''), max_length=200)
        
        # Revoga consentimento
        success = consent_system.revoke_consent(consent_id, reason)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Consentimento {consent_id} revogado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Consentimento não encontrado ou já revogado'
            }), 404
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao revogar consentimento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@consent_bp.route('/list/<parent_id>', methods=['GET'])
def list_consents(parent_id: str):
    """
    Lista consentimentos de um pai
    
    Query params:
        status: str (opcional)
        consent_type: str (opcional)
    """
    try:
        # Sanitização do parent_id
        parent_id = InputValidation.sanitize_string(parent_id, max_length=100)
        
        # Parâmetros de filtro
        status = request.args.get('status')
        consent_type = request.args.get('consent_type')
        
        # Sanitização dos parâmetros opcionais
        if status:
            status = InputValidation.sanitize_string(status, max_length=20)
        if consent_type:
            consent_type = InputValidation.sanitize_string(consent_type, max_length=50)
        
        # Lista consentimentos
        consents = consent_system.get_consents_by_parent(parent_id, status, consent_type)
        
        return jsonify({
            'success': True,
            'consents': [
                {
                    'consent_id': consent.consent_id,
                    'parent_id': consent.parent_id,
                    'child_id': consent.child_id,
                    'consent_type': consent.consent_type,
                    'description': consent.description,
                    'status': consent.status.value,
                    'created_at': consent.created_at.isoformat(),
                    'expires_at': consent.expires_at.isoformat() if consent.expires_at else None,
                    'revoked_at': consent.revoked_at.isoformat() if consent.revoked_at else None,
                    'revoke_reason': consent.revoke_reason
                }
                for consent in consents
            ]
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao listar consentimentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@consent_bp.route('/<consent_id>', methods=['GET'])
def get_consent(consent_id: str):
    """
    Obtém detalhes de um consentimento específico
    """
    try:
        # Sanitização do consent_id
        consent_id = InputValidation.sanitize_string(consent_id, max_length=100)
        
        # Busca consentimento
        consent = consent_system.get_consent(consent_id)
        
        if not consent:
            return jsonify({
                'success': False,
                'error': 'Consentimento não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'consent': {
                'consent_id': consent.consent_id,
                'parent_id': consent.parent_id,
                'child_id': consent.child_id,
                'consent_type': consent.consent_type,
                'description': consent.description,
                'status': consent.status.value,
                'created_at': consent.created_at.isoformat(),
                'expires_at': consent.expires_at.isoformat() if consent.expires_at else None,
                'revoked_at': consent.revoked_at.isoformat() if consent.revoked_at else None,
                'revoke_reason': consent.revoke_reason
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao obter consentimento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500 