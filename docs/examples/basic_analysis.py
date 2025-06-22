"""
Exemplo de análise básica usando o Workflow Automático
"""

import os
from workflow import BaseAnalyzer

def main():
    """Função principal do exemplo."""
    print("🚀 Iniciando análise básica...")
    
    # Configura diretórios
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_file = os.path.join(project_dir, "config", "base_config.json")
    
    # Inicializa analisador
    analyzer = BaseAnalyzer(config_file)
    
    # Executa análise
    print("\n📊 Analisando projeto...")
    results = analyzer.analyze_project(project_dir)
    
    # Gera relatório
    print("\n📝 Gerando relatório...")
    output_file = os.path.join(project_dir, "outputs", "basic_output.txt")
    analyzer.generate_report(output_file)
    
    print("\n✅ Análise concluída!")
    print(f"📄 Relatório salvo em: {output_file}")
    
if __name__ == "__main__":
    main() 