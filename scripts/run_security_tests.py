#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Script para Executar Testes de Segurança - TarefaMágica
Executa todos os testes de segurança implementados
"""

import subprocess
import sys
import os
from datetime import datetime

def run_security_tests():
    """Executa todos os testes de segurança"""
    
    print("🔒 EXECUTANDO TESTES DE SEGURANÇA - TarefaMágica")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar se pytest está instalado
    try:
        import pytest
        print("✅ pytest encontrado")
    except ImportError:
        print("❌ pytest não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
    
    # Executar testes de segurança
    print("\n🧪 Executando testes de segurança...")
    
    test_results = []
    
    # Teste 1: Testes unitários de segurança
    print("\n1️⃣ Testes Unitários de Segurança")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/security/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Testes unitários passaram")
            test_results.append(("Unitários", "PASSOU"))
        else:
            print("❌ Testes unitários falharam")
            print(result.stdout)
            print(result.stderr)
            test_results.append(("Unitários", "FALHOU"))
            
    except Exception as e:
        print(f"❌ Erro ao executar testes unitários: {e}")
        test_results.append(("Unitários", "ERRO"))
    
    # Teste 2: Análise estática de segurança
    print("\n2️⃣ Análise Estática de Segurança")
    try:
        # Verificar se bandit está instalado
        try:
            import bandit
        except ImportError:
            print("📦 Instalando bandit...")
            subprocess.run([sys.executable, "-m", "pip", "install", "bandit"])
        
        result = subprocess.run([
            sys.executable, "-m", "bandit", 
            "-r", "workflow/security/",
            "-f", "json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Análise estática passou")
            test_results.append(("Análise Estática", "PASSOU"))
        else:
            print("⚠️ Análise estática encontrou problemas")
            print(result.stdout)
            test_results.append(("Análise Estática", "AVISO"))
            
    except Exception as e:
        print(f"❌ Erro na análise estática: {e}")
        test_results.append(("Análise Estática", "ERRO"))
    
    # Teste 3: Validação de dependências
    print("\n3️⃣ Validação de Dependências")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "check"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências válidas")
            test_results.append(("Dependências", "PASSOU"))
        else:
            print("❌ Problemas com dependências")
            print(result.stdout)
            test_results.append(("Dependências", "FALHOU"))
            
    except Exception as e:
        print(f"❌ Erro na validação de dependências: {e}")
        test_results.append(("Dependências", "ERRO"))
    
    # Teste 4: Verificação de arquivos de segurança
    print("\n4️⃣ Verificação de Arquivos de Segurança")
    security_files = [
        "docs/SECURITY.md",
        "docs/SECURITY_PENTEST.md",
        "workflow/security/",
        "checklists/CHECKLIST_Seguranca.md"
    ]
    
    missing_files = []
    for file_path in security_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NÃO ENCONTRADO")
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ Todos os arquivos de segurança encontrados")
        test_results.append(("Arquivos", "PASSOU"))
    else:
        print(f"❌ {len(missing_files)} arquivos de segurança faltando")
        test_results.append(("Arquivos", "FALHOU"))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, status in test_results:
        print(f"{'✅' if status == 'PASSOU' else '❌'} {test_name}: {status}")
        if status == "PASSOU":
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Resultado: {passed}/{len(test_results)} testes passaram")
    
    if failed == 0:
        print("🎉 TODOS OS TESTES DE SEGURANÇA PASSARAM!")
        return True
    else:
        print(f"⚠️ {failed} teste(s) falharam. Verifique os detalhes acima.")
        return False

def main():
    """Função principal"""
    success = run_security_tests()
    
    if success:
        print("\n🚀 Sistema de segurança validado com sucesso!")
        sys.exit(0)
    else:
        print("\n🔧 Corrija os problemas identificados antes de prosseguir.")
        sys.exit(1)

if __name__ == "__main__":
    main() 