"""
Módulo de Proteção de Dados - TarefaMágica
Implementa a criptografia e proteção de dados sensíveis
"""

import base64
import json
import logging
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
from typing import Dict, Optional

class DataProtection:
    def __init__(self, storage_path: str = "data/protected"):
        """
        Inicializa o sistema de proteção de dados
        
        Args:
            storage_path: Caminho para armazenamento dos dados protegidos
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._setup_encryption()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para auditoria"""
        log_path = os.path.join(self.storage_path, "protection_audit.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _setup_encryption(self):
        """Configura sistema de criptografia"""
        # Em produção, usar variáveis de ambiente
        salt = b"tarefamagica_salt"
        password = b"your-secret-key-here"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
        
    def encrypt_child_data(
        self,
        child_id: str,
        data: Dict,
        parent_id: str
    ) -> str:
        """
        Criptografa dados da criança
        
        Args:
            child_id: ID da criança
            data: Dicionário com dados a serem criptografados
            parent_id: ID do responsável
            
        Returns:
            str: ID do registro criptografado
        """
        try:
            # Adiciona metadados
            protected_data = {
                "data": data,
                "child_id": child_id,
                "parent_id": parent_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            # Criptografa
            json_data = json.dumps(protected_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Gera ID único
            record_id = f"rec_{child_id}_{datetime.utcnow().timestamp()}"
            
            # Salva dados criptografados
            file_path = os.path.join(self.storage_path, f"{record_id}.enc")
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
                
            logging.info(f"Dados criptografados para criança {child_id}")
            return record_id
            
        except Exception as e:
            logging.error(f"Erro ao criptografar dados: {str(e)}")
            raise
            
    def decrypt_child_data(
        self,
        record_id: str,
        parent_id: str
    ) -> Optional[Dict]:
        """
        Descriptografa dados da criança
        
        Args:
            record_id: ID do registro criptografado
            parent_id: ID do responsável (para validação)
            
        Returns:
            Dict: Dados descriptografados ou None se não autorizado
        """
        try:
            # Carrega dados criptografados
            file_path = os.path.join(self.storage_path, f"{record_id}.enc")
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
                
            # Descriptografa
            json_data = self.cipher_suite.decrypt(encrypted_data).decode()
            protected_data = json.loads(json_data)
            
            # Valida autorização
            if protected_data["parent_id"] != parent_id:
                logging.warning(f"Tentativa não autorizada de acesso aos dados: {record_id}")
                return None
                
            logging.info(f"Dados descriptografados: {record_id}")
            return protected_data["data"]
            
        except Exception as e:
            logging.error(f"Erro ao descriptografar dados: {str(e)}")
            return None
            
    def update_child_data(
        self,
        record_id: str,
        new_data: Dict,
        parent_id: str
    ) -> bool:
        """
        Atualiza dados criptografados da criança
        
        Args:
            record_id: ID do registro
            new_data: Novos dados
            parent_id: ID do responsável
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Carrega dados existentes
            file_path = os.path.join(self.storage_path, f"{record_id}.enc")
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
                
            # Descriptografa
            json_data = self.cipher_suite.decrypt(encrypted_data).decode()
            protected_data = json.loads(json_data)
            
            # Valida autorização
            if protected_data["parent_id"] != parent_id:
                logging.warning(f"Tentativa não autorizada de atualização: {record_id}")
                return False
                
            # Atualiza dados
            protected_data["data"] = new_data
            protected_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Criptografa novamente
            json_data = json.dumps(protected_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Salva
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
                
            logging.info(f"Dados atualizados: {record_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao atualizar dados: {str(e)}")
            return False
            
    def delete_child_data(
        self,
        record_id: str,
        parent_id: str
    ) -> bool:
        """
        Remove dados criptografados da criança
        
        Args:
            record_id: ID do registro
            parent_id: ID do responsável
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            # Verifica autorização primeiro
            if not self.decrypt_child_data(record_id, parent_id):
                return False
                
            # Remove arquivo
            file_path = os.path.join(self.storage_path, f"{record_id}.enc")
            os.remove(file_path)
            
            logging.info(f"Dados removidos: {record_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao remover dados: {str(e)}")
            return False 