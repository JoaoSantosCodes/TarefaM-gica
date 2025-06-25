"""
Sistema de Monitoramento de Segurança - TarefaMágica
Implementa detecção de anomalias, alertas e monitoramento em tempo real
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import hashlib
import ipaddress

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    MULTIPLE_LOGIN_ATTEMPTS = "multiple_login_attempts"
    SUSPICIOUS_IP = "suspicious_ip"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    FINANCIAL_FRAUD = "financial_fraud"
    CONSENT_VIOLATION = "consent_violation"
    SYSTEM_ANOMALY = "system_anomaly"

@dataclass
class SecurityAlert:
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    user_id: Optional[str]
    ip_address: Optional[str]
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    details: Optional[Dict] = None

@dataclass
class SecurityMetric:
    metric_id: str
    metric_name: str
    value: float
    timestamp: datetime
    user_id: Optional[str] = None
    context: Optional[Dict] = None

class SecurityMonitoring:
    def __init__(self, storage_path: str = "data/security"):
        """
        Inicializa o sistema de monitoramento de segurança
        
        Args:
            storage_path: Caminho para armazenamento dos dados de segurança
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._setup_alert_queue()
        self._load_configuration()
        self._start_monitoring_thread()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "alerts"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "metrics"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "blacklist"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "whitelist"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para monitoramento"""
        log_path = os.path.join(self.storage_path, "security_monitoring.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _setup_alert_queue(self):
        """Configura fila de alertas"""
        self.alert_queue = queue.Queue()
        self.alert_handlers = []
        
    def _load_configuration(self):
        """Carrega configurações de monitoramento"""
        self.config = {
            "login_attempts_threshold": 5,
            "login_attempts_window": 300,  # 5 minutos
            "suspicious_ip_threshold": 10,
            "data_access_threshold": 100,
            "financial_threshold": 1000.0,
            "alert_retention_days": 90,
            "metrics_retention_days": 30
        }
        
        # Carrega configuração de arquivo se existir
        config_file = os.path.join(self.storage_path, "monitoring_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception as e:
                logging.error(f"Erro ao carregar configuração: {str(e)}")
                
    def _start_monitoring_thread(self):
        """Inicia thread de monitoramento"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Processa alertas na fila
                while not self.alert_queue.empty():
                    alert = self.alert_queue.get_nowait()
                    self._process_alert(alert)
                    
                # Executa verificações periódicas
                self._check_system_health()
                self._cleanup_old_data()
                
                time.sleep(10)  # Verifica a cada 10 segundos
                
            except Exception as e:
                logging.error(f"Erro no loop de monitoramento: {str(e)}")
                time.sleep(30)
                
    def monitor_login_attempt(self, user_id: str, ip_address: str, success: bool):
        """
        Monitora tentativa de login
        
        Args:
            user_id: ID do usuário
            ip_address: Endereço IP
            success: Se o login foi bem-sucedido
        """
        try:
            # Registra métrica
            self._record_metric("login_attempts", 1, user_id, {
                "ip_address": ip_address,
                "success": success
            })
            
            # Verifica múltiplas tentativas
            if not success:
                self._check_multiple_login_attempts(user_id, ip_address)
                
            # Verifica IP suspeito
            self._check_suspicious_ip(ip_address)
            
        except Exception as e:
            logging.error(f"Erro ao monitorar login: {str(e)}")
            
    def monitor_data_access(self, user_id: str, resource: str, action: str):
        """
        Monitora acesso a dados
        
        Args:
            user_id: ID do usuário
            resource: Recurso acessado
            action: Ação realizada
        """
        try:
            # Registra métrica
            self._record_metric("data_access", 1, user_id, {
                "resource": resource,
                "action": action
            })
            
            # Verifica padrões suspeitos
            self._check_data_access_patterns(user_id, resource, action)
            
        except Exception as e:
            logging.error(f"Erro ao monitorar acesso a dados: {str(e)}")
            
    def monitor_financial_activity(self, user_id: str, amount: float, transaction_type: str):
        """
        Monitora atividade financeira
        
        Args:
            user_id: ID do usuário
            amount: Valor da transação
            transaction_type: Tipo de transação
        """
        try:
            # Registra métrica
            self._record_metric("financial_activity", amount, user_id, {
                "transaction_type": transaction_type
            })
            
            # Verifica transações suspeitas
            self._check_suspicious_financial_activity(user_id, amount, transaction_type)
            
        except Exception as e:
            logging.error(f"Erro ao monitorar atividade financeira: {str(e)}")
            
    def monitor_consent_activity(self, user_id: str, consent_action: str, child_id: Optional[str] = None):
        """
        Monitora atividade de consentimento
        
        Args:
            user_id: ID do usuário
            consent_action: Ação de consentimento
            child_id: ID da criança (se aplicável)
        """
        try:
            # Registra métrica
            self._record_metric("consent_activity", 1, user_id, {
                "consent_action": consent_action,
                "child_id": child_id
            })
            
            # Verifica violações de consentimento
            self._check_consent_violations(user_id, consent_action, child_id)
            
        except Exception as e:
            logging.error(f"Erro ao monitorar atividade de consentimento: {str(e)}")
            
    def monitor_request(
        self,
        ip_address: str,
        user_agent: str,
        method: str,
        path: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Monitora requisição HTTP
        
        Args:
            ip_address: Endereço IP
            user_agent: User agent
            method: Método HTTP
            path: Caminho da requisição
            user_id: ID do usuário (opcional)
            
        Returns:
            True se monitorado com sucesso
        """
        try:
            # Registra métrica de requisição
            self._record_metric("http_requests", 1, user_id, {
                "ip_address": ip_address,
                "method": method,
                "path": path,
                "user_agent": user_agent
            })
            
            # Verifica IP suspeito
            self._check_suspicious_ip(ip_address)
            
            # Verifica padrões de acesso se houver usuário
            if user_id:
                self._check_data_access_patterns(user_id, path, method)
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao monitorar requisição: {str(e)}")
            return False
            
    def _check_multiple_login_attempts(self, user_id: str, ip_address: str):
        """Verifica múltiplas tentativas de login"""
        try:
            window_start = datetime.utcnow() - timedelta(seconds=self.config["login_attempts_window"])
            
            # Conta tentativas recentes
            attempts = self._get_login_attempts(user_id, ip_address, window_start)
            
            if len(attempts) >= self.config["login_attempts_threshold"]:
                alert = SecurityAlert(
                    alert_id=f"login_attempts_{int(time.time())}",
                    alert_type=AlertType.MULTIPLE_LOGIN_ATTEMPTS,
                    level=AlertLevel.HIGH,
                    user_id=user_id,
                    ip_address=ip_address,
                    description=f"Múltiplas tentativas de login detectadas: {len(attempts)} tentativas",
                    timestamp=datetime.utcnow(),
                    details={
                        "attempts_count": len(attempts),
                        "window_seconds": self.config["login_attempts_window"],
                        "attempts": attempts
                    }
                )
                
                self._create_alert(alert)
                
        except Exception as e:
            logging.error(f"Erro ao verificar múltiplas tentativas: {str(e)}")
            
    def _check_suspicious_ip(self, ip_address: str):
        """Verifica IP suspeito"""
        try:
            # Verifica se IP está na blacklist
            if self._is_ip_blacklisted(ip_address):
                alert = SecurityAlert(
                    alert_id=f"suspicious_ip_{int(time.time())}",
                    alert_type=AlertType.SUSPICIOUS_IP,
                    level=AlertLevel.CRITICAL,
                    user_id=None,
                    ip_address=ip_address,
                    description=f"Tentativa de acesso de IP na blacklist: {ip_address}",
                    timestamp=datetime.utcnow()
                )
                
                self._create_alert(alert)
                return
                
            # Verifica padrões suspeitos
            recent_activity = self._get_ip_activity(ip_address)
            
            if len(recent_activity) > self.config["suspicious_ip_threshold"]:
                alert = SecurityAlert(
                    alert_id=f"suspicious_ip_activity_{int(time.time())}",
                    alert_type=AlertType.SUSPICIOUS_IP,
                    level=AlertLevel.MEDIUM,
                    user_id=None,
                    ip_address=ip_address,
                    description=f"Atividade suspeita detectada do IP: {ip_address}",
                    timestamp=datetime.utcnow(),
                    details={
                        "activity_count": len(recent_activity),
                        "recent_activity": recent_activity
                    }
                )
                
                self._create_alert(alert)
                
        except Exception as e:
            logging.error(f"Erro ao verificar IP suspeito: {str(e)}")
            
    def _check_data_access_patterns(self, user_id: str, resource: str, action: str):
        """Verifica padrões suspeitos de acesso a dados"""
        try:
            # Verifica acesso não autorizado
            if not self._is_authorized_access(user_id, resource, action):
                alert = SecurityAlert(
                    alert_id=f"unauthorized_access_{int(time.time())}",
                    alert_type=AlertType.UNAUTHORIZED_ACCESS,
                    level=AlertLevel.HIGH,
                    user_id=user_id,
                    ip_address=None,
                    description=f"Acesso não autorizado detectado: {user_id} -> {resource}",
                    timestamp=datetime.utcnow(),
                    details={
                        "resource": resource,
                        "action": action
                    }
                )
                
                self._create_alert(alert)
                
        except Exception as e:
            logging.error(f"Erro ao verificar padrões de acesso: {str(e)}")
            
    def _check_suspicious_financial_activity(self, user_id: str, amount: float, transaction_type: str):
        """Verifica atividade financeira suspeita"""
        try:
            # Verifica transações de alto valor
            if amount > self.config["financial_threshold"]:
                alert = SecurityAlert(
                    alert_id=f"high_value_transaction_{int(time.time())}",
                    alert_type=AlertType.FINANCIAL_FRAUD,
                    level=AlertLevel.MEDIUM,
                    user_id=user_id,
                    ip_address=None,
                    description=f"Transação de alto valor detectada: R$ {amount:.2f}",
                    timestamp=datetime.utcnow(),
                    details={
                        "amount": amount,
                        "transaction_type": transaction_type
                    }
                )
                
                self._create_alert(alert)
                
        except Exception as e:
            logging.error(f"Erro ao verificar atividade financeira: {str(e)}")
            
    def _check_consent_violations(self, user_id: str, consent_action: str, child_id: Optional[str] = None):
        """Verifica violações de consentimento"""
        try:
            # Verifica se ação requer consentimento válido
            if not self._has_valid_consent(user_id, child_id, consent_action):
                alert = SecurityAlert(
                    alert_id=f"consent_violation_{int(time.time())}",
                    alert_type=AlertType.CONSENT_VIOLATION,
                    level=AlertLevel.HIGH,
                    user_id=user_id,
                    ip_address=None,
                    description=f"Violation de consentimento detectada: {consent_action}",
                    timestamp=datetime.utcnow(),
                    details={
                        "consent_action": consent_action,
                        "child_id": child_id
                    }
                )
                
                self._create_alert(alert)
                
        except Exception as e:
            logging.error(f"Erro ao verificar violações de consentimento: {str(e)}")
            
    def _create_alert(self, alert: SecurityAlert):
        """Cria e processa alerta"""
        try:
            # Salva alerta
            self._save_alert(alert)
            
            # Adiciona à fila de processamento
            self.alert_queue.put(alert)
            
            # Log do alerta
            logging.warning(f"Alerta de segurança criado: {alert.alert_type.value} - {alert.level.value}")
            
        except Exception as e:
            logging.error(f"Erro ao criar alerta: {str(e)}")
            
    def _process_alert(self, alert: SecurityAlert):
        """Processa alerta"""
        try:
            # Executa ações baseadas no tipo e nível do alerta
            if alert.level == AlertLevel.CRITICAL:
                self._handle_critical_alert(alert)
            elif alert.level == AlertLevel.HIGH:
                self._handle_high_alert(alert)
            elif alert.level == AlertLevel.MEDIUM:
                self._handle_medium_alert(alert)
            else:
                self._handle_low_alert(alert)
                
            # Notifica handlers registrados
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logging.error(f"Erro no handler de alerta: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Erro ao processar alerta: {str(e)}")
            
    def _handle_critical_alert(self, alert: SecurityAlert):
        """Processa alerta crítico"""
        # Bloqueia IP se necessário
        if alert.ip_address:
            self._add_to_blacklist(alert.ip_address)
            
        # Notifica administradores
        self._notify_administrators(alert)
        
    def _handle_high_alert(self, alert: SecurityAlert):
        """Processa alerta de alta prioridade"""
        # Registra para análise
        self._log_alert_for_analysis(alert)
        
        # Notifica se necessário
        if alert.alert_type in [AlertType.UNAUTHORIZED_ACCESS, AlertType.CONSENT_VIOLATION]:
            self._notify_administrators(alert)
            
    def _handle_medium_alert(self, alert: SecurityAlert):
        """Processa alerta de média prioridade"""
        # Registra para análise
        self._log_alert_for_analysis(alert)
        
    def _handle_low_alert(self, alert: SecurityAlert):
        """Processa alerta de baixa prioridade"""
        # Apenas registra
        self._log_alert_for_analysis(alert)
        
    def get_security_dashboard_data(self, days: int = 7) -> Dict:
        """
        Obtém dados para dashboard de segurança
        
        Args:
            days: Número de dias para buscar
            
        Returns:
            Dict: Dados do dashboard
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Obtém alertas
            alerts = self._get_alerts_in_period(start_date, end_date)
            
            # Obtém métricas
            metrics = self._get_metrics_in_period(start_date, end_date)
            
            # Calcula estatísticas
            stats = self._calculate_security_stats(alerts, metrics)
            
            return {
                "alerts": [self._alert_to_dict(alert) for alert in alerts],
                "metrics": [self._metric_to_dict(metric) for metric in metrics],
                "statistics": stats,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter dados do dashboard: {str(e)}")
            return {}
            
    def _calculate_security_stats(self, alerts: List[SecurityAlert], metrics: List[SecurityMetric]) -> Dict:
        """Calcula estatísticas de segurança"""
        try:
            total_alerts = len(alerts)
            critical_alerts = len([a for a in alerts if a.level == AlertLevel.CRITICAL])
            high_alerts = len([a for a in alerts if a.level == AlertLevel.HIGH])
            medium_alerts = len([a for a in alerts if a.level == AlertLevel.MEDIUM])
            low_alerts = len([a for a in alerts if a.level == AlertLevel.LOW])
            
            resolved_alerts = len([a for a in alerts if a.resolved])
            unresolved_alerts = total_alerts - resolved_alerts
            
            # Calcula métricas de atividade
            login_attempts = sum([m.value for m in metrics if m.metric_name == "login_attempts"])
            data_access = sum([m.value for m in metrics if m.metric_name == "data_access"])
            financial_activity = sum([m.value for m in metrics if m.metric_name == "financial_activity"])
            
            return {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "high_alerts": high_alerts,
                "medium_alerts": medium_alerts,
                "low_alerts": low_alerts,
                "resolved_alerts": resolved_alerts,
                "unresolved_alerts": unresolved_alerts,
                "login_attempts": login_attempts,
                "data_access": data_access,
                "financial_activity": financial_activity,
                "alert_resolution_rate": (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0
            }
            
        except Exception as e:
            logging.error(f"Erro ao calcular estatísticas: {str(e)}")
            return {}
            
    def add_alert_handler(self, handler):
        """Adiciona handler de alerta"""
        self.alert_handlers.append(handler)
        
    def _record_metric(self, metric_name: str, value: float, user_id: Optional[str] = None, context: Optional[Dict] = None):
        """Registra métrica"""
        try:
            metric = SecurityMetric(
                metric_id=f"metric_{int(time.time())}_{hashlib.md5(f'{metric_name}{user_id}'.encode()).hexdigest()[:8]}",
                metric_name=metric_name,
                value=value,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                context=context
            )
            
            self._save_metric(metric)
            
        except Exception as e:
            logging.error(f"Erro ao registrar métrica: {str(e)}")
            
    def _save_alert(self, alert: SecurityAlert):
        """Salva alerta"""
        try:
            filename = f"{alert.alert_id}.json"
            filepath = os.path.join(self.storage_path, "alerts", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._alert_to_dict(alert), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao salvar alerta: {str(e)}")
            
    def _save_metric(self, metric: SecurityMetric):
        """Salva métrica"""
        try:
            filename = f"{metric.metric_id}.json"
            filepath = os.path.join(self.storage_path, "metrics", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._metric_to_dict(metric), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao salvar métrica: {str(e)}")
            
    def _alert_to_dict(self, alert: SecurityAlert) -> Dict:
        """Converte alerta para dicionário"""
        return {
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type.value,
            "level": alert.level.value,
            "user_id": alert.user_id,
            "ip_address": alert.ip_address,
            "description": alert.description,
            "timestamp": alert.timestamp.isoformat(),
            "resolved": alert.resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "resolved_by": alert.resolved_by,
            "details": alert.details
        }
        
    def _metric_to_dict(self, metric: SecurityMetric) -> Dict:
        """Converte métrica para dicionário"""
        return {
            "metric_id": metric.metric_id,
            "metric_name": metric.metric_name,
            "value": metric.value,
            "timestamp": metric.timestamp.isoformat(),
            "user_id": metric.user_id,
            "context": metric.context
        }
        
    # Métodos auxiliares (implementação simplificada)
    def _get_login_attempts(self, user_id: str, ip_address: str, since: datetime) -> List[Dict]:
        """Obtém tentativas de login recentes"""
        # Implementação simplificada - em produção seria uma consulta ao banco
        return []
        
    def _is_ip_blacklisted(self, ip_address: str) -> bool:
        """Verifica se IP está na blacklist"""
        blacklist_file = os.path.join(self.storage_path, "blacklist", "ips.json")
        if os.path.exists(blacklist_file):
            try:
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
                    return ip_address in blacklist
            except Exception:
                pass
        return False
        
    def _get_ip_activity(self, ip_address: str) -> List[Dict]:
        """Obtém atividade recente do IP"""
        # Implementação simplificada
        return []
        
    def _is_authorized_access(self, user_id: str, resource: str, action: str) -> bool:
        """Verifica se acesso é autorizado"""
        # Implementação simplificada - em produção seria integrada com o sistema de permissões
        return True
        
    def _has_valid_consent(self, user_id: str, child_id: Optional[str], action: str) -> bool:
        """Verifica se há consentimento válido"""
        # Implementação simplificada - em produção seria integrada com o sistema de consentimento
        return True
        
    def _add_to_blacklist(self, ip_address: str):
        """Adiciona IP à blacklist"""
        try:
            blacklist_file = os.path.join(self.storage_path, "blacklist", "ips.json")
            blacklist = []
            
            if os.path.exists(blacklist_file):
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
                    
            if ip_address not in blacklist:
                blacklist.append(ip_address)
                
                with open(blacklist_file, 'w', encoding='utf-8') as f:
                    json.dump(blacklist, f, indent=2)
                    
        except Exception as e:
            logging.error(f"Erro ao adicionar IP à blacklist: {str(e)}")
            
    def _notify_administrators(self, alert: SecurityAlert):
        """Notifica administradores"""
        # Implementação simplificada - em produção seria email, SMS, etc.
        logging.critical(f"NOTIFICAÇÃO ADMIN: {alert.description}")
        
    def _log_alert_for_analysis(self, alert: SecurityAlert):
        """Registra alerta para análise"""
        logging.info(f"Alerta registrado para análise: {alert.alert_id}")
        
    def _get_alerts_in_period(self, start_date: datetime, end_date: datetime) -> List[SecurityAlert]:
        """Obtém alertas em período"""
        alerts = []
        alerts_dir = os.path.join(self.storage_path, "alerts")
        
        if os.path.exists(alerts_dir):
            for filename in os.listdir(alerts_dir):
                if filename.endswith(".json"):
                    try:
                        filepath = os.path.join(alerts_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        alert_timestamp = datetime.fromisoformat(data["timestamp"])
                        if start_date <= alert_timestamp <= end_date:
                            alert = SecurityAlert(
                                alert_id=data["alert_id"],
                                alert_type=AlertType(data["alert_type"]),
                                level=AlertLevel(data["level"]),
                                user_id=data.get("user_id"),
                                ip_address=data.get("ip_address"),
                                description=data["description"],
                                timestamp=alert_timestamp,
                                resolved=data["resolved"],
                                resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
                                resolved_by=data.get("resolved_by"),
                                details=data.get("details")
                            )
                            alerts.append(alert)
                    except Exception as e:
                        logging.error(f"Erro ao carregar alerta: {str(e)}")
                        
        return alerts
        
    def _get_metrics_in_period(self, start_date: datetime, end_date: datetime) -> List[SecurityMetric]:
        """Obtém métricas em período"""
        metrics = []
        metrics_dir = os.path.join(self.storage_path, "metrics")
        
        if os.path.exists(metrics_dir):
            for filename in os.listdir(metrics_dir):
                if filename.endswith(".json"):
                    try:
                        filepath = os.path.join(metrics_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        metric_timestamp = datetime.fromisoformat(data["timestamp"])
                        if start_date <= metric_timestamp <= end_date:
                            metric = SecurityMetric(
                                metric_id=data["metric_id"],
                                metric_name=data["metric_name"],
                                value=data["value"],
                                timestamp=metric_timestamp,
                                user_id=data.get("user_id"),
                                context=data.get("context")
                            )
                            metrics.append(metric)
                    except Exception as e:
                        logging.error(f"Erro ao carregar métrica: {str(e)}")
                        
        return metrics
        
    def _check_system_health(self):
        """Verifica saúde do sistema"""
        # Implementação simplificada
        pass
        
    def _cleanup_old_data(self):
        """Remove dados antigos"""
        try:
            # Remove alertas antigos
            alert_retention = datetime.utcnow() - timedelta(days=self.config["alert_retention_days"])
            metrics_retention = datetime.utcnow() - timedelta(days=self.config["metrics_retention_days"])
            
            # Implementação simplificada - em produção seria mais robusta
            pass
            
        except Exception as e:
            logging.error(f"Erro ao limpar dados antigos: {str(e)}")
            
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join(timeout=5) 