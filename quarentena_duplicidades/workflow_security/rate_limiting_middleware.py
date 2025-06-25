#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 Middleware de Rate Limiting - TarefaMágica
Aplica rate limiting automaticamente em todas as rotas da API
"""

from flask import request, jsonify, g
from functools import wraps
import logging
from typing import Optional, Callable
from .rate_limiting import rate_limiter, RateLimitType

def apply_rate_limiting(limit_type: RateLimitType, identifier_func: Optional[Callable] = None):
    """
    Decorator para aplicar rate limiting em rotas
    
    Args:
        limit_type: Tipo de limite a ser aplicado
        identifier_func: Função para gerar identificador (padrão: IP do cliente)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Gera identificador
                if identifier_func:
                    identifier = identifier_func(request)
                else:
                    identifier = get_client_identifier(request)
                
                # Verifica rate limit
                allowed, message = rate_limiter.check_rate_limit(identifier, limit_type)
                
                if not allowed:
                    # Registra tentativa bloqueada
                    rate_limiter.record_attempt(identifier, limit_type, success=False)
                    
                    return jsonify({
                        'success': False,
                        'error': 'Rate limit exceeded',
                        'message': message,
                        'retry_after': get_retry_after(identifier, limit_type)
                    }), 429  # Too Many Requests
                
                # Registra tentativa permitida
                rate_limiter.record_attempt(identifier, limit_type, success=True)
                
                # Adiciona headers de rate limit
                response = f(*args, **kwargs)
                
                # Se response é uma tupla (data, status_code)
                if isinstance(response, tuple):
                    data, status_code = response
                    if isinstance(data, dict):
                        data['rate_limit_info'] = {
                            'remaining': get_remaining_attempts(identifier, limit_type),
                            'reset_time': get_reset_time(identifier, limit_type)
                        }
                    response = (data, status_code)
                else:
                    # Se response é apenas data
                    if hasattr(response, 'json'):
                        data = response.get_json()
                        if data and isinstance(data, dict):
                            data['rate_limit_info'] = {
                                'remaining': get_remaining_attempts(identifier, limit_type),
                                'reset_time': get_reset_time(identifier, limit_type)
                            }
                            response = jsonify(data)
                
                return response
                
            except Exception as e:
                logging.error(f"Erro no rate limiting: {str(e)}")
                # Em caso de erro, permite a ação
                return f(*args, **kwargs)
                
        return decorated_function
    return decorator

def get_client_identifier(request) -> str:
    """
    Obtém identificador único do cliente
    
    Args:
        request: Objeto request do Flask
        
    Returns:
        str: Identificador único
    """
    # Prioriza IP real (atrás de proxy)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    # Adiciona user agent para maior especificidade
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Combina IP + User Agent (hash para privacidade)
    import hashlib
    combined = f"{ip}:{user_agent}"
    return hashlib.md5(combined.encode()).hexdigest()

def get_remaining_attempts(identifier: str, limit_type: RateLimitType) -> int:
    """Obtém tentativas restantes"""
    try:
        status = rate_limiter.get_status(identifier, limit_type)
        return status.get('remaining_attempts', 0)
    except:
        return 0

def get_reset_time(identifier: str, limit_type: RateLimitType) -> Optional[str]:
    """Obtém tempo de reset"""
    try:
        status = rate_limiter.get_status(identifier, limit_type)
        return status.get('reset_time')
    except:
        return None

