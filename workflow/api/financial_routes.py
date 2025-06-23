"""
Rotas da API para sistema financeiro
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from ..security.financial_security import FinancialSecurity, Transaction, TransactionStatus, RiskLevel
from .mobile_security import get_api_key
from ..security.input_validation import InputValidation

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

@router.post("/validate-transaction")
async def validate_transaction(
    request: Dict
) -> Dict:
    """
    Valida transação PIX antes da execução
    
    Body:
        user_id: str
        amount: float
        recipient: str
        description: str
        pix_key: str
        pix_key_type: str
    """
    try:
        # Validação dos dados de entrada
        if not request:
            return {
                "success": False,
                "error": "Dados obrigatórios não fornecidos"
            }, 400
            
        # Validação dos campos obrigatórios
        required_fields = ['user_id', 'amount', 'recipient', 'description', 'pix_key', 'pix_key_type']
        for field in required_fields:
            if field not in request:
                return {
                    "success": False,
                    "error": f"Campo obrigatório ausente: {field}"
                }, 400
        
        # Sanitização dos dados
        user_id = InputValidation.sanitize_string(request['user_id'], max_length=100)
        amount = InputValidation.sanitize_float(request['amount'], min_value=0.01, max_value=10000.0)
        recipient = InputValidation.sanitize_string(request['recipient'], max_length=200)
        description = InputValidation.sanitize_string(request['description'], max_length=500)
        pix_key = InputValidation.sanitize_string(request['pix_key'], max_length=100)
        pix_key_type = InputValidation.sanitize_string(request['pix_key_type'], max_length=20)
        
        # Validação de tipos de chave PIX permitidos
        allowed_key_types = ['cpf', 'cnpj', 'email', 'phone', 'random']
        if pix_key_type not in allowed_key_types:
            return {
                "success": False,
                "error": f"Tipo de chave PIX inválido. Tipos permitidos: {', '.join(allowed_key_types)}"
            }, 400
        
        # Valida transação
        validation_result = financial_security.validate_transaction(
            user_id=user_id,
            amount=amount,
            recipient=recipient,
            description=description,
            pix_key=pix_key,
            pix_key_type=pix_key_type
        )
        
        return {
            "success": True,
            "validation": {
                "approved": validation_result.approved,
                "risk_level": validation_result.risk_level.value,
                "risk_score": validation_result.risk_score,
                "warnings": validation_result.warnings,
                "recommendations": validation_result.recommendations
            }
        }, 200
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }, 400
    except Exception as e:
        logging.error(f"Erro ao validar transação: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno do servidor"
        }, 500

@router.post("/process-transaction")
async def process_transaction(
    request: Dict
) -> Dict:
    """
    Processa transação PIX com validação de segurança
    
    Body:
        user_id: str
        amount: float
        recipient: str
        description: str
        pix_key: str
        pix_key_type: str
        force_approval: bool (opcional)
    """
    try:
        # Validação dos dados de entrada
        if not request:
            return {
                "success": False,
                "error": "Dados obrigatórios não fornecidos"
            }, 400
            
        # Validação dos campos obrigatórios
        required_fields = ['user_id', 'amount', 'recipient', 'description', 'pix_key', 'pix_key_type']
        for field in required_fields:
            if field not in request:
                return {
                    "success": False,
                    "error": f"Campo obrigatório ausente: {field}"
                }, 400
        
        # Sanitização dos dados
        user_id = InputValidation.sanitize_string(request['user_id'], max_length=100)
        amount = InputValidation.sanitize_float(request['amount'], min_value=0.01, max_value=10000.0)
        recipient = InputValidation.sanitize_string(request['recipient'], max_length=200)
        description = InputValidation.sanitize_string(request['description'], max_length=500)
        pix_key = InputValidation.sanitize_string(request['pix_key'], max_length=100)
        pix_key_type = InputValidation.sanitize_string(request['pix_key_type'], max_length=20)
        force_approval = request.get('force_approval', False)
        
        # Validação de tipos de chave PIX permitidos
        allowed_key_types = ['cpf', 'cnpj', 'email', 'phone', 'random']
        if pix_key_type not in allowed_key_types:
            return {
                "success": False,
                "error": f"Tipo de chave PIX inválido. Tipos permitidos: {', '.join(allowed_key_types)}"
            }, 400
        
        # Processa transação
        transaction_result = financial_security.process_transaction(
            user_id=user_id,
            amount=amount,
            recipient=recipient,
            description=description,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
            force_approval=force_approval
        )
        
        if transaction_result.approved:
            return {
                "success": True,
                "transaction": {
                    "transaction_id": transaction_result.transaction_id,
                    "user_id": transaction_result.user_id,
                    "amount": transaction_result.amount,
                    "recipient": transaction_result.recipient,
                    "status": transaction_result.status.value,
                    "risk_level": transaction_result.risk_level.value,
                    "created_at": transaction_result.created_at.isoformat(),
                    "pix_code": transaction_result.pix_code
                }
            }, 201
        else:
            return {
                "success": False,
                "error": "Transação rejeitada por questões de segurança",
                "details": {
                    "risk_level": transaction_result.risk_level.value,
                    "risk_score": transaction_result.risk_score,
                    "warnings": transaction_result.warnings,
                    "recommendations": transaction_result.recommendations
                }
            }, 400
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }, 400
    except Exception as e:
        logging.error(f"Erro ao processar transação: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno do servidor"
        }, 500

@router.get("/transactions/{user_id}")
async def get_user_transactions(
    user_id: str,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Obtém histórico de transações de um usuário
    
    Query params:
        status: str (opcional)
        start_date: str (opcional)
        end_date: str (opcional)
        limit: int (padrão: 50)
        offset: int (padrão: 0)
    """
    try:
        # Sanitização do user_id
        user_id = InputValidation.sanitize_string(user_id, max_length=100)
        
        # Sanitização dos parâmetros
        if status:
            status = InputValidation.sanitize_string(status, max_length=20)
        
        try:
            limit = InputValidation.sanitize_int(limit, min_value=1, max_value=100)
            offset = InputValidation.sanitize_int(offset, min_value=0)
        except ValueError:
            return {
                "success": False,
                "error": "Parâmetros limit e offset devem ser números inteiros"
            }, 400
        
        # Processamento das datas
        start_date = None
        end_date = None
        
        if start_date:
            try:
                start_date = InputValidation.sanitize_string(start_date)
            except ValueError:
                return {
                    "success": False,
                    "error": "Formato de data inválido para start_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }, 400
        
        if end_date:
            try:
                end_date = InputValidation.sanitize_string(end_date)
            except ValueError:
                return {
                    "success": False,
                    "error": "Formato de data inválido para end_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }, 400
        
        # Obtém transações
        transactions = financial_security.get_user_transactions(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "user_id": t.user_id,
                    "amount": t.amount,
                    "recipient": t.recipient,
                    "description": t.description,
                    "status": t.status.value,
                    "risk_level": t.risk_level.value,
                    "risk_score": t.risk_score,
                    "created_at": t.created_at.isoformat(),
                    "pix_code": t.pix_code,
                    "warnings": t.warnings
                }
                for t in transactions
            ]
        }, 200
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }, 400
    except Exception as e:
        logging.error(f"Erro ao obter transações: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno do servidor"
        }, 500

