"""
Workflow Automático - Sistema modular de análise e automação de workflows
"""

__version__ = "0.1.0"
__author__ = "João Santos"
__email__ = "joao.santos.codes@gmail.com"

from .base_analyzer import BaseAnalyzer
from .ia_analyzer import IAAnalyzer
from .diagram_generator import DiagramGenerator

__all__ = ["BaseAnalyzer", "IAAnalyzer", "DiagramGenerator"] 