#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Testes Automatizados - Módulos de Segurança TarefaMágica
Testa todos os módulos de segurança implementados (P1-P4)
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import json
import hashlib
import time

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'workflow'))

# Importar módulos de segurança
from security.authentication import AuthenticationManager
from security.authorization import AuthorizationManager
from security.encryption import EncryptionManager
from security.consent import ConsentManager
from security.access_control import AccessControlManager
from security.monitoring import SecurityMonitoring
from security.backup import SecureBackup
from security.audit import AuditSystem
from security.input_validation import InputValidator
from security.rate_limiting import RateLimiter
from security.security_headers import SecurityHeaders
from security.ssl_validation import SSLValidator
from security.log_sanitization import LogSanitizer
from security.timeout_config import TimeoutManager
from security.data_integrity import DataIntegrityValidator

class TestAuthentication:
    """Testes para módulo de autenticação (P1-1)"""
    
    def setup_method(self):
        self.auth_manager = AuthenticationManager()
    
    def test_user_registration(self):
        """Testa registro de usuário"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "role": "PARENT"
        }
        
        result = self.auth_manager.register_user(user_data)
        assert result["success"] == True
        assert "user_id" in result
    
    def test_user_login(self):
        """Testa login de usuário"""
        credentials = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        result = self.auth_manager.login(credentials)
        assert result["success"] == True
        assert "token" in result
    
    def test_invalid_login(self):
        """Testa login inválido"""
        credentials = {
            "email": "test@example.com",
            "password": "WrongPassword"
        }
        
        result = self.auth_manager.login(credentials)
        assert result["success"] == False
    
    def test_2fa_generation(self):
        """Testa geração de 2FA"""
        user_id = "test_user_123"
        result = self.auth_manager.generate_2fa(user_id)
        
        assert result["success"] == True
        assert "secret" in result
        assert "qr_code" in result
        assert "backup_codes" in result
    
    def test_2fa_verification(self):
        """Testa verificação de 2FA"""
        user_id = "test_user_123"
        token = "123456"  # TOTP válido
        
        result = self.auth_manager.verify_2fa(user_id, token)
        assert result["success"] == True

class TestAuthorization:
    """Testes para módulo de autorização (P1-2)"""
    
    def setup_method(self):
        self.auth_manager = AuthorizationManager()
    
    def test_role_creation(self):
        """Testa criação de roles"""
        role_data = {
            "name": "MODERATOR",
            "permissions": ["content:read", "content:moderate"]
        }
        
        result = self.auth_manager.create_role(role_data)
        assert result["success"] == True
    
    def test_permission_check(self):
        """Testa verificação de permissões"""
        user_id = "test_user_123"
        permission = "user:read"
        
        result = self.auth_manager.check_permission(user_id, permission)
        assert isinstance(result, bool)
    
    def test_role_assignment(self):
        """Testa atribuição de roles"""
        user_id = "test_user_123"
        role = "PARENT"
        
        result = self.auth_manager.assign_role(user_id, role)
        assert result["success"] == True

class TestEncryption:
    """Testes para módulo de criptografia (P1-3)"""
    
    def setup_method(self):
        self.encryption_manager = EncryptionManager()
    
    def test_data_encryption(self):
        """Testa criptografia de dados"""
        sensitive_data = "Dados sensíveis da criança"
        
        encrypted = self.encryption_manager.encrypt_data(sensitive_data)
        assert encrypted != sensitive_data
        assert isinstance(encrypted, str)
    
    def test_data_decryption(self):
        """Testa descriptografia de dados"""
        sensitive_data = "Dados sensíveis da criança"
        
        encrypted = self.encryption_manager.encrypt_data(sensitive_data)
        decrypted = self.encryption_manager.decrypt_data(encrypted)
        
        assert decrypted == sensitive_data
    
    def test_password_hashing(self):
        """Testa hash de senhas"""
        password = "MinhaSenha123!"
        
        hashed = self.encryption_manager.hash_password(password)
        assert hashed != password
        assert self.encryption_manager.verify_password(password, hashed) == True

class TestConsent:
    """Testes para módulo de consentimento (P1-4)"""
    
    def setup_method(self):
        self.consent_manager = ConsentManager()
    
    def test_consent_creation(self):
        """Testa criação de consentimento"""
        consent_data = {
            "parent_id": "parent_123",
            "child_id": "child_456",
            "purpose": "educacional",
            "duration": "1 year"
        }
        
        result = self.consent_manager.create_consent(consent_data)
        assert result["success"] == True
        assert "consent_id" in result
    
    def test_consent_validation(self):
        """Testa validação de consentimento"""
        consent_id = "consent_123"
        
        result = self.consent_manager.validate_consent(consent_id)
        assert isinstance(result, bool)
    
    def test_consent_revocation(self):
        """Testa revogação de consentimento"""
        consent_id = "consent_123"
        
        result = self.consent_manager.revoke_consent(consent_id)
        assert result["success"] == True

class TestAccessControl:
    """Testes para módulo de controle de acesso (P1-5)"""
    
    def setup_method(self):
        self.access_manager = AccessControlManager()
    
    def test_access_grant(self):
        """Testa concessão de acesso"""
        user_id = "user_123"
        resource = "child_data"
        permission = "read"
        
        result = self.access_manager.grant_access(user_id, resource, permission)
        assert result["success"] == True
    
    def test_access_check(self):
        """Testa verificação de acesso"""
        user_id = "user_123"
        resource = "child_data"
        action = "read"
        
        result = self.access_manager.check_access(user_id, resource, action)
        assert isinstance(result, bool)
    
    def test_access_revoke(self):
        """Testa revogação de acesso"""
        user_id = "user_123"
        resource = "child_data"
        
        result = self.access_manager.revoke_access(user_id, resource)
        assert result["success"] == True

class TestSecurityMonitoring:
    """Testes para módulo de monitoramento (P1-6)"""
    
    def setup_method(self):
        self.monitoring = SecurityMonitoring()
    
    def test_anomaly_detection(self):
        """Testa detecção de anomalias"""
        event_data = {
            "user_id": "user_123",
            "action": "login",
            "ip": "192.168.1.100",
            "timestamp": time.time()
        }
        
        result = self.monitoring.detect_anomaly(event_data)
        assert isinstance(result, dict)
        assert "is_anomaly" in result
    
    def test_alert_generation(self):
        """Testa geração de alertas"""
        alert_data = {
            "type": "suspicious_login",
            "severity": "HIGH",
            "description": "Múltiplas tentativas de login"
        }
        
        result = self.monitoring.generate_alert(alert_data)
        assert result["success"] == True

class TestSecureBackup:
    """Testes para módulo de backup seguro (P1-7)"""
    
    def setup_method(self):
        self.backup_manager = SecureBackup()
    
    def test_backup_creation(self):
        """Testa criação de backup"""
        data = {"test": "data"}
        
        result = self.backup_manager.create_backup(data)
        assert result["success"] == True
        assert "backup_id" in result
    
    def test_backup_restoration(self):
        """Testa restauração de backup"""
        backup_id = "backup_123"
        
        result = self.backup_manager.restore_backup(backup_id)
        assert result["success"] == True

class TestAuditSystem:
    """Testes para módulo de auditoria (P1-8)"""
    
    def setup_method(self):
        self.audit_system = AuditSystem()
    
    def test_log_creation(self):
        """Testa criação de logs"""
        log_data = {
            "user_id": "user_123",
            "action": "data_access",
            "resource": "child_profile",
            "timestamp": time.time()
        }
        
        result = self.audit_system.create_log(log_data)
        assert result["success"] == True
    
    def test_log_query(self):
        """Testa consulta de logs"""
        filters = {
            "user_id": "user_123",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        result = self.audit_system.query_logs(filters)
        assert isinstance(result, list)

class TestInputValidation:
    """Testes para módulo de validação de entrada (P2-1)"""
    
    def setup_method(self):
        self.validator = InputValidator()
    
    def test_email_validation(self):
        """Testa validação de email"""
        valid_email = "test@example.com"
        invalid_email = "invalid-email"
        
        assert self.validator.validate_email(valid_email) == True
        assert self.validator.validate_email(invalid_email) == False
    
    def test_string_sanitization(self):
        """Testa sanitização de strings"""
        dirty_string = "<script>alert('xss')</script>"
        clean_string = self.validator.sanitize_string(dirty_string)
        
        assert "<script>" not in clean_string
        assert "alert" not in clean_string
    
    def test_integer_validation(self):
        """Testa validação de inteiros"""
        valid_int = "123"
        invalid_int = "abc"
        
        assert self.validator.validate_integer(valid_int) == True
        assert self.validator.validate_integer(invalid_int) == False

class TestRateLimiting:
    """Testes para módulo de rate limiting (P2-2)"""
    
    def setup_method(self):
        self.rate_limiter = RateLimiter()
    
    def test_rate_limit_check(self):
        """Testa verificação de rate limit"""
        user_id = "user_123"
        action = "login"
        
        # Primeira tentativa
        result1 = self.rate_limiter.check_limit(user_id, action)
        assert result1["allowed"] == True
        
        # Múltiplas tentativas
        for _ in range(10):
            self.rate_limiter.check_limit(user_id, action)
        
        result2 = self.rate_limiter.check_limit(user_id, action)
        assert result2["allowed"] == False

class TestSecurityHeaders:
    """Testes para módulo de headers de segurança (P2-3)"""
    
    def setup_method(self):
        self.headers_manager = SecurityHeaders()
    
    def test_headers_generation(self):
        """Testa geração de headers de segurança"""
        headers = self.headers_manager.generate_headers()
        
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers

class TestSSLValidation:
    """Testes para módulo de validação SSL (P2-4)"""
    
    def setup_method(self):
        self.ssl_validator = SSLValidator()
    
    def test_certificate_validation(self):
        """Testa validação de certificados"""
        hostname = "google.com"
        
        result = self.ssl_validator.validate_certificate(hostname)
        assert isinstance(result, dict)
        assert "valid" in result

class TestLogSanitization:
    """Testes para módulo de sanitização de logs (P3-1)"""
    
    def setup_method(self):
        self.log_sanitizer = LogSanitizer()
    
    def test_log_sanitization(self):
        """Testa sanitização de logs"""
        sensitive_log = "User 123.456.789-00 accessed data"
        
        sanitized = self.log_sanitizer.sanitize_log(sensitive_log)
        assert "123.456.789-00" not in sanitized
        assert "***" in sanitized

class TestTimeoutManager:
    """Testes para módulo de timeout (P3-2)"""
    
    def setup_method(self):
        self.timeout_manager = TimeoutManager()
    
    def test_session_timeout(self):
        """Testa timeout de sessão"""
        session_id = "session_123"
        
        result = self.timeout_manager.check_timeout(session_id)
        assert isinstance(result, bool)

class TestDataIntegrity:
    """Testes para módulo de integridade de dados (P3-3)"""
    
    def setup_method(self):
        self.integrity_validator = DataIntegrityValidator()
    
    def test_data_verification(self):
        """Testa verificação de integridade"""
        data = "Dados importantes"
        
        hash_value = self.integrity_validator.generate_hash(data)
        result = self.integrity_validator.verify_integrity(data, hash_value)
        
        assert result == True

# Testes de Integração
class TestSecurityIntegration:
    """Testes de integração entre módulos de segurança"""
    
    def setup_method(self):
        self.auth_manager = AuthenticationManager()
        self.auth_manager = AuthorizationManager()
        self.encryption_manager = EncryptionManager()
    
    def test_complete_user_flow(self):
        """Testa fluxo completo de usuário"""
        # 1. Registro
        user_data = {
            "email": "integration@test.com",
            "password": "SecurePass123!",
            "role": "PARENT"
        }
        
        register_result = self.auth_manager.register_user(user_data)
        assert register_result["success"] == True
        
        # 2. Login
        credentials = {
            "email": "integration@test.com",
            "password": "SecurePass123!"
        }
        
        login_result = self.auth_manager.login(credentials)
        assert login_result["success"] == True
        
        # 3. Verificação de permissões
        user_id = register_result["user_id"]
        permission_result = self.auth_manager.check_permission(user_id, "user:read")
        assert isinstance(permission_result, bool)

# Execução dos testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 