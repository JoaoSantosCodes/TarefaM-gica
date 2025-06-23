"""
Módulo de Segurança Mobile - TarefaMágica
Implementa a camada de segurança para integração com app Android
"""

from datetime import datetime, timedelta
import jwt
import logging
from typing import Dict, Optional
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

class MobileSecurityManager:
    def __init__(self, secret_key: str, token_expiry: int = 24):
        self.secret_key = secret_key
        self.token_expiry = token_expiry  # horas
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            filename="logs/mobile_security.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def generate_mobile_token(self, device_id: str, user_id: str) -> str:
        """
        Gera token JWT para dispositivo móvel
        
        Args:
            device_id: ID único do dispositivo Android
            user_id: ID do usuário (pai/responsável)
            
        Returns:
            str: Token JWT
        """
        try:
            payload = {
                "device_id": device_id,
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(hours=self.token_expiry),
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            logging.info(f"Token gerado para device: {device_id}")
            
            return token
            
        except Exception as e:
            logging.error(f"Erro ao gerar token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar token de acesso"
            )

    def validate_mobile_token(self, token: str) -> Dict:
        """
        Valida token JWT do dispositivo móvel
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            Dict: Payload do token se válido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
            
        except jwt.ExpiredSignatureError:
            logging.warning(f"Token expirado: {token[:10]}...")
            raise HTTPException(
                status_code=401,
                detail="Token expirado"
            )
            
        except jwt.InvalidTokenError:
            logging.warning(f"Token inválido: {token[:10]}...")
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

    def revoke_mobile_token(self, token: str) -> bool:
        """
        Revoga um token JWT (para logout ou comprometimento)
        
        Args:
            token: Token JWT a ser revogado
            
        Returns:
            bool: True se revogado com sucesso
        """
        try:
            # Aqui implementaríamos uma lista negra de tokens
            # Por hora, apenas registramos o evento
            logging.info(f"Token revogado: {token[:10]}...")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao revogar token: {str(e)}")
            return False

# Configuração do header de autenticação
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Valida API Key do app Android"""
    if not api_key.startswith("tm_"):
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )
    return api_key 