"""
Exemplo de customização usando o Workflow Automático
"""

import os
from typing import Dict, List

from workflow import BaseAnalyzer, IAAnalyzer
from workflow.utils import OutputFormatter
from workflow.plugins import BasePlugin

class CustomFormatter(OutputFormatter):
    """Formatador customizado."""
    
    def format_report(self, data: Dict) -> str:
        """Formata relatório customizado.
        
        Args:
            data: Dados a serem formatados
            
        Returns:
            String com relatório formatado
        """
        output = []
        
        # Cabeçalho customizado
        output.append("=== RELATÓRIO CUSTOMIZADO ===")
        output.append("---------------------------")
        output.append("")
        
        # Seções customizadas
        for section, content in data.items():
            # Título da seção
            output.append(f"### {section.upper()} ###")
            output.append("")
            
            # Conteúdo formatado
            if isinstance(content, dict):
                for key, value in content.items():
                    output.append(f"{key}:")
                    output.append(f"  {value}")
            elif isinstance(content, list):
                for item in content:
                    output.append(f"- {item}")
            else:
                output.append(str(content))
                
            output.append("")
            output.append("---------------------------")
            output.append("")
            
        return "\n".join(output)

class CustomPlugin(BasePlugin):
    """Plugin customizado."""
    
    def process(self, data: Dict) -> Dict:
        """Processa dados customizados.
        
        Args:
            data: Dados a serem processados
            
        Returns:
            Dict com dados processados
        """
        results = {}
        
        # Análise customizada
        results["custom_metrics"] = self._calculate_metrics(data)
        results["custom_insights"] = self._generate_insights(data)
        
        return results
        
    def _calculate_metrics(self, data: Dict) -> Dict:
        """Calcula métricas customizadas."""
        metrics = {}
        
        # Exemplo de métrica customizada
        if "checklists" in data:
            total = len(data["checklists"])
            completed = sum(1 for c in data["checklists"] if c.get("done"))
            metrics["completion_rate"] = f"{(completed/total)*100:.1f}%"
            
        return metrics
        
    def _generate_insights(self, data: Dict) -> List[str]:
        """Gera insights customizados."""
        insights = []
        
        # Exemplo de insight customizado
        if "priorities" in data:
            critical = len([p for p in data["priorities"] if p.get("level") == "critical"])
            if critical > 5:
                insights.append("⚠️ Alto número de itens críticos")
                
        return insights

class CustomAnalyzer(BaseAnalyzer):
    """Analisador customizado."""
    
    def __init__(self, config_path: str = None):
        """Inicializa analisador customizado."""
        super().__init__(config_path)
        self.formatter = CustomFormatter()
        self.plugin = CustomPlugin()
        
    def analyze_project(self, project_path: str) -> Dict:
        """Análise customizada de projeto.
        
        Args:
            project_path: Caminho do projeto
            
        Returns:
            Dict com resultados da análise
        """
        # Análise base
        results = super().analyze_project(project_path)
        
        # Processamento customizado
        custom_results = self.plugin.process(results)
        results.update(custom_results)
        
        return results

def main():
    """Função principal do exemplo."""
    print("🎨 Iniciando customização...")
    
    # Configura diretórios
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_file = os.path.join(project_dir, "config", "base_config.json")
    output_dir = os.path.join(project_dir, "outputs")
    
    # Cria diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializa analisador customizado
    analyzer = CustomAnalyzer(config_file)
    
    # Executa análise
    print("\n📊 Executando análise customizada...")
    results = analyzer.analyze_project(project_dir)
    
    # Gera relatório
    print("\n📝 Gerando relatório customizado...")
    output_file = os.path.join(output_dir, "custom_output.txt")
    analyzer.generate_report(output_file)
    
    print("\n✅ Customização concluída!")
    print(f"📄 Relatório salvo em: {output_file}")
    
if __name__ == "__main__":
    main() 