#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 Integração PIX - TarefaMágica
Módulo completo para integração com PIX, incluindo geração de QR Code,
validação de transações e relatórios financeiros
"""

import json
import hashlib
import hmac
import base64
import requests
import qrcode
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import os
import logging

@dataclass
class PIXTransaction:
    """Estrutura de transação PIX"""
    transaction_id: str
    parent_id: str
    child_id: str
    amount: float
    description: str
    qr_code: str
    status: str  # pending, confirmed, failed, cancelled
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None

class PIXIntegration:
    """Integração completa com PIX"""
    
    def __init__(self, config_path: str = "workflow/config/pix_config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.transactions: Dict[str, PIXTransaction] = {}
        
        # Configurações PIX
        self.config = self._load_config()
        self.merchant_id = self.config.get("merchant_id", "test_merchant")
        self.pix_key = self.config.get("pix_key", "test@tarefamagica.com")
        self.pix_key_type = self.config.get("pix_key_type", "email")
        self.api_url = self.config.get("api_url", "https://api.pix.example.com")
        self.api_key = self.config.get("api_key", "test_api_key")
        
        # Limites de segurança
        self.max_amount = self.config.get("max_amount", 10.00)
        self.daily_limit = self.config.get("daily_limit", 50.00)
        self.monthly_limit = self.config.get("monthly_limit", 200.00)
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Carrega configuração PIX"""
        default_config = {
            "merchant_id": "tarefamagica_merchant",
            "pix_key": "pix@tarefamagica.com",
            "pix_key_type": "email",
            "api_url": "https://api.pix.example.com",
            "api_key": "your_api_key_here",
            "max_amount": 10.00,
            "daily_limit": 50.00,
            "monthly_limit": 200.00,
            "webhook_url": "https://tarefamagica.com/webhook/pix",
            "environment": "sandbox"  # sandbox, production
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Cria arquivo de configuração padrão
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração PIX: {e}")
            return default_config
    
    def _setup_logging(self):
        """Configura logging para PIX"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/pix_integration.log'),
                logging.StreamHandler()
            ]
        )
    
    def create_pix_transaction(self, parent_id: str, child_id: str, amount: float, 
                             description: str) -> Dict[str, Any]:
        """Cria nova transação PIX"""
        try:
            # Validações básicas
            if amount <= 0:
                return {
                    "success": False,
                    "error": "Valor deve ser maior que zero"
                }
            
            if amount > 100:  # Limite máximo de R$ 100
                return {
                    "success": False,
                    "error": "Valor máximo permitido é R$ 100,00"
                }
            
            # Valida transação
            validation = self._validate_transaction(parent_id, child_id, amount)
            if not validation["success"]:
                return validation
            
            # Gera ID único da transação
            transaction_id = f"pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(f'{parent_id}{child_id}{amount}'.encode()).hexdigest()[:8]}"
            
            # Gera QR Code PIX
            qr_code_data = self._generate_pix_qr_code(transaction_id, amount, description)
            
            # Cria transação
            transaction = PIXTransaction(
                transaction_id=transaction_id,
                parent_id=parent_id,
                child_id=child_id,
                amount=amount,
                description=description,
                qr_code=qr_code_data["qr_code"],
                status="pending",
                created_at=datetime.now(),
                pix_key=self.pix_key,
                pix_key_type=self.pix_key_type
            )
            
            # Salva transação
            self.transactions[transaction_id] = transaction
            self._save_transaction(transaction)
            
            self.logger.info(f"Transação PIX criada: {transaction_id} - R$ {amount:.2f}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "qr_code": qr_code_data["qr_code"],
                "qr_code_image": qr_code_data["qr_code_image"],
                "amount": amount,
                "status": "pending"
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao criar transação PIX: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_transaction(self, parent_id: str, child_id: str, amount: float) -> Dict[str, Any]:
        """Valida transação antes de criar"""
        # Valida valor máximo
        if amount > self.max_amount:
            return {
                "success": False,
                "error": f"Valor máximo permitido é R$ {self.max_amount:.2f}"
            }
        
        # Valida limite diário
        daily_total = self._get_daily_total(parent_id)
        if daily_total + amount > self.daily_limit:
            return {
                "success": False,
                "error": f"Limite diário excedido. Disponível: R$ {self.daily_limit - daily_total:.2f}"
            }
        
        # Valida limite mensal
        monthly_total = self._get_monthly_total(parent_id)
        if monthly_total + amount > self.monthly_limit:
            return {
                "success": False,
                "error": f"Limite mensal excedido. Disponível: R$ {self.monthly_limit - monthly_total:.2f}"
            }
        
        return {"success": True, "error": None}
    
    def _generate_pix_qr_code(self, transaction_id: str, amount: float, description: str) -> Dict[str, str]:
        """Gera QR Code PIX"""
        # Estrutura PIX (formato simplificado para exemplo)
        pix_data = {
            "merchant_id": self.merchant_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "description": description,
            "pix_key": self.pix_key,
            "pix_key_type": self.pix_key_type
        }
        
        # Gera QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(pix_data))
        qr.make(fit=True)
        
        # Salva imagem do QR Code
        qr_image_path = f"outputs/pix_qr_{transaction_id}.png"
        os.makedirs("outputs", exist_ok=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_image_path)
        
        return {
            "qr_code": json.dumps(pix_data),
            "qr_code_image": qr_image_path
        }
    
    def check_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Verifica status da transação PIX"""
        try:
            if transaction_id not in self.transactions:
                return {
                    "success": False,
                    "error": "Transação não encontrada"
                }
            
            transaction = self.transactions[transaction_id]
            
            # Em produção, faria chamada para API do banco
            # Aqui simula verificação
            status = self._simulate_status_check(transaction)
            
            # Atualiza status se necessário
            if status != transaction.status:
                transaction.status = status
                if status == "confirmed":
                    transaction.confirmed_at = datetime.now()
                self._save_transaction(transaction)
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": status,
                "amount": transaction.amount,
                "created_at": transaction.created_at.isoformat(),
                "confirmed_at": transaction.confirmed_at.isoformat() if transaction.confirmed_at else None
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar status da transação {transaction_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _simulate_status_check(self, transaction: PIXTransaction) -> str:
        """Simula verificação de status (em produção seria API real)"""
        # Simula que transações criadas há mais de 5 minutos são confirmadas
        if (datetime.now() - transaction.created_at).total_seconds() > 300:  # 5 minutos
            return "confirmed"
        return transaction.status
    
    def cancel_transaction(self, transaction_id: str, parent_id: str) -> Dict[str, Any]:
        """Cancela transação PIX"""
        try:
            if transaction_id not in self.transactions:
                return {
                    "success": False,
                    "error": "Transação não encontrada"
                }
            
            transaction = self.transactions[transaction_id]
            
            # Verifica se o pai pode cancelar
            if transaction.parent_id != parent_id:
                return {
                    "success": False,
                    "error": "Não autorizado a cancelar esta transação"
                }
            
            # Verifica se pode ser cancelada
            if transaction.status not in ["pending"]:
                return {
                    "success": False,
                    "error": f"Transação não pode ser cancelada no status: {transaction.status}"
                }
            
            # Cancela transação
            transaction.status = "cancelled"
            self._save_transaction(transaction)
            
            self.logger.info(f"Transação PIX cancelada: {transaction_id}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "cancelled",
                "message": "Transação cancelada com sucesso"
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao cancelar transação {transaction_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transaction_history(self, parent_id: str, limit: int = 50) -> Dict[str, Any]:
        """Obtém histórico de transações"""
        try:
            user_transactions = [
                {
                    "transaction_id": t.transaction_id,
                    "amount": t.amount,
                    "description": t.description,
                    "status": t.status,
                    "created_at": t.created_at.isoformat(),
                    "confirmed_at": t.confirmed_at.isoformat() if t.confirmed_at else None
                }
                for t in self.transactions.values()
                if t.parent_id == parent_id
            ]
            
            # Ordena por data de criação (mais recente primeiro)
            user_transactions.sort(key=lambda x: x["created_at"], reverse=True)
            
            return {
                "success": True,
                "transactions": user_transactions[:limit],
                "total": len(user_transactions)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de transações: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_financial_report(self, parent_id: str, start_date: datetime, 
                                end_date: datetime) -> Dict[str, Any]:
        """Gera relatório financeiro"""
        try:
            # Filtra transações do período
            period_transactions = [
                t for t in self.transactions.values()
                if t.parent_id == parent_id and start_date <= t.created_at <= end_date
            ]
            
            # Calcula estatísticas
            total_amount = sum(t.amount for t in period_transactions)
            confirmed_amount = sum(t.amount for t in period_transactions if t.status == "confirmed")
            pending_amount = sum(t.amount for t in period_transactions if t.status == "pending")
            cancelled_amount = sum(t.amount for t in period_transactions if t.status == "cancelled")
            
            # Conta transações por status
            status_counts = {}
            for t in period_transactions:
                status_counts[t.status] = status_counts.get(t.status, 0) + 1
            
            report = {
                "parent_id": parent_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_transactions": len(period_transactions),
                    "total_amount": total_amount,
                    "confirmed_amount": confirmed_amount,
                    "pending_amount": pending_amount,
                    "cancelled_amount": cancelled_amount
                },
                "status_breakdown": status_counts,
                "transactions": [
                    {
                        "transaction_id": t.transaction_id,
                        "amount": t.amount,
                        "description": t.description,
                        "status": t.status,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in period_transactions
                ]
            }
            
            # Salva relatório
            report_file = f"outputs/financial_report_{parent_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
            os.makedirs("outputs", exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "report": report,
                "report_file": report_file
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório financeiro: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_daily_total(self, parent_id: str) -> float:
        """Calcula total diário de transações"""
        today = datetime.now().date()
        daily_transactions = [
            t.amount for t in self.transactions.values()
            if t.parent_id == parent_id and t.created_at.date() == today
        ]
        return sum(daily_transactions)
    
    def _get_monthly_total(self, parent_id: str) -> float:
        """Calcula total mensal de transações"""
        current_month = datetime.now().replace(day=1).date()
        monthly_transactions = [
            t.amount for t in self.transactions.values()
            if t.parent_id == parent_id and t.created_at.date() >= current_month
        ]
        return sum(monthly_transactions)
    
    def _save_transaction(self, transaction: PIXTransaction):
        """Salva transação em arquivo"""
        try:
            transactions_file = "outputs/pix_transactions.json"
            os.makedirs("outputs", exist_ok=True)
            
            # Carrega transações existentes
            transactions_data = {}
            if os.path.exists(transactions_file):
                with open(transactions_file, 'r', encoding='utf-8') as f:
                    transactions_data = json.load(f)
            
            # Adiciona/atualiza transação
            transactions_data[transaction.transaction_id] = {
                "transaction_id": transaction.transaction_id,
                "parent_id": transaction.parent_id,
                "child_id": transaction.child_id,
                "amount": transaction.amount,
                "description": transaction.description,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat(),
                "confirmed_at": transaction.confirmed_at.isoformat() if transaction.confirmed_at else None,
                "pix_key": transaction.pix_key,
                "pix_key_type": transaction.pix_key_type
            }
            
            # Salva arquivo
            with open(transactions_file, 'w', encoding='utf-8') as f:
                json.dump(transactions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar transação: {e}")

def main():
    """Função principal para testes"""
    print("💰 TESTE DE INTEGRAÇÃO PIX - TarefaMágica")
    print("=" * 50)
    
    # Inicializa integração PIX
    pix = PIXIntegration()
    
    # Testa criação de transação
    print("1. Criando transação PIX...")
    result = pix.create_pix_transaction(
        parent_id="parent_001",
        child_id="child_001",
        amount=5.00,
        description="Recompensa por tarefas"
    )
    
    if result["success"]:
        print(f"✅ Transação criada: {result['transaction_id']}")
        print(f"   QR Code gerado: {result['qr_code_image']}")
        
        # Testa verificação de status
        print("\n2. Verificando status da transação...")
        status_result = pix.check_transaction_status(result["transaction_id"])
        if status_result["success"]:
            print(f"✅ Status: {status_result['status']}")
        
        # Testa histórico
        print("\n3. Gerando histórico...")
        history_result = pix.get_transaction_history("parent_001")
        if history_result["success"]:
            print(f"✅ Histórico: {history_result['total']} transações")
        
        # Testa relatório financeiro
        print("\n4. Gerando relatório financeiro...")
        report_result = pix.generate_financial_report(
            parent_id="parent_001",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        if report_result["success"]:
            print(f"✅ Relatório gerado: {report_result['report_file']}")
    
    else:
        print(f"❌ Erro: {result['error']}")

if __name__ == "__main__":
    main() 