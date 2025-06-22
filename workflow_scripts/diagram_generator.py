#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGRAM GENERATOR - TarefaMágica
===============================

Gera diagramas automaticamente para README e ROADMAP
"""

import os
import sys
from pathlib import Path
import re
from datetime import datetime

class DiagramGenerator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.readme_file = self.project_root / 'README.md'
        self.roadmap_file = self.project_root / 'ROADMAP.md'
        
    def generate_structure_diagram(self):
        """Gera diagrama da estrutura do projeto."""
        return '''graph TD
    A[TarefaMágica] --> B[checklists]
    A --> C[docs]
    A --> D[workflow_scripts]
    A --> E[outputs]
    
    B --> B1[CHECKLIST_Deploy.md]
    B --> B2[CHECKLIST_DevOps.md]
    B --> B3[CHECKLIST_Funcionalidades.md]
    B --> B4[Outros Checklists]
    
    C --> C1[ia]
    C --> C2[resumo]
    
    C1 --> C1A[README.md]
    C1 --> C1B[STRUCTURE.md]
    C1 --> C1C[WORKFLOW.md]
    C1 --> C1D[EXAMPLES.md]
    C1 --> C1E[CONTEXT.md]
    
    D --> D1[checklist_analyzer.py]
    D --> D2[checklist_generator.py]
    D --> D3[ia_docs_generator.py]
    D --> D4[workflow_scripts]
    
    E --> E1[base_output.txt]
    E --> E2[ia_tasks_output.txt]
    E --> E3[ia_flow_output.txt]'''

    def generate_workflow_diagram(self):
        """Gera diagrama do fluxo de trabalho."""
        return '''graph TD
    A[Início] --> B[Análise do Resumo]
    B --> C[Geração de Checklists]
    C --> D[Análise por IA]
    
    D --> E[Análise de Tarefas]
    D --> F[Análise de Fluxos]
    D --> G[Análise de Prioridades]
    
    E --> H[ia_tasks_output.txt]
    F --> I[ia_flow_output.txt]
    G --> J[base_output.txt]
    
    H --> K[Sugestões de Implementação]
    I --> K
    J --> K
    
    K --> L[Atualização de Documentação]
    L --> M[Fim]'''

    def generate_execution_diagram(self):
        """Gera diagrama do fluxo de execução."""
        return '''graph TD
    A[Início] --> B[Scan Checklists]
    B --> C{Tipo de Análise}
    
    C -->|Base| D[Análise Base]
    C -->|IA| E[Análise IA]
    
    D --> D1[Verificar Checklists]
    D1 --> D2[Calcular Prioridades]
    D2 --> D3[Gerar Relatório]
    
    E --> E1[Processar Checklists]
    E1 --> E2[Identificar Padrões]
    E2 --> E3[Gerar Sugestões]
    
    D3 --> F[Salvar Outputs]
    E3 --> F
    
    F --> G[Fim]'''

    def generate_roadmap_diagram(self):
        """Gera diagrama do roadmap."""
        return '''graph TD
    A[TarefaMágica] --> B[Versão 1.0]
    A --> C[Versão 1.1]
    A --> D[Versão 1.2]
    A --> E[Versão 2.0]
    
    B --> B1[Funcionalidades Base]
    B --> B2[Análise por IA]
    
    C --> C1[Melhorias Workflow]
    C --> C2[Visualização]
    C --> C3[IA Avançada]
    
    D --> D1[Análise Avançada]
    D --> D2[Interface Web]
    D --> D3[Integração Contínua]
    
    E --> E1[IA Cognitiva]
    E --> E2[Automação Total]
    E --> E3[Colaboração]'''

    def update_readme(self):
        """Atualiza o README com os diagramas."""
        if not self.readme_file.exists():
            print("❌ README.md não encontrado!")
            return False
            
        content = self.readme_file.read_text(encoding='utf-8')
        
        # Adiciona seção de diagramas se não existir
        if "## 📊 Diagramas" not in content:
            diagrams_section = f"""
## 📊 Diagramas

### 📁 Estrutura do Projeto
```mermaid
{self.generate_structure_diagram()}
```

### 🔄 Fluxo de Trabalho
```mermaid
{self.generate_workflow_diagram()}
```

### ⚙️ Fluxo de Execução
```mermaid
{self.generate_execution_diagram()}
```
"""
            # Insere antes da seção de Status
            content = content.replace("## 📊 Status do Projeto", f"{diagrams_section}\n## 📊 Status do Projeto")
            
        self.readme_file.write_text(content, encoding='utf-8')
        print("✅ README.md atualizado com diagramas!")
        return True

    def update_roadmap(self):
        """Atualiza o ROADMAP com o diagrama."""
        if not self.roadmap_file.exists():
            print("❌ ROADMAP.md não encontrado!")
            return False
            
        content = self.roadmap_file.read_text(encoding='utf-8')
        
        # Adiciona seção de diagrama se não existir
        if "## 📊 Visão Geral" not in content:
            diagram_section = f"""
## 📊 Visão Geral

```mermaid
{self.generate_roadmap_diagram()}
```
"""
            # Insere após o título principal
            content = content.replace("# 🗺️ Roadmap - TarefaMágica", f"# 🗺️ Roadmap - TarefaMágica\n{diagram_section}")
            
        self.roadmap_file.write_text(content, encoding='utf-8')
        print("✅ ROADMAP.md atualizado com diagrama!")
        return True

def main():
    """Função principal."""
    try:
        print("\n📊 GERADOR DE DIAGRAMAS - TarefaMágica")
        print("=" * 50)
        
        # Usa o diretório atual ou o passado como argumento
        project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
        
        generator = DiagramGenerator(project_dir)
        
        # Atualiza README e ROADMAP
        generator.update_readme()
        generator.update_roadmap()
        
        print("\n🎉 Diagramas gerados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar diagramas: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 