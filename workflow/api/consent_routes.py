"""
Rotas da API para gerenciamento de consentimento parental
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Optional

from ..security.parental_consent import ParentalConsent

router = APIRouter(prefix="/consent", tags=["consent"])
templates = Jinja2Templates(directory="templates")
consent_manager = ParentalConsent()

class ConsentRequest(BaseModel):
    parent_id: str
    child_id: str
    parent_name: str
    child_name: str
    data_usage: Dict[str, str]

class ConsentAction(BaseModel):
    consent_id: str
    parent_id: str

@router.get("/form", response_class=HTMLResponse)
async def get_consent_form(request: Request):
    """Retorna o formulário de consentimento"""
    return templates.TemplateResponse(
        "consent_form.html",
        {"request": request}
    )

@router.post("/request")
async def request_consent(consent_req: ConsentRequest) -> Dict:
    """
    Processa uma nova solicitação de consentimento
    """
    try:
        consent_id = consent_manager.request_consent(
            parent_id=consent_req.parent_id,
            child_id=consent_req.child_id,
            data_usage={
                "parent_name": consent_req.parent_name,
                "child_name": consent_req.child_name,
                **consent_req.data_usage
            }
        )
        
        return {
            "status": "success",
            "consent_id": consent_id,
            "message": "Solicitação de consentimento criada com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar solicitação de consentimento: {str(e)}"
        )

@router.post("/grant")
async def grant_consent(action: ConsentAction) -> Dict:
    """
    Registra a concessão do consentimento
    """
    success = consent_manager.grant_consent(
        consent_id=action.consent_id,
        parent_id=action.parent_id
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

@router.post("/revoke")
async def revoke_consent(action: ConsentAction) -> Dict:
    """
    Revoga um consentimento existente
    """
    success = consent_manager.revoke_consent(
        consent_id=action.consent_id,
        parent_id=action.parent_id
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

@router.get("/status/{consent_id}")
async def check_consent_status(consent_id: str) -> Dict:
    """
    Verifica o status de um consentimento
    """
    status = consent_manager.check_consent_status(consent_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Consentimento não encontrado"
        )
        
    return {
        "status": "success",
        "consent_data": status
    } 