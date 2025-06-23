"""
Rotas da API para Sistema de Backup Seguro - TarefaMágica
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import os

from ..security.secure_backup import (
    SecureBackup, BackupJob, BackupType, BackupStatus
)

# Configuração do blueprint
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

# Instância do sistema de backup
backup_system = SecureBackup()

@backup_bp.route('/jobs', methods=['POST'])
def create_backup_job():
    """
    Cria um novo job de backup
    
    Body:
        source_paths: List[str]
        backup_type: str (full, incremental, differential)
        retention_days: int (opcional)
    """
    try:
        data = request.get_json()
        
        if not data or 'source_paths' not in data:
            return jsonify({
                'success': False,
                'error': 'source_paths é obrigatório'
            }), 400
            
        source_paths = data['source_paths']
        backup_type_str = data.get('backup_type', 'full')
        retention_days = data.get('retention_days')
        
        # Valida tipo de backup
        try:
            backup_type = BackupType(backup_type_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Tipo de backup inválido: {backup_type_str}'
            }), 400
            
        # Cria job
        job = backup_system.create_backup_job(
            source_paths=source_paths,
            backup_type=backup_type,
            retention_days=retention_days
        )
        
        return jsonify({
            'success': True,
            'job': {
                'job_id': job.job_id,
                'backup_type': job.backup_type.value,
                'source_paths': job.source_paths,
                'destination_path': job.destination_path,
                'status': job.status.value,
                'created_at': job.created_at.isoformat(),
                'retention_days': job.retention_days
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Erro ao criar job de backup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/jobs/<job_id>/execute', methods=['POST'])
def execute_backup(job_id: str):
    """
    Executa backup
    
    Args:
        job_id: ID do job
    """
    try:
        success = backup_system.execute_backup(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Backup {job_id} executado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Erro ao executar backup {job_id}'
            }), 500
            
    except Exception as e:
        logging.error(f"Erro ao executar backup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/jobs', methods=['GET'])
def list_backups():
    """
    Lista backups
    
    Query params:
        status: str (opcional)
    """
    try:
        status_str = request.args.get('status')
        status = None
        
        if status_str:
            try:
                status = BackupStatus(status_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Status inválido: {status_str}'
                }), 400
                
        jobs = backup_system.list_backups(status)
        
        return jsonify({
            'success': True,
            'jobs': [
                {
                    'job_id': job.job_id,
                    'backup_type': job.backup_type.value,
                    'source_paths': job.source_paths,
                    'destination_path': job.destination_path,
                    'status': job.status.value,
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'file_count': job.file_count,
                    'total_size': job.total_size,
                    'checksum': job.checksum,
                    'error_message': job.error_message,
                    'retention_days': job.retention_days
                }
                for job in jobs
            ]
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao listar backups: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/jobs/<job_id>', methods=['GET'])
def get_backup_job(job_id: str):
    """
    Obtém detalhes de um job de backup
    """
    try:
        job = backup_system._load_backup_job(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job não encontrado'
            }), 404
            
        return jsonify({
            'success': True,
            'job': {
                'job_id': job.job_id,
                'backup_type': job.backup_type.value,
                'source_paths': job.source_paths,
                'destination_path': job.destination_path,
                'status': job.status.value,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'file_count': job.file_count,
                'total_size': job.total_size,
                'checksum': job.checksum,
                'error_message': job.error_message,
                'retention_days': job.retention_days
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter job: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/jobs/<job_id>/restore', methods=['POST'])
def restore_backup(job_id: str):
    """
    Restaura backup
    
    Body:
        destination_path: str
    """
    try:
        data = request.get_json()
        
        if not data or 'destination_path' not in data:
            return jsonify({
                'success': False,
                'error': 'destination_path é obrigatório'
            }), 400
            
        destination_path = data['destination_path']
        
        success = backup_system.restore_backup(job_id, destination_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Backup {job_id} restaurado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Erro ao restaurar backup {job_id}'
            }), 500
            
    except Exception as e:
        logging.error(f"Erro ao restaurar backup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/cleanup', methods=['POST'])
def cleanup_old_backups():
    """
    Remove backups antigos
    """
    try:
        removed_count = backup_system.cleanup_old_backups()
        
        return jsonify({
            'success': True,
            'message': f'{removed_count} backups antigos removidos',
            'removed_count': removed_count
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao limpar backups: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@backup_bp.route('/status', methods=['GET'])
def get_backup_status():
    """
    Obtém status do sistema de backup
    """
    try:
        # Obtém estatísticas
        all_jobs = backup_system.list_backups()
        
        total_jobs = len(all_jobs)
        completed_jobs = len([j for j in all_jobs if j.status == BackupStatus.COMPLETED])
        failed_jobs = len([j for j in all_jobs if j.status == BackupStatus.FAILED])
        pending_jobs = len([j for j in all_jobs if j.status == BackupStatus.PENDING])
        
        # Calcula tamanho total dos backups
        total_size = sum([j.total_size for j in all_jobs if j.total_size])
        
        # Último backup
        last_backup = None
        if completed_jobs > 0:
            completed_jobs_list = [j for j in all_jobs if j.status == BackupStatus.COMPLETED]
            last_backup = max(completed_jobs_list, key=lambda x: x.completed_at)
            
        return jsonify({
            'success': True,
            'status': {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'pending_jobs': pending_jobs,
                'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024) if total_size else 0,
                'last_backup': {
                    'job_id': last_backup.job_id,
                    'completed_at': last_backup.completed_at.isoformat(),
                    'file_count': last_backup.file_count,
                    'total_size': last_backup.total_size
                } if last_backup else None,
                'scheduler_active': backup_system.scheduler_active
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500 