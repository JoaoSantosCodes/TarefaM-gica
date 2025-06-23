"""
Sistema de Backup Seguro - TarefaMágica
Implementa backup criptografado com retenção configurável
"""

import json
import logging
import os
import shutil
import zipfile
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import schedule
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"

@dataclass
class BackupJob:
    job_id: str
    backup_type: BackupType
    source_paths: List[str]
    destination_path: str
    encryption_key: bytes
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_count: int = 0
    total_size: int = 0
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    retention_days: int = 30

@dataclass
class BackupMetadata:
    backup_id: str
    job_id: str
    backup_type: str
    source_paths: List[str]
    file_count: int
    total_size: int
    checksum: str
    created_at: datetime
    encryption_key_hash: str
    compression_ratio: float
    verification_status: bool

class SecureBackup:
    def __init__(self, storage_path: str = "data/backups", encryption_password: str = None):
        """
        Inicializa o sistema de backup seguro
        
        Args:
            storage_path: Caminho para armazenamento dos backups
            encryption_password: Senha para criptografia (se None, gera automaticamente)
        """
        self.storage_path = storage_path
        self.encryption_password = encryption_password or self._generate_password()
        self._setup_storage()
        self._setup_logging()
        self._load_configuration()
        self._start_backup_scheduler()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "jobs"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "backups"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "metadata"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "temp"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para backup"""
        log_path = os.path.join(self.storage_path, "backup.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_configuration(self):
        """Carrega configurações de backup"""
        self.config = {
            "default_retention_days": 30,
            "max_backup_size_gb": 10,
            "compression_level": 6,
            "encryption_algorithm": "AES-256",
            "backup_schedule": {
                "full_backup": "weekly",
                "incremental_backup": "daily",
                "time": "02:00"
            },
            "exclude_patterns": [
                "*.tmp",
                "*.log",
                "__pycache__",
                ".git",
                "node_modules"
            ]
        }
        
        # Carrega configuração de arquivo se existir
        config_file = os.path.join(self.storage_path, "backup_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception as e:
                logging.error(f"Erro ao carregar configuração: {str(e)}")
                
    def _generate_password(self) -> str:
        """Gera senha aleatória para criptografia"""
        import secrets
        return secrets.token_urlsafe(32)
        
    def _start_backup_scheduler(self):
        """Inicia agendador de backups"""
        self.scheduler_active = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
    def _scheduler_loop(self):
        """Loop do agendador"""
        while self.scheduler_active:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logging.error(f"Erro no agendador: {str(e)}")
                time.sleep(300)  # Espera 5 minutos em caso de erro
                
    def create_backup_job(
        self,
        source_paths: List[str],
        backup_type: BackupType = BackupType.FULL,
        retention_days: Optional[int] = None
    ) -> BackupJob:
        """
        Cria um novo job de backup
        
        Args:
            source_paths: Lista de caminhos para backup
            backup_type: Tipo de backup
            retention_days: Dias de retenção
            
        Returns:
            BackupJob: Job criado
        """
        try:
            job_id = f"backup_{int(time.time())}_{hashlib.md5(str(source_paths).encode()).hexdigest()[:8]}"
            
            # Gera chave de criptografia
            encryption_key = self._generate_encryption_key()
            
            # Define caminho de destino
            destination_path = os.path.join(
                self.storage_path,
                "backups",
                f"{job_id}.encrypted"
            )
            
            # Cria job
            job = BackupJob(
                job_id=job_id,
                backup_type=backup_type,
                source_paths=source_paths,
                destination_path=destination_path,
                encryption_key=encryption_key,
                status=BackupStatus.PENDING,
                created_at=datetime.utcnow(),
                retention_days=retention_days or self.config["default_retention_days"]
            )
            
            # Salva job
            self._save_backup_job(job)
            
            logging.info(f"Job de backup criado: {job_id}")
            return job
            
        except Exception as e:
            logging.error(f"Erro ao criar job de backup: {str(e)}")
            raise
            
    def execute_backup(self, job_id: str) -> bool:
        """
        Executa backup
        
        Args:
            job_id: ID do job
            
        Returns:
            bool: True se executado com sucesso
        """
        try:
            # Carrega job
            job = self._load_backup_job(job_id)
            if not job:
                raise ValueError(f"Job não encontrado: {job_id}")
                
            # Atualiza status
            job.status = BackupStatus.IN_PROGRESS
            job.started_at = datetime.utcnow()
            self._save_backup_job(job)
            
            # Executa backup
            success = self._perform_backup(job)
            
            if success:
                job.status = BackupStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                
                # Verifica integridade
                if self._verify_backup(job):
                    job.status = BackupStatus.VERIFIED
                    
            else:
                job.status = BackupStatus.FAILED
                
            # Salva job atualizado
            self._save_backup_job(job)
            
            return success
            
        except Exception as e:
            logging.error(f"Erro ao executar backup: {str(e)}")
            
            # Atualiza job com erro
            if 'job' in locals():
                job.status = BackupStatus.FAILED
                job.error_message = str(e)
                self._save_backup_job(job)
                
            return False
            
    def _perform_backup(self, job: BackupJob) -> bool:
        """Executa o backup"""
        try:
            # Cria arquivo temporário
            temp_file = os.path.join(self.storage_path, "temp", f"{job.job_id}.zip")
            
            # Cria arquivo ZIP
            with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=self.config["compression_level"]) as zipf:
                file_count = 0
                total_size = 0
                
                for source_path in job.source_paths:
                    if os.path.exists(source_path):
                        if os.path.isfile(source_path):
                            # Arquivo único
                            if not self._should_exclude(source_path):
                                zipf.write(source_path, os.path.basename(source_path))
                                file_count += 1
                                total_size += os.path.getsize(source_path)
                        else:
                            # Diretório
                            for root, dirs, files in os.walk(source_path):
                                # Remove diretórios excluídos
                                dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d))]
                                
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    if not self._should_exclude(file_path):
                                        arcname = os.path.relpath(file_path, source_path)
                                        zipf.write(file_path, arcname)
                                        file_count += 1
                                        total_size += os.path.getsize(file_path)
                                        
            # Atualiza estatísticas
            job.file_count = file_count
            job.total_size = total_size
            
            # Calcula checksum
            job.checksum = self._calculate_checksum(temp_file)
            
            # Criptografa arquivo
            self._encrypt_file(temp_file, job.destination_path, job.encryption_key)
            
            # Remove arquivo temporário
            os.remove(temp_file)
            
            # Cria metadados
            self._create_backup_metadata(job)
            
            logging.info(f"Backup executado com sucesso: {job.job_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao executar backup: {str(e)}")
            return False
            
    def _should_exclude(self, path: str) -> bool:
        """Verifica se caminho deve ser excluído"""
        for pattern in self.config["exclude_patterns"]:
            if pattern.startswith("*."):
                # Extensão de arquivo
                if path.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                # Padrão de diretório
                return True
        return False
        
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum do arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def _generate_encryption_key(self) -> bytes:
        """Gera chave de criptografia"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_password.encode()))
        return key
        
    def _encrypt_file(self, source_path: str, destination_path: str, key: bytes):
        """Criptografa arquivo"""
        fernet = Fernet(key)
        
        with open(source_path, 'rb') as file:
            file_data = file.read()
            
        encrypted_data = fernet.encrypt(file_data)
        
        with open(destination_path, 'wb') as file:
            file.write(encrypted_data)
            
    def _decrypt_file(self, source_path: str, destination_path: str, key: bytes):
        """Descriptografa arquivo"""
        fernet = Fernet(key)
        
        with open(source_path, 'rb') as file:
            encrypted_data = file.read()
            
        decrypted_data = fernet.decrypt(encrypted_data)
        
        with open(destination_path, 'wb') as file:
            file.write(decrypted_data)
            
    def _verify_backup(self, job: BackupJob) -> bool:
        """Verifica integridade do backup"""
        try:
            # Descriptografa temporariamente
            temp_file = os.path.join(self.storage_path, "temp", f"verify_{job.job_id}.zip")
            self._decrypt_file(job.destination_path, temp_file, job.encryption_key)
            
            # Verifica checksum
            current_checksum = self._calculate_checksum(temp_file)
            
            # Remove arquivo temporário
            os.remove(temp_file)
            
            return current_checksum == job.checksum
            
        except Exception as e:
            logging.error(f"Erro ao verificar backup: {str(e)}")
            return False
            
    def restore_backup(self, job_id: str, destination_path: str) -> bool:
        """
        Restaura backup
        
        Args:
            job_id: ID do job
            destination_path: Caminho de destino
            
        Returns:
            bool: True se restaurado com sucesso
        """
        try:
            # Carrega job
            job = self._load_backup_job(job_id)
            if not job:
                raise ValueError(f"Job não encontrado: {job_id}")
                
            # Verifica se backup existe
            if not os.path.exists(job.destination_path):
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {job.destination_path}")
                
            # Cria diretório de destino
            os.makedirs(destination_path, exist_ok=True)
            
            # Descriptografa backup
            temp_file = os.path.join(self.storage_path, "temp", f"restore_{job.job_id}.zip")
            self._decrypt_file(job.destination_path, temp_file, job.encryption_key)
            
            # Extrai arquivos
            with zipfile.ZipFile(temp_file, 'r') as zipf:
                zipf.extractall(destination_path)
                
            # Remove arquivo temporário
            os.remove(temp_file)
            
            logging.info(f"Backup restaurado com sucesso: {job_id} -> {destination_path}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao restaurar backup: {str(e)}")
            return False
            
    def list_backups(self, status: Optional[BackupStatus] = None) -> List[BackupJob]:
        """
        Lista backups
        
        Args:
            status: Filtro por status
            
        Returns:
            List[BackupJob]: Lista de jobs
        """
        try:
            jobs = []
            jobs_dir = os.path.join(self.storage_path, "jobs")
            
            if os.path.exists(jobs_dir):
                for filename in os.listdir(jobs_dir):
                    if filename.endswith(".json"):
                        job = self._load_backup_job_from_file(filename)
                        if job and (status is None or job.status == status):
                            jobs.append(job)
                            
            # Ordena por data de criação
            jobs.sort(key=lambda x: x.created_at, reverse=True)
            
            return jobs
            
        except Exception as e:
            logging.error(f"Erro ao listar backups: {str(e)}")
            return []
            
    def cleanup_old_backups(self) -> int:
        """
        Remove backups antigos
        
        Returns:
            int: Número de backups removidos
        """
        try:
            removed_count = 0
            jobs = self.list_backups()
            
            for job in jobs:
                if job.completed_at:
                    retention_date = job.completed_at + timedelta(days=job.retention_days)
                    
                    if datetime.utcnow() > retention_date:
                        if self._delete_backup(job):
                            removed_count += 1
                            
            logging.info(f"Backups antigos removidos: {removed_count}")
            return removed_count
            
        except Exception as e:
            logging.error(f"Erro ao limpar backups antigos: {str(e)}")
            return 0
            
    def _delete_backup(self, job: BackupJob) -> bool:
        """Remove backup"""
        try:
            # Remove arquivo de backup
            if os.path.exists(job.destination_path):
                os.remove(job.destination_path)
                
            # Remove metadados
            metadata_file = os.path.join(self.storage_path, "metadata", f"{job.job_id}.json")
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
                
            # Remove job
            job_file = os.path.join(self.storage_path, "jobs", f"{job.job_id}.json")
            if os.path.exists(job_file):
                os.remove(job_file)
                
            logging.info(f"Backup removido: {job.job_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao remover backup: {str(e)}")
            return False
            
    def _save_backup_job(self, job: BackupJob):
        """Salva job de backup"""
        try:
            filename = f"{job.job_id}.json"
            filepath = os.path.join(self.storage_path, "jobs", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._job_to_dict(job), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao salvar job: {str(e)}")
            
    def _load_backup_job(self, job_id: str) -> Optional[BackupJob]:
        """Carrega job de backup"""
        try:
            filename = f"{job_id}.json"
            return self._load_backup_job_from_file(filename)
        except Exception as e:
            logging.error(f"Erro ao carregar job: {str(e)}")
            return None
            
    def _load_backup_job_from_file(self, filename: str) -> Optional[BackupJob]:
        """Carrega job de backup de arquivo"""
        try:
            filepath = os.path.join(self.storage_path, "jobs", filename)
            
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return self._dict_to_job(data)
            
        except Exception as e:
            logging.error(f"Erro ao carregar job de arquivo: {str(e)}")
            return None
            
    def _create_backup_metadata(self, job: BackupJob):
        """Cria metadados do backup"""
        try:
            metadata = BackupMetadata(
                backup_id=f"backup_{job.job_id}",
                job_id=job.job_id,
                backup_type=job.backup_type.value,
                source_paths=job.source_paths,
                file_count=job.file_count,
                total_size=job.total_size,
                checksum=job.checksum,
                created_at=job.completed_at or datetime.utcnow(),
                encryption_key_hash=hashlib.sha256(job.encryption_key).hexdigest(),
                compression_ratio=0.0,  # Calculado posteriormente se necessário
                verification_status=job.status == BackupStatus.VERIFIED
            )
            
            filename = f"{job.job_id}.json"
            filepath = os.path.join(self.storage_path, "metadata", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._metadata_to_dict(metadata), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao criar metadados: {str(e)}")
            
    def _job_to_dict(self, job: BackupJob) -> Dict:
        """Converte job para dicionário"""
        return {
            "job_id": job.job_id,
            "backup_type": job.backup_type.value,
            "source_paths": job.source_paths,
            "destination_path": job.destination_path,
            "encryption_key": base64.b64encode(job.encryption_key).decode(),
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "file_count": job.file_count,
            "total_size": job.total_size,
            "checksum": job.checksum,
            "error_message": job.error_message,
            "retention_days": job.retention_days
        }
        
    def _dict_to_job(self, data: Dict) -> BackupJob:
        """Converte dicionário para job"""
        return BackupJob(
            job_id=data["job_id"],
            backup_type=BackupType(data["backup_type"]),
            source_paths=data["source_paths"],
            destination_path=data["destination_path"],
            encryption_key=base64.b64decode(data["encryption_key"]),
            status=BackupStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            file_count=data.get("file_count", 0),
            total_size=data.get("total_size", 0),
            checksum=data.get("checksum"),
            error_message=data.get("error_message"),
            retention_days=data.get("retention_days", 30)
        )
        
    def _metadata_to_dict(self, metadata: BackupMetadata) -> Dict:
        """Converte metadados para dicionário"""
        return {
            "backup_id": metadata.backup_id,
            "job_id": metadata.job_id,
            "backup_type": metadata.backup_type,
            "source_paths": metadata.source_paths,
            "file_count": metadata.file_count,
            "total_size": metadata.total_size,
            "checksum": metadata.checksum,
            "created_at": metadata.created_at.isoformat(),
            "encryption_key_hash": metadata.encryption_key_hash,
            "compression_ratio": metadata.compression_ratio,
            "verification_status": metadata.verification_status
        }
        
    def stop_scheduler(self):
        """Para o agendador"""
        self.scheduler_active = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join(timeout=5) 