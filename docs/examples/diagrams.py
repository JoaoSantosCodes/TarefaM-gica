"""
Exemplo de geração de diagramas usando o Workflow Automático
"""

import os
from workflow import DiagramGenerator

def main():
    """Função principal do exemplo."""
    print("📊 Iniciando geração de diagramas...")
    
    # Configura diretórios
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_file = os.path.join(project_dir, "config", "diagram_config.json")
    output_dir = os.path.join(project_dir, "outputs", "diagrams")
    
    # Cria diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializa gerador
    generator = DiagramGenerator(config_file)
    
    # Gera diagrama de estrutura
    print("\n📐 Gerando diagrama de estrutura...")
    structure = generator.generate_structure_diagram(project_dir)
    structure_file = os.path.join(output_dir, "structure.svg")
    with open(structure_file, "w", encoding="utf-8") as f:
        f.write(structure)
    
    # Gera diagrama de workflow
    print("\n🔄 Gerando diagrama de workflow...")
    workflow = generator.generate_workflow_diagram({})
    workflow_file = os.path.join(output_dir, "workflow.svg")
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write(workflow)
    
    # Gera diagrama de execução
    print("\n⚡ Gerando diagrama de execução...")
    execution = generator.generate_execution_diagram({})
    execution_file = os.path.join(output_dir, "execution.svg")
    with open(execution_file, "w", encoding="utf-8") as f:
        f.write(execution)
    
    # Gera diagrama de roadmap
    print("\n🗺️ Gerando diagrama de roadmap...")
    roadmap = generator.generate_roadmap_diagram({})
    roadmap_file = os.path.join(output_dir, "roadmap.svg")
    with open(roadmap_file, "w", encoding="utf-8") as f:
        f.write(roadmap)
    
    print("\n✅ Geração concluída!")
    print(f"📄 Diagramas salvos em: {output_dir}")
    
if __name__ == "__main__":
    main() 