@router.post("/risk-assessment")
async def assess_risk(
    request: Dict
) -> Dict:
    """
    Avalia risco de uma transação
    
    Body:
        user_id: str
        amount: float
        recipient: str
        pix_key: str
        pix_key_type: str
    """
    try:
        # Validação dos dados de entrada
        if not request:
            return {
                "success": False,
                "error": "Dados obrigatórios não fornecidos"
            }, 400
            
        # Validação dos campos obrigatórios
        required_fields = ['user_id', 'amount', 'recipient', 'pix_key', 'pix_key_type']
        for field in required_fields:
            if field not in request:
                return {
                    "success": False,
                    "error": f"Campo obrigatório ausente: {field}"
                }, 400
        
        # Sanitização dos dados
        user_id = InputValidation.sanitize_string(request['user_id'], max_length=100)
        amount = InputValidation.sanitize_float(request['amount'], min_value=0.01, max_value=10000.0)
        recipient = InputValidation.sanitize_string(request['recipient'], max_length=200)
        pix_key = InputValidation.sanitize_string(request['pix_key'], max_length=100)
        pix_key_type = InputValidation.sanitize_string(request['pix_key_type'], max_length=20)
        
        # Validação de tipos de chave PIX permitidos
        allowed_key_types = ['cpf', 'cnpj', 'email', 'phone', 'random']
        if pix_key_type not in allowed_key_types:
            return {
                "success": False,
                "error": f"Tipo de chave PIX inválido. Tipos permitidos: {', '.join(allowed_key_types)}"
            }, 400
        
        # Avalia risco
        risk_assessment = financial_security.assess_risk(
            user_id=user_id,
            amount=amount,
            recipient=recipient,
            pix_key=pix_key,
            pix_key_type=pix_key_type
        )
        
        return {
            "success": True,
            "risk_assessment": {
                "risk_level": risk_assessment.risk_level.value,
                "risk_score": risk_assessment.risk_score,
                "factors": risk_assessment.factors,
                "warnings": risk_assessment.warnings,
                "recommendations": risk_assessment.recommendations
            }
        }, 200
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }, 400
    except Exception as e:
        logging.error(f"Erro ao avaliar risco: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno do servidor"
        }, 500

@router.get("/limits/{user_id}")
async def get_user_limits(
    user_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict:
    """
    Obtém limites financeiros de um usuário
    """
    try:
        # Sanitização do user_id
        user_id = InputValidation.sanitize_string(user_id, max_length=100)
        
        # Obtém limites
        limits = financial_security.get_user_limits(user_id)
        
        return {
            "success": True,
            "limits": {
                "daily_limit": limits.daily_limit,
                "monthly_limit": limits.monthly_limit,
                "single_transaction_limit": limits.single_transaction_limit,
                "daily_used": limits.daily_used,
                "monthly_used": limits.monthly_used,
                "daily_remaining": limits.daily_remaining,
                "monthly_remaining": limits.monthly_remaining
            }
        }, 200
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }, 400
    except Exception as e:
        logging.error(f"Erro ao obter limites: {str(e)}")
        return {
            "success": False,
            "error": "Erro interno do servidor"
        }, 500 