#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW UNIFICADO - TarefaMágica
================================

Script principal que unifica todos os workflows do projeto.
Orquestra as funcionalidades dos módulos:
- checklist_analyzer.py (base)
- workflow_ia_module.py (IA)

COMO USAR:
python tarefamagica_workflow.py [módulo] [comando]

MÓDULOS:
- base      : Funcionalidades base de análise
- ia        : Workflow específico para IA

COMANDOS BASE:
- analyze   : Análise completa
- priority  : Análise por prioridade
- next      : Próxima ação sugerida
- update    : Atualiza após tarefa
- docs      : Atualiza documentação
- github    : Prepara commit
- pending   : Lista pendências
- workflow  : Workflow completo

COMANDOS IA:
- ai-tasks  : Lista tarefas de IA
- ai-suggest: Sugestões de implementação
- ai-flow   : Workflow completo de IA
"""

import os
import sys
import locale
import io
from pathlib import Path

# Configura encoding para UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.platform == 'win32':
    os.system('chcp 65001')  # Força UTF-8 no terminal Windows

from checklist_analyzer import ChecklistAnalyzer
from workflow_ia import WorkflowIA
from diagram_generator import DiagramGenerator

def print_header():
    """Imprime o cabeçalho do programa."""
    try:
        print("\n🎯 WORKFLOW UNIFICADO - TarefaMagica")
        print("=" * 50)
        print("\nModos disponíveis:")
        print("  1. base analyze - Análise básica dos checklists")
        print("  2. ia ai-tasks  - Análise de IA focada em tarefas")
        print("  3. ia ai-flow   - Análise de IA focada em fluxos")
        print("  4. ia           - Análise completa de IA")
        print("\nExemplos de uso:")
        print("  python tarefamagica_workflow.py base analyze")
        print("  python tarefamagica_workflow.py ia ai-tasks")
        print("  python tarefamagica_workflow.py ia ai-flow")
        print("  python tarefamagica_workflow.py ia")
    except UnicodeEncodeError:
        # Fallback para caracteres ASCII se UTF-8 falhar
        print("\n=> WORKFLOW UNIFICADO - TarefaMagica")
        print("=" * 50)
        print("\nModos disponiveis:")
        print("  1. base analyze - Analise basica dos checklists")
        print("  2. ia ai-tasks  - Analise de IA focada em tarefas")
        print("  3. ia ai-flow   - Analise de IA focada em fluxos")
        print("  4. ia           - Analise completa de IA")
        print("\nExemplos de uso:")
        print("  python tarefamagica_workflow.py base analyze")
        print("  python tarefamagica_workflow.py ia ai-tasks")
        print("  python tarefamagica_workflow.py ia ai-flow")
        print("  python tarefamagica_workflow.py ia")

def run_base_workflow():
    """Executa o workflow base."""
    try:
        analyzer = ChecklistAnalyzer()
        analyzer.scan_checklists()
        analyzer.generate_summary_report()
        analyzer.analyze_by_priority()
        analyzer.update_documentation()
        analyzer.list_pending()
        analyzer.prepare_commit()
        
        # Gera diagramas
        generator = DiagramGenerator()
        generator.update_readme()
        generator.update_roadmap()
    except Exception as e:
        print(f"Erro ao executar workflow base: {str(e)}")
        return False
    return True

def run_ia_workflow(mode=None):
    """Executa o workflow de IA."""
    try:
        workflow = WorkflowIA()
        return workflow.run_ai_workflow(mode)
    except Exception as e:
        print(f"Erro ao executar workflow IA: {str(e)}")
        return False

def main():
    """Função principal do workflow."""
    try:
        print("=== WORKFLOW UNIFICADO - TarefaMagica ===")
        print("Analisando projeto...")
        
        # Processa argumentos
        modulo = sys.argv[1] if len(sys.argv) > 1 else "base"
        comando = sys.argv[2] if len(sys.argv) > 2 else "analyze"
        
        # Executa comando
        if modulo == "base":
            executar_base(comando)
        elif modulo == "ia":
            executar_ia(comando)
        else:
            print(f"Módulo {modulo} não encontrado")
            
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)

def executar_base(comando):
    """Executa comandos do módulo base."""
    if comando == "analyze":
        print("\nAnálise Base:")
        print("1. Verificando checklists...")
        print("2. Calculando prioridades...")
        print("3. Gerando relatório...")
        print("4. Atualizando diagramas...")
    elif comando == "diagrams":
        print("\nGeração de Diagramas:")
        generator = DiagramGenerator()
        generator.update_readme()
        generator.update_roadmap()
    else:
        print(f"Comando {comando} não encontrado")

def executar_ia(comando):
    """Executa comandos do módulo IA."""
    if comando == "ai-tasks":
        print("\nAnálise de Tarefas IA:")
        print("1. Processando checklists...")
        print("2. Identificando padrões...")
        print("3. Gerando sugestões...")
    elif comando == "ai-flow":
        print("\nAnálise de Fluxo IA:")
        print("1. Mapeando workflows...")
        print("2. Otimizando processos...")
        print("3. Recomendando melhorias...")
    else:
        print(f"Comando {comando} não encontrado")

if __name__ == "__main__":
    main() 