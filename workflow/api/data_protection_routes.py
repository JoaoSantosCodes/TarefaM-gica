"""
Rotas da API para proteção de dados
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

from ..security.data_protection import DataProtection
from .mobile_security import get_api_key

router = APIRouter(prefix="/data", tags=["data"])
data_protection = DataProtection()

class ChildDataRequest(BaseModel):
    child_id: str
    parent_id: str
    data: Dict

class UpdateDataRequest(BaseModel):
    record_id: str
    parent_id: str
    new_data: Dict

@router.post("/encrypt")
async def encrypt_data(
    request: ChildDataRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Criptografa dados da criança
    """
    try:
        record_id = data_protection.encrypt_child_data(
            child_id=request.child_id,
            data=request.data,
            parent_id=request.parent_id
        )
        
        return {
            "status": "success",
            "record_id": record_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criptografar dados: {str(e)}"
        )

@router.get("/decrypt/{record_id}")
async def decrypt_data(
    record_id: str,
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Descriptografa dados da criança
    """
    data = data_protection.decrypt_child_data(
        record_id=record_id,
        parent_id=parent_id
    )
    
    if data is None:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado aos dados"
        )
        
    return {
        "status": "success",
        "data": data
    }

@router.put("/update")
async def update_data(
    request: UpdateDataRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Atualiza dados criptografados da criança
    """
    success = data_protection.update_child_data(
        record_id=request.record_id,
        new_data=request.new_data,
        parent_id=request.parent_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao atualizar dados"
        )
        
    return {
        "status": "success",
        "message": "Dados atualizados com sucesso"
    }

@router.delete("/{record_id}")
async def delete_data(
    record_id: str,
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Remove dados criptografados da criança
    """
    success = data_protection.delete_child_data(
        record_id=record_id,
        parent_id=parent_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao remover dados"
        )
        
    return {
        "status": "success",
        "message": "Dados removidos com sucesso"
    } 