"""
Rotas da API para sistema financeiro
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from ..security.financial_security import FinancialSecurity, Transaction, TransactionStatus, RiskLevel
from .mobile_security import get_api_key

router = APIRouter(prefix="/financial", tags=["financial"])
financial_security = FinancialSecurity()

class CreateTransactionRequest(BaseModel):
    parent_id: str
    child_id: str
    amount: float
    pix_key: str
    description: str

class ApproveTransactionRequest(BaseModel):
    transaction_id: str
    parent_id: str

class RejectTransactionRequest(BaseModel):
    transaction_id: str
    parent_id: str
    reason: str

class TransactionResponse(BaseModel):
    transaction_id: str
    parent_id: str
    child_id: str
    amount: float
    pix_key: str
    description: str
    status: str
    risk_level: str
    created_at: str
    approved_at: Optional[str] = None
    rejected_at: Optional[str] = None
    rejection_reason: Optional[str] = None

@router.post("/transaction/create")
async def create_transaction(
    request: CreateTransactionRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Cria uma nova transação PIX
    """
    try:
        transaction = financial_security.create_transaction(
            parent_id=request.parent_id,
            child_id=request.child_id,
            amount=request.amount,
            pix_key=request.pix_key,
            description=request.description
        )
        
        return {
            "status": "success",
            "message": "Transação criada com sucesso",
            "transaction": {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "risk_level": transaction.risk_level.value,
                "status": transaction.status.value
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar transação: {str(e)}"
        )

@router.post("/transaction/approve")
async def approve_transaction(
    request: ApproveTransactionRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Aprova uma transação
    """
    try:
        success = financial_security.approve_transaction(
            transaction_id=request.transaction_id,
            parent_id=request.parent_id
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Falha ao aprovar transação"
            )
            
        return {
            "status": "success",
            "message": "Transação aprovada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao aprovar transação: {str(e)}"
        )

@router.post("/transaction/reject")
async def reject_transaction(
    request: RejectTransactionRequest,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Rejeita uma transação
    """
    try:
        success = financial_security.reject_transaction(
            transaction_id=request.transaction_id,
            parent_id=request.parent_id,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Falha ao rejeitar transação"
            )
            
        return {
            "status": "success",
            "message": "Transação rejeitada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao rejeitar transação: {str(e)}"
        )

@router.get("/transaction/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> TransactionResponse:
    """
    Obtém detalhes de uma transação
    """
    try:
        transaction = financial_security._load_transaction(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transação não encontrada"
            )
            
        if transaction.parent_id != parent_id:
            raise HTTPException(
                status_code=403,
                detail="Acesso não autorizado"
            )
            
        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            parent_id=transaction.parent_id,
            child_id=transaction.child_id,
            amount=transaction.amount,
            pix_key=transaction.pix_key,
            description=transaction.description,
            status=transaction.status.value,
            risk_level=transaction.risk_level.value,
            created_at=transaction.created_at.isoformat(),
            approved_at=transaction.approved_at.isoformat() if transaction.approved_at else None,
            rejected_at=transaction.rejected_at.isoformat() if transaction.rejected_at else None,
            rejection_reason=transaction.rejection_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter transação: {str(e)}"
        )

@router.get("/history/{parent_id}")
async def get_transaction_history(
    parent_id: str,
    days: int = 30,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Obtém histórico de transações
    """
    try:
        transactions = financial_security.get_transaction_history(parent_id, days)
        
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                "transaction_id": transaction.transaction_id,
                "child_id": transaction.child_id,
                "amount": transaction.amount,
                "pix_key": transaction.pix_key,
                "description": transaction.description,
                "status": transaction.status.value,
                "risk_level": transaction.risk_level.value,
                "created_at": transaction.created_at.isoformat(),
                "approved_at": transaction.approved_at.isoformat() if transaction.approved_at else None,
                "rejected_at": transaction.rejected_at.isoformat() if transaction.rejected_at else None,
                "rejection_reason": transaction.rejection_reason
            })
            
        return {
            "status": "success",
            "parent_id": parent_id,
            "days": days,
            "total_transactions": len(transaction_list),
            "transactions": transaction_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter histórico: {str(e)}"
        )

@router.get("/limits/{parent_id}")
async def get_limits(
    parent_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Obtém limites e estatísticas financeiras
    """
    try:
        # Calcula totais
        daily_total = financial_security._get_daily_total(parent_id)
        recent_transactions = financial_security._get_recent_transactions(parent_id, hours=24)
        
        # Obtém regras de risco
        risk_rules = financial_security.risk_rules
        
        return {
            "status": "success",
            "parent_id": parent_id,
            "limits": {
                "max_daily_amount": risk_rules["max_daily_amount"],
                "max_transaction_amount": risk_rules["max_transaction_amount"],
                "max_monthly_amount": risk_rules["max_monthly_amount"]
            },
            "current_usage": {
                "daily_total": daily_total,
                "daily_remaining": risk_rules["max_daily_amount"] - daily_total,
                "transactions_today": len(recent_transactions)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter limites: {str(e)}"
        ) 