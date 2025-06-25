#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Script de Validação Completa - TarefaMágica
Executa todos os testes de validação e gera relatório final
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

def run_security_tests():
    """Executa testes de segurança"""
    print("🔒 Executando testes de segurança...")
    
    try:
        from tests.security.test_penetration import PenetrationTester
        
        tester = PenetrationTester()
        results = tester.run_all_tests()
        
        return {
            "success": True,
            "results": results,
            "score": results["summary"]["security_score"]
        }
    except Exception as e:
        print(f"❌ Erro nos testes de segurança: {e}")
        return {
            "success": False,
            "error": str(e),
            "score": 0
        }

def run_usability_tests():
    """Executa testes de usabilidade"""
    print("📱 Executando testes de usabilidade...")
    
    try:
        from tests.usability.test_usability import UsabilityTester
        
        tester = UsabilityTester()
        results = tester.run_all_tests()
        
        return {
            "success": True,
            "results": results,
            "score": results["summary"]["average_score"]
        }
    except Exception as e:
        print(f"❌ Erro nos testes de usabilidade: {e}")
        return {
            "success": False,
            "error": str(e),
            "score": 0
        }

def run_unit_tests():
    """Executa testes unitários"""
    print("🧪 Executando testes unitários...")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--json-report"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "score": 100
            }
        else:
            return {
                "success": False,
                "output": result.stderr,
                "score": 0
            }
    except Exception as e:
        print(f"❌ Erro nos testes unitários: {e}")
        return {
            "success": False,
            "error": str(e),
            "score": 0
        }

def generate_final_report(security_results, usability_results, unit_results):
    """Gera relatório final de validação"""
    
    print("\n📊 Gerando relatório final...")
    
    # Calcula scores
    security_score = security_results.get("score", 0)
    usability_score = usability_results.get("score", 0)
    unit_score = unit_results.get("score", 0)
    
    # Score geral (ponderado)
    overall_score = (security_score * 0.4 + usability_score * 0.3 + unit_score * 0.3)
    
    # Determina status geral
    if overall_score >= 90:
        status = "🟢 EXCELENTE"
        recommendation = "Projeto pronto para produção"
    elif overall_score >= 80:
        status = "🟡 BOM"
        recommendation = "Pequenas melhorias recomendadas"
    elif overall_score >= 70:
        status = "🟠 MODERADO"
        recommendation = "Melhorias necessárias antes da produção"
    else:
        status = "🔴 CRÍTICO"
        recommendation = "Correções críticas necessárias"
    
    # Identifica áreas que precisam de atenção
    areas_for_improvement = []
    if security_score < 80:
        areas_for_improvement.append("Segurança")
    if usability_score < 70:
        areas_for_improvement.append("Usabilidade")
    if unit_score < 90:
        areas_for_improvement.append("Testes Unitários")
    
    report = {
        "validation_summary": {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "status": status,
            "recommendation": recommendation,
            "areas_for_improvement": areas_for_improvement
        },
        "detailed_scores": {
            "security": {
                "score": security_score,
                "status": "✅ PASSOU" if security_score >= 80 else "❌ FALHOU",
                "details": security_results
            },
            "usability": {
                "score": usability_score,
                "status": "✅ PASSOU" if usability_score >= 70 else "❌ FALHOU",
                "details": usability_results
            },
            "unit_tests": {
                "score": unit_score,
                "status": "✅ PASSOU" if unit_score >= 90 else "❌ FALHOU",
                "details": unit_results
            }
        },
        "next_steps": generate_next_steps(security_score, usability_score, unit_score)
    }
    
    return report

def generate_next_steps(security_score, usability_score, unit_score):
    """Gera próximos passos baseado nos resultados"""
    
    next_steps = []
    
    if security_score < 80:
        next_steps.extend([
            "Implementar testes de penetração adicionais",
            "Revisar configurações de segurança",
            "Validar compliance LGPD",
            "Implementar headers de segurança adicionais"
        ])
    
    if usability_score < 70:
        next_steps.extend([
            "Melhorar interface para crianças",
            "Implementar sistema de ajuda",
            "Adicionar funcionalidades de acessibilidade",
            "Otimizar fluxo de criação de tarefas"
        ])
    
    if unit_score < 90:
        next_steps.extend([
            "Aumentar cobertura de testes",
            "Corrigir testes falhando",
            "Implementar testes de integração",
            "Adicionar testes de performance"
        ])
    
    if not next_steps:
        next_steps.append("Projeto pronto para próxima fase de desenvolvimento")
    
    return next_steps

def save_report(report, filename="validation_report.json"):
    """Salva relatório em arquivo"""
    
    # Cria diretório se não existir
    os.makedirs("test_reports", exist_ok=True)
    
    filepath = os.path.join("test_reports", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return filepath

def print_summary(report):
    """Imprime resumo dos resultados"""
    
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL DE VALIDAÇÃO - TarefaMágica")
    print("=" * 80)
    
    summary = report["validation_summary"]
    scores = report["detailed_scores"]
    
    print(f"📊 Score Geral: {summary['overall_score']:.1f}/100")
    print(f"🎯 Status: {summary['status']}")
    print(f"💡 Recomendação: {summary['recommendation']}")
    
    print(f"\n📋 Scores Detalhados:")
    print(f"   🔒 Segurança: {scores['security']['score']:.1f}/100 - {scores['security']['status']}")
    print(f"   📱 Usabilidade: {scores['usability']['score']:.1f}/100 - {scores['usability']['status']}")
    print(f"   🧪 Testes Unitários: {scores['unit_tests']['score']:.1f}/100 - {scores['unit_tests']['status']}")
    
    if summary['areas_for_improvement']:
        print(f"\n⚠️  Áreas que Precisam de Melhoria:")
        for area in summary['areas_for_improvement']:
            print(f"   - {area}")
    
    print(f"\n📋 Próximos Passos:")
    for i, step in enumerate(report['next_steps'], 1):
        print(f"   {i}. {step}")
    
    print("=" * 80)

def main():
    """Função principal"""
    
    print("🎯 INICIANDO VALIDAÇÃO COMPLETA - TarefaMágica")
    print("=" * 60)
    
    start_time = time.time()
    
    # Executa todos os testes
    print("🚀 Executando bateria completa de testes...")
    
    security_results = run_security_tests()
    usability_results = run_usability_tests()
    unit_results = run_unit_tests()
    
    # Gera relatório final
    report = generate_final_report(security_results, usability_results, unit_results)
    
    # Salva relatório
    filepath = save_report(report)
    
    # Imprime resumo
    print_summary(report)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️  Tempo total de execução: {duration:.2f} segundos")
    print(f"📋 Relatório completo salvo em: {filepath}")
    
    # Retorna código de saída
    overall_score = report["validation_summary"]["overall_score"]
    
    if overall_score >= 80:
        print("\n🎉 VALIDAÇÃO PASSOU! Projeto está pronto para próxima fase.")
        return 0
    else:
        print("\n⚠️  VALIDAÇÃO FALHOU! Correções necessárias antes de prosseguir.")
        return 1

if __name__ == "__main__":
    exit(main()) 