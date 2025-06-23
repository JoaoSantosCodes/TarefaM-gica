#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Rotas de Backup - TarefaMágica
API para gerenciamento de backup e monitoramento
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Any, Optional

# Importa módulos de backup
from ..backup.automated_backup import AutomatedBackup
from ..backup.backup_monitor import BackupMonitor

# Cria blueprint
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

# Instâncias globais
backup_system = None
backup_monitor = None

def init_backup_system():
    """Inicializa sistema de backup"""
    global backup_system, backup_monitor
    
    if backup_system is None:
        backup_system = AutomatedBackup()
    
    if backup_monitor is None:
        backup_monitor = BackupMonitor()
        backup_monitor.start_monitoring()

@backup_bp.route('/create', methods=['POST'])
def create_backup():
    """Cria novo backup"""
    try:
        init_backup_system()
        
        data = request.get_json() or {}
        backup_type = data.get('backup_type', 'manual')
        description = data.get('description', 'Backup manual via API')
        
        result = backup_system.create_backup(
            backup_type=backup_type,
            description=description
        )
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Backup criado com sucesso",
                "backup_id": result["backup_id"],
                "file_path": result["file_path"],
                "size_bytes": result["size_bytes"],
                "checksum": result["checksum"],
                "copied_files": result["copied_files"]
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/list', methods=['GET'])
def list_backups():
    """Lista todos os backups"""
    try:
        init_backup_system()
        
        result = backup_system.list_backups()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "backups": result["backups"],
                "total": result["total"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/restore/<backup_id>', methods=['POST'])
def restore_backup(backup_id: str):
    """Restaura backup específico"""
    try:
        init_backup_system()
        
        data = request.get_json() or {}
        restore_path = data.get('restore_path', f'restored_{backup_id}')
        
        result = backup_system.restore_backup(
            backup_id=backup_id,
            restore_path=restore_path
        )
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Backup restaurado com sucesso",
                "backup_id": backup_id,
                "restore_path": restore_path,
                "restored_files": result["restored_files"],
                "backup_timestamp": result["backup_timestamp"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/delete/<backup_id>', methods=['DELETE'])
def delete_backup(backup_id: str):
    """Remove backup específico"""
    try:
        init_backup_system()
        
        # Encontra backup
        list_result = backup_system.list_backups()
        if not list_result["success"]:
            return jsonify({
                "success": False,
                "error": "Erro ao listar backups"
            }), 500
        
        backup_found = None
        for backup in list_result["backups"]:
            if backup["backup_id"] == backup_id:
                backup_found = backup
                break
        
        if not backup_found:
            return jsonify({
                "success": False,
                "error": f"Backup {backup_id} não encontrado"
            }), 404
        
        # Remove arquivo
        backup_file = backup_found.get("file_path")
        if backup_file and os.path.exists(backup_file):
            os.remove(backup_file)
        
        return jsonify({
            "success": True,
            "message": f"Backup {backup_id} removido com sucesso"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/cleanup', methods=['POST'])
def cleanup_backups():
    """Remove backups antigos"""
    try:
        init_backup_system()
        
        result = backup_system.cleanup_old_backups()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "Limpeza concluída",
                "removed_count": result["removed_count"],
                "cutoff_date": result["cutoff_date"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/metrics', methods=['GET'])
def get_backup_metrics():
    """Obtém métricas de backup"""
    try:
        init_backup_system()
        
        result = backup_monitor.get_metrics()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "metrics": result["metrics"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Obtém alertas de backup"""
    try:
        init_backup_system()
        
        # Parâmetros de filtro
        level = request.args.get('level')
        resolved = request.args.get('resolved')
        
        if resolved is not None:
            resolved = resolved.lower() == 'true'
        
        alerts = backup_monitor.get_alerts(level=level, resolved=resolved)
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "total": len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id: str):
    """Resolve alerta específico"""
    try:
        init_backup_system()
        
        data = request.get_json() or {}
        resolution_message = data.get('resolution_message', 'Resolvido via API')
        
        success = backup_monitor.resolve_alert(alert_id, resolution_message)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Alerta {alert_id} resolvido com sucesso"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": f"Alerta {alert_id} não encontrado ou já resolvido"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/config', methods=['GET'])
def get_backup_config():
    """Obtém configuração de backup"""
    try:
        init_backup_system()
        
        config = backup_system.config
        
        return jsonify({
            "success": True,
            "config": config
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/config', methods=['PUT'])
def update_backup_config():
    """Atualiza configuração de backup"""
    try:
        init_backup_system()
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados de configuração não fornecidos"
            }), 400
        
        # Atualiza configuração
        backup_system.config.update(data)
        
        # Salva configuração
        config_dir = os.path.dirname(backup_system.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        with open(backup_system.config_path, 'w') as f:
            json.dump(backup_system.config, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": "Configuração atualizada com sucesso",
            "config": backup_system.config
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/status', methods=['GET'])
def get_backup_status():
    """Obtém status geral do sistema de backup"""
    try:
        init_backup_system()
        
        # Status do monitor
        monitor_status = {
            "active": backup_monitor.monitoring_active,
            "thread_alive": backup_monitor.monitor_thread.is_alive() if backup_monitor.monitor_thread else False
        }
        
        # Métricas básicas
        metrics_result = backup_monitor.get_metrics()
        metrics = metrics_result.get("metrics", {}) if metrics_result["success"] else {}
        
        # Alertas ativos
        active_alerts = backup_monitor.get_alerts(resolved=False)
        
        # Status do disco
        import psutil
        disk_usage = psutil.disk_usage(backup_system.backup_dir)
        disk_status = {
            "total_bytes": disk_usage.total,
            "used_bytes": disk_usage.used,
            "free_bytes": disk_usage.free,
            "usage_percent": (disk_usage.used / disk_usage.total) * 100
        }
        
        return jsonify({
            "success": True,
            "status": {
                "monitor": monitor_status,
                "metrics": metrics,
                "active_alerts": len(active_alerts),
                "disk": disk_status,
                "last_check": datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@backup_bp.route('/health', methods=['GET'])
def backup_health_check():
    """Verificação de saúde do sistema de backup"""
    try:
        init_backup_system()
        
        health_status = {
            "status": "healthy",
            "checks": {}
        }
        
        # Verifica se monitor está ativo
        if not backup_monitor.monitoring_active:
            health_status["status"] = "warning"
            health_status["checks"]["monitor"] = "inactive"
        else:
            health_status["checks"]["monitor"] = "active"
        
        # Verifica uso do disco
        import psutil
        disk_usage = psutil.disk_usage(backup_system.backup_dir)
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if usage_percent > 95:
            health_status["status"] = "critical"
            health_status["checks"]["disk"] = f"critical ({usage_percent:.1f}%)"
        elif usage_percent > 80:
            health_status["status"] = "warning"
            health_status["checks"]["disk"] = f"warning ({usage_percent:.1f}%)"
        else:
            health_status["checks"]["disk"] = f"ok ({usage_percent:.1f}%)"
        
        # Verifica alertas críticos
        critical_alerts = backup_monitor.get_alerts(level="critical", resolved=False)
        if critical_alerts:
            health_status["status"] = "critical"
            health_status["checks"]["alerts"] = f"critical ({len(critical_alerts)} alerts)"
        else:
            health_status["checks"]["alerts"] = "ok"
        
        # Verifica último backup
        metrics_result = backup_monitor.get_metrics()
        if metrics_result["success"]:
            metrics = metrics_result["metrics"]
            if metrics.get("last_backup_time"):
                last_backup = datetime.fromisoformat(metrics["last_backup_time"])
                hours_since_backup = (datetime.now() - last_backup).total_seconds() / 3600
                
                if hours_since_backup > 48:
                    health_status["status"] = "critical"
                    health_status["checks"]["last_backup"] = f"critical ({hours_since_backup:.1f}h ago)"
                elif hours_since_backup > 24:
                    health_status["status"] = "warning"
                    health_status["checks"]["last_backup"] = f"warning ({hours_since_backup:.1f}h ago)"
                else:
                    health_status["checks"]["last_backup"] = f"ok ({hours_since_backup:.1f}h ago)"
            else:
                health_status["checks"]["last_backup"] = "no_backups"
        else:
            health_status["checks"]["last_backup"] = "error"
        
        return jsonify({
            "success": True,
            "health": health_status,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

# Registra blueprint
def register_backup_routes(app):
    """Registra rotas de backup na aplicação"""
    app.register_blueprint(backup_bp)
    return backup_bp 