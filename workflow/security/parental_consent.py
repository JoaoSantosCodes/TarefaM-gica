"""
Módulo de Consentimento Parental - TarefaMágica
Implementa o sistema de consentimento parental de acordo com LGPD
"""

import datetime
import hashlib
import json
import logging
import os
from typing import Dict, Optional, Tuple

class ParentalConsent:
    def __init__(self, storage_path: str = "data/consent"):
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
    
    def _setup_storage(self) -> None:
        """Configura o armazenamento seguro para os registros de consentimento"""
        os.makedirs(self.storage_path, exist_ok=True)
        
    def _setup_logging(self) -> None:
        """Configura logging para auditoria"""
        logging.basicConfig(
            filename=os.path.join(self.storage_path, "consent_audit.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def request_consent(self, parent_id: str, child_id: str, data_usage: Dict) -> str:
        """
        Gera um novo pedido de consentimento
        
        Args:
            parent_id: ID único do pai/responsável
            child_id: ID único da criança
            data_usage: Dicionário detalhando o uso dos dados
            
        Returns:
            consent_id: ID único do pedido de consentimento
        """
        consent_id = self._generate_consent_id(parent_id, child_id)
        timestamp = datetime.datetime.now().isoformat()
        
        consent_data = {
            "consent_id": consent_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "data_usage": data_usage,
            "status": "pending",
            "timestamp_requested": timestamp,
            "timestamp_responded": None,
            "is_valid": False
        }
        
        self._save_consent_data(consent_id, consent_data)
        logging.info(f"Novo pedido de consentimento gerado: {consent_id}")
        
        return consent_id
    
    def validate_consent(self, consent_id: str, parent_id: str) -> Tuple[bool, str]:
        """
        Valida um pedido de consentimento
        
        Args:
            consent_id: ID do consentimento
            parent_id: ID do pai/responsável para validação
            
        Returns:
            (is_valid, message): Tupla com status e mensagem
        """
        consent_data = self._load_consent_data(consent_id)
        
        if not consent_data:
            return False, "Consentimento não encontrado"
            
        if consent_data["parent_id"] != parent_id:
            logging.warning(f"Tentativa inválida de validação: {consent_id}")
            return False, "ID do responsável não corresponde"
            
        return True, "Consentimento válido"
    
    def grant_consent(self, consent_id: str, parent_id: str) -> bool:
        """
        Registra o consentimento do responsável
        
        Args:
            consent_id: ID do consentimento
            parent_id: ID do pai/responsável
            
        Returns:
            bool: True se consentimento foi registrado com sucesso
        """
        is_valid, message = self.validate_consent(consent_id, parent_id)
        
        if not is_valid:
            logging.error(f"Falha ao conceder consentimento: {message}")
            return False
            
        consent_data = self._load_consent_data(consent_id)
        consent_data["status"] = "granted"
        consent_data["timestamp_responded"] = datetime.datetime.now().isoformat()
        consent_data["is_valid"] = True
        
        self._save_consent_data(consent_id, consent_data)
        logging.info(f"Consentimento concedido: {consent_id}")
        
        return True
    
    def revoke_consent(self, consent_id: str, parent_id: str) -> bool:
        """
        Revoga um consentimento previamente dado
        
        Args:
            consent_id: ID do consentimento
            parent_id: ID do pai/responsável
            
        Returns:
            bool: True se consentimento foi revogado com sucesso
        """
        is_valid, message = self.validate_consent(consent_id, parent_id)
        
        if not is_valid:
            logging.error(f"Falha ao revogar consentimento: {message}")
            return False
            
        consent_data = self._load_consent_data(consent_id)
        consent_data["status"] = "revoked"
        consent_data["timestamp_responded"] = datetime.datetime.now().isoformat()
        consent_data["is_valid"] = False
        
        self._save_consent_data(consent_id, consent_data)
        logging.info(f"Consentimento revogado: {consent_id}")
        
        return True
    
    def check_consent_status(self, consent_id: str) -> Optional[Dict]:
        """
        Verifica o status atual de um consentimento
        
        Args:
            consent_id: ID do consentimento
            
        Returns:
            Dict: Dados do consentimento ou None se não encontrado
        """
        return self._load_consent_data(consent_id)
    
    def _generate_consent_id(self, parent_id: str, child_id: str) -> str:
        """Gera um ID único para o consentimento"""
        timestamp = datetime.datetime.now().isoformat()
        data = f"{parent_id}{child_id}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _get_consent_file_path(self, consent_id: str) -> str:
        """Retorna o caminho do arquivo de consentimento"""
        return os.path.join(self.storage_path, f"{consent_id}.json")
    
    def _save_consent_data(self, consent_id: str, data: Dict) -> None:
        """Salva os dados do consentimento em arquivo"""
        file_path = self._get_consent_file_path(consent_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_consent_data(self, consent_id: str) -> Optional[Dict]:
        """Carrega os dados do consentimento do arquivo"""
        file_path = self._get_consent_file_path(consent_id)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None 