def get_retry_after(identifier: str, limit_type: RateLimitType) -> int:
    """Obtém tempo para retry"""
    try:
        status = rate_limiter.get_status(identifier, limit_type)
        blocked_until = status.get('blocked_until')
        if blocked_until:
            from datetime import datetime
            blocked_time = datetime.fromisoformat(blocked_until)
            remaining = (blocked_time - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
    except:
        pass
    return 60  # Padrão: 1 minuto

# Decorators específicos para diferentes tipos de rota
def login_rate_limit(f):
    """Rate limiting para tentativas de login"""
    return apply_rate_limiting(RateLimitType.LOGIN_ATTEMPTS)(f)

def api_rate_limit(f):
    """Rate limiting para requisições da API"""
    return apply_rate_limiting(RateLimitType.API_REQUESTS)(f)

def password_reset_rate_limit(f):
    """Rate limiting para reset de senha"""
    return apply_rate_limiting(RateLimitType.PASSWORD_RESET)(f)

def two_factor_rate_limit(f):
    """Rate limiting para tentativas 2FA"""
    return apply_rate_limiting(RateLimitType.TWO_FACTOR_ATTEMPTS)(f)

def financial_rate_limit(f):
    """Rate limiting para transações financeiras"""
    return apply_rate_limiting(RateLimitType.FINANCIAL_TRANSACTIONS)(f)

def consent_rate_limit(f):
    """Rate limiting para requisições de consentimento"""
    return apply_rate_limiting(RateLimitType.CONSENT_REQUESTS)(f)

# Middleware global para aplicar rate limiting em todas as rotas
def setup_rate_limiting_middleware(app):
    """
    Configura middleware de rate limiting global
    
    Args:
        app: Aplicação Flask
    """
    
    @app.before_request
    def apply_global_rate_limiting():
        """Aplica rate limiting global antes de cada requisição"""
        try:
            # Identifica tipo de rota
            path = request.path
            method = request.method
            
            # Define rate limit baseado na rota
            if '/api/auth/login' in path and method == 'POST':
                limit_type = RateLimitType.LOGIN_ATTEMPTS
            elif '/api/auth/password-reset' in path and method == 'POST':
                limit_type = RateLimitType.PASSWORD_RESET
            elif '/api/auth/2fa' in path and method == 'POST':
                limit_type = RateLimitType.TWO_FACTOR_ATTEMPTS
            elif '/api/financial' in path and method == 'POST':
                limit_type = RateLimitType.FINANCIAL_TRANSACTIONS
            elif '/api/consent' in path and method == 'POST':
                limit_type = RateLimitType.CONSENT_REQUESTS
            elif path.startswith('/api/'):
                limit_type = RateLimitType.API_REQUESTS
            else:
                # Rotas não-API não têm rate limiting
                return
            
            # Obtém identificador
            identifier = get_client_identifier(request)
            
            # Verifica rate limit
            allowed, message = rate_limiter.check_rate_limit(identifier, limit_type)
            
            if not allowed:
                # Registra tentativa bloqueada
                rate_limiter.record_attempt(identifier, limit_type, success=False)
                
                # Retorna erro 429
                response = jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'message': message,
                    'retry_after': get_retry_after(identifier, limit_type)
                })
                response.status_code = 429
                
                # Adiciona headers de rate limit
                response.headers['X-RateLimit-Limit'] = str(rate_limiter.limits[limit_type].max_attempts)
                response.headers['X-RateLimit-Remaining'] = str(get_remaining_attempts(identifier, limit_type))
                response.headers['X-RateLimit-Reset'] = str(get_reset_time(identifier, limit_type) or '')
                response.headers['Retry-After'] = str(get_retry_after(identifier, limit_type))
                
                return response
            
            # Registra tentativa permitida
            rate_limiter.record_attempt(identifier, limit_type, success=True)
            
            # Adiciona informações de rate limit ao contexto
            g.rate_limit_info = {
                'type': limit_type.value,
                'remaining': get_remaining_attempts(identifier, limit_type),
                'reset_time': get_reset_time(identifier, limit_type)
            }
            
        except Exception as e:
            logging.error(f"Erro no middleware de rate limiting: {str(e)}")
            # Em caso de erro, permite a requisição
    
    @app.after_request
    def add_rate_limit_headers(response):
        """Adiciona headers de rate limit à resposta"""
        try:
            if hasattr(g, 'rate_limit_info'):
                response.headers['X-RateLimit-Limit'] = str(rate_limiter.limits[RateLimitType.API_REQUESTS].max_attempts)
                response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_info.get('remaining', 0))
                response.headers['X-RateLimit-Reset'] = str(g.rate_limit_info.get('reset_time', ''))
        except:
            pass
        return response

# Função para testar rate limiting
def test_rate_limiting():
    """Testa se o rate limiting está funcionando"""
    print("🧪 Testando Rate Limiting...")
    
    # Simula múltiplas tentativas de login
    test_identifier = "test_user_123"
    
    for i in range(10):
        allowed, message = rate_limiter.check_rate_limit(test_identifier, RateLimitType.LOGIN_ATTEMPTS)
        print(f"Tentativa {i+1}: {'✅ Permitido' if allowed else '❌ Bloqueado'} - {message}")
        
        if not allowed:
            print(f"✅ Rate limiting funcionando! Bloqueado na tentativa {i+1}")
            return True
    
    print("❌ Rate limiting não está bloqueando adequadamente")
    return False

if __name__ == "__main__":
    test_rate_limiting() 