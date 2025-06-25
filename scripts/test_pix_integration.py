#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 Teste Completo da Integração PIX - TarefaMágica
Valida todas as funcionalidades da integração PIX
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.financial.pix_integration import PIXIntegration
from datetime import datetime, timedelta
import json

def test_pix_creation():
    """Testa criação de transações PIX"""
    print("🧪 Testando Criação de Transações PIX...")
    
    pix = PIXIntegration()
    
    # Teste 1: Transação válida
    result1 = pix.create_pix_transaction(
        parent_id="parent_001",
        child_id="child_001",
        amount=5.00,
        description="Recompensa por arrumar a cama"
    )
    
    if result1["success"]:
        print(f"  ✅ Transação 1 criada: {result1['transaction_id']}")
        transaction_id1 = result1["transaction_id"]
    else:
        print(f"  ❌ Erro na transação 1: {result1['error']}")
        return False
    
    # Teste 2: Transação com valor maior
    result2 = pix.create_pix_transaction(
        parent_id="parent_001",
        child_id="child_001",
        amount=10.00,
        description="Recompensa por lavar louça"
    )
    
    if result2["success"]:
        print(f"  ✅ Transação 2 criada: {result2['transaction_id']}")
        transaction_id2 = result2["transaction_id"]
    else:
        print(f"  ❌ Erro na transação 2: {result2['error']}")
        return False
    
    # Teste 3: Transação inválida (valor muito alto)
    result3 = pix.create_pix_transaction(
        parent_id="parent_001",
        child_id="child_001",
        amount=1000.00,
        description="Teste de limite"
    )
    
    if not result3["success"]:
        print(f"  ✅ Transação 3 rejeitada corretamente: {result3['error']}")
    else:
        print(f"  ❌ Transação 3 deveria ter sido rejeitada")
        return False
    
    return True, [transaction_id1, transaction_id2]

def test_pix_status_check():
    """Testa verificação de status das transações"""
    print("\n🧪 Testando Verificação de Status...")
    
    pix = PIXIntegration()
    
    # Cria uma transação para testar
    result = pix.create_pix_transaction(
        parent_id="parent_002",
        child_id="child_002",
        amount=3.50,
        description="Teste de status"
    )
    
    if not result["success"]:
        print(f"  ❌ Erro ao criar transação para teste: {result['error']}")
        return False
    
    transaction_id = result["transaction_id"]
    
    # Verifica status
    status_result = pix.check_transaction_status(transaction_id)
    
    if status_result["success"]:
        print(f"  ✅ Status verificado: {status_result['status']}")
        return True
    else:
        print(f"  ❌ Erro ao verificar status: {status_result['error']}")
        return False

def test_pix_cancellation():
    """Testa cancelamento de transações"""
    print("\n🧪 Testando Cancelamento de Transações...")
    
    pix = PIXIntegration()
    
    # Cria uma transação para cancelar
    result = pix.create_pix_transaction(
        parent_id="parent_003",
        child_id="child_003",
        amount=7.00,
        description="Teste de cancelamento"
    )
    
    if not result["success"]:
        print(f"  ❌ Erro ao criar transação para cancelamento: {result['error']}")
        return False
    
    transaction_id = result["transaction_id"]
    
    # Cancela a transação
    cancel_result = pix.cancel_transaction(transaction_id, "parent_003")
    
    if cancel_result["success"]:
        print(f"  ✅ Transação cancelada: {cancel_result['message']}")
        
        # Verifica se o status foi atualizado
        status_result = pix.check_transaction_status(transaction_id)
        if status_result["success"] and status_result["status"] == "cancelled":
            print(f"  ✅ Status atualizado corretamente: {status_result['status']}")
            return True
        else:
            print(f"  ❌ Status não foi atualizado corretamente")
            return False
    else:
        print(f"  ❌ Erro ao cancelar transação: {cancel_result['error']}")
        return False

