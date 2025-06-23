"""
Validação e Sanitização de Entrada - TarefaMágica (P2-1)
"""
import re
import html
from typing import Any, Dict, List, Optional

class InputValidation:
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        if not isinstance(value, str):
            raise ValueError("Valor não é string")
        value = value.strip()
        value = html.escape(value)
        if max_length:
            value = value[:max_length]
        return value

    @staticmethod
    def validate_email(email: str) -> bool:
        if not isinstance(email, str):
            return False
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_email(email: str) -> str:
        email = InputValidation.sanitize_string(email, max_length=255)
        if not InputValidation.validate_email(email):
            raise ValueError("Email inválido")
        return email

    @staticmethod
    def sanitize_int(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        try:
            value = int(value)
        except Exception:
            raise ValueError("Valor não é inteiro")
        if min_value is not None and value < min_value:
            raise ValueError(f"Valor menor que o mínimo permitido: {min_value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"Valor maior que o máximo permitido: {max_value}")
        return value

    @staticmethod
    def sanitize_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
        try:
            value = float(value)
        except Exception:
            raise ValueError("Valor não é float")
        if min_value is not None and value < min_value:
            raise ValueError(f"Valor menor que o mínimo permitido: {min_value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"Valor maior que o máximo permitido: {max_value}")
        return value

    @staticmethod
    def sanitize_list(value: Any, item_type: type = str, max_length: Optional[int] = None) -> List:
        if not isinstance(value, list):
            raise ValueError("Valor não é lista")
        if max_length and len(value) > max_length:
            raise ValueError(f"Lista excede o tamanho máximo de {max_length}")
        sanitized = []
        for item in value:
            if item_type == str:
                sanitized.append(InputValidation.sanitize_string(item))
            elif item_type == int:
                sanitized.append(InputValidation.sanitize_int(item))
            elif item_type == float:
                sanitized.append(InputValidation.sanitize_float(item))
            else:
                sanitized.append(item)
        return sanitized

    @staticmethod
    def sanitize_json(data: Any, schema: Optional[Dict] = None) -> Dict:
        if not isinstance(data, dict):
            raise ValueError("JSON inválido")
        # Se schema for fornecido, valida os campos obrigatórios
        if schema:
            for key, rule in schema.items():
                if rule.get('required', False) and key not in data:
                    raise ValueError(f"Campo obrigatório ausente: {key}")
        return data

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        # Permite apenas letras, números, hífen, underline e ponto
        return re.match(r'^[\w\-.]+$', filename) is not None 