"""
Exemplo de integração com CI/CD usando o Workflow Automático
"""

import os
import sys
from workflow import BaseAnalyzer, IAAnalyzer, DiagramGenerator

def analyze_project():
    """Analisa o projeto."""
    print("🔍 Analisando projeto...")
    
    # Configura diretórios
    project_dir = os.environ.get("GITHUB_WORKSPACE", "./")
    config_dir = os.path.join(project_dir, "config")
    output_dir = os.path.join(project_dir, "outputs")
    
    # Cria diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Análise base
    print("\n📊 Executando análise base...")
    base = BaseAnalyzer(os.path.join(config_dir, "base_config.json"))
    base_results = base.analyze_project(project_dir)
    base.generate_report(os.path.join(output_dir, "ci_base_output.txt"))
    
    # Análise IA
    print("\n🤖 Executando análise IA...")
    ia = IAAnalyzer(os.path.join(config_dir, "ia_config.json"))
    ia_results = ia.analyze_tasks(project_dir)
    ia.generate_report(os.path.join(output_dir, "ci_ia_output.txt"))
    
    # Diagramas
    print("\n📈 Gerando diagramas...")
    diagrams = DiagramGenerator(os.path.join(config_dir, "diagram_config.json"))
    diagrams_dir = os.path.join(output_dir, "ci_diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    
    structure = diagrams.generate_structure_diagram(project_dir)
    with open(os.path.join(diagrams_dir, "structure.svg"), "w") as f:
        f.write(structure)
        
    workflow = diagrams.generate_workflow_diagram(ia_results)
    with open(os.path.join(diagrams_dir, "workflow.svg"), "w") as f:
        f.write(workflow)
        
    return base_results, ia_results

def check_quality(base_results, ia_results):
    """Verifica qualidade do código."""
    print("\n🔍 Verificando qualidade...")
    
    errors = []
    
    # Verifica cobertura de testes
    if base_results.get("metrics", {}).get("test_coverage", 0) < 80:
        errors.append("Cobertura de testes abaixo de 80%")
        
    # Verifica documentação
    if base_results.get("metrics", {}).get("doc_coverage", 0) < 70:
        errors.append("Cobertura de documentação abaixo de 70%")
        
    # Verifica complexidade
    if base_results.get("metrics", {}).get("complexity", 0) > 10:
        errors.append("Complexidade muito alta")
        
    return errors

def comment_pr(base_results, ia_results, errors):
    """Comenta no PR."""
    print("\n💬 Comentando no PR...")
    
    # Monta comentário
    comment = ["## 🤖 Análise do Workflow Automático\n"]
    
    # Adiciona métricas
    comment.append("### 📊 Métricas")
    metrics = base_results.get("metrics", {})
    for key, value in metrics.items():
        comment.append(f"- {key}: {value}")
    comment.append("")
    
    # Adiciona sugestões
    comment.append("### 💡 Sugestões")
    suggestions = ia_results.get("suggestions", [])
    for suggestion in suggestions:
        comment.append(f"- {suggestion}")
    comment.append("")
    
    # Adiciona erros
    if errors:
        comment.append("### ❌ Erros")
        for error in errors:
            comment.append(f"- {error}")
        comment.append("")
        
    # Salva comentário
    comment_file = os.environ.get("GITHUB_STEP_SUMMARY", "ci_comment.md")
    with open(comment_file, "w") as f:
        f.write("\n".join(comment))
        
def main():
    """Função principal."""
    try:
        # Analisa projeto
        base_results, ia_results = analyze_project()
        
        # Verifica qualidade
        errors = check_quality(base_results, ia_results)
        
        # Comenta no PR
        comment_pr(base_results, ia_results, errors)
        
        # Define status
        if errors:
            print("\n❌ Análise falhou!")
            print("Erros encontrados:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("\n✅ Análise passou!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main() 