def test_pix_history():
    """Testa histórico de transações"""
    print("\n🧪 Testando Histórico de Transações...")
    
    pix = PIXIntegration()
    
    # Cria algumas transações para o mesmo pai
    parent_id = "parent_004"
    
    for i in range(3):
        result = pix.create_pix_transaction(
            parent_id=parent_id,
            child_id=f"child_{i}",
            amount=2.00 + i,
            description=f"Transação teste {i+1}"
        )
        if not result["success"]:
            print(f"  ❌ Erro ao criar transação {i+1}: {result['error']}")
            return False
    
    # Obtém histórico
    history_result = pix.get_transaction_history(parent_id)
    
    if history_result["success"]:
        print(f"  ✅ Histórico obtido: {history_result['total']} transações")
        
        # Verifica se as transações estão no histórico
        transactions = history_result["transactions"]
        if len(transactions) >= 3:
            print(f"  ✅ Todas as transações encontradas no histórico")
            return True
        else:
            print(f"  ❌ Transações faltando no histórico")
            return False
    else:
        print(f"  ❌ Erro ao obter histórico: {history_result['error']}")
        return False

def test_pix_financial_report():
    """Testa geração de relatórios financeiros"""
    print("\n🧪 Testando Relatórios Financeiros...")
    
    pix = PIXIntegration()
    
    # Cria transações para relatório
    parent_id = "parent_005"
    
    for i in range(5):
        result = pix.create_pix_transaction(
            parent_id=parent_id,
            child_id=f"child_{i}",
            amount=1.50 + i,
            description=f"Transação relatório {i+1}"
        )
        if not result["success"]:
            print(f"  ❌ Erro ao criar transação para relatório: {result['error']}")
            return False
    
    # Gera relatório
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    report_result = pix.generate_financial_report(parent_id, start_date, end_date)
    
    if report_result["success"]:
        report = report_result["report"]
        print(f"  ✅ Relatório gerado: {report_result['report_file']}")
        print(f"  📊 Total de transações: {report['summary']['total_transactions']}")
        print(f"  💰 Valor total: R$ {report['summary']['total_amount']:.2f}")
        return True
    else:
        print(f"  ❌ Erro ao gerar relatório: {report_result['error']}")
        return False

def test_pix_validation():
    """Testa validações de segurança"""
    print("\n🧪 Testando Validações de Segurança...")
    
    pix = PIXIntegration()
    
    # Teste 1: Valor negativo
    result1 = pix.create_pix_transaction(
        parent_id="parent_006",
        child_id="child_006",
        amount=-5.00,
        description="Teste valor negativo"
    )
    
    if not result1["success"]:
        print(f"  ✅ Valor negativo rejeitado: {result1['error']}")
    else:
        print(f"  ❌ Valor negativo deveria ter sido rejeitado")
        return False
    
    # Teste 2: Valor zero
    result2 = pix.create_pix_transaction(
        parent_id="parent_006",
        child_id="child_006",
        amount=0.00,
        description="Teste valor zero"
    )
    
    if not result2["success"]:
        print(f"  ✅ Valor zero rejeitado: {result2['error']}")
    else:
        print(f"  ❌ Valor zero deveria ter sido rejeitado")
        return False
    
    # Teste 3: Valor muito alto (acima de 100)
    result3 = pix.create_pix_transaction(
        parent_id="parent_006",
        child_id="child_006",
        amount=150.00,
        description="Teste valor alto"
    )
    
    if not result3["success"]:
        print(f"  ✅ Valor alto rejeitado: {result3['error']}")
    else:
        print(f"  ❌ Valor alto deveria ter sido rejeitado")
        return False
    
    return True

def main():
    """Função principal de teste"""
    print("💰 Teste Completo da Integração PIX - TarefaMágica")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Criação de Transações", test_pix_creation),
        ("Verificação de Status", test_pix_status_check),
        ("Cancelamento", test_pix_cancellation),
        ("Histórico", test_pix_history),
        ("Relatórios Financeiros", test_pix_financial_report),
        ("Validações de Segurança", test_pix_validation)
    ]
    
    # Executa testes
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {str(e)}")
    
    print(f"\n📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎯 Status Final: ✅ INTEGRAÇÃO PIX FUNCIONANDO")
        print("✅ Todas as funcionalidades PIX estão operacionais!")
        print("✅ Segurança e validações implementadas!")
        print("✅ Relatórios e histórico funcionando!")
    else:
        print("\n🎯 Status Final: ❌ PRECISA DE CORREÇÕES")
        print("❌ Algumas funcionalidades PIX precisam de ajustes")
    
    return passed == total

if __name__ == "__main__":
    main() 