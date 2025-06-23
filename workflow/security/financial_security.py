"""
Módulo de Segurança Financeira - TarefaMágica
Implementa proteção para transações PIX e sistema de recompensas
"""

import hashlib
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TransactionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Transaction:
    transaction_id: str
    parent_id: str
    child_id: str
    amount: float
    pix_key: str
    description: str
    status: TransactionStatus
    risk_level: RiskLevel
    created_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

class FinancialSecurity:
    def __init__(self, storage_path: str = "data/financial"):
        """
        Inicializa o sistema de segurança financeira
        
        Args:
            storage_path: Caminho para armazenamento dos dados financeiros
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._load_risk_rules()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "transactions"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "logs"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para auditoria financeira"""
        log_path = os.path.join(self.storage_path, "logs", "financial_audit.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_risk_rules(self):
        """Carrega regras de risco para transações"""
        self.risk_rules = {
            "max_daily_amount": 100.0,  # R$ 100 por dia
            "max_transaction_amount": 50.0,  # R$ 50 por transação
            "max_monthly_amount": 500.0,  # R$ 500 por mês
            "suspicious_patterns": [
                "multiple_small_transactions",
                "unusual_hours",
                "new_pix_key",
                "high_frequency"
            ]
        }
        
    def create_transaction(
        self,
        parent_id: str,
        child_id: str,
        amount: float,
        pix_key: str,
        description: str
    ) -> Transaction:
        """
        Cria uma nova transação com validações de segurança
        
        Args:
            parent_id: ID do responsável
            child_id: ID da criança
            amount: Valor da transação
            pix_key: Chave PIX
            description: Descrição da transação
            
        Returns:
            Transaction: Transação criada
        """
        try:
            # Gera ID único para transação
            transaction_id = f"tx_{int(time.time())}_{secrets.token_hex(4)}"
            
            # Validações básicas
            if amount <= 0:
                raise ValueError("Valor da transação deve ser positivo")
                
            if amount > self.risk_rules["max_transaction_amount"]:
                raise ValueError(f"Valor máximo por transação: R$ {self.risk_rules['max_transaction_amount']}")
                
            # Verifica limite diário
            daily_total = self._get_daily_total(parent_id)
            if daily_total + amount > self.risk_rules["max_daily_amount"]:
                raise ValueError(f"Limite diário excedido. Disponível: R$ {self.risk_rules['max_daily_amount'] - daily_total}")
                
            # Avalia risco da transação
            risk_level = self._assess_risk(parent_id, amount, pix_key)
            
            # Cria transação
            transaction = Transaction(
                transaction_id=transaction_id,
                parent_id=parent_id,
                child_id=child_id,
                amount=amount,
                pix_key=pix_key,
                description=description,
                status=TransactionStatus.PENDING,
                risk_level=risk_level,
                created_at=datetime.utcnow()
            )
            
            # Salva transação
            self._save_transaction(transaction)
            
            # Log da transação
            logging.info(f"Transação criada: {transaction_id} - R$ {amount} - Risco: {risk_level.value}")
            
            return transaction
            
        except Exception as e:
            logging.error(f"Erro ao criar transação: {str(e)}")
            raise
            
    def _assess_risk(
        self,
        parent_id: str,
        amount: float,
        pix_key: str
    ) -> RiskLevel:
        """
        Avalia o nível de risco de uma transação
        
        Args:
            parent_id: ID do responsável
            amount: Valor da transação
            pix_key: Chave PIX
            
        Returns:
            RiskLevel: Nível de risco identificado
        """
        risk_score = 0
        
        # Verifica valor da transação
        if amount > 30.0:
            risk_score += 2
        elif amount > 20.0:
            risk_score += 1
            
        # Verifica frequência de transações
        recent_transactions = self._get_recent_transactions(parent_id, hours=24)
        if len(recent_transactions) > 5:
            risk_score += 3
        elif len(recent_transactions) > 3:
            risk_score += 1
            
        # Verifica se é uma nova chave PIX
        if not self._is_known_pix_key(parent_id, pix_key):
            risk_score += 2
            
        # Verifica horário da transação
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 23:
            risk_score += 1
            
        # Determina nível de risco
        if risk_score >= 5:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
            
    def approve_transaction(self, transaction_id: str, parent_id: str) -> bool:
        """
        Aprova uma transação
        
        Args:
            transaction_id: ID da transação
            parent_id: ID do responsável
            
        Returns:
            bool: True se aprovada com sucesso
        """
        try:
            transaction = self._load_transaction(transaction_id)
            
            if not transaction:
                return False
                
            if transaction.parent_id != parent_id:
                logging.warning(f"Tentativa não autorizada de aprovar transação: {transaction_id}")
                return False
                
            if transaction.status != TransactionStatus.PENDING:
                return False
                
            # Atualiza status
            transaction.status = TransactionStatus.APPROVED
            transaction.approved_at = datetime.utcnow()
            
            # Salva transação
            self._save_transaction(transaction)
            
            # Log da aprovação
            logging.info(f"Transação aprovada: {transaction_id} - R$ {transaction.amount}")
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao aprovar transação: {str(e)}")
            return False
            
    def reject_transaction(
        self,
        transaction_id: str,
        parent_id: str,
        reason: str
    ) -> bool:
        """
        Rejeita uma transação
        
        Args:
            transaction_id: ID da transação
            parent_id: ID do responsável
            reason: Motivo da rejeição
            
        Returns:
            bool: True se rejeitada com sucesso
        """
        try:
            transaction = self._load_transaction(transaction_id)
            
            if not transaction:
                return False
                
            if transaction.parent_id != parent_id:
                logging.warning(f"Tentativa não autorizada de rejeitar transação: {transaction_id}")
                return False
                
            if transaction.status != TransactionStatus.PENDING:
                return False
                
            # Atualiza status
            transaction.status = TransactionStatus.REJECTED
            transaction.rejected_at = datetime.utcnow()
            transaction.rejection_reason = reason
            
            # Salva transação
            self._save_transaction(transaction)
            
            # Log da rejeição
            logging.info(f"Transação rejeitada: {transaction_id} - Motivo: {reason}")
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao rejeitar transação: {str(e)}")
            return False
            
    def get_transaction_history(
        self,
        parent_id: str,
        days: int = 30
    ) -> List[Transaction]:
        """
        Obtém histórico de transações
        
        Args:
            parent_id: ID do responsável
            days: Número de dias para buscar
            
        Returns:
            List[Transaction]: Lista de transações
        """
        try:
            transactions = []
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Busca transações no período
            for filename in os.listdir(os.path.join(self.storage_path, "transactions")):
                if filename.startswith(f"tx_{parent_id}_"):
                    transaction = self._load_transaction_from_file(filename)
                    if transaction and transaction.created_at >= cutoff_date:
                        transactions.append(transaction)
                        
            # Ordena por data de criação
            transactions.sort(key=lambda x: x.created_at, reverse=True)
            
            return transactions
            
        except Exception as e:
            logging.error(f"Erro ao buscar histórico: {str(e)}")
            return []
            
    def _save_transaction(self, transaction: Transaction):
        """Salva transação em arquivo"""
        filename = f"{transaction.transaction_id}.json"
        filepath = os.path.join(self.storage_path, "transactions", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._transaction_to_dict(transaction), f, indent=2, default=str)
            
    def _load_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Carrega transação por ID"""
        filename = f"{transaction_id}.json"
        return self._load_transaction_from_file(filename)
        
    def _load_transaction_from_file(self, filename: str) -> Optional[Transaction]:
        """Carrega transação de arquivo"""
        try:
            filepath = os.path.join(self.storage_path, "transactions", filename)
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return self._dict_to_transaction(data)
            
        except Exception as e:
            logging.error(f"Erro ao carregar transação: {str(e)}")
            return None
            
    def _transaction_to_dict(self, transaction: Transaction) -> Dict:
        """Converte transação para dicionário"""
        return {
            "transaction_id": transaction.transaction_id,
            "parent_id": transaction.parent_id,
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
        }
        
    def _dict_to_transaction(self, data: Dict) -> Transaction:
        """Converte dicionário para transação"""
        return Transaction(
            transaction_id=data["transaction_id"],
            parent_id=data["parent_id"],
            child_id=data["child_id"],
            amount=data["amount"],
            pix_key=data["pix_key"],
            description=data["description"],
            status=TransactionStatus(data["status"]),
            risk_level=RiskLevel(data["risk_level"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            approved_at=datetime.fromisoformat(data["approved_at"]) if data["approved_at"] else None,
            rejected_at=datetime.fromisoformat(data["rejected_at"]) if data["rejected_at"] else None,
            rejection_reason=data["rejection_reason"]
        )
        
    def _get_daily_total(self, parent_id: str) -> float:
        """Calcula total de transações do dia"""
        today = datetime.utcnow().date()
        transactions = self._get_recent_transactions(parent_id, hours=24)
        
        return sum(t.amount for t in transactions if t.created_at.date() == today)
        
    def _get_recent_transactions(self, parent_id: str, hours: int) -> List[Transaction]:
        """Obtém transações recentes"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        transactions = []
        
        for filename in os.listdir(os.path.join(self.storage_path, "transactions")):
            if filename.startswith(f"tx_{parent_id}_"):
                transaction = self._load_transaction_from_file(filename)
                if transaction and transaction.created_at >= cutoff_time:
                    transactions.append(transaction)
                    
        return transactions
        
    def _is_known_pix_key(self, parent_id: str, pix_key: str) -> bool:
        """Verifica se chave PIX é conhecida"""
        transactions = self.get_transaction_history(parent_id, days=90)
        return any(t.pix_key == pix_key for t in transactions) 