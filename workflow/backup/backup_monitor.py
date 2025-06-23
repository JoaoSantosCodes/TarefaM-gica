#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Monitor de Backup - TarefaMágica
Monitoramento, alertas e métricas de backup
"""

import os
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import sqlite3

@dataclass
class BackupMetrics:
    """Métricas de backup"""
    total_backups: int
    successful_backups: int
    failed_backups: int
    total_size_bytes: int
    average_size_bytes: int
    last_backup_time: Optional[datetime]
    next_scheduled_backup: Optional[datetime]
    disk_usage_percent: float
    backup_success_rate: float

@dataclass
class BackupAlert:
    """Alerta de backup"""
    alert_id: str
    timestamp: datetime
    level: str  # info, warning, error, critical
    message: str
    backup_id: Optional[str]
    resolved: bool
    resolution_time: Optional[datetime]

class BackupMonitor:
    """Monitor de backup com alertas e métricas"""
    
    def __init__(self, backup_dir: str = "backups", config_path: str = "workflow/config/backup_config.json"):
        self.backup_dir = backup_dir
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = self._load_config()
        self.monitoring_config = self.config.get("monitoring", {})
        
        # Alertas
        self.alerts: List[BackupAlert] = []
        self.alert_thresholds = {
            "disk_usage_warning": 80.0,  # 80% de uso do disco
            "disk_usage_critical": 95.0,  # 95% de uso do disco
            "backup_failure_threshold": 3,  # 3 falhas consecutivas
            "backup_age_warning": 24,  # 24 horas sem backup
            "backup_age_critical": 48,  # 48 horas sem backup
            "size_growth_warning": 50.0,  # 50% de crescimento
            "size_growth_critical": 100.0  # 100% de crescimento
        }
        
        # Métricas
        self.metrics_history: List[BackupMetrics] = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup
        self._setup_logging()
        self._load_alerts()
        
    def _load_config(self) -> Dict:
        """Carrega configuração"""
        default_config = {
            "monitoring": {
                "enabled": True,
                "check_interval": 3600,  # 1 hora
                "alert_on_failure": True,
                "metrics_retention_days": 30
            },
            "alerts": {
                "webhook_url": None,
                "email": None,
                "log_level": "INFO"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return default_config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            return default_config
    
    def _setup_logging(self):
        """Configura logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup_monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.monitoring_active:
            self.logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Monitoramento de backup iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        self.logger.info("Monitoramento de backup parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        check_interval = self.monitoring_config.get("check_interval", 3600)
        
        while self.monitoring_active:
            try:
                # Executa verificações
                self._check_backup_health()
                self._check_disk_usage()
                self._check_backup_schedule()
                self._check_backup_size_growth()
                
                # Atualiza métricas
                self._update_metrics()
                
                # Aguarda próximo check
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Aguarda 1 minuto em caso de erro
    
    def _check_backup_health(self):
        """Verifica saúde dos backups"""
        try:
            # Carrega histórico de backups
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            if not os.path.exists(history_file):
                self._create_alert("warning", "Arquivo de histórico de backup não encontrado")
                return
            
            with open(history_file, 'r', encoding='utf-8') as f:
                backup_history = json.load(f)
            
            if not backup_history:
                self._create_alert("warning", "Nenhum backup encontrado no histórico")
                return
            
            # Verifica backups recentes
            recent_backups = []
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for backup in backup_history:
                backup_time = datetime.fromisoformat(backup["timestamp"])
                if backup_time > cutoff_time:
                    recent_backups.append(backup)
            
            # Verifica falhas consecutivas
            failed_count = 0
            for backup in recent_backups[-5:]:  # Últimos 5 backups
                if backup.get("status") == "failed":
                    failed_count += 1
                else:
                    failed_count = 0
            
            if failed_count >= self.alert_thresholds["backup_failure_threshold"]:
                self._create_alert(
                    "critical",
                    f"{failed_count} falhas consecutivas de backup detectadas"
                )
            
            # Verifica último backup
            last_backup = max(backup_history, key=lambda x: x["timestamp"])
            last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
            hours_since_backup = (datetime.now() - last_backup_time).total_seconds() / 3600
            
            if hours_since_backup > self.alert_thresholds["backup_age_critical"]:
                self._create_alert(
                    "critical",
                    f"Último backup há {hours_since_backup:.1f} horas"
                )
            elif hours_since_backup > self.alert_thresholds["backup_age_warning"]:
                self._create_alert(
                    "warning",
                    f"Último backup há {hours_since_backup:.1f} horas"
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde dos backups: {e}")
            self._create_alert("error", f"Erro na verificação de saúde: {str(e)}")
    
    def _check_disk_usage(self):
        """Verifica uso do disco"""
        try:
            # Obtém uso do disco
            disk_usage = psutil.disk_usage(self.backup_dir)
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent > self.alert_thresholds["disk_usage_critical"]:
                self._create_alert(
                    "critical",
                    f"Uso crítico do disco: {usage_percent:.1f}%"
                )
            elif usage_percent > self.alert_thresholds["disk_usage_warning"]:
                self._create_alert(
                    "warning",
                    f"Uso alto do disco: {usage_percent:.1f}%"
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar uso do disco: {e}")
    
    def _check_backup_schedule(self):
        """Verifica agendamento de backups"""
        try:
            # Verifica se há backup agendado para hoje
            config = self._load_config()
            backup_schedule = config.get("backup_schedule", "02:00")
            
            # Lógica simples: se não há backup nas últimas 24h, pode haver problema no agendamento
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    backup_history = json.load(f)
                
                if backup_history:
                    last_backup = max(backup_history, key=lambda x: x["timestamp"])
                    last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
                    
                    # Se último backup foi há mais de 26 horas, pode haver problema no agendamento
                    if (datetime.now() - last_backup_time).total_seconds() > 93600:  # 26 horas
                        self._create_alert(
                            "warning",
                            "Possível problema no agendamento de backup"
                        )
                        
        except Exception as e:
            self.logger.error(f"Erro ao verificar agendamento: {e}")
    
    def _check_backup_size_growth(self):
        """Verifica crescimento do tamanho dos backups"""
        try:
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            if not os.path.exists(history_file):
                return
            
            with open(history_file, 'r', encoding='utf-8') as f:
                backup_history = json.load(f)
            
            if len(backup_history) < 2:
                return
            
            # Compara tamanho dos últimos 2 backups
            recent_backups = sorted(backup_history, key=lambda x: x["timestamp"])[-2:]
            
            size1 = recent_backups[0]["size_bytes"]
            size2 = recent_backups[1]["size_bytes"]
            
            if size1 > 0:
                growth_percent = ((size2 - size1) / size1) * 100
                
                if growth_percent > self.alert_thresholds["size_growth_critical"]:
                    self._create_alert(
                        "critical",
                        f"Crescimento crítico do backup: {growth_percent:.1f}%"
                    )
                elif growth_percent > self.alert_thresholds["size_growth_warning"]:
                    self._create_alert(
                        "warning",
                        f"Crescimento alto do backup: {growth_percent:.1f}%"
                    )
                    
        except Exception as e:
            self.logger.error(f"Erro ao verificar crescimento: {e}")
    
    def _create_alert(self, level: str, message: str, backup_id: Optional[str] = None):
        """Cria novo alerta"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = BackupAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            level=level,
            message=message,
            backup_id=backup_id,
            resolved=False,
            resolution_time=None
        )
        
        self.alerts.append(alert)
        self._save_alerts()
        
        # Log do alerta
        if level == "critical":
            self.logger.critical(f"ALERTA CRÍTICO: {message}")
        elif level == "error":
            self.logger.error(f"ALERTA DE ERRO: {message}")
        elif level == "warning":
            self.logger.warning(f"ALERTA DE AVISO: {message}")
        else:
            self.logger.info(f"ALERTA INFO: {message}")
        
        # Envia notificação
        self._send_alert_notification(alert)
    
    def resolve_alert(self, alert_id: str, resolution_message: str = ""):
        """Resolve alerta"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                
                self.logger.info(f"Alerta {alert_id} resolvido: {resolution_message}")
                self._save_alerts()
                return True
        
        return False
    
    def get_alerts(self, level: Optional[str] = None, resolved: Optional[bool] = None) -> List[Dict]:
        """Obtém alertas filtrados"""
        filtered_alerts = []
        
        for alert in self.alerts:
            if level and alert.level != level:
                continue
            if resolved is not None and alert.resolved != resolved:
                continue
            
            filtered_alerts.append({
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.level,
                "message": alert.message,
                "backup_id": alert.backup_id,
                "resolved": alert.resolved,
                "resolution_time": alert.resolution_time.isoformat() if alert.resolution_time else None
            })
        
        return filtered_alerts
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas atuais"""
        try:
            # Carrega histórico de backups
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            if not os.path.exists(history_file):
                return {
                    "success": False,
                    "error": "Arquivo de histórico não encontrado"
                }
            
            with open(history_file, 'r', encoding='utf-8') as f:
                backup_history = json.load(f)
            
            if not backup_history:
                return {
                    "success": True,
                    "metrics": {
                        "total_backups": 0,
                        "successful_backups": 0,
                        "failed_backups": 0,
                        "total_size_bytes": 0,
                        "average_size_bytes": 0,
                        "last_backup_time": None,
                        "next_scheduled_backup": None,
                        "disk_usage_percent": 0.0,
                        "backup_success_rate": 0.0
                    }
                }
            
            # Calcula métricas
            total_backups = len(backup_history)
            successful_backups = len([b for b in backup_history if b.get("status") == "success"])
            failed_backups = total_backups - successful_backups
            
            total_size = sum(b.get("size_bytes", 0) for b in backup_history)
            average_size = total_size / total_backups if total_backups > 0 else 0
            
            # Último backup
            last_backup = max(backup_history, key=lambda x: x["timestamp"])
            last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
            
            # Próximo backup agendado (estimativa)
            config = self._load_config()
            backup_schedule = config.get("backup_schedule", "02:00")
            next_backup_time = last_backup_time + timedelta(days=1)
            
            # Uso do disco
            disk_usage = psutil.disk_usage(self.backup_dir)
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Taxa de sucesso
            success_rate = (successful_backups / total_backups) * 100 if total_backups > 0 else 0
            
            metrics = BackupMetrics(
                total_backups=total_backups,
                successful_backups=successful_backups,
                failed_backups=failed_backups,
                total_size_bytes=total_size,
                average_size_bytes=average_size,
                last_backup_time=last_backup_time,
                next_scheduled_backup=next_backup_time,
                disk_usage_percent=disk_usage_percent,
                backup_success_rate=success_rate
            )
            
            # Adiciona ao histórico
            self.metrics_history.append(metrics)
            
            # Limpa histórico antigo
            retention_days = self.monitoring_config.get("metrics_retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            self.metrics_history = [
                m for m in self.metrics_history 
                if hasattr(m, 'last_backup_time') and m.last_backup_time and m.last_backup_time > cutoff_date
            ]
            
            return {
                "success": True,
                "metrics": {
                    "total_backups": metrics.total_backups,
                    "successful_backups": metrics.successful_backups,
                    "failed_backups": metrics.failed_backups,
                    "total_size_bytes": metrics.total_size_bytes,
                    "average_size_bytes": metrics.average_size_bytes,
                    "last_backup_time": metrics.last_backup_time.isoformat() if metrics.last_backup_time else None,
                    "next_scheduled_backup": metrics.next_scheduled_backup.isoformat() if metrics.next_scheduled_backup else None,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "backup_success_rate": metrics.backup_success_rate
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _update_metrics(self):
        """Atualiza métricas"""
        try:
            metrics = self.get_metrics()
            if metrics["success"]:
                self.logger.debug("Métricas atualizadas")
        except Exception as e:
            self.logger.error(f"Erro ao atualizar métricas: {e}")
    
    def _save_alerts(self):
        """Salva alertas"""
        try:
            alerts_file = os.path.join(self.backup_dir, "backup_alerts.json")
            
            alerts_data = []
            for alert in self.alerts:
                alerts_data.append({
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level,
                    "message": alert.message,
                    "backup_id": alert.backup_id,
                    "resolved": alert.resolved,
                    "resolution_time": alert.resolution_time.isoformat() if alert.resolution_time else None
                })
            
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar alertas: {e}")
    
    def _load_alerts(self):
        """Carrega alertas salvos"""
        try:
            alerts_file = os.path.join(self.backup_dir, "backup_alerts.json")
            if os.path.exists(alerts_file):
                with open(alerts_file, 'r', encoding='utf-8') as f:
                    alerts_data = json.load(f)
                
                for alert_data in alerts_data:
                    alert = BackupAlert(
                        alert_id=alert_data["alert_id"],
                        timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                        level=alert_data["level"],
                        message=alert_data["message"],
                        backup_id=alert_data.get("backup_id"),
                        resolved=alert_data["resolved"],
                        resolution_time=datetime.fromisoformat(alert_data["resolution_time"]) if alert_data.get("resolution_time") else None
                    )
                    self.alerts.append(alert)
                    
        except Exception as e:
            self.logger.error(f"Erro ao carregar alertas: {e}")
    
    def _send_alert_notification(self, alert: BackupAlert):
        """Envia notificação de alerta"""
        if not self.config.get("alerts", {}).get("webhook_url"):
            return
        
        notification_data = {
            "timestamp": alert.timestamp.isoformat(),
            "level": alert.level,
            "message": alert.message,
            "alert_id": alert.alert_id,
            "backup_id": alert.backup_id,
            "application": "TarefaMágica Backup Monitor"
        }
        
        try:
            import requests
            webhook_url = self.config["alerts"]["webhook_url"]
            requests.post(webhook_url, json=notification_data, timeout=5)
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação de alerta: {e}")

def main():
    """Função principal para testes"""
    print("📊 TESTE DE MONITOR DE BACKUP - TarefaMágica")
    print("=" * 50)
    
    # Inicializa monitor
    monitor = BackupMonitor()
    
    # Testa métricas
    print("1. Obtendo métricas...")
    metrics = monitor.get_metrics()
    
    if metrics["success"]:
        m = metrics["metrics"]
        print(f"✅ Total de backups: {m['total_backups']}")
        print(f"   Sucessos: {m['successful_backups']}")
        print(f"   Falhas: {m['failed_backups']}")
        print(f"   Taxa de sucesso: {m['backup_success_rate']:.1f}%")
        print(f"   Uso do disco: {m['disk_usage_percent']:.1f}%")
    else:
        print(f"❌ Erro: {metrics['error']}")
    
    # Testa alertas
    print("\n2. Verificando alertas...")
    alerts = monitor.get_alerts(resolved=False)
    print(f"✅ Alertas ativos: {len(alerts)}")
    
    # Inicia monitoramento
    print("\n3. Iniciando monitoramento...")
    monitor.start_monitoring()
    
    try:
        print("Monitoramento ativo. Pressione Ctrl+C para parar...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando monitoramento...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 