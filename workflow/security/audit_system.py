"""
Sistema de Auditoria Completa - TarefaMágica
Implementa logs detalhados de todas as ações do sistema
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import hashlib
import uuid

from .log_sanitization import log_sanitizer

class AuditLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditCategory(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    FINANCIAL = "financial"
    CONSENT = "consent"
    SECURITY = "security"
    SYSTEM = "system"
    USER_MANAGEMENT = "user_management"
    CONFIGURATION = "configuration"

class AuditAction(Enum):
    # Autenticação
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR_ENABLE = "two_factor_enable"
    TWO_FACTOR_DISABLE = "two_factor_disable"
    
    # Autorização
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    ROLE_CHANGED = "role_changed"
    ACCESS_DENIED = "access_denied"
    
    # Acesso a dados
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    
    # Financeiro
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_APPROVED = "transaction_approved"
    TRANSACTION_REJECTED = "transaction_rejected"
    PAYMENT_PROCESSED = "payment_processed"
    
    # Consentimento
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    CONSENT_UPDATED = "consent_updated"
    CONSENT_EXPIRED = "consent_expired"
    
    # Segurança
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Sistema
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # Gerenciamento de usuários
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"

@dataclass
class AuditEvent:
    event_id: str
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    category: AuditCategory
    action: AuditAction
    level: AuditLevel
    description: str
    details: Optional[Dict[str, Any]] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    success: bool = True
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class AuditQuery:
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    category: Optional[AuditCategory] = None
    action: Optional[AuditAction] = None
    level: Optional[AuditLevel] = None
    success: Optional[bool] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    limit: int = 1000
    offset: int = 0

class AuditSystem:
    def __init__(self, storage_path: str = "data/audit"):
        """
        Inicializa o sistema de auditoria
        
        Args:
            storage_path: Caminho para armazenamento dos logs de auditoria
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._load_configuration()
        self._start_audit_processor()
        
        # Configura logger com sanitização automática
        self.audit_logger = log_sanitizer.create_sanitized_logger('audit_system', logging.INFO)
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "events"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "archives"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para auditoria"""
        log_path = os.path.join(self.storage_path, "audit_system.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_configuration(self):
        """Carrega configurações de auditoria"""
        self.config = {
            "retention_days": 365,
            "max_file_size_mb": 100,
            "compression_enabled": True,
            "real_time_processing": True,
            "batch_size": 100,
            "archive_after_days": 30,
            "sanitization_enabled": True  # Habilita sanitização por padrão
        }
        
        # Carrega configuração de arquivo se existir
        config_file = os.path.join(self.storage_path, "audit_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception as e:
                logging.error(f"Erro ao carregar configuração: {str(e)}")
                
    def _start_audit_processor(self):
        """Inicia processador de auditoria"""
        self.processor_active = True
        self.event_queue = []
        self.processor_thread = threading.Thread(target=self._processor_loop)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        
    def _processor_loop(self):
        """Loop do processador de auditoria"""
        while self.processor_active:
            try:
                # Processa eventos em lote
                if len(self.event_queue) >= self.config["batch_size"]:
                    self._process_batch()
                    
                time.sleep(1)  # Verifica a cada segundo
                
            except Exception as e:
                logging.error(f"Erro no processador de auditoria: {str(e)}")
                time.sleep(10)
                
    def _process_batch(self):
        """Processa lote de eventos"""
        try:
            if not self.event_queue:
                return
                
            # Remove eventos do início da fila
            batch = self.event_queue[:self.config["batch_size"]]
            self.event_queue = self.event_queue[self.config["batch_size"]:]
            
            # Sanitiza eventos antes de salvar
            if self.config.get("sanitization_enabled", True):
                sanitized_batch = []
                for event in batch:
                    sanitized_event = self._sanitize_audit_event(event)
                    sanitized_batch.append(sanitized_event)
                batch = sanitized_batch
            
            # Salva lote sanitizado
            self._save_events_batch(batch)
            
        except Exception as e:
            logging.error(f"Erro ao processar lote de auditoria: {str(e)}")
            
    def _sanitize_audit_event(self, event: AuditEvent) -> AuditEvent:
        """
        Sanitiza um evento de auditoria removendo dados sensíveis
        
        Args:
            event: Evento de auditoria
            
        Returns:
            AuditEvent: Evento sanitizado
        """
        try:
            # Sanitiza campos de texto
            sanitized_description = log_sanitizer.sanitize_string(event.description)
            sanitized_error_message = None
            if event.error_message:
                sanitized_error_message = log_sanitizer.sanitize_string(event.error_message)
                
            # Sanitiza detalhes se existirem
            sanitized_details = None
            if event.details:
                sanitized_details = log_sanitizer.sanitize_json(event.details)
                
            # Sanitiza user_agent
            sanitized_user_agent = None
            if event.user_agent:
                sanitized_user_agent = log_sanitizer.sanitize_string(event.user_agent)
                
            # Cria novo evento sanitizado
            sanitized_event = AuditEvent(
                event_id=event.event_id,
                timestamp=event.timestamp,
                user_id=event.user_id,  # Não sanitiza user_id pois é necessário para auditoria
                session_id=event.session_id,
                ip_address=event.ip_address,  # Não sanitiza IP pois é necessário para auditoria
                user_agent=sanitized_user_agent,
                category=event.category,
                action=event.action,
                level=event.level,
                description=sanitized_description,
                details=sanitized_details,
                resource_id=event.resource_id,
                resource_type=event.resource_type,
                success=event.success,
                duration_ms=event.duration_ms,
                error_message=sanitized_error_message
            )
            
            return sanitized_event
            
        except Exception as e:
            logging.error(f"Erro ao sanitizar evento de auditoria: {str(e)}")
            return event  # Retorna evento original em caso de erro
            
    def log_event(
        self,
        user_id: Optional[str],
        category: AuditCategory,
        action: AuditAction,
        description: str,
        level: AuditLevel = AuditLevel.INFO,
        details: Optional[Dict[str, Any]] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: bool = True,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
        request_info: Optional[Dict] = None
    ):
        """
        Registra evento de auditoria
        
        Args:
            user_id: ID do usuário
            category: Categoria do evento
            action: Ação realizada
            description: Descrição do evento
            level: Nível do evento
            details: Detalhes adicionais
            resource_id: ID do recurso
            resource_type: Tipo do recurso
            success: Se a ação foi bem-sucedida
            duration_ms: Duração em milissegundos
            error_message: Mensagem de erro
            request_info: Informações da requisição
        """
        try:
            # Extrai informações da requisição
            ip_address = None
            user_agent = None
            session_id = None
            
            if request_info:
                ip_address = request_info.get('ip_address')
                user_agent = request_info.get('user_agent')
                session_id = request_info.get('session_id')
                
            # Cria evento
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                category=category,
                action=action,
                level=level,
                description=description,
                details=details,
                resource_id=resource_id,
                resource_type=resource_type,
                success=success,
                duration_ms=duration_ms,
                error_message=error_message
            )
            
            # Adiciona à fila de processamento
            if self.config["real_time_processing"]:
                self._save_event_immediate(event)
            else:
                self.event_queue.append(event)
                
        except Exception as e:
            logging.error(f"Erro ao registrar evento: {str(e)}")
            
    def _save_event_immediate(self, event: AuditEvent):
        """Salva evento imediatamente"""
        try:
            filename = f"{event.timestamp.strftime('%Y%m%d')}.json"
            filepath = os.path.join(self.storage_path, "events", filename)
            
            # Carrega eventos existentes
            events = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                    
            # Adiciona novo evento
            events.append(self._event_to_dict(event))
            
            # Salva arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao salvar evento imediato: {str(e)}")
            
    def _save_events_batch(self, events: List[AuditEvent]):
        """Salva lote de eventos"""
        try:
            # Agrupa eventos por data
            events_by_date = {}
            for event in events:
                date_key = event.timestamp.strftime('%Y%m%d')
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                events_by_date[date_key].append(event)
                
            # Salva eventos por data
            for date_key, date_events in events_by_date.items():
                filename = f"{date_key}.json"
                filepath = os.path.join(self.storage_path, "events", filename)
                
                # Carrega eventos existentes
                existing_events = []
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_events = json.load(f)
                        
                # Adiciona novos eventos
                for event in date_events:
                    existing_events.append(self._event_to_dict(event))
                    
                # Salva arquivo
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(existing_events, f, indent=2, default=str)
                    
        except Exception as e:
            logging.error(f"Erro ao salvar lote de eventos: {str(e)}")
            
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """
        Consulta eventos de auditoria
        
        Args:
            query: Parâmetros da consulta
            
        Returns:
            List[AuditEvent]: Lista de eventos
        """
        try:
            events = []
            
            # Define período de busca
            start_date = query.start_date or (datetime.utcnow() - timedelta(days=30))
            end_date = query.end_date or datetime.utcnow()
            
            # Itera sobre arquivos de eventos no período
            current_date = start_date
            while current_date <= end_date:
                filename = f"{current_date.strftime('%Y%m%d')}.json"
                filepath = os.path.join(self.storage_path, "events", filename)
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_events = json.load(f)
                        
                    for event_data in file_events:
                        event = self._dict_to_event(event_data)
                        
                        # Aplica filtros
                        if self._matches_query(event, query):
                            events.append(event)
                            
                current_date += timedelta(days=1)
                
            # Ordena por timestamp
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Aplica paginação
            events = events[query.offset:query.offset + query.limit]
            
            return events
            
        except Exception as e:
            logging.error(f"Erro ao consultar eventos: {str(e)}")
            return []
            
    def _matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Verifica se evento corresponde à consulta"""
        try:
            # Filtro por data
            if query.start_date and event.timestamp < query.start_date:
                return False
            if query.end_date and event.timestamp > query.end_date:
                return False
                
            # Filtro por usuário
            if query.user_id and event.user_id != query.user_id:
                return False
                
            # Filtro por categoria
            if query.category and event.category != query.category:
                return False
                
            # Filtro por ação
            if query.action and event.action != query.action:
                return False
                
            # Filtro por nível
            if query.level and event.level != query.level:
                return False
                
            # Filtro por sucesso
            if query.success is not None and event.success != query.success:
                return False
                
            # Filtro por recurso
            if query.resource_id and event.resource_id != query.resource_id:
                return False
                
            # Filtro por IP
            if query.ip_address and event.ip_address != query.ip_address:
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao verificar correspondência: {str(e)}")
            return False
            
    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "summary"
    ) -> Dict:
        """
        Gera relatório de auditoria
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            report_type: Tipo de relatório
            
        Returns:
            Dict: Relatório gerado
        """
        try:
            query = AuditQuery(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Busca mais eventos para relatório
            )
            
            events = self.query_events(query)
            
            if report_type == "summary":
                return self._generate_summary_report(events, start_date, end_date)
            elif report_type == "user_activity":
                return self._generate_user_activity_report(events)
            elif report_type == "security_events":
                return self._generate_security_events_report(events)
            elif report_type == "financial_audit":
                return self._generate_financial_audit_report(events)
            else:
                return self._generate_summary_report(events, start_date, end_date)
                
        except Exception as e:
            logging.error(f"Erro ao gerar relatório: {str(e)}")
            return {}
            
    def _generate_summary_report(self, events: List[AuditEvent], start_date: datetime, end_date: datetime) -> Dict:
        """Gera relatório resumido"""
        try:
            total_events = len(events)
            successful_events = len([e for e in events if e.success])
            failed_events = total_events - successful_events
            
            # Estatísticas por categoria
            category_stats = {}
            for event in events:
                category = event.category.value
                if category not in category_stats:
                    category_stats[category] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0
                    }
                category_stats[category]["total"] += 1
                if event.success:
                    category_stats[category]["successful"] += 1
                else:
                    category_stats[category]["failed"] += 1
                    
            # Estatísticas por nível
            level_stats = {}
            for event in events:
                level = event.level.value
                if level not in level_stats:
                    level_stats[level] = 0
                level_stats[level] += 1
                
            # Usuários mais ativos
            user_activity = {}
            for event in events:
                if event.user_id:
                    if event.user_id not in user_activity:
                        user_activity[event.user_id] = 0
                    user_activity[event.user_id] += 1
                    
            top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "report_type": "summary",
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "statistics": {
                    "total_events": total_events,
                    "successful_events": successful_events,
                    "failed_events": failed_events,
                    "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0
                },
                "category_statistics": category_stats,
                "level_statistics": level_stats,
                "top_users": top_users,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório resumido: {str(e)}")
            return {}
            
    def _generate_user_activity_report(self, events: List[AuditEvent]) -> Dict:
        """Gera relatório de atividade de usuários"""
        try:
            user_activity = {}
            
            for event in events:
                if event.user_id:
                    if event.user_id not in user_activity:
                        user_activity[event.user_id] = {
                            "total_events": 0,
                            "categories": {},
                            "actions": {},
                            "last_activity": None,
                            "ip_addresses": set(),
                            "sessions": set()
                        }
                        
                    user_activity[event.user_id]["total_events"] += 1
                    
                    # Categorias
                    category = event.category.value
                    if category not in user_activity[event.user_id]["categories"]:
                        user_activity[event.user_id]["categories"][category] = 0
                    user_activity[event.user_id]["categories"][category] += 1
                    
                    # Ações
                    action = event.action.value
                    if action not in user_activity[event.user_id]["actions"]:
                        user_activity[event.user_id]["actions"][action] = 0
                    user_activity[event.user_id]["actions"][action] += 1
                    
                    # Última atividade
                    if not user_activity[event.user_id]["last_activity"] or event.timestamp > user_activity[event.user_id]["last_activity"]:
                        user_activity[event.user_id]["last_activity"] = event.timestamp
                        
                    # IPs
                    if event.ip_address:
                        user_activity[event.user_id]["ip_addresses"].add(event.ip_address)
                        
                    # Sessões
                    if event.session_id:
                        user_activity[event.user_id]["sessions"].add(event.session_id)
                        
            # Converte sets para listas para serialização JSON
            for user_id, activity in user_activity.items():
                activity["ip_addresses"] = list(activity["ip_addresses"])
                activity["sessions"] = list(activity["sessions"])
                activity["last_activity"] = activity["last_activity"].isoformat() if activity["last_activity"] else None
                
            return {
                "report_type": "user_activity",
                "user_activity": user_activity,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de atividade: {str(e)}")
            return {}
            
    def _generate_security_events_report(self, events: List[AuditEvent]) -> Dict:
        """Gera relatório de eventos de segurança"""
        try:
            security_events = [e for e in events if e.category == AuditCategory.SECURITY]
            
            # Agrupa por tipo de evento
            event_types = {}
            for event in security_events:
                action = event.action.value
                if action not in event_types:
                    event_types[action] = []
                event_types[action].append(self._event_to_dict(event))
                
            # Estatísticas de segurança
            security_stats = {
                "total_security_events": len(security_events),
                "critical_events": len([e for e in security_events if e.level == AuditLevel.CRITICAL]),
                "high_events": len([e for e in security_events if e.level == AuditLevel.ERROR]),
                "warning_events": len([e for e in security_events if e.level == AuditLevel.WARNING]),
                "failed_events": len([e for e in security_events if not e.success])
            }
            
            return {
                "report_type": "security_events",
                "security_statistics": security_stats,
                "event_types": event_types,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de segurança: {str(e)}")
            return {}
            
    def _generate_financial_audit_report(self, events: List[AuditEvent]) -> Dict:
        """Gera relatório de auditoria financeira"""
        try:
            financial_events = [e for e in events if e.category == AuditCategory.FINANCIAL]
            
            # Estatísticas financeiras
            total_transactions = len(financial_events)
            successful_transactions = len([e for e in financial_events if e.success])
            failed_transactions = total_transactions - successful_transactions
            
            # Análise por tipo de transação
            transaction_types = {}
            for event in financial_events:
                action = event.action.value
                if action not in transaction_types:
                    transaction_types[action] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0
                    }
                transaction_types[action]["total"] += 1
                if event.success:
                    transaction_types[action]["successful"] += 1
                else:
                    transaction_types[action]["failed"] += 1
                    
            return {
                "report_type": "financial_audit",
                "financial_statistics": {
                    "total_transactions": total_transactions,
                    "successful_transactions": successful_transactions,
                    "failed_transactions": failed_transactions,
                    "success_rate": (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
                },
                "transaction_types": transaction_types,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório financeiro: {str(e)}")
            return {}
            
    def cleanup_old_events(self) -> int:
        """
        Remove eventos antigos
        
        Returns:
            int: Número de eventos removidos
        """
        try:
            removed_count = 0
            retention_date = datetime.utcnow() - timedelta(days=self.config["retention_days"])
            
            events_dir = os.path.join(self.storage_path, "events")
            if os.path.exists(events_dir):
                for filename in os.listdir(events_dir):
                    if filename.endswith(".json"):
                        try:
                            file_date_str = filename.replace(".json", "")
                            file_date = datetime.strptime(file_date_str, "%Y%m%d")
                            
                            if file_date < retention_date:
                                filepath = os.path.join(events_dir, filename)
                                os.remove(filepath)
                                removed_count += 1
                                
                        except Exception as e:
                            logging.error(f"Erro ao processar arquivo {filename}: {str(e)}")
                            
            logging.info(f"Eventos antigos removidos: {removed_count}")
            return removed_count
            
        except Exception as e:
            logging.error(f"Erro ao limpar eventos antigos: {str(e)}")
            return 0
            
    def _event_to_dict(self, event: AuditEvent) -> Dict:
        """Converte evento para dicionário com sanitização de dados sensíveis"""
        # Sanitiza dados sensíveis antes da conversão
        sanitized_description = log_sanitizer.sanitize_string(event.description)
        sanitized_error_message = None
        if event.error_message:
            sanitized_error_message = log_sanitizer.sanitize_string(event.error_message)
            
        sanitized_user_agent = None
        if event.user_agent:
            sanitized_user_agent = log_sanitizer.sanitize_string(event.user_agent)
            
        sanitized_details = None
        if event.details:
            sanitized_details = log_sanitizer.sanitize_json(event.details)
            
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,  # Mantém user_id para auditoria
            "session_id": event.session_id,
            "ip_address": event.ip_address,  # Mantém IP para auditoria
            "user_agent": sanitized_user_agent,
            "category": event.category.value,
            "action": event.action.value,
            "level": event.level.value,
            "description": sanitized_description,
            "details": sanitized_details,
            "resource_id": event.resource_id,
            "resource_type": event.resource_type,
            "success": event.success,
            "duration_ms": event.duration_ms,
            "error_message": sanitized_error_message
        }
        
    def _dict_to_event(self, data: Dict) -> AuditEvent:
        """Converte dicionário para evento"""
        return AuditEvent(
            event_id=data["event_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            category=AuditCategory(data["category"]),
            action=AuditAction(data["action"]),
            level=AuditLevel(data["level"]),
            description=data["description"],
            details=data.get("details"),
            resource_id=data.get("resource_id"),
            resource_type=data.get("resource_type"),
            success=data.get("success", True),
            duration_ms=data.get("duration_ms"),
            error_message=data.get("error_message")
        )
        
    def stop_processor(self):
        """Para o processador"""
        self.processor_active = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5) 