"""
Headers de Segurança HTTP - TarefaMágica (P2-3)
Implementa middleware para headers de segurança
"""

from flask import request, make_response
from typing import Dict, List, Optional
import logging

class SecurityHeaders:
    def __init__(self):
        """
        Inicializa o sistema de headers de segurança
        """
        self.headers = {
            # Prevenção de XSS
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            
            # HSTS (HTTP Strict Transport Security)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            
            # Prevenção de clickjacking
            'Content-Security-Policy': self._get_csp_policy(),
            
            # Referrer Policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions Policy
            'Permissions-Policy': self._get_permissions_policy(),
            
            # Cache Control
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            
            # Outros headers de segurança
            'X-Permitted-Cross-Domain-Policies': 'none',
            'X-Download-Options': 'noopen',
            'X-DNS-Prefetch-Control': 'off'
        }
        
        # Configuração CORS
        self.cors_config = {
            'allowed_origins': [
                'https://tarefamagica.com',
                'https://www.tarefamagica.com',
                'https://app.tarefamagica.com',
                'https://api.tarefamagica.com'
            ],
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allowed_headers': [
                'Content-Type',
                'Authorization',
                'X-Requested-With',
                'X-API-Key',
                'X-Client-Version'
            ],
            'expose_headers': [
                'X-Rate-Limit-Remaining',
                'X-Rate-Limit-Reset',
                'X-Total-Count'
            ],
            'max_age': 86400,  # 24 horas
            'credentials': True
        }
        
    def _get_csp_policy(self) -> str:
        """
        Retorna política de Content Security Policy
        """
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: blob:; "
            "media-src 'self' https:; "
            "connect-src 'self' https://api.tarefamagica.com https://cdn.jsdelivr.net; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests;"
        )
        
    def _get_permissions_policy(self) -> str:
        """
        Retorna política de permissões
        """
        return (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "keyboard-map=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
        
    def add_security_headers(self, response):
        """
        Adiciona headers de segurança à resposta
        
        Args:
            response: Resposta Flask
            
        Returns:
            Response: Resposta com headers de segurança
        """
        try:
            # Adiciona headers básicos de segurança
            for header, value in self.headers.items():
                response.headers[header] = value
                
            # Adiciona headers específicos baseados no tipo de resposta
            if 'application/json' in response.headers.get('Content-Type', ''):
                response.headers['X-Content-Type-Options'] = 'nosniff'
                
            # Headers para APIs
            if request.path.startswith('/api/'):
                response.headers['X-API-Version'] = '1.0'
                response.headers['X-Request-ID'] = self._generate_request_id()
                
            return response
            
        except Exception as e:
            logging.error(f"Erro ao adicionar headers de segurança: {str(e)}")
            return response
            
    def add_cors_headers(self, response, origin: Optional[str] = None):
        """
        Adiciona headers CORS à resposta
        
        Args:
            response: Resposta Flask
            origin: Origem da requisição
            
        Returns:
            Response: Resposta com headers CORS
        """
        try:
            # Determina origem permitida
            allowed_origin = self._get_allowed_origin(origin)
            
            if allowed_origin:
                response.headers['Access-Control-Allow-Origin'] = allowed_origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = ', '.join(self.cors_config['allowed_methods'])
                response.headers['Access-Control-Allow-Headers'] = ', '.join(self.cors_config['allowed_headers'])
                response.headers['Access-Control-Expose-Headers'] = ', '.join(self.cors_config['expose_headers'])
                response.headers['Access-Control-Max-Age'] = str(self.cors_config['max_age'])
                
            return response
            
        except Exception as e:
            logging.error(f"Erro ao adicionar headers CORS: {str(e)}")
            return response
            
    def _get_allowed_origin(self, origin: Optional[str] = None) -> Optional[str]:
        """
        Determina se a origem é permitida
        
        Args:
            origin: Origem da requisição
            
        Returns:
            Optional[str]: Origem permitida ou None
        """
        if not origin:
            origin = request.headers.get('Origin')
            
        if origin in self.cors_config['allowed_origins']:
            return origin
            
        # Verifica se é uma origem de desenvolvimento
        if origin and ('localhost' in origin or '127.0.0.1' in origin):
            return origin
            
        return None
        
    def _generate_request_id(self) -> str:
        """
        Gera ID único para a requisição
        
        Returns:
            str: ID da requisição
        """
        import uuid
        return str(uuid.uuid4())
        
    def handle_preflight_request(self):
        """
        Manipula requisições preflight OPTIONS
        
        Returns:
            Response: Resposta para requisição preflight
        """
        try:
            origin = request.headers.get('Origin')
            allowed_origin = self._get_allowed_origin(origin)
            
            if not allowed_origin:
                return make_response('', 403)
                
            response = make_response('', 200)
            response.headers['Access-Control-Allow-Origin'] = allowed_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.cors_config['allowed_methods'])
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.cors_config['allowed_headers'])
            response.headers['Access-Control-Max-Age'] = str(self.cors_config['max_age'])
            
            return response
            
        except Exception as e:
            logging.error(f"Erro ao manipular requisição preflight: {str(e)}")
            return make_response('', 500)
            
    def add_rate_limit_headers(self, response, remaining: int, reset_time: int):
        """
        Adiciona headers de rate limiting
        
        Args:
            response: Resposta Flask
            remaining: Tentativas restantes
            reset_time: Timestamp de reset
            
        Returns:
            Response: Resposta com headers de rate limiting
        """
        try:
            response.headers['X-Rate-Limit-Remaining'] = str(remaining)
            response.headers['X-Rate-Limit-Reset'] = str(reset_time)
            return response
            
        except Exception as e:
            logging.error(f"Erro ao adicionar headers de rate limiting: {str(e)}")
            return response
            
    def add_cache_headers(self, response, cache_control: str = 'no-cache'):
        """
        Adiciona headers de cache
        
        Args:
            response: Resposta Flask
            cache_control: Política de cache
            
        Returns:
            Response: Resposta com headers de cache
        """
        try:
            response.headers['Cache-Control'] = cache_control
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
        except Exception as e:
            logging.error(f"Erro ao adicionar headers de cache: {str(e)}")
            return response
            
    def add_content_security_policy(self, response, policy: Optional[str] = None):
        """
        Adiciona Content Security Policy personalizada
        
        Args:
            response: Resposta Flask
            policy: Política CSP personalizada
            
        Returns:
            Response: Resposta com CSP
        """
        try:
            if policy:
                response.headers['Content-Security-Policy'] = policy
            else:
                response.headers['Content-Security-Policy'] = self._get_csp_policy()
                
            return response
            
        except Exception as e:
            logging.error(f"Erro ao adicionar CSP: {str(e)}")
            return response
            
    def get_security_report(self) -> Dict:
        """
        Gera relatório de headers de segurança
        
        Returns:
            Dict: Relatório de segurança
        """
        try:
            return {
                'headers_configured': list(self.headers.keys()),
                'cors_config': {
                    'allowed_origins': self.cors_config['allowed_origins'],
                    'allowed_methods': self.cors_config['allowed_methods'],
                    'allowed_headers': self.cors_config['allowed_headers']
                },
                'csp_policy': self._get_csp_policy(),
                'permissions_policy': self._get_permissions_policy()
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de segurança: {str(e)}")
            return {}

# Instância global do sistema de headers de segurança
security_headers = SecurityHeaders() 