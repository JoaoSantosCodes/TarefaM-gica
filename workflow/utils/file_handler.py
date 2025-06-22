"""
Módulo de manipulação de arquivos do Workflow Automático
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

class FileHandler:
    """Classe para manipulação de arquivos."""
    
    def __init__(self):
        """Inicializa o manipulador de arquivos."""
        self._setup_encoding()
        
    def _setup_encoding(self) -> None:
        """Configura encoding para UTF-8."""
        os.environ["PYTHONIOENCODING"] = "utf-8"
        
        if sys.platform == 'win32':
            os.system('chcp 65001')  # Força UTF-8 no Windows
            
    def load_json(self, file_path: str) -> Dict:
        """Carrega arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict com conteúdo do arquivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️ Erro ao decodificar JSON: {file_path}")
            return {}
            
    def save_json(self, data: Dict, file_path: str) -> None:
        """Salva dados em arquivo JSON.
        
        Args:
            data: Dados a serem salvos
            file_path: Caminho do arquivo
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    def load_markdown(self, file_path: str) -> str:
        """Carrega arquivo Markdown.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            String com conteúdo do arquivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
            return ""
            
    def save_markdown(self, content: str, file_path: str) -> None:
        """Salva conteúdo em arquivo Markdown.
        
        Args:
            content: Conteúdo a ser salvo
            file_path: Caminho do arquivo
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def save_output(self, content: str, file_path: str) -> None:
        """Salva output com encoding correto.
        
        Args:
            content: Conteúdo a ser salvo
            file_path: Caminho do arquivo
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if sys.platform == 'win32':
            # No Windows, usa UTF-8-SIG (UTF-8 com BOM)
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """Lista arquivos em um diretório.
        
        Args:
            directory: Diretório a ser listado
            pattern: Padrão para filtrar arquivos
            
        Returns:
            Lista de caminhos de arquivos
        """
        path = Path(directory)
        return [str(f) for f in path.glob(pattern) if f.is_file()]
        
    def ensure_directory(self, directory: str) -> None:
        """Garante que um diretório existe.
        
        Args:
            directory: Caminho do diretório
        """
        os.makedirs(directory, exist_ok=True) 