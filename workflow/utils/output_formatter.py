"""
Módulo de formatação de saída do Workflow Automático
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

class OutputFormatter:
    """Classe para formatação de saída."""
    
    def __init__(self):
        """Inicializa o formatador de saída."""
        pass
        
    def format_report(self, data: Dict) -> str:
        """Formata dados em relatório.
        
        Args:
            data: Dados a serem formatados
            
        Returns:
            String com relatório formatado
        """
        output = []
        
        # Cabeçalho
        output.append("=== WORKFLOW AUTOMÁTICO ===")
        output.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
        output.append("")
        
        # Seções
        for section, content in data.items():
            output.append(f"## {section.upper()}")
            output.append("-" * 30)
            
            if isinstance(content, dict):
                output.extend(self._format_dict(content))
            elif isinstance(content, list):
                output.extend(self._format_list(content))
            else:
                output.append(str(content))
                
            output.append("")
            
        return "\n".join(output)
        
    def _format_dict(self, data: Dict, indent: int = 0) -> List[str]:
        """Formata dicionário.
        
        Args:
            data: Dicionário a ser formatado
            indent: Nível de indentação
            
        Returns:
            Lista de linhas formatadas
        """
        output = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                output.append(f"{prefix}{key}:")
                output.extend(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                output.append(f"{prefix}{key}:")
                output.extend(self._format_list(value, indent + 1))
            else:
                output.append(f"{prefix}{key}: {value}")
                
        return output
        
    def _format_list(self, data: List, indent: int = 0) -> List[str]:
        """Formata lista.
        
        Args:
            data: Lista a ser formatada
            indent: Nível de indentação
            
        Returns:
            Lista de linhas formatadas
        """
        output = []
        prefix = "  " * indent
        
        for item in data:
            if isinstance(item, dict):
                output.extend(self._format_dict(item, indent))
            elif isinstance(item, list):
                output.extend(self._format_list(item, indent))
            else:
                output.append(f"{prefix}- {item}")
                
        return output
        
    def format_checklist(self, checklist: Dict) -> str:
        """Formata checklist.
        
        Args:
            checklist: Dados do checklist
            
        Returns:
            String com checklist formatado
        """
        output = []
        
        # Cabeçalho
        output.append(f"# {checklist.get('title', 'Checklist')}")
        output.append("")
        
        # Descrição
        if description := checklist.get('description'):
            output.append(description)
            output.append("")
            
        # Itens
        for section in checklist.get('sections', []):
            output.append(f"## {section['title']}")
            output.append("")
            
            for item in section.get('items', []):
                status = "✅" if item.get('done') else "⬜"
                priority = item.get('priority', '')
                text = item.get('text', '')
                output.append(f"- [{status}] {priority} {text}")
                
            output.append("")
            
        return "\n".join(output)
        
    def format_metrics(self, metrics: Dict) -> str:
        """Formata métricas.
        
        Args:
            metrics: Dados das métricas
            
        Returns:
            String com métricas formatadas
        """
        output = []
        
        # Cabeçalho
        output.append("📊 MÉTRICAS")
        output.append("-" * 30)
        output.append("")
        
        # Totais
        if totals := metrics.get('totals'):
            output.append("### Totais")
            for key, value in totals.items():
                output.append(f"- {key}: {value}")
            output.append("")
            
        # Progresso
        if progress := metrics.get('progress'):
            output.append("### Progresso")
            for key, value in progress.items():
                output.append(f"- {key}: {value}%")
            output.append("")
            
        # Prioridades
        if priorities := metrics.get('priorities'):
            output.append("### Prioridades")
            for priority, count in priorities.items():
                output.append(f"- {priority}: {count}")
            output.append("")
            
        return "\n".join(output)
        
    def format_suggestions(self, suggestions: List[Dict]) -> str:
        """Formata sugestões.
        
        Args:
            suggestions: Lista de sugestões
            
        Returns:
            String com sugestões formatadas
        """
        output = []
        
        # Cabeçalho
        output.append("💡 SUGESTÕES")
        output.append("-" * 30)
        output.append("")
        
        # Agrupa por prioridade
        for priority in ["🔥", "⚡", "📈"]:
            items = [s for s in suggestions if s.get('priority') == priority]
            if items:
                output.append(f"### {priority} Prioridade {priority}")
                output.append("")
                
                for item in items:
                    output.append(f"- {item.get('text')}")
                    if details := item.get('details'):
                        output.append(f"  - {details}")
                        
                output.append("")
                
        return "\n".join(output) 