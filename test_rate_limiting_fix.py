#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Teste e Correção do Rate Limiting - TarefaMágica
Identifica e corrige problemas no sistema de rate limiting
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.security.rate_limiting import rate_limiter, RateLimitType

def test_rate_limiting_basic():
    """Testa funcionalidade básica do rate limiting"""
    print("🧪 Testando Rate Limiting Básico...")
    
    # Teste 1: Primeiras tentativas devem passar
    identifier = "test_user_001"
    passed_attempts = 0
    
    for i in range(5):  # Limite é 5
        allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
        if allowed:
            passed_attempts += 1
            print(f"  ✅ Tentativa {i+1}: Permitida")
        else:
            print(f"  ❌ Tentativa {i+1}: Bloqueada - {message}")
    
    print(f"  📊 Tentativas permitidas: {passed_attempts}/5")
    
    # Teste 2: 6ª tentativa deve ser bloqueada
    allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
    if not allowed:
        print(f"  ✅ 6ª tentativa: Bloqueada corretamente - {message}")
        return True
    else:
        print(f"  ❌ 6ª tentativa: Deveria ter sido bloqueada")
        return False

def test_rate_limiting_penetration():
    """Testa se o rate limiting previne ataques de força bruta"""
    print("\n🔒 Testando Rate Limiting contra Ataques...")
    
    identifier = "attacker_ip_123"
    blocked_attempts = 0
    
    # Simula 20 tentativas de ataque
    for i in range(20):
        allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
        if not allowed:
            blocked_attempts += 1
            print(f"  🛡️ Tentativa {i+1}: Bloqueada - {message}")
        else:
            print(f"  ⚠️ Tentativa {i+1}: Permitida")
    
    print(f"  📊 Tentativas bloqueadas: {blocked_attempts}/20")
    
    # Deve bloquear pelo menos 15 tentativas (após as primeiras 5)
    if blocked_attempts >= 15:
        print(f"  ✅ Rate limiting funcionando: {blocked_attempts} tentativas bloqueadas")
        return True
    else:
        print(f"  ❌ Rate limiting falhou: apenas {blocked_attempts} tentativas bloqueadas")
        return False

def test_rate_limiting_reset():
    """Testa reset do rate limiting após expiração"""
    print("\n🔄 Testando Reset do Rate Limiting...")
    
    identifier = "test_reset_001"
    
    # Faz 5 tentativas para atingir o limite
    for i in range(5):
        rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
    
    # 6ª tentativa deve ser bloqueada
    allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
    if not allowed:
        print(f"  ✅ Limite atingido: {message}")
    else:
        print(f"  ❌ Limite não foi aplicado")
        return False
    
    # Simula passagem de tempo modificando diretamente a entrada
    print("  ⏰ Simulando passagem de 5 minutos...")
    
    # Modifica diretamente o timestamp para simular expiração
    key = f"{RateLimitType.LOGIN_ATTEMPTS.value}:{identifier}"
    with rate_limiter.lock:
        if key in rate_limiter.entries:
            # Subtrai 6 minutos do first_attempt para simular expiração
            from datetime import timedelta
            rate_limiter.entries[key].first_attempt -= timedelta(minutes=6)
            print(f"  ✅ Timestamp modificado para simular expiração")
    
    # Tenta novamente - deve permitir
    allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
    if allowed:
        print(f"  ✅ Reset funcionando: tentativa permitida após expiração")
        return True
    else:
        print(f"  ❌ Reset falhou: ainda bloqueado - {message}")
        return False

def test_rate_limiting_concurrency():
    """Testa rate limiting com múltiplas threads"""
    print("\n🔄 Testando Rate Limiting com Concorrência...")
    
    import threading
    
    results = []
    threads = []
    
    def make_attempt(thread_id):
        identifier = f"concurrent_user_{thread_id}"
        allowed, message = rate_limiter.check_rate_limit(identifier, RateLimitType.LOGIN_ATTEMPTS)
        results.append((thread_id, allowed))
    
    # Cria 10 threads simultâneas
    for i in range(10):
        thread = threading.Thread(target=make_attempt, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()
    
    # Verifica resultados
    allowed_count = sum(1 for _, allowed in results if allowed)
    blocked_count = len(results) - allowed_count
    
    print(f"  📊 Resultados: {allowed_count} permitidas, {blocked_count} bloqueadas")
    
    if allowed_count > 0 and blocked_count == 0:
        print(f"  ✅ Concorrência funcionando: todas as tentativas permitidas")
        return True
    else:
        print(f"  ❌ Problema de concorrência detectado")
        return False

def main():
    """Função principal de teste"""
    print("🔧 Teste e Correção do Rate Limiting - TarefaMágica")
    print("=" * 60)
    
    # Executa testes
    tests = [
        ("Funcionalidade Básica", test_rate_limiting_basic),
        ("Proteção contra Ataques", test_rate_limiting_penetration),
        ("Reset após Expiração", test_rate_limiting_reset),
        ("Concorrência", test_rate_limiting_concurrency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {str(e)}")
    
    print(f"\n📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎯 Status: ✅ RATE LIMITING FUNCIONANDO")
        print("✅ Sistema de rate limiting está operacional!")
        print("✅ Proteção contra ataques implementada!")
        print("✅ Concorrência e reset funcionando!")
    else:
        print("\n🎯 Status: ❌ PRECISA DE CORREÇÕES")
        print("❌ Alguns problemas no rate limiting precisam ser corrigidos")
    
    return passed == total

if __name__ == "__main__":
    main() 