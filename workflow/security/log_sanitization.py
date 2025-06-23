"""
Sanitização de Logs - TarefaMágica (P3-1)
Remove dados sensíveis dos logs antes do armazenamento
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class SensitivePattern:
    name: str
    pattern: str
    replacement: str
    description: str
    risk_level: str

class LogSanitizer:
    def __init__(self):
        """
        Inicializa o sistema de sanitização de logs
        """
        # Padrões sensíveis para detecção e substituição
        self.sensitive_patterns = [
            # CPF (formato: 000.000.000-00 ou 00000000000)
            SensitivePattern(
                name="cpf",
                pattern=r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
                replacement="[CPF_REDACTED]",
                description="Número de CPF",
                risk_level="HIGH"
            ),
            
            # CNPJ (formato: 00.000.000/0000-00 ou 00000000000000)
            SensitivePattern(
                name="cnpj",
                pattern=r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b',
                replacement="[CNPJ_REDACTED]",
                description="Número de CNPJ",
                risk_level="HIGH"
            ),
            
            # Email
            SensitivePattern(
                name="email",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                replacement="[EMAIL_REDACTED]",
                description="Endereço de email",
                risk_level="MEDIUM"
            ),
            
            # Telefone (formato: (00) 00000-0000 ou 00000000000)
            SensitivePattern(
                name="phone",
                pattern=r'\b\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b',
                replacement="[PHONE_REDACTED]",
                description="Número de telefone",
                risk_level="MEDIUM"
            ),
            
            # Chave PIX (formato: email, CPF, CNPJ, telefone, chave aleatória)
            SensitivePattern(
                name="pix_key",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b|\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b|\b\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b|\b[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}\b',
                replacement="[PIX_KEY_REDACTED]",
                description="Chave PIX",
                risk_level="HIGH"
            ),
            
            # Senha (padrões comuns)
            SensitivePattern(
                name="password",
                pattern=r'("password"\s*:\s*"[^"]*"|"senha"\s*:\s*"[^"]*"|"pass"\s*:\s*"[^"]*"|password\s*=\s*[^\s&]+|senha\s*=\s*[^\s&]+)',
                replacement="[PASSWORD_REDACTED]",
                description="Senha em texto plano",
                risk_level="CRITICAL"
            ),
            
            # Token de autenticação
            SensitivePattern(
                name="auth_token",
                pattern=r'("token"\s*:\s*"[^"]*"|"access_token"\s*:\s*"[^"]*"|"refresh_token"\s*:\s*"[^"]*"|"api_key"\s*:\s*"[^"]*"|Bearer\s+[A-Za-z0-9._-]+)',
                replacement="[TOKEN_REDACTED]",
                description="Token de autenticação",
                risk_level="HIGH"
            ),
            
            # Chave de API
            SensitivePattern(
                name="api_key",
                pattern=r'("api_key"\s*:\s*"[^"]*"|"apikey"\s*:\s*"[^"]*"|"key"\s*:\s*"[^"]*"|api_key\s*=\s*[^\s&]+)',
                replacement="[API_KEY_REDACTED]",
                description="Chave de API",
                risk_level="HIGH"
            ),
            
            # Número de cartão de crédito (formato: 0000 0000 0000 0000)
            SensitivePattern(
                name="credit_card",
                pattern=r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',
                replacement="[CARD_REDACTED]",
                description="Número de cartão de crédito",
                risk_level="CRITICAL"
            ),
            
            # Endereço IP privado
            SensitivePattern(
                name="private_ip",
                pattern=r'\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b',
                replacement="[PRIVATE_IP_REDACTED]",
                description="Endereço IP privado",
                risk_level="LOW"
            ),
            
            # Nome completo (padrão: Nome Sobrenome)
            SensitivePattern(
                name="full_name",
                pattern=r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                replacement="[NAME_REDACTED]",
                description="Nome completo",
                risk_level="MEDIUM"
            ),
            
            # Data de nascimento (formato: DD/MM/YYYY)
            SensitivePattern(
                name="birth_date",
                pattern=r'\b\d{2}/\d{2}/\d{4}\b',
                replacement="[BIRTH_DATE_REDACTED]",
                description="Data de nascimento",
                risk_level="MEDIUM"
            ),
            
            # Endereço (padrões comuns)
            SensitivePattern(
                name="address",
                pattern=r'\b(Rua|Avenida|Av\.|Travessa|Trav\.|Alameda|Al\.|Praça|Pça\.)\s+[^,]+,\s*\d+',
                replacement="[ADDRESS_REDACTED]",
                description="Endereço residencial",
                risk_level="MEDIUM"
            )
        ]
        
        # Campos sensíveis específicos para JSON
        self.sensitive_json_fields = [
            'password', 'senha', 'pass', 'token', 'access_token', 'refresh_token',
            'api_key', 'apikey', 'key', 'secret', 'secret_key', 'private_key',
            'cpf', 'cnpj', 'email', 'phone', 'telefone', 'celular',
            'address', 'endereco', 'birth_date', 'data_nascimento',
            'credit_card', 'cartao', 'card_number', 'pix_key'
        ]
        
        # Configuração de logging
        self.sanitization_logger = logging.getLogger('log_sanitization')
        self.sanitization_logger.setLevel(logging.INFO)
        
    def sanitize_string(self, text: str) -> str:
        """
        Sanitiza uma string removendo dados sensíveis
        
        Args:
            text: Texto a ser sanitizado
            
        Returns:
            str: Texto sanitizado
        """
        if not text:
            return text
            
        sanitized_text = text
        
        # Aplica todos os padrões sensíveis
        for pattern in self.sensitive_patterns:
            sanitized_text = re.sub(pattern.pattern, pattern.replacement, sanitized_text)
            
        # Log de sanitização se houve mudanças
        if sanitized_text != text:
            self.sanitization_logger.info(f"Sanitização aplicada: {len(text)} -> {len(sanitized_text)} caracteres")
            
        return sanitized_text
        
    def sanitize_json(self, data: Union[Dict, List, str]) -> Union[Dict, List, str]:
        """
        Sanitiza dados JSON removendo campos sensíveis
        
        Args:
            data: Dados JSON a serem sanitizados
            
        Returns:
            Union[Dict, List, str]: Dados sanitizados
        """
        if isinstance(data, str):
            try:
                # Tenta fazer parse do JSON
                parsed_data = json.loads(data)
                sanitized_data = self._sanitize_json_object(parsed_data)
                return json.dumps(sanitized_data, ensure_ascii=False)
            except json.JSONDecodeError:
                # Se não for JSON válido, sanitiza como string
                return self.sanitize_string(data)
        elif isinstance(data, dict):
            return self._sanitize_json_object(data)
        elif isinstance(data, list):
            return [self.sanitize_json(item) for item in data]
        else:
            return data
            
    def _sanitize_json_object(self, obj: Any) -> Any:
        """
        Sanitiza um objeto JSON recursivamente
        
        Args:
            obj: Objeto a ser sanitizado
            
        Returns:
            Any: Objeto sanitizado
        """
        if isinstance(obj, dict):
            sanitized_obj = {}
            for key, value in obj.items():
                # Sanitiza a chave
                sanitized_key = self.sanitize_string(str(key))
                
                # Verifica se é um campo sensível
                if self._is_sensitive_field(sanitized_key):
                    sanitized_obj[sanitized_key] = "[SENSITIVE_DATA_REDACTED]"
                else:
                    # Sanitiza o valor recursivamente
                    sanitized_obj[sanitized_key] = self._sanitize_json_object(value)
                    
            return sanitized_obj
        elif isinstance(obj, list):
            return [self._sanitize_json_object(item) for item in obj]
        elif isinstance(obj, str):
            return self.sanitize_string(obj)
        else:
            return obj
            
    def _is_sensitive_field(self, field_name: str) -> bool:
        """
        Verifica se um campo é sensível
        
        Args:
            field_name: Nome do campo
            
        Returns:
            bool: True se for sensível
        """
        field_lower = field_name.lower()
        return any(sensitive_field in field_lower for sensitive_field in self.sensitive_json_fields)
        
    def sanitize_log_message(self, message: str, level: str = "INFO") -> str:
        """
        Sanitiza uma mensagem de log
        
        Args:
            message: Mensagem de log
            level: Nível do log
            
        Returns:
            str: Mensagem sanitizada
        """
        # Sanitiza a mensagem
        sanitized_message = self.sanitize_string(message)
        
        # Adiciona metadados de sanitização
        sanitization_metadata = {
            "original_length": len(message),
            "sanitized_length": len(sanitized_message),
            "sanitization_applied": sanitized_message != message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Se houve sanitização, adiciona metadados
        if sanitization_metadata["sanitization_applied"]:
            sanitized_message += f" [SANITIZED: {json.dumps(sanitization_metadata)}]"
            
        return sanitized_message
        
    def sanitize_log_record(self, record: logging.LogRecord) -> logging.LogRecord:
        """
        Sanitiza um registro de log
        
        Args:
            record: Registro de log
            
        Returns:
            logging.LogRecord: Registro sanitizado
        """
        # Sanitiza a mensagem
        record.msg = self.sanitize_log_message(str(record.msg), record.levelname)
        
        # Sanitiza argumentos se existirem
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(self.sanitize_json(arg) for arg in record.args)
            else:
                record.args = self.sanitize_json(record.args)
                
        return record
        
    def create_sanitized_logger(self, name: str, level: int = logging.INFO) -> logging.Logger:
        """
        Cria um logger com sanitização automática
        
        Args:
            name: Nome do logger
            level: Nível de logging
            
        Returns:
            logging.Logger: Logger com sanitização
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Adiciona filtro de sanitização
        class SanitizationFilter(logging.Filter):
            def __init__(self, sanitizer):
                super().__init__()
                self.sanitizer = sanitizer
                
            def filter(self, record):
                # Sanitiza o registro antes de ser processado
                self.sanitizer.sanitize_log_record(record)
                return True
                
        logger.addFilter(SanitizationFilter(self))
        
        return logger
        
    def get_sanitization_stats(self) -> Dict:
        """
        Obtém estatísticas de sanitização
        
        Returns:
            Dict: Estatísticas
        """
        return {
            "patterns_configured": len(self.sensitive_patterns),
            "sensitive_fields": self.sensitive_json_fields,
            "risk_levels": {
                "CRITICAL": len([p for p in self.sensitive_patterns if p.risk_level == "CRITICAL"]),
                "HIGH": len([p for p in self.sensitive_patterns if p.risk_level == "HIGH"]),
                "MEDIUM": len([p for p in self.sensitive_patterns if p.risk_level == "MEDIUM"]),
                "LOW": len([p for p in self.sensitive_patterns if p.risk_level == "LOW"])
            },
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "risk_level": p.risk_level,
                    "replacement": p.replacement
                }
                for p in self.sensitive_patterns
            ]
        }
        
    def add_custom_pattern(self, name: str, pattern: str, replacement: str, description: str, risk_level: str = "MEDIUM"):
        """
        Adiciona um padrão personalizado de sanitização
        
        Args:
            name: Nome do padrão
            pattern: Expressão regular
            replacement: Texto de substituição
            description: Descrição do padrão
            risk_level: Nível de risco (CRITICAL, HIGH, MEDIUM, LOW)
        """
        try:
            # Valida a expressão regular
            re.compile(pattern)
            
            custom_pattern = SensitivePattern(
                name=name,
                pattern=pattern,
                replacement=replacement,
                description=description,
                risk_level=risk_level
            )
            
            self.sensitive_patterns.append(custom_pattern)
            self.sanitization_logger.info(f"Padrão personalizado adicionado: {name}")
            
        except re.error as e:
            self.sanitization_logger.error(f"Erro ao adicionar padrão personalizado: {e}")
            
    def remove_pattern(self, name: str) -> bool:
        """
        Remove um padrão de sanitização
        
        Args:
            name: Nome do padrão
            
        Returns:
            bool: True se removido com sucesso
        """
        for i, pattern in enumerate(self.sensitive_patterns):
            if pattern.name == name:
                removed_pattern = self.sensitive_patterns.pop(i)
                self.sanitization_logger.info(f"Padrão removido: {removed_pattern.name}")
                return True
        return False
        
    def test_sanitization(self, test_data: Dict) -> Dict:
        """
        Testa a sanitização com dados de exemplo
        
        Args:
            test_data: Dados de teste
            
        Returns:
            Dict: Resultados do teste
        """
        results = {
            "original": test_data,
            "sanitized": self.sanitize_json(test_data),
            "patterns_applied": [],
            "fields_redacted": []
        }
        
        # Identifica padrões aplicados
        test_str = json.dumps(test_data)
        for pattern in self.sensitive_patterns:
            if re.search(pattern.pattern, test_str):
                results["patterns_applied"].append({
                    "name": pattern.name,
                    "description": pattern.description,
                    "risk_level": pattern.risk_level
                })
                
        # Identifica campos redatados
        if isinstance(test_data, dict):
            for key in test_data.keys():
                if self._is_sensitive_field(str(key)):
                    results["fields_redacted"].append(key)
                    
        return results

# Instância global do sanitizador de logs
log_sanitizer = LogSanitizer() 