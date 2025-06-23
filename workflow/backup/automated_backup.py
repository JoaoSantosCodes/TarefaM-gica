#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 Sistema de Backup Automático - TarefaMágica
Backup automático, retenção, restauração e monitoramento
"""

import os
import json
import shutil
import zipfile
import hashlib
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
import psutil

@dataclass
class BackupInfo:
    """Informações do backup"""
    backup_id: str
    timestamp: datetime
    size_bytes: int
    file_path: str
    backup_type: str  # full, incremental, database
    status: str  # success, failed, in_progress
    checksum: str
    retention_days: int
    description: str

class AutomatedBackup:
    """Sistema de backup automático"""
    
    def __init__(self, config_path: str = "workflow/config/backup_config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.backup_history: List[BackupInfo] = []
        
        # Configurações
        self.config = self._load_config()
        self.backup_dir = self.config.get("backup_dir", "backups")
        self.retention_days = self.config.get("retention_days", 30)
        self.max_backups = self.config.get("max_backups", 100)
        self.backup_schedule = self.config.get("backup_schedule", "02:00")  # 2 AM
        
        # Diretórios para backup
        self.backup_paths = self.config.get("backup_paths", [
            "workflow/",
            "outputs/",
            "logs/",
            "checklists/",
            "docs/"
        ])
        
        # Setup logging
        self._setup_logging()
        
        # Cria diretório de backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def _load_config(self) -> Dict:
        """Carrega configuração de backup"""
        default_config = {
            "backup_dir": "backups",
            "retention_days": 30,
            "max_backups": 100,
            "backup_schedule": "02:00",
            "backup_paths": [
                "workflow/",
                "outputs/",
                "logs/",
                "checklists/",
                "docs/"
            ],
            "compression": True,
            "encryption": False,
            "notifications": {
                "enabled": True,
                "webhook_url": None,
                "email": None
            },
            "monitoring": {
                "enabled": True,
                "check_interval": 3600,  # 1 hora
                "alert_on_failure": True
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
            self.logger.error(f"Erro ao carregar configuração de backup: {e}")
            return default_config
    
    def _setup_logging(self):
        """Configura logging para backup"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup.log'),
                logging.StreamHandler()
            ]
        )
    
    def create_backup(self, backup_type: str = "full", description: str = "") -> Dict[str, Any]:
        """Cria backup completo"""
        try:
            # Gera ID único do backup
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_type}"
            
            # Cria diretório temporário
            temp_dir = f"temp_backup_{backup_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            self.logger.info(f"Iniciando backup: {backup_id}")
            
            # Copia arquivos para backup
            copied_files = []
            total_size = 0
            
            for path in self.backup_paths:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        # Copia diretório
                        dest_path = os.path.join(temp_dir, path)
                        shutil.copytree(path, dest_path)
                        copied_files.append(path)
                        
                        # Calcula tamanho
                        for root, dirs, files in os.walk(dest_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                    else:
                        # Copia arquivo
                        dest_path = os.path.join(temp_dir, os.path.basename(path))
                        shutil.copy2(path, dest_path)
                        copied_files.append(path)
                        total_size += os.path.getsize(path)
            
            # Cria arquivo de metadados
            metadata = {
                "backup_id": backup_id,
                "timestamp": datetime.now().isoformat(),
                "backup_type": backup_type,
                "description": description,
                "copied_files": copied_files,
                "total_size": total_size,
                "version": "1.0"
            }
            
            metadata_file = os.path.join(temp_dir, "backup_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Comprime backup
            backup_file = os.path.join(self.backup_dir, f"{backup_id}.zip")
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Calcula checksum
            checksum = self._calculate_checksum(backup_file)
            
            # Obtém tamanho final
            final_size = os.path.getsize(backup_file)
            
            # Cria info do backup
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now(),
                size_bytes=final_size,
                file_path=backup_file,
                backup_type=backup_type,
                status="success",
                checksum=checksum,
                retention_days=self.retention_days,
                description=description
            )
            
            # Adiciona ao histórico
            self.backup_history.append(backup_info)
            
            # Salva histórico
            self._save_backup_history()
            
            # Limpa diretório temporário
            shutil.rmtree(temp_dir)
            
            # Log do sucesso
            self.logger.info(f"Backup concluído: {backup_id} - {final_size} bytes")
            
            # Envia notificação
            self._send_notification("success", f"Backup {backup_id} concluído com sucesso")
            
            return {
                "success": True,
                "backup_id": backup_id,
                "file_path": backup_file,
                "size_bytes": final_size,
                "checksum": checksum,
                "copied_files": len(copied_files)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            
            # Envia notificação de erro
            self._send_notification("error", f"Erro no backup: {str(e)}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_backup(self, backup_id: str, restore_path: str = "restored") -> Dict[str, Any]:
        """Restaura backup"""
        try:
            # Encontra backup
            backup_info = self._find_backup(backup_id)
            if not backup_info:
                return {
                    "success": False,
                    "error": f"Backup {backup_id} não encontrado"
                }
            
            self.logger.info(f"Iniciando restauração: {backup_id}")
            
            # Cria diretório de restauração
            os.makedirs(restore_path, exist_ok=True)
            
            # Verifica checksum
            current_checksum = self._calculate_checksum(backup_info.file_path)
            if current_checksum != backup_info.checksum:
                return {
                    "success": False,
                    "error": "Checksum do backup não confere"
                }
            
            # Extrai backup
            with zipfile.ZipFile(backup_info.file_path, 'r') as zipf:
                zipf.extractall(restore_path)
            
            # Carrega metadados
            metadata_file = os.path.join(restore_path, "backup_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.logger.info(f"Restauração concluída: {backup_id}")
                self.logger.info(f"Arquivos restaurados: {len(metadata.get('copied_files', []))}")
                
                return {
                    "success": True,
                    "backup_id": backup_id,
                    "restore_path": restore_path,
                    "restored_files": metadata.get('copied_files', []),
                    "backup_timestamp": metadata.get('timestamp')
                }
            else:
                return {
                    "success": False,
                    "error": "Metadados do backup não encontrados"
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup {backup_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> Dict[str, Any]:
        """Lista todos os backups"""
        try:
            backups = []
            for backup_info in self.backup_history:
                backups.append({
                    "backup_id": backup_info.backup_id,
                    "timestamp": backup_info.timestamp.isoformat(),
                    "size_bytes": backup_info.size_bytes,
                    "backup_type": backup_info.backup_type,
                    "status": backup_info.status,
                    "description": backup_info.description,
                    "retention_days": backup_info.retention_days
                })
            
            # Ordena por timestamp (mais recente primeiro)
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {
                "success": True,
                "backups": backups,
                "total": len(backups)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Remove backups antigos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0
            
            backups_to_remove = []
            for backup_info in self.backup_history:
                if backup_info.timestamp < cutoff_date:
                    backups_to_remove.append(backup_info)
            
            for backup_info in backups_to_remove:
                try:
                    # Remove arquivo
                    if os.path.exists(backup_info.file_path):
                        os.remove(backup_info.file_path)
                    
                    # Remove do histórico
                    self.backup_history.remove(backup_info)
                    removed_count += 1
                    
                    self.logger.info(f"Backup removido: {backup_info.backup_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao remover backup {backup_info.backup_id}: {e}")
            
            # Salva histórico atualizado
            self._save_backup_history()
            
            return {
                "success": True,
                "removed_count": removed_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_backup(self):
        """Agenda backup automático"""
        schedule.every().day.at(self.backup_schedule).do(self._scheduled_backup)
        
        self.logger.info(f"Backup agendado para {self.backup_schedule}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    
    def _scheduled_backup(self):
        """Executa backup agendado"""
        self.logger.info("Executando backup agendado...")
        
        result = self.create_backup(
            backup_type="scheduled",
            description="Backup automático diário"
        )
        
        if result["success"]:
            self.logger.info("Backup agendado concluído com sucesso")
        else:
            self.logger.error(f"Erro no backup agendado: {result['error']}")
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA-256 do arquivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _find_backup(self, backup_id: str) -> Optional[BackupInfo]:
        """Encontra backup pelo ID"""
        for backup_info in self.backup_history:
            if backup_info.backup_id == backup_id:
                return backup_info
        return None
    
    def _save_backup_history(self):
        """Salva histórico de backups"""
        try:
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            
            history_data = []
            for backup_info in self.backup_history:
                history_data.append({
                    "backup_id": backup_info.backup_id,
                    "timestamp": backup_info.timestamp.isoformat(),
                    "size_bytes": backup_info.size_bytes,
                    "file_path": backup_info.file_path,
                    "backup_type": backup_info.backup_type,
                    "status": backup_info.status,
                    "checksum": backup_info.checksum,
                    "retention_days": backup_info.retention_days,
                    "description": backup_info.description
                })
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {e}")
    
    def _send_notification(self, level: str, message: str):
        """Envia notificação"""
        if not self.config.get("notifications", {}).get("enabled", False):
            return
        
        notification_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "application": "TarefaMágica Backup"
        }
        
        # Webhook
        webhook_url = self.config.get("notifications", {}).get("webhook_url")
        if webhook_url:
            try:
                import requests
                requests.post(webhook_url, json=notification_data, timeout=5)
                self.logger.info(f"Notificação enviada: {message}")
            except Exception as e:
                self.logger.error(f"Erro ao enviar notificação: {e}")
        
        # Log da notificação
        if level == "error":
            self.logger.error(f"NOTIFICAÇÃO [{level.upper()}]: {message}")
        else:
            self.logger.info(f"NOTIFICAÇÃO [{level.upper()}]: {message}")

def main():
    """Função principal para testes"""
    print("📋 TESTE DE BACKUP AUTOMÁTICO - TarefaMágica")
    print("=" * 50)
    
    # Inicializa sistema de backup
    backup_system = AutomatedBackup()
    
    # Testa criação de backup
    print("1. Criando backup...")
    result = backup_system.create_backup(
        backup_type="test",
        description="Backup de teste"
    )
    
    if result["success"]:
        print(f"✅ Backup criado: {result['backup_id']}")
        print(f"   Tamanho: {result['size_bytes']} bytes")
        print(f"   Arquivos: {result['copied_files']}")
        
        # Testa listagem
        print("\n2. Listando backups...")
        list_result = backup_system.list_backups()
        if list_result["success"]:
            print(f"✅ Total de backups: {list_result['total']}")
        
        # Testa limpeza
        print("\n3. Limpando backups antigos...")
        cleanup_result = backup_system.cleanup_old_backups()
        if cleanup_result["success"]:
            print(f"✅ Backups removidos: {cleanup_result['removed_count']}")
    
    else:
        print(f"❌ Erro: {result['error']}")

if __name__ == "__main__":
    main() 