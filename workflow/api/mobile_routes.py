"""
Rotas da API para integração com app Android
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

from .mobile_security import MobileSecurityManager, get_api_key
from ..security.parental_consent import ParentalConsent

router = APIRouter(prefix="/mobile", tags=["mobile"])
security_manager = MobileSecurityManager(secret_key="your-secret-key-here")  # Em produção, usar variável de ambiente
consent_manager = ParentalConsent()

class MobileAuthRequest(BaseModel):
    device_id: str
    user_id: str

class MobileConsentRequest(BaseModel):
    device_id: str
    user_id: str
    child_id: str
    parent_name: str
    child_name: str

@router.post("/auth")
async def mobile_auth(
    request: MobileAuthRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Autentica dispositivo móvel e retorna token JWT
    """
    try:
        token = security_manager.generate_mobile_token(
            device_id=request.device_id,
            user_id=request.user_id
        )
        
        return {
            "status": "success",
            "token": token,
            "expires_in": security_manager.token_expiry * 3600  # segundos
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na autenticação mobile: {str(e)}"
        )

@router.post("/consent/request")
async def request_mobile_consent(
    request: MobileConsentRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Processa solicitação de consentimento via app
    """
    try:
        # Validar token do device primeiro
        token = security_manager.generate_mobile_token(
            device_id=request.device_id,
            user_id=request.user_id
        )
        
        # Gerar consentimento
        consent_id = consent_manager.request_consent(
            parent_id=request.user_id,
            child_id=request.child_id,
            data_usage={
                "parent_name": request.parent_name,
                "child_name": request.child_name,
                "device_id": request.device_id,
                "platform": "android"
            }
        )
        
        return {
            "status": "success",
            "consent_id": consent_id,
            "token": token
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar consentimento mobile: {str(e)}"
        )

@router.post("/consent/grant/{consent_id}")
async def grant_mobile_consent(
    consent_id: str,
    user_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Registra concessão de consentimento via app
    """
    success = consent_manager.grant_consent(
        consent_id=consent_id,
        parent_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao conceder consentimento"
        )
        
    return {
        "status": "success",
        "message": "Consentimento concedido com sucesso"
    }

@router.post("/consent/revoke/{consent_id}")
async def revoke_mobile_consent(
    consent_id: str,
    user_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Revoga consentimento via app
    """
    success = consent_manager.revoke_consent(
        consent_id=consent_id,
        parent_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao revogar consentimento"
        )
        
    return {
        "status": "success",
        "message": "Consentimento revogado com sucesso"
    } 