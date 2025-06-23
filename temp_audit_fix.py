#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script temporário para adicionar método log_api_call ao AuditSystem
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.security.audit_system import AuditSystem, AuditAction, AuditCategory, AuditLevel

# Testa o método log_api_call
def test_audit_api_call():
    """Testa o método log_api_call"""
    try:
        audit = AuditSystem()
        
        # Testa registro de chamada de API
        result = audit.log_api_call(
            user_id="test_user",
            action="GET",
            resource="/api/test",
            status_code=200,
            ip_address="127.0.0.1",
            user_agent="Test Agent",
            success=True
        )
        
        if result:
            print("✅ AuditSystem.log_api_call funcionando")
            return True
        else:
            print("❌ AuditSystem.log_api_call falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

if __name__ == "__main__":
    test_audit_api_call() 