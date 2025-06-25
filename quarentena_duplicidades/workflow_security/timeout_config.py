"""
Configuração de Timeout - TarefaMágica (P3-2)
Gerencia timeouts de sessão e conexão
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import os

class TimeoutType(Enum):
    SESSION = "session"
    CONNECTION = "connection"
    REQUEST = "request"
    LOGIN = "login"
    TWO_FACTOR = "two_factor"
    CONSENT = "consent"
    FINANCIAL = "financial"
    API = "api"

class TimeoutLevel(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTENDED = "extended"

@dataclass
class TimeoutConfig:
    timeout_type: TimeoutType
    level: TimeoutLevel
    duration_seconds: int
    description: str
    auto_extend: bool = False
    max_extensions: int = 0
    warning_before_expiry: int = 300  # 5 minutos
    cleanup_interval: int = 3600  # 1 hora

@dataclass
class TimeoutSession:
    session_id: str
    user_id: str
    timeout_type: TimeoutType
    level: TimeoutLevel
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    extensions_used: int = 0
    max_extensions: int = 0
    auto_extend: bool = False
    metadata: Optional[Dict[str, Any]] = None

class TimeoutManager:
    def __init__(self, config_path: str = "data/timeout_config.json"):
        """
        Inicializa o gerenciador de timeout
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config_path = config_path
        self.sessions: Dict[str, TimeoutSession] = {}
        self.timeout_configs: Dict[TimeoutType, Dict[TimeoutLevel, TimeoutConfig]] = {}
        self.cleanup_thread = None
        self.cleanup_active = True
        
        # Callbacks para eventos de timeout
        self.timeout_callbacks: Dict[TimeoutType, List[Callable]] = {}
        self.warning_callbacks: Dict[TimeoutType, List[Callable]] = {}
        
        # Configuração de logging
        self.logger = logging.getLogger('timeout_manager')
        self.logger.setLevel(logging.INFO)
        
        # Inicializa configurações padrão
        self._setup_default_configs()
        self._load_configuration()
        self._start_cleanup_thread()
        
    def _setup_default_configs(self):
        """Configura timeouts padrão"""
        default_configs = [
            # Sessões
            TimeoutConfig(
                timeout_type=TimeoutType.SESSION,
                level=TimeoutLevel.SHORT,
                duration_seconds=1800,  # 30 minutos
                description="Sessão de usuário curta",
                auto_extend=True,
                max_extensions=2
            ),
            TimeoutConfig(
                timeout_type=TimeoutType.SESSION,
                level=TimeoutLevel.MEDIUM,
                duration_seconds=3600,  # 1 hora
                description="Sessão de usuário padrão",
                auto_extend=True,
                max_extensions=3
            ),
            TimeoutConfig(
                timeout_type=TimeoutType.SESSION,
                level=TimeoutLevel.LONG,
                duration_seconds=7200,  # 2 horas
                description="Sessão de usuário longa",
                auto_extend=True,
                max_extensions=5
            ),
            
            # Conexões
            TimeoutConfig(
                timeout_type=TimeoutType.CONNECTION,
                level=TimeoutLevel.SHORT,
                duration_seconds=300,  # 5 minutos
                description="Conexão de API curta",
                auto_extend=False
            ),
            TimeoutConfig(
                timeout_type=TimeoutType.CONNECTION,
                level=TimeoutLevel.MEDIUM,
                duration_seconds=900,  # 15 minutos
                description="Conexão de API padrão",
                auto_extend=False
            ),
            
            # Requisições
            TimeoutConfig(
                timeout_type=TimeoutType.REQUEST,
                level=TimeoutLevel.SHORT,
                duration_seconds=30,  # 30 segundos
                description="Requisição rápida",
                auto_extend=False
            ),
            TimeoutConfig(
                timeout_type=TimeoutType.REQUEST,
                level=TimeoutLevel.MEDIUM,
                duration_seconds=60,  # 1 minuto
                description="Requisição padrão",
                auto_extend=False
            ),
            TimeoutConfig(
                timeout_type=TimeoutType.REQUEST,
                level=TimeoutLevel.LONG,
                duration_seconds=300,  # 5 minutos
                description="Requisição longa",
                auto_extend=False
            ),
            
            # Login
            TimeoutConfig(
                timeout_type=TimeoutType.LOGIN,
                level=TimeoutLevel.SHORT,
                duration_seconds=300,  # 5 minutos
                description="Tentativa de login",
                auto_extend=False
            ),
            
            # 2FA
            TimeoutConfig(
                timeout_type=TimeoutType.TWO_FACTOR,
                level=TimeoutLevel.SHORT,
                duration_seconds=600,  # 10 minutos
                description="Verificação 2FA",
                auto_extend=False
            ),
            
            # Consentimento
            TimeoutConfig(
                timeout_type=TimeoutType.CONSENT,
                level=TimeoutLevel.MEDIUM,
                duration_seconds=1800,  # 30 minutos
                description="Sessão de consentimento",
                auto_extend=True,
                max_extensions=1
            ),
            
            # Financeiro
            TimeoutConfig(
                timeout_type=TimeoutType.FINANCIAL,
                level=TimeoutLevel.SHORT,
                duration_seconds=900,  # 15 minutos
                description="Transação financeira",
                auto_extend=False
            ),
            
            # API
            TimeoutConfig(
                timeout_type=TimeoutType.API,
                level=TimeoutLevel.SHORT,
                duration_seconds=60,  # 1 minuto
                description="Chamada de API",
                auto_extend=False
            )
        ]
        
        # Organiza configurações por tipo e nível
        for config in default_configs:
            if config.timeout_type not in self.timeout_configs:
                self.timeout_configs[config.timeout_type] = {}
            self.timeout_configs[config.timeout_type][config.level] = config
            
    def _load_configuration(self):
        """Carrega configuração de arquivo"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Atualiza configurações com dados do arquivo
                for timeout_type_str, levels in config_data.items():
                    timeout_type = TimeoutType(timeout_type_str)
                    if timeout_type not in self.timeout_configs:
                        self.timeout_configs[timeout_type] = {}
                        
                    for level_str, config_data in levels.items():
                        level = TimeoutLevel(level_str)
                        config = TimeoutConfig(
                            timeout_type=timeout_type,
                            level=level,
                            duration_seconds=config_data['duration_seconds'],
                            description=config_data['description'],
                            auto_extend=config_data.get('auto_extend', False),
                            max_extensions=config_data.get('max_extensions', 0),
                            warning_before_expiry=config_data.get('warning_before_expiry', 300),
                            cleanup_interval=config_data.get('cleanup_interval', 3600)
                        )
                        self.timeout_configs[timeout_type][level] = config
                        
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {str(e)}")
            
    def _save_configuration(self):
        """Salva configuração em arquivo"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_data = {}
            for timeout_type, levels in self.timeout_configs.items():
                config_data[timeout_type.value] = {}
                for level, config in levels.items():
                    config_data[timeout_type.value][level.value] = {
                        'duration_seconds': config.duration_seconds,
                        'description': config.description,
                        'auto_extend': config.auto_extend,
                        'max_extensions': config.max_extensions,
                        'warning_before_expiry': config.warning_before_expiry,
                        'cleanup_interval': config.cleanup_interval
                    }
                    
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {str(e)}")
            
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza"""
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
    def _cleanup_loop(self):
        """Loop de limpeza de sessões expiradas"""
        while self.cleanup_active:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                # Identifica sessões expiradas
                for session_id, session in self.sessions.items():
                    if current_time > session.expires_at:
                        expired_sessions.append(session_id)
                        
                # Remove sessões expiradas
                for session_id in expired_sessions:
                    self._handle_session_expiry(session_id)
                    
                # Verifica avisos de expiração
                self._check_warnings()
                    
                time.sleep(60)  # Verifica a cada minuto
                
            except Exception as e:
                self.logger.error(f"Erro no loop de limpeza: {str(e)}")
                time.sleep(300)  # Espera 5 minutos em caso de erro
                
    def _handle_session_expiry(self, session_id: str):
        """Trata expiração de sessão"""
        try:
            session = self.sessions.pop(session_id, None)
            if session:
                self.logger.info(f"Sessão expirada: {session_id} (usuário: {session.user_id})")
                
                # Executa callbacks de timeout
                if session.timeout_type in self.timeout_callbacks:
                    for callback in self.timeout_callbacks[session.timeout_type]:
                        try:
                            callback(session)
                        except Exception as e:
                            self.logger.error(f"Erro em callback de timeout: {str(e)}")
                            
        except Exception as e:
            self.logger.error(f"Erro ao tratar expiração de sessão: {str(e)}")
            
    def _check_warnings(self):
        """Verifica avisos de expiração"""
        try:
            current_time = datetime.utcnow()
            
            for session_id, session in self.sessions.items():
                if session.timeout_type in self.warning_callbacks:
                    config = self.timeout_configs.get(session.timeout_type, {}).get(session.level)
                    if config and config.warning_before_expiry > 0:
                        warning_time = session.expires_at - timedelta(seconds=config.warning_before_expiry)
                        
                        if current_time >= warning_time and not session.metadata.get('warning_sent'):
                            # Marca aviso como enviado
                            session.metadata = session.metadata or {}
                            session.metadata['warning_sent'] = True
                            
                            # Executa callbacks de aviso
                            for callback in self.warning_callbacks[session.timeout_type]:
                                try:
                                    callback(session)
                                except Exception as e:
                                    self.logger.error(f"Erro em callback de aviso: {str(e)}")
                                    
        except Exception as e:
            self.logger.error(f"Erro ao verificar avisos: {str(e)}")
            
    def create_session(
        self,
        session_id: str,
        user_id: str,
        timeout_type: TimeoutType,
        level: TimeoutLevel = TimeoutLevel.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TimeoutSession:
        """
        Cria uma nova sessão com timeout
        
        Args:
            session_id: ID único da sessão
            user_id: ID do usuário
            timeout_type: Tipo de timeout
            level: Nível de timeout
            metadata: Metadados adicionais
            
        Returns:
            TimeoutSession: Sessão criada
        """
        try:
            # Obtém configuração de timeout
            config = self.timeout_configs.get(timeout_type, {}).get(level)
            if not config:
                raise ValueError(f"Configuração não encontrada para {timeout_type.value}.{level.value}")
                
            current_time = datetime.utcnow()
            expires_at = current_time + timedelta(seconds=config.duration_seconds)
            
            session = TimeoutSession(
                session_id=session_id,
                user_id=user_id,
                timeout_type=timeout_type,
                level=level,
                created_at=current_time,
                expires_at=expires_at,
                last_activity=current_time,
                max_extensions=config.max_extensions,
                auto_extend=config.auto_extend,
                metadata=metadata or {}
            )
            
            self.sessions[session_id] = session
            self.logger.info(f"Sessão criada: {session_id} (usuário: {user_id}, tipo: {timeout_type.value}, nível: {level.value})")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Erro ao criar sessão: {str(e)}")
            raise
            
    def extend_session(self, session_id: str, duration_seconds: Optional[int] = None) -> bool:
        """
        Estende uma sessão
        
        Args:
            session_id: ID da sessão
            duration_seconds: Duração adicional em segundos (opcional)
            
        Returns:
            bool: True se estendida com sucesso
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
                
            # Verifica se pode estender
            if session.extensions_used >= session.max_extensions:
                self.logger.warning(f"Sessão {session_id} atingiu limite de extensões")
                return False
                
            # Calcula nova duração
            if duration_seconds is None:
                config = self.timeout_configs.get(session.timeout_type, {}).get(session.level)
                duration_seconds = config.duration_seconds if config else 3600
                
            # Estende sessão
            session.expires_at += timedelta(seconds=duration_seconds)
            session.last_activity = datetime.utcnow()
            session.extensions_used += 1
            session.metadata['warning_sent'] = False  # Reset aviso
            
            self.logger.info(f"Sessão estendida: {session_id} (+{duration_seconds}s, extensão {session.extensions_used}/{session.max_extensions})")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao estender sessão: {str(e)}")
            return False
            
    def update_activity(self, session_id: str) -> bool:
        """
        Atualiza atividade de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            bool: True se atualizada com sucesso
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
                
            session.last_activity = datetime.utcnow()
            
            # Auto-extensão se configurada
            if session.auto_extend and session.extensions_used < session.max_extensions:
                config = self.timeout_configs.get(session.timeout_type, {}).get(session.level)
                if config:
                    # Estende se estiver próximo de expirar (últimos 25% do tempo)
                    time_remaining = (session.expires_at - datetime.utcnow()).total_seconds()
                    if time_remaining < (config.duration_seconds * 0.25):
                        self.extend_session(session_id)
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar atividade: {str(e)}")
            return False
            
    def get_session(self, session_id: str) -> Optional[TimeoutSession]:
        """
        Obtém uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Optional[TimeoutSession]: Sessão ou None se não encontrada/expirada
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
                
            # Verifica se expirou
            if datetime.utcnow() > session.expires_at:
                self._handle_session_expiry(session_id)
                return None
                
            return session
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sessão: {str(e)}")
            return None
            
    def remove_session(self, session_id: str) -> bool:
        """
        Remove uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            bool: True se removida com sucesso
        """
        try:
            if session_id in self.sessions:
                session = self.sessions.pop(session_id)
                self.logger.info(f"Sessão removida: {session_id} (usuário: {session.user_id})")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao remover sessão: {str(e)}")
            return False
            
    def get_user_sessions(self, user_id: str) -> List[TimeoutSession]:
        """
        Obtém todas as sessões de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[TimeoutSession]: Lista de sessões
        """
        try:
            return [session for session in self.sessions.values() if session.user_id == user_id]
        except Exception as e:
            self.logger.error(f"Erro ao obter sessões do usuário: {str(e)}")
            return []
            
    def get_sessions_by_type(self, timeout_type: TimeoutType) -> List[TimeoutSession]:
        """
        Obtém sessões por tipo
        
        Args:
            timeout_type: Tipo de timeout
            
        Returns:
            List[TimeoutSession]: Lista de sessões
        """
        try:
            return [session for session in self.sessions.values() if session.timeout_type == timeout_type]
        except Exception as e:
            self.logger.error(f"Erro ao obter sessões por tipo: {str(e)}")
            return []
            
    def add_timeout_callback(self, timeout_type: TimeoutType, callback: Callable):
        """
        Adiciona callback para eventos de timeout
        
        Args:
            timeout_type: Tipo de timeout
            callback: Função callback
        """
        if timeout_type not in self.timeout_callbacks:
            self.timeout_callbacks[timeout_type] = []
        self.timeout_callbacks[timeout_type].append(callback)
        
    def add_warning_callback(self, timeout_type: TimeoutType, callback: Callable):
        """
        Adiciona callback para avisos de expiração
        
        Args:
            timeout_type: Tipo de timeout
            callback: Função callback
        """
        if timeout_type not in self.warning_callbacks:
            self.warning_callbacks[timeout_type] = []
        self.warning_callbacks[timeout_type].append(callback)
        
    def update_config(self, timeout_type: TimeoutType, level: TimeoutLevel, config: TimeoutConfig):
        """
        Atualiza configuração de timeout
        
        Args:
            timeout_type: Tipo de timeout
            level: Nível de timeout
            config: Nova configuração
        """
        try:
            if timeout_type not in self.timeout_configs:
                self.timeout_configs[timeout_type] = {}
            self.timeout_configs[timeout_type][level] = config
            self._save_configuration()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configuração: {str(e)}")
            
    def get_config(self, timeout_type: TimeoutType, level: TimeoutLevel) -> Optional[TimeoutConfig]:
        """
        Obtém configuração de timeout
        
        Args:
            timeout_type: Tipo de timeout
            level: Nível de timeout
            
        Returns:
            Optional[TimeoutConfig]: Configuração ou None
        """
        return self.timeout_configs.get(timeout_type, {}).get(level)
        
    def get_all_configs(self) -> Dict[TimeoutType, Dict[TimeoutLevel, TimeoutConfig]]:
        """
        Obtém todas as configurações
        
        Returns:
            Dict: Todas as configurações
        """
        return self.timeout_configs.copy()
        
    def get_statistics(self) -> Dict:
        """
        Obtém estatísticas do sistema
        
        Returns:
            Dict: Estatísticas
        """
        try:
            current_time = datetime.utcnow()
            
            # Estatísticas por tipo
            type_stats = {}
            for timeout_type in TimeoutType:
                sessions = self.get_sessions_by_type(timeout_type)
                type_stats[timeout_type.value] = {
                    'total_sessions': len(sessions),
                    'active_sessions': len([s for s in sessions if current_time <= s.expires_at]),
                    'expired_sessions': len([s for s in sessions if current_time > s.expires_at])
                }
                
            # Estatísticas gerais
            total_sessions = len(self.sessions)
            active_sessions = len([s for s in self.sessions.values() if current_time <= s.expires_at])
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'expired_sessions': total_sessions - active_sessions,
                'by_type': type_stats,
                'configurations': len([c for levels in self.timeout_configs.values() for c in levels.values()])
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
            
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessões expiradas manualmente
        
        Returns:
            int: Número de sessões removidas
        """
        try:
            current_time = datetime.utcnow()
            expired_sessions = [sid for sid, session in self.sessions.items() if current_time > session.expires_at]
            
            for session_id in expired_sessions:
                self._handle_session_expiry(session_id)
                
            return len(expired_sessions)
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar sessões expiradas: {str(e)}")
            return 0
            
    def stop(self):
        """Para o gerenciador de timeout"""
        self.cleanup_active = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)

# Instância global do gerenciador de timeout
timeout_manager = TimeoutManager() 