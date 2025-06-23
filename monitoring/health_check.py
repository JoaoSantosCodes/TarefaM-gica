#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Sistema de Monitoramento e Health Check - TarefaMágica
Monitora a saúde da aplicação e gera alertas
"""

import time
import requests
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

@dataclass
class HealthMetric:
    """Métrica de saúde"""
    name: str
    value: float
    unit: str
    status: str  # 'healthy', 'warning', 'critical'
    timestamp: datetime
    description: str

@dataclass
class HealthCheck:
    """Check de saúde"""
    check_id: str
    name: str
    status: str  # 'pass', 'fail', 'warning'
    response_time: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None

class HealthMonitor:
    """Monitor de saúde da aplicação"""
    
    def __init__(self, config_path: str = "monitoring/config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.metrics: List[HealthMetric] = []
        self.checks: List[HealthCheck] = []
        
        # Configurações
        self.config = self._load_config()
        self.thresholds = self.config.get('thresholds', {})
        self.endpoints = self.config.get('endpoints', [])
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Carrega configuração do monitoramento"""
        default_config = {
            "thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 3.0,
                "error_rate": 5.0
            },
            "endpoints": [
                {
                    "name": "API Health",
                    "url": "http://localhost:8000/health",
                    "method": "GET",
                    "timeout": 5
                },
                {
                    "name": "Database",
                    "url": "http://localhost:8000/health/db",
                    "method": "GET",
                    "timeout": 3
                }
            ],
            "alerting": {
                "enabled": True,
                "webhook_url": None,
                "email": None
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Cria arquivo de configuração padrão
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
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
                logging.FileHandler('monitoring/health.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_system_metrics(self) -> List[HealthMetric]:
        """Verifica métricas do sistema"""
        metrics = []
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = self._get_status(cpu_percent, self.thresholds.get('cpu_usage', 80))
        metrics.append(HealthMetric(
            name="CPU Usage",
            value=cpu_percent,
            unit="%",
            status=cpu_status,
            timestamp=datetime.now(),
            description=f"CPU usage: {cpu_percent:.1f}%"
        ))
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_status = self._get_status(memory_percent, self.thresholds.get('memory_usage', 85))
        metrics.append(HealthMetric(
            name="Memory Usage",
            value=memory_percent,
            unit="%",
            status=memory_status,
            timestamp=datetime.now(),
            description=f"Memory usage: {memory_percent:.1f}% ({memory.used // 1024**3:.1f}GB / {memory.total // 1024**3:.1f}GB)"
        ))
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_status = self._get_status(disk_percent, self.thresholds.get('disk_usage', 90))
        metrics.append(HealthMetric(
            name="Disk Usage",
            value=disk_percent,
            unit="%",
            status=disk_status,
            timestamp=datetime.now(),
            description=f"Disk usage: {disk_percent:.1f}% ({disk.used // 1024**3:.1f}GB / {disk.total // 1024**3:.1f}GB)"
        ))
        
        self.metrics.extend(metrics)
        return metrics
    
    def check_endpoints(self) -> List[HealthCheck]:
        """Verifica endpoints da aplicação"""
        checks = []
        
        for endpoint in self.endpoints:
            check = self._check_endpoint(endpoint)
            checks.append(check)
        
        self.checks.extend(checks)
        return checks
    
    def _check_endpoint(self, endpoint: Dict) -> HealthCheck:
        """Verifica um endpoint específico"""
        start_time = time.time()
        
        try:
            response = requests.request(
                method=endpoint.get('method', 'GET'),
                url=endpoint['url'],
                timeout=endpoint.get('timeout', 5)
            )
            
            response_time = time.time() - start_time
            status = 'pass' if response.status_code == 200 else 'fail'
            
            if response_time > self.thresholds.get('response_time', 3):
                status = 'warning'
            
            return HealthCheck(
                check_id=f"endpoint_{endpoint['name'].lower().replace(' ', '_')}",
                name=endpoint['name'],
                status=status,
                response_time=response_time,
                timestamp=datetime.now(),
                details={
                    'url': endpoint['url'],
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                check_id=f"endpoint_{endpoint['name'].lower().replace(' ', '_')}",
                name=endpoint['name'],
                status='fail',
                response_time=response_time,
                timestamp=datetime.now(),
                details={'url': endpoint['url']},
                error_message=str(e)
            )
    
    def _get_status(self, value: float, threshold: float) -> str:
        """Determina status baseado no valor e threshold"""
        if value >= threshold:
            return 'critical'
        elif value >= threshold * 0.8:
            return 'warning'
        else:
            return 'healthy'
    
    def generate_health_report(self) -> Dict:
        """Gera relatório de saúde"""
        # Filtra métricas das últimas 24 horas
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        recent_checks = [c for c in self.checks if c.timestamp > cutoff_time]
        
        # Calcula estatísticas
        total_checks = len(recent_checks)
        passed_checks = len([c for c in recent_checks if c.status == 'pass'])
        failed_checks = len([c for c in recent_checks if c.status == 'fail'])
        warning_checks = len([c for c in recent_checks if c.status == 'warning'])
        
        # Calcula uptime
        uptime_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Status geral
        overall_status = 'healthy'
        if failed_checks > 0:
            overall_status = 'critical'
        elif warning_checks > 0:
            overall_status = 'warning'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'uptime_percentage': uptime_percentage,
            'statistics': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'warning_checks': warning_checks
            },
            'current_metrics': [
                {
                    'name': m.name,
                    'value': m.value,
                    'unit': m.unit,
                    'status': m.status,
                    'description': m.description
                }
                for m in recent_metrics[-10:]  # Últimas 10 métricas
            ],
            'recent_checks': [
                {
                    'name': c.name,
                    'status': c.status,
                    'response_time': c.response_time,
                    'timestamp': c.timestamp.isoformat(),
                    'error_message': c.error_message
                }
                for c in recent_checks[-20:]  # Últimos 20 checks
            ]
        }
        
        return report
    
    def send_alert(self, message: str, level: str = 'warning'):
        """Envia alerta"""
        if not self.config.get('alerting', {}).get('enabled', False):
            return
        
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'application': 'TarefaMágica'
        }
        
        # Webhook
        webhook_url = self.config.get('alerting', {}).get('webhook_url')
        if webhook_url:
            try:
                requests.post(webhook_url, json=alert_data, timeout=5)
                self.logger.info(f"Alerta enviado via webhook: {message}")
            except Exception as e:
                self.logger.error(f"Erro ao enviar alerta via webhook: {e}")
        
        # Log do alerta
        self.logger.warning(f"ALERTA [{level.upper()}]: {message}")
    
    def run_health_check(self) -> Dict:
        """Executa verificação completa de saúde"""
        self.logger.info("Iniciando verificação de saúde...")
        
        # Verifica métricas do sistema
        system_metrics = self.check_system_metrics()
        
        # Verifica endpoints
        endpoint_checks = self.check_endpoints()
        
        # Gera relatório
        report = self.generate_health_report()
        
        # Verifica se precisa enviar alertas
        critical_metrics = [m for m in system_metrics if m.status == 'critical']
        failed_checks = [c for c in endpoint_checks if c.status == 'fail']
        
        if critical_metrics:
            self.send_alert(f"Métricas críticas detectadas: {[m.name for m in critical_metrics]}", 'critical')
        
        if failed_checks:
            self.send_alert(f"Endpoints falharam: {[c.name for c in failed_checks]}", 'critical')
        
        # Salva relatório
        self._save_report(report)
        
        self.logger.info(f"Verificação de saúde concluída. Status: {report['overall_status']}")
        return report
    
    def _save_report(self, report: Dict):
        """Salva relatório em arquivo"""
        try:
            os.makedirs('monitoring/reports', exist_ok=True)
            filename = f"monitoring/reports/health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    monitor = HealthMonitor()
    report = monitor.run_health_check()
    
    print("📊 RELATÓRIO DE SAÚDE - TarefaMágica")
    print("=" * 50)
    print(f"Status Geral: {report['overall_status'].upper()}")
    print(f"Uptime: {report['uptime_percentage']:.1f}%")
    print(f"Total de Checks: {report['statistics']['total_checks']}")
    print(f"Passaram: {report['statistics']['passed_checks']}")
    print(f"Falharam: {report['statistics']['failed_checks']}")
    print(f"Avisos: {report['statistics']['warning_checks']}")
    
    if report['overall_status'] != 'healthy':
        print("\n⚠️ PROBLEMAS DETECTADOS:")
        for check in report['recent_checks']:
            if check['status'] != 'pass':
                print(f"  • {check['name']}: {check['status']} ({check.get('error_message', 'N/A')})")

if __name__ == "__main__":
    main() 