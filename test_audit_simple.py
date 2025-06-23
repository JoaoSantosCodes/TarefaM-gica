#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar o método log_api_call
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.security.audit_system import AuditSystem

def test_audit_method():
    """Testa se o método log_api_call existe"""
    try:
        audit = AuditSystem()
        
        # Verifica se o método existe
        if hasattr(audit, 'log_api_call'):
            print("✅ Método log_api_call existe")
            
            # Testa o método
            result = audit.log_api_call(
                user_id="test_user",
                action="GET",
                resource="/test",
                status_code=200,
                ip_address="127.0.0.1",
                user_agent="Test Agent",
                success=True
            )
            
            if result:
                print("✅ Método log_api_call funcionando")
                return True
            else:
                print("❌ Método log_api_call retornou False")
                return False
        else:
            print("❌ Método log_api_call não existe")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    test_audit_method() 