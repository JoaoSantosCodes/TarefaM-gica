"""
Módulo de Autenticação 2FA - TarefaMágica
Implementa autenticação de dois fatores para responsáveis
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import pyotp
import qrcode
from cryptography.fernet import Fernet

class TwoFactorAuth:
    def __init__(self, storage_path: str = "data/2fa"):
        """
        Inicializa o sistema de autenticação 2FA
        
        Args:
            storage_path: Caminho para armazenamento dos dados 2FA
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._setup_encryption()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "qr_codes"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para auditoria"""
        log_path = os.path.join(self.storage_path, "2fa_audit.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _setup_encryption(self):
        """Configura criptografia para dados sensíveis"""
        # Em produção, usar variáveis de ambiente
        key = Fernet.generate_key()
        self.cipher_suite = Fernet(key)
        
    def generate_totp_secret(self, parent_id: str) -> str:
        """
        Gera chave secreta TOTP para um responsável
        
        Args:
            parent_id: ID do responsável
            
        Returns:
            str: Chave secreta TOTP
        """
        # Gera chave secreta aleatória
        secret = pyotp.random_base32()
        
        # Criptografa e salva
        encrypted_secret = self.cipher_suite.encrypt(secret.encode())
        
        secret_file = os.path.join(self.storage_path, f"{parent_id}_secret.enc")
        with open(secret_file, "wb") as f:
            f.write(encrypted_secret)
            
        logging.info(f"Chave TOTP gerada para responsável: {parent_id}")
        return secret
        
    def generate_qr_code(self, parent_id: str, email: str) -> str:
        """
        Gera QR code para configuração do app autenticador
        
        Args:
            parent_id: ID do responsável
            email: Email do responsável
            
        Returns:
            str: Caminho para o arquivo QR code
        """
        # Gera chave secreta se não existir
        secret = self.get_totp_secret(parent_id)
        if not secret:
            secret = self.generate_totp_secret(parent_id)
            
        # Cria URI para QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="TarefaMágica"
        )
        
        # Gera QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva QR code
        qr_path = os.path.join(self.storage_path, "qr_codes", f"{parent_id}_qr.png")
        img.save(qr_path)
        
        logging.info(f"QR code gerado para responsável: {parent_id}")
        return qr_path
        
    def get_totp_secret(self, parent_id: str) -> Optional[str]:
        """
        Recupera chave secreta TOTP de um responsável
        
        Args:
            parent_id: ID do responsável
            
        Returns:
            str: Chave secreta ou None se não encontrada
        """
        try:
            secret_file = os.path.join(self.storage_path, f"{parent_id}_secret.enc")
            if not os.path.exists(secret_file):
                return None
                
            with open(secret_file, "rb") as f:
                encrypted_secret = f.read()
                
            secret = self.cipher_suite.decrypt(encrypted_secret).decode()
            return secret
            
        except Exception as e:
            logging.error(f"Erro ao recuperar chave TOTP: {str(e)}")
            return None
            
    def verify_totp(self, parent_id: str, token: str) -> bool:
        """
        Verifica token TOTP
        
        Args:
            parent_id: ID do responsável
            token: Token TOTP fornecido
            
        Returns:
            bool: True se token válido
        """
        try:
            secret = self.get_totp_secret(parent_id)
            if not secret:
                return False
                
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(token)
            
            if is_valid:
                logging.info(f"Token TOTP válido para responsável: {parent_id}")
            else:
                logging.warning(f"Token TOTP inválido para responsável: {parent_id}")
                
            return is_valid
            
        except Exception as e:
            logging.error(f"Erro ao verificar token TOTP: {str(e)}")
            return False
            
    def generate_backup_codes(self, parent_id: str) -> list:
        """
        Gera códigos de backup para recuperação
        
        Args:
            parent_id: ID do responsável
            
        Returns:
            list: Lista de códigos de backup
        """
        # Gera 10 códigos de backup
        backup_codes = []
        for _ in range(10):
            code = secrets.token_hex(4).upper()  # 8 caracteres hex
            backup_codes.append(code)
            
        # Criptografa e salva códigos
        encrypted_codes = self.cipher_suite.encrypt(json.dumps(backup_codes).encode())
        
        backup_file = os.path.join(self.storage_path, f"{parent_id}_backup.enc")
        with open(backup_file, "wb") as f:
            f.write(encrypted_codes)
            
        logging.info(f"Códigos de backup gerados para responsável: {parent_id}")
        return backup_codes
        
    def verify_backup_code(self, parent_id: str, code: str) -> bool:
        """
        Verifica código de backup
        
        Args:
            parent_id: ID do responsável
            code: Código de backup fornecido
            
        Returns:
            bool: True se código válido
        """
        try:
            backup_file = os.path.join(self.storage_path, f"{parent_id}_backup.enc")
            if not os.path.exists(backup_file):
                return False
                
            with open(backup_file, "rb") as f:
                encrypted_codes = f.read()
                
            backup_codes = json.loads(self.cipher_suite.decrypt(encrypted_codes).decode())
            
            if code.upper() in backup_codes:
                # Remove código usado
                backup_codes.remove(code.upper())
                
                # Salva códigos restantes
                encrypted_codes = self.cipher_suite.encrypt(json.dumps(backup_codes).encode())
                with open(backup_file, "wb") as f:
                    f.write(encrypted_codes)
                    
                logging.info(f"Código de backup usado para responsável: {parent_id}")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Erro ao verificar código de backup: {str(e)}")
            return False
            
    def is_2fa_enabled(self, parent_id: str) -> bool:
        """
        Verifica se 2FA está habilitado para um responsável
        
        Args:
            parent_id: ID do responsável
            
        Returns:
            bool: True se 2FA habilitado
        """
        secret_file = os.path.join(self.storage_path, f"{parent_id}_secret.enc")
        return os.path.exists(secret_file)
        
    def disable_2fa(self, parent_id: str) -> bool:
        """
        Desabilita 2FA para um responsável
        
        Args:
            parent_id: ID do responsável
            
        Returns:
            bool: True se desabilitado com sucesso
        """
        try:
            # Remove arquivos relacionados
            files_to_remove = [
                os.path.join(self.storage_path, f"{parent_id}_secret.enc"),
                os.path.join(self.storage_path, f"{parent_id}_backup.enc"),
                os.path.join(self.storage_path, "qr_codes", f"{parent_id}_qr.png")
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            logging.info(f"2FA desabilitado para responsável: {parent_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao desabilitar 2FA: {str(e)}")
            return False 