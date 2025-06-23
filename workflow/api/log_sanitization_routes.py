"""
Rotas da API para Sanitização de Logs - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, List
import logging

from ..security.log_sanitization import log_sanitizer
from ..security.input_validation import InputValidation

# Configuração do blueprint
log_sanitization_bp = Blueprint('log_sanitization', __name__, url_prefix='/api/log-sanitization')

@log_sanitization_bp.route('/sanitize', methods=['POST'])
def sanitize_data():
    """
    Sanitiza dados removendo informações sensíveis
    
    Body:
        data: str ou dict - Dados a serem sanitizados
        data_type: str (opcional) - Tipo de dados (string, json)
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo data é obrigatório'
            }), 400
        
        # Sanitização dos dados
        input_data = data['data']
        data_type = InputValidation.sanitize_string(data.get('data_type', 'auto'), max_length=20)
        
        # Determina o tipo de dados automaticamente se não especificado
        if data_type == 'auto':
            if isinstance(input_data, dict):
                data_type = 'json'
            elif isinstance(input_data, str):
                data_type = 'string'
            else:
                data_type = 'string'
        
        # Sanitiza os dados baseado no tipo
        if data_type == 'json':
            sanitized_data = log_sanitizer.sanitize_json(input_data)
        else:
            sanitized_data = log_sanitizer.sanitize_string(str(input_data))
        
        return jsonify({
            'success': True,
            'original_data': input_data,
            'sanitized_data': sanitized_data,
            'data_type': data_type,
            'sanitization_applied': sanitized_data != input_data
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao sanitizar dados: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/sanitize-message', methods=['POST'])
def sanitize_log_message():
    """
    Sanitiza uma mensagem de log
    
    Body:
        message: str - Mensagem de log
        level: str (opcional) - Nível do log
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo message é obrigatório'
            }), 400
        
        # Sanitização dos dados
        message = InputValidation.sanitize_string(data['message'], max_length=10000)
        level = InputValidation.sanitize_string(data.get('level', 'INFO'), max_length=20)
        
        # Validação do nível de log
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level.upper() not in allowed_levels:
            return jsonify({
                'success': False,
                'error': f'Nível de log inválido. Níveis permitidos: {", ".join(allowed_levels)}'
            }), 400
        
        # Sanitiza a mensagem
        sanitized_message = log_sanitizer.sanitize_log_message(message, level.upper())
        
        return jsonify({
            'success': True,
            'original_message': message,
            'sanitized_message': sanitized_message,
            'level': level.upper(),
            'sanitization_applied': sanitized_message != message
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao sanitizar mensagem: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/test', methods=['POST'])
def test_sanitization():
    """
    Testa a sanitização com dados de exemplo
    
    Body:
        test_data: dict - Dados de teste
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'test_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo test_data é obrigatório'
            }), 400
        
        # Sanitização dos dados de teste
        test_data = data['test_data']
        
        # Valida se é um dicionário
        if not isinstance(test_data, dict):
            return jsonify({
                'success': False,
                'error': 'test_data deve ser um objeto JSON'
            }), 400
        
        # Testa a sanitização
        test_results = log_sanitizer.test_sanitization(test_data)
        
        return jsonify({
            'success': True,
            'test_results': test_results
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao testar sanitização: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/patterns', methods=['GET'])
def get_patterns():
    """
    Obtém todos os padrões de sanitização configurados
    """
    try:
        stats = log_sanitizer.get_sanitization_stats()
        
        return jsonify({
            'success': True,
            'patterns': stats['patterns'],
            'statistics': {
                'total_patterns': stats['patterns_configured'],
                'risk_levels': stats['risk_levels'],
                'sensitive_fields': stats['sensitive_fields']
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter padrões: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/patterns', methods=['POST'])
def add_pattern():
    """
    Adiciona um padrão personalizado de sanitização
    
    Body:
        name: str - Nome do padrão
        pattern: str - Expressão regular
        replacement: str - Texto de substituição
        description: str - Descrição do padrão
        risk_level: str (opcional) - Nível de risco
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        required_fields = ['name', 'pattern', 'replacement', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Sanitização dos dados
        name = InputValidation.sanitize_string(data['name'], max_length=100)
        pattern = InputValidation.sanitize_string(data['pattern'], max_length=500)
        replacement = InputValidation.sanitize_string(data['replacement'], max_length=200)
        description = InputValidation.sanitize_string(data['description'], max_length=500)
        risk_level = InputValidation.sanitize_string(data.get('risk_level', 'MEDIUM'), max_length=20)
        
        # Validação do nível de risco
        allowed_risk_levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        if risk_level.upper() not in allowed_risk_levels:
            return jsonify({
                'success': False,
                'error': f'Nível de risco inválido. Níveis permitidos: {", ".join(allowed_risk_levels)}'
            }), 400
        
        # Adiciona o padrão
        log_sanitizer.add_custom_pattern(
            name=name,
            pattern=pattern,
            replacement=replacement,
            description=description,
            risk_level=risk_level.upper()
        )
        
        return jsonify({
            'success': True,
            'message': f'Padrão {name} adicionado com sucesso',
            'pattern': {
                'name': name,
                'pattern': pattern,
                'replacement': replacement,
                'description': description,
                'risk_level': risk_level.upper()
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao adicionar padrão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/patterns/<pattern_name>', methods=['DELETE'])
def remove_pattern(pattern_name: str):
    """
    Remove um padrão de sanitização
    
    Args:
        pattern_name: Nome do padrão a ser removido
    """
    try:
        # Sanitização do nome do padrão
        pattern_name = InputValidation.sanitize_string(pattern_name, max_length=100)
        
        # Remove o padrão
        success = log_sanitizer.remove_pattern(pattern_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Padrão {pattern_name} removido com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Padrão {pattern_name} não encontrado'
            }), 404
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao remover padrão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/logger/create', methods=['POST'])
def create_sanitized_logger():
    """
    Cria um logger com sanitização automática
    
    Body:
        name: str - Nome do logger
        level: str (opcional) - Nível de logging
    """
    try:
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo name é obrigatório'
            }), 400
        
        # Sanitização dos dados
        name = InputValidation.sanitize_string(data['name'], max_length=100)
        level_str = InputValidation.sanitize_string(data.get('level', 'INFO'), max_length=20)
        
        # Validação do nível de logging
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level_str.upper() not in allowed_levels:
            return jsonify({
                'success': False,
                'error': f'Nível de logging inválido. Níveis permitidos: {", ".join(allowed_levels)}'
            }), 400
        
        # Converte nível de string para constante
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        level = level_map[level_str.upper()]
        
        # Cria o logger
        logger = log_sanitizer.create_sanitized_logger(name, level)
        
        return jsonify({
            'success': True,
            'message': f'Logger {name} criado com sanitização automática',
            'logger_info': {
                'name': name,
                'level': level_str.upper(),
                'sanitization_enabled': True
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logging.error(f"Erro ao criar logger: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@log_sanitization_bp.route('/stats', methods=['GET'])
def get_sanitization_stats():
    """
    Obtém estatísticas de sanitização
    """
    try:
        stats = log_sanitizer.get_sanitization_stats()
        
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