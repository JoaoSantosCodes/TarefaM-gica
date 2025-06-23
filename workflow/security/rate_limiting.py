"""
Sistema de Rate Limiting - TarefaMágica (P2-2)
Implementa limitação de tentativas de acesso para prevenir ataques
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class RateLimitType(Enum):
    LOGIN_ATTEMPTS = "login_attempts"
    API_REQUESTS = "api_requests"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR_ATTEMPTS = "two_factor_attempts"
    FINANCIAL_TRANSACTIONS = "financial_transactions"
    CONSENT_REQUESTS = "consent_requests"

@dataclass
class RateLimitConfig:
    max_attempts: int
    window_seconds: int
    block_duration_seconds: int
    warning_threshold: float = 0.8

@dataclass
class RateLimitEntry:
    identifier: str
    attempts: int
    first_attempt: datetime
    last_attempt: datetime
    blocked_until: Optional[datetime] = None
    warnings_sent: int = 0

class RateLimiter:
    def __init__(self):
        """
        Inicializa o sistema de rate limiting
        """
        self.limits: Dict[RateLimitType, RateLimitConfig] = {
            RateLimitType.LOGIN_ATTEMPTS: RateLimitConfig(
                max_attempts=5,
                window_seconds=300,  # 5 minutos
                block_duration_seconds=1800  # 30 minutos
            ),
            RateLimitType.API_REQUESTS: RateLimitConfig(
                max_attempts=100,
                window_seconds=60,  # 1 minuto
                block_duration_seconds=300  # 5 minutos
            ),
            RateLimitType.PASSWORD_RESET: RateLimitConfig(
                max_attempts=3,
                window_seconds=3600,  # 1 hora
                block_duration_seconds=7200  # 2 horas
            ),
            RateLimitType.TWO_FACTOR_ATTEMPTS: RateLimitConfig(
                max_attempts=3,
                window_seconds=300,  # 5 minutos
                block_duration_seconds=1800  # 30 minutos
            ),
            RateLimitType.FINANCIAL_TRANSACTIONS: RateLimitConfig(
                max_attempts=10,
                window_seconds=3600,  # 1 hora
                block_duration_seconds=7200  # 2 horas
            ),
            RateLimitType.CONSENT_REQUESTS: RateLimitConfig(
                max_attempts=5,
                window_seconds=1800,  # 30 minutos
                block_duration_seconds=3600  # 1 hora
            )
        }
        
        self.entries: Dict[str, RateLimitEntry] = {}
        self.lock = threading.Lock()
        self._cleanup_thread = None
        self._cleanup_active = True
        self._start_cleanup_thread()
        
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza de entradas expiradas"""
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()
        
    def _cleanup_loop(self):
        """Loop de limpeza de entradas expiradas"""
        while self._cleanup_active:
            try:
                self._cleanup_expired_entries()
                time.sleep(60)  # Limpa a cada minuto
            except Exception as e:
                logging.error(f"Erro no loop de limpeza: {str(e)}")
                time.sleep(300)  # Espera 5 minutos em caso de erro
                
    def _cleanup_expired_entries(self):
        """Remove entradas expiradas"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.entries.items():
                # Verifica se a janela de tempo expirou
                if current_time - entry.first_attempt > timedelta(seconds=self._get_config(key).window_seconds):
                    expired_keys.append(key)
                    
        # Remove entradas expiradas
        for key in expired_keys:
            del self.entries[key]
            
    def _get_config(self, key: str) -> RateLimitConfig:
        """Obtém configuração baseada na chave"""
        # Extrai tipo do rate limit da chave
        for limit_type in RateLimitType:
            if limit_type.value in key:
                return self.limits[limit_type]
        # Configuração padrão
        return RateLimitConfig(max_attempts=10, window_seconds=60, block_duration_seconds=300)
        
    def check_rate_limit(self, identifier: str, limit_type: RateLimitType) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a ação está dentro do limite de taxa
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
            limit_type: Tipo de limite
            
        Returns:
            Tuple[bool, Optional[str]]: (permitido, mensagem de erro)
        """
        try:
            key = f"{limit_type.value}:{identifier}"
            config = self.limits[limit_type]
            current_time = datetime.utcnow()
            
            with self.lock:
                # Verifica se existe entrada
                if key not in self.entries:
                    # Cria nova entrada
                    self.entries[key] = RateLimitEntry(
                        identifier=identifier,
                        attempts=1,
                        first_attempt=current_time,
                        last_attempt=current_time
                    )
                    return True, None
                
                entry = self.entries[key]
                
                # Verifica se está bloqueado
                if entry.blocked_until and current_time < entry.blocked_until:
                    remaining_time = entry.blocked_until - current_time
                    return False, f"Bloqueado por {int(remaining_time.total_seconds())} segundos"
                
                # Verifica se a janela de tempo expirou
                if current_time - entry.first_attempt > timedelta(seconds=config.window_seconds):
                    # Reseta contador
                    entry.attempts = 1
                    entry.first_attempt = current_time
                    entry.last_attempt = current_time
                    entry.blocked_until = None
                    entry.warnings_sent = 0
                    return True, None
                
                # Verifica se excedeu o limite
                if entry.attempts >= config.max_attempts:
                    # Bloqueia
                    entry.blocked_until = current_time + timedelta(seconds=config.block_duration_seconds)
                    return False, f"Limite excedido. Bloqueado por {config.block_duration_seconds} segundos"
                
                # Incrementa tentativas
                entry.attempts += 1
                entry.last_attempt = current_time
                
                # Verifica se está próximo do limite
                if entry.attempts >= int(config.max_attempts * config.warning_threshold):
                    remaining_attempts = config.max_attempts - entry.attempts
                    return True, f"Atenção: {remaining_attempts} tentativas restantes"
                
                return True, None
                
        except Exception as e:
            logging.error(f"Erro ao verificar rate limit: {str(e)}")
            return True, None  # Em caso de erro, permite a ação
            
    def record_attempt(self, identifier: str, limit_type: RateLimitType, success: bool = False):
        """
        Registra tentativa (para casos onde check_rate_limit não é chamado)
        
        Args:
            identifier: Identificador único
            limit_type: Tipo de limite
            success: Se a tentativa foi bem-sucedida
        """
        try:
            key = f"{limit_type.value}:{identifier}"
            current_time = datetime.utcnow()
            
            with self.lock:
                if key not in self.entries:
                    self.entries[key] = RateLimitEntry(
                        identifier=identifier,
                        attempts=1,
                        first_attempt=current_time,
                        last_attempt=current_time
                    )
                else:
                    entry = self.entries[key]
                    entry.attempts += 1
                    entry.last_attempt = current_time
                    
                    # Se foi bem-sucedida, reduz o contador
                    if success and entry.attempts > 1:
                        entry.attempts = max(1, entry.attempts - 1)
                        
        except Exception as e:
            logging.error(f"Erro ao registrar tentativa: {str(e)}")
            
    def reset_limits(self, identifier: str, limit_type: Optional[RateLimitType] = None):
        """
        Reseta limites para um identificador
        
        Args:
            identifier: Identificador único
            limit_type: Tipo específico (se None, reseta todos)
        """
        try:
            with self.lock:
                if limit_type:
                    key = f"{limit_type.value}:{identifier}"
                    if key in self.entries:
                        del self.entries[key]
                else:
                    # Remove todas as entradas para este identificador
                    keys_to_remove = [k for k in self.entries.keys() if identifier in k]
                    for key in keys_to_remove:
                        del self.entries[key]
                        
        except Exception as e:
            logging.error(f"Erro ao resetar limites: {str(e)}")
            
    def get_status(self, identifier: str, limit_type: RateLimitType) -> Dict:
        """
        Obtém status dos limites para um identificador
        
        Args:
            identifier: Identificador único
            limit_type: Tipo de limite
            
        Returns:
            Dict: Status dos limites
        """
        try:
            key = f"{limit_type.value}:{identifier}"
            config = self.limits[limit_type]
            current_time = datetime.utcnow()
            
            with self.lock:
                if key not in self.entries:
                    return {
                        "identifier": identifier,
                        "limit_type": limit_type.value,
                        "attempts": 0,
                        "max_attempts": config.max_attempts,
                        "remaining_attempts": config.max_attempts,
                        "window_seconds": config.window_seconds,
                        "blocked": False,
                        "blocked_until": None,
                        "remaining_block_time": 0
                    }
                
                entry = self.entries[key]
                blocked = entry.blocked_until and current_time < entry.blocked_until
                remaining_block_time = 0
                
                if blocked:
                    remaining_block_time = int((entry.blocked_until - current_time).total_seconds())
                
                return {
                    "identifier": identifier,
                    "limit_type": limit_type.value,
                    "attempts": entry.attempts,
                    "max_attempts": config.max_attempts,
                    "remaining_attempts": max(0, config.max_attempts - entry.attempts),
                    "window_seconds": config.window_seconds,
                    "blocked": blocked,
                    "blocked_until": entry.blocked_until.isoformat() if entry.blocked_until else None,
                    "remaining_block_time": remaining_block_time,
                    "first_attempt": entry.first_attempt.isoformat(),
                    "last_attempt": entry.last_attempt.isoformat()
                }
                
        except Exception as e:
            logging.error(f"Erro ao obter status: {str(e)}")
            return {}
            
    def get_statistics(self) -> Dict:
        """
        Obtém estatísticas do sistema de rate limiting
        
        Returns:
            Dict: Estatísticas
        """
        try:
            with self.lock:
                total_entries = len(self.entries)
                blocked_entries = sum(1 for entry in self.entries.values() 
                                    if entry.blocked_until and datetime.utcnow() < entry.blocked_until)
                
                # Estatísticas por tipo
                stats_by_type = {}
                for limit_type in RateLimitType:
                    type_entries = [entry for key, entry in self.entries.items() 
                                   if limit_type.value in key]
                    stats_by_type[limit_type.value] = {
                        "total_entries": len(type_entries),
                        "blocked_entries": sum(1 for entry in type_entries 
                                             if entry.blocked_until and datetime.utcnow() < entry.blocked_until),
                        "average_attempts": sum(entry.attempts for entry in type_entries) / len(type_entries) if type_entries else 0
                    }
                
                return {
                    "total_entries": total_entries,
                    "blocked_entries": blocked_entries,
                    "active_entries": total_entries - blocked_entries,
                    "stats_by_type": stats_by_type
                }
                
        except Exception as e:
            logging.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
            
    def stop_cleanup(self):
        """Para o thread de limpeza"""
        self._cleanup_active = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)

# Instância global do rate limiter
rate_limiter = RateLimiter() 