"""
Rotas da API para autenticação 2FA
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List
import os

from ..security.two_factor_auth import TwoFactorAuth
from .mobile_security import get_api_key

router = APIRouter(prefix="/2fa", tags=["2fa"])
two_factor_auth = TwoFactorAuth()

class Enable2FARequest(BaseModel):
    parent_id: str
    email: str

class Verify2FARequest(BaseModel):
    parent_id: str
    token: str

class BackupCodeRequest(BaseModel):
    parent_id: str
    code: str

@router.post("/enable")
async def enable_2fa(
    request: Enable2FARequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Habilita 2FA para um responsável
    """
    try:
        # Gera QR code
        qr_path = two_factor_auth.generate_qr_code(
            parent_id=request.parent_id,
            email=request.email
        )
        
        # Gera códigos de backup
        backup_codes = two_factor_auth.generate_backup_codes(request.parent_id)
        
        return {
            "status": "success",
            "message": "2FA habilitado com sucesso",
            "qr_code_path": qr_path,
            "backup_codes": backup_codes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao habilitar 2FA: {str(e)}"
        )

@router.get("/qr/{parent_id}")
async def get_qr_code(
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> FileResponse:
    """
    Retorna QR code para configuração
    """
    try:
        qr_path = os.path.join(two_factor_auth.storage_path, "qr_codes", f"{parent_id}_qr.png")
        
        if not os.path.exists(qr_path):
            raise HTTPException(
                status_code=404,
                detail="QR code não encontrado"
            )
            
        return FileResponse(qr_path, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter QR code: {str(e)}"
        )

@router.post("/verify")
async def verify_2fa(
    request: Verify2FARequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Verifica token 2FA
    """
    try:
        is_valid = two_factor_auth.verify_totp(
            parent_id=request.parent_id,
            token=request.token
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Token 2FA inválido"
            )
            
        return {
            "status": "success",
            "message": "Token 2FA válido"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar token: {str(e)}"
        )

@router.post("/backup/verify")
async def verify_backup_code(
    request: BackupCodeRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Verifica código de backup
    """
    try:
        is_valid = two_factor_auth.verify_backup_code(
            parent_id=request.parent_id,
            code=request.code
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Código de backup inválido"
            )
            
        return {
            "status": "success",
            "message": "Código de backup válido"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar código de backup: {str(e)}"
        )

@router.get("/status/{parent_id}")
async def get_2fa_status(
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Verifica status do 2FA para um responsável
    """
    try:
        is_enabled = two_factor_auth.is_2fa_enabled(parent_id)
        
        return {
            "status": "success",
            "parent_id": parent_id,
            "2fa_enabled": is_enabled
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar status 2FA: {str(e)}"
        )

@router.delete("/disable/{parent_id}")
async def disable_2fa(
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Desabilita 2FA para um responsável
    """
    try:
        success = two_factor_auth.disable_2fa(parent_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Falha ao desabilitar 2FA"
            )
            
        return {
            "status": "success",
            "message": "2FA desabilitado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao desabilitar 2FA: {str(e)}"
        ) 