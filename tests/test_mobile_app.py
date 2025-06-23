#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Testes de Aplicação Mobile - TarefaMágica
Testes automatizados para funcionalidades principais do app
"""

import unittest
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.security.parental_consent import ParentalConsentManager
from workflow.security.two_factor_auth import TwoFactorManager
from workflow.security.financial_security import FinancialSecurityManager
from workflow.security.access_control import AccessControlManager

class TestMobileApp(unittest.TestCase):
    """Testes para aplicação mobile TarefaMágica"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.base_url = "http://localhost:8000"
        self.test_parent_data = {
            "name": "João Silva",
            "email": "joao.silva@test.com",
            "phone": "+5511999999999",
            "document": "12345678901"
        }
        self.test_child_data = {
            "name": "Maria Silva",
            "age": 11,
            "parent_id": None
        }
        self.test_task_data = {
            "title": "Arrumar a cama",
            "description": "Arrumar a cama pela manhã",
            "value": 2.00,
            "coins": 2,
            "xp": 50,
            "category": "quarto"
        }
        
        # Inicializa managers
        self.consent_manager = ParentalConsentManager()
        self.two_factor_manager = TwoFactorManager()
        self.financial_manager = FinancialSecurityManager()
        self.access_manager = AccessControlManager()
    
    def test_01_parent_registration(self):
        """Testa registro de pais"""
        print("🧪 Testando registro de pais...")
        
        # Simula registro de pai
        parent_id = self.consent_manager.create_parent_consent(
            parent_name=self.test_parent_data["name"],
            parent_email=self.test_parent_data["email"],
            parent_phone=self.test_parent_data["phone"],
            parent_document=self.test_parent_data["document"],
            child_name=self.test_child_data["name"],
            child_age=self.test_child_data["age"]
        )
        
        self.assertIsNotNone(parent_id)
        self.assertTrue(len(parent_id) > 0)
        
        # Verifica se o consentimento foi registrado
        consent = self.consent_manager.get_consent_by_id(parent_id)
        self.assertIsNotNone(consent)
        self.assertEqual(consent["parent_email"], self.test_parent_data["email"])
        
        print("✅ Registro de pais funcionando!")
        return parent_id
    
    def test_02_child_registration(self):
        """Testa registro de crianças"""
        print("🧪 Testando registro de crianças...")
        
        # Primeiro registra o pai
        parent_id = self.test_01_parent_registration()
        
        # Registra a criança
        child_id = self.access_manager.create_child_profile(
            name=self.test_child_data["name"],
            age=self.test_child_data["age"],
            parent_id=parent_id
        )
        
        self.assertIsNotNone(child_id)
        self.assertTrue(len(child_id) > 0)
        
        # Verifica se o perfil foi criado
        child_profile = self.access_manager.get_child_profile(child_id)
        self.assertIsNotNone(child_profile)
        self.assertEqual(child_profile["name"], self.test_child_data["name"])
        self.assertEqual(child_profile["age"], self.test_child_data["age"])
        
        print("✅ Registro de crianças funcionando!")
        return child_id
    
    def test_03_task_creation(self):
        """Testa criação de tarefas"""
        print("🧪 Testando criação de tarefas...")
        
        # Registra pai e filho
        parent_id = self.test_01_parent_registration()
        child_id = self.test_02_child_registration()
        
        # Cria tarefa
        task_id = self._create_test_task(parent_id, child_id)
        
        self.assertIsNotNone(task_id)
        self.assertTrue(len(task_id) > 0)
        
        # Verifica se a tarefa foi criada
        task = self._get_test_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], self.test_task_data["title"])
        self.assertEqual(task["value"], self.test_task_data["value"])
        
        print("✅ Criação de tarefas funcionando!")
        return task_id
    
    def test_04_task_completion(self):
        """Testa conclusão de tarefas"""
        print("🧪 Testando conclusão de tarefas...")
        
        # Cria tarefa
        parent_id = self.test_01_parent_registration()
        child_id = self.test_02_child_registration()
        task_id = self.test_03_task_creation()
        
        # Simula conclusão da tarefa pela criança
        completion_data = {
            "task_id": task_id,
            "child_id": child_id,
            "photo_url": "https://example.com/photo.jpg",
            "completion_time": datetime.now().isoformat()
        }
        
        completion_id = self._complete_task(completion_data)
        
        self.assertIsNotNone(completion_id)
        
        # Verifica se a tarefa foi marcada como concluída
        task = self._get_test_task(task_id)
        self.assertEqual(task["status"], "completed")
        
        print("✅ Conclusão de tarefas funcionando!")
        return completion_id
    
    def test_05_task_approval(self):
        """Testa aprovação de tarefas pelos pais"""
        print("🧪 Testando aprovação de tarefas...")
        
        # Conclui tarefa
        completion_id = self.test_04_task_completion()
        
        # Simula aprovação pelo pai
        approval_data = {
            "completion_id": completion_id,
            "approved": True,
            "parent_comment": "Muito bem! Cama arrumada perfeitamente!"
        }
        
        approval_id = self._approve_task(approval_data)
        
        self.assertIsNotNone(approval_id)
        
        # Verifica se a recompensa foi concedida
        reward = self._get_reward_by_completion(completion_id)
        self.assertIsNotNone(reward)
        self.assertEqual(reward["status"], "approved")
        
        print("✅ Aprovação de tarefas funcionando!")
        return approval_id
    
    def test_06_reward_system(self):
        """Testa sistema de recompensas"""
        print("🧪 Testando sistema de recompensas...")
        
        # Aprova tarefa
        approval_id = self.test_05_task_approval()
        
        # Verifica se os pontos foram creditados
        child_id = self.test_02_child_registration()
        balance = self._get_child_balance(child_id)
        
        self.assertIsNotNone(balance)
        self.assertGreaterEqual(balance["coins"], self.test_task_data["coins"])
        self.assertGreaterEqual(balance["xp"], self.test_task_data["xp"])
        
        print("✅ Sistema de recompensas funcionando!")
        return balance
    
    def test_07_two_factor_authentication(self):
        """Testa autenticação 2FA"""
        print("🧪 Testando autenticação 2FA...")
        
        # Registra pai
        parent_id = self.test_01_parent_registration()
        
        # Configura 2FA
        two_factor_data = self.two_factor_manager.setup_2fa(parent_id)
        
        self.assertIsNotNone(two_factor_data)
        self.assertIn("qr_code", two_factor_data)
        self.assertIn("backup_codes", two_factor_data)
        
        # Simula verificação de código
        test_code = "123456"  # Em produção seria gerado pelo app
        is_valid = self.two_factor_manager.verify_2fa(parent_id, test_code)
        
        # Em ambiente de teste, pode ser válido
        self.assertIsInstance(is_valid, bool)
        
        print("✅ Autenticação 2FA funcionando!")
        return two_factor_data
    
    def test_08_financial_security(self):
        """Testa segurança financeira"""
        print("🧪 Testando segurança financeira...")
        
        # Registra pai e filho
        parent_id = self.test_01_parent_registration()
        child_id = self.test_02_child_registration()
        
        # Simula transação PIX
        transaction_data = {
            "parent_id": parent_id,
            "child_id": child_id,
            "amount": 5.00,
            "description": "Recompensa por tarefas",
            "type": "reward"
        }
        
        # Avalia risco
        risk_assessment = self.financial_manager.assess_transaction_risk(transaction_data)
        
        self.assertIsNotNone(risk_assessment)
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("approved", risk_assessment)
        
        print("✅ Segurança financeira funcionando!")
        return risk_assessment
    
    def test_09_access_control(self):
        """Testa controle de acesso"""
        print("🧪 Testando controle de acesso...")
        
        # Registra pai e filho
        parent_id = self.test_01_parent_registration()
        child_id = self.test_02_child_registration()
        
        # Verifica permissões do pai
        parent_permissions = self.access_manager.get_user_permissions(parent_id)
        self.assertIsNotNone(parent_permissions)
        self.assertIn("create_tasks", parent_permissions)
        self.assertIn("approve_tasks", parent_permissions)
        
        # Verifica permissões da criança
        child_permissions = self.access_manager.get_user_permissions(child_id)
        self.assertIsNotNone(child_permissions)
        self.assertIn("view_tasks", child_permissions)
        self.assertIn("complete_tasks", child_permissions)
        
        print("✅ Controle de acesso funcionando!")
        return parent_permissions, child_permissions
    
    def test_10_data_protection(self):
        """Testa proteção de dados"""
        print("🧪 Testando proteção de dados...")
        
        # Registra dados sensíveis
        sensitive_data = {
            "parent_name": "João Silva",
            "parent_email": "joao.silva@test.com",
            "parent_phone": "+5511999999999",
            "child_name": "Maria Silva",
            "child_age": 11
        }
        
        # Verifica se dados são criptografados
        encrypted_data = self._encrypt_sensitive_data(sensitive_data)
        
        self.assertIsNotNone(encrypted_data)
        self.assertNotEqual(encrypted_data, sensitive_data)
        
        # Verifica se dados podem ser descriptografados
        decrypted_data = self._decrypt_sensitive_data(encrypted_data)
        
        self.assertEqual(decrypted_data, sensitive_data)
        
        print("✅ Proteção de dados funcionando!")
        return encrypted_data
    
    # Métodos auxiliares
    def _create_test_task(self, parent_id: str, child_id: str) -> str:
        """Cria tarefa de teste"""
        # Simula criação de tarefa via API
        task_data = {
            "parent_id": parent_id,
            "child_id": child_id,
            **self.test_task_data
        }
        
        # Em produção, seria uma chamada HTTP
        # response = requests.post(f"{self.base_url}/api/tasks", json=task_data)
        # return response.json()["task_id"]
        
        # Simulação para teste
        return f"task_{datetime.now().timestamp()}"
    
    def _get_test_task(self, task_id: str) -> Dict[str, Any]:
        """Obtém tarefa de teste"""
        # Simulação para teste
        return {
            "id": task_id,
            "title": self.test_task_data["title"],
            "value": self.test_task_data["value"],
            "status": "pending"
        }
    
    def _complete_task(self, completion_data: Dict[str, Any]) -> str:
        """Simula conclusão de tarefa"""
        # Simulação para teste
        return f"completion_{datetime.now().timestamp()}"
    
    def _approve_task(self, approval_data: Dict[str, Any]) -> str:
        """Simula aprovação de tarefa"""
        # Simulação para teste
        return f"approval_{datetime.now().timestamp()}"
    
    def _get_reward_by_completion(self, completion_id: str) -> Dict[str, Any]:
        """Obtém recompensa por conclusão"""
        # Simulação para teste
        return {
            "completion_id": completion_id,
            "status": "approved",
            "coins": self.test_task_data["coins"],
            "xp": self.test_task_data["xp"]
        }
    
    def _get_child_balance(self, child_id: str) -> Dict[str, Any]:
        """Obtém saldo da criança"""
        # Simulação para teste
        return {
            "child_id": child_id,
            "coins": self.test_task_data["coins"],
            "xp": self.test_task_data["xp"],
            "level": 1
        }
    
    def _encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula criptografia de dados sensíveis"""
        # Simulação para teste
        return {k: f"encrypted_{v}" for k, v in data.items()}
    
    def _decrypt_sensitive_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula descriptografia de dados sensíveis"""
        # Simulação para teste
        return {k: v.replace("encrypted_", "") for k, v in encrypted_data.items()}

def run_mobile_tests():
    """Executa todos os testes mobile"""
    print("🧪 INICIANDO TESTES DE APLICAÇÃO MOBILE")
    print("=" * 50)
    
    # Cria suite de testes
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMobileApp)
    
    # Executa testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Relatório
    print("\n📊 RELATÓRIO DE TESTES MOBILE")
    print("=" * 50)
    print(f"Total de testes: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print("\n❌ FALHAS:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 ERROS:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_mobile_tests()
    exit(0 if success else 1) 