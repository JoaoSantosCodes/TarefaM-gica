"""
Validação de Integridade de Dados - TarefaMágica (P3-3)
Verifica integridade de dados e detecta corrupção
"""

import hashlib
import hmac
import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import base64
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class IntegrityAlgorithm(Enum):
    """Algoritmos de hash suportados (apenas seguros)"""
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"

class IntegrityLevel(Enum):
    """Níveis de integridade"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class IntegrityCheck:
    """Check de integridade"""
    check_id: str
    data_type: str
    data_id: str
    algorithm: IntegrityAlgorithm
    level: IntegrityLevel
    original_hash: str
    created_at: datetime
    last_verified: Optional[datetime] = None
    verification_count: int = 0
    failed_attempts: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class IntegrityResult:
    """Resultado da verificação de integridade"""
    is_valid: bool
    check_id: str
    data_id: str
    algorithm: IntegrityAlgorithm
    original_hash: str
    current_hash: str
    verification_time: datetime
    duration_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class DataIntegrityValidator:
    """Validador de integridade de dados"""
    
    def __init__(self, storage_path: str = "data/integrity", secret_key: Optional[str] = None):
        """
        Inicializa o validador
        
        Args:
            storage_path: Caminho para armazenamento
            secret_key: Chave secreta para HMAC (opcional)
        """
        self.storage_path = storage_path
        self.checks_file = os.path.join(storage_path, "integrity_checks.json")
        self.secret_key = secret_key or os.urandom(32)
        self.checks: Dict[str, IntegrityCheck] = {}
        self.verification_thread = None
        self.running = False
        
        # Configurações por nível
        self.level_configs = {
            IntegrityLevel.BASIC: {
                'algorithm': IntegrityAlgorithm.SHA256,
                'verify_interval': timedelta(hours=24),
                'max_failures': 3
            },
            IntegrityLevel.STANDARD: {
                'algorithm': IntegrityAlgorithm.SHA256,
                'verify_interval': timedelta(hours=12),
                'max_failures': 2
            },
            IntegrityLevel.HIGH: {
                'algorithm': IntegrityAlgorithm.SHA512,
                'verify_interval': timedelta(hours=6),
                'max_failures': 1
            },
            IntegrityLevel.CRITICAL: {
                'algorithm': IntegrityAlgorithm.SHA512,
                'verify_interval': timedelta(hours=1),
                'max_failures': 1
            }
        }
        
        # Configuração de logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Setup inicial
        self._setup_storage()
        self._load_checks()
        self._start_verification_thread()
        
        self.logger.info("DataIntegrityValidator inicializado")

    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _load_checks(self):
        """Carrega checks salvos"""
        try:
            if os.path.exists(self.checks_file):
                with open(self.checks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for check_data in data:
                    # Converte strings de volta para enums
                    check_data['algorithm'] = IntegrityAlgorithm(check_data['algorithm'])
                    check_data['level'] = IntegrityLevel(check_data['level'])
                    check_data['created_at'] = datetime.fromisoformat(check_data['created_at'])
                    
                    if check_data.get('last_verified'):
                        check_data['last_verified'] = datetime.fromisoformat(check_data['last_verified'])
                    
                    check = IntegrityCheck(**check_data)
                    self.checks[check.check_id] = check
                    
                self.logger.info(f"Carregados {len(self.checks)} checks de integridade")
        except Exception as e:
            self.logger.error(f"Erro ao carregar checks: {e}")

    def _save_checks(self):
        """Salva checks em arquivo"""
        try:
            data = []
            for check in self.checks.values():
                check_dict = asdict(check)
                # Converte enums para strings
                check_dict['algorithm'] = check.algorithm.value
                check_dict['level'] = check.level.value
                check_dict['created_at'] = check.created_at.isoformat()
                
                if check.last_verified:
                    check_dict['last_verified'] = check.last_verified.isoformat()
                    
                data.append(check_dict)
                
            with open(self.checks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar checks: {e}")

    def _start_verification_thread(self):
        """Inicia thread de verificação automática"""
        self.running = True
        self.verification_thread = threading.Thread(target=self._verification_loop, daemon=True)
        self.verification_thread.start()

    def _verification_loop(self):
        """Loop de verificação automática"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for check in list(self.checks.values()):
                    if self._should_verify_check(check, current_time):
                        self._verify_check_async(check)
                        
                time.sleep(60)  # Verifica a cada minuto
                
            except Exception as e:
                self.logger.error(f"Erro no loop de verificação: {e}")
                time.sleep(60)

    def _should_verify_check(self, check: IntegrityCheck, current_time: datetime) -> bool:
        """Verifica se deve fazer verificação automática"""
        if not check.last_verified:
            return True
            
        interval = self.level_configs[check.level]['verify_interval']
        return current_time - check.last_verified >= interval

    def _verify_check_async(self, check: IntegrityCheck):
        """Verifica check de forma assíncrona"""
        try:
            # Aqui você implementaria a lógica para obter os dados atuais
            # Por enquanto, apenas atualiza o timestamp
            check.last_verified = datetime.utcnow()
            check.verification_count += 1
            self._save_checks()
            
        except Exception as e:
            self.logger.error(f"Erro na verificação assíncrona: {e}")
            check.failed_attempts += 1

    def _calculate_hash(self, data: Union[str, bytes, Dict, List], algorithm: IntegrityAlgorithm) -> str:
        """
        Calcula hash dos dados
        
        Args:
            data: Dados a serem processados
            algorithm: Algoritmo de hash
            
        Returns:
            str: Hash calculado
        """
        try:
            # Converte dados para bytes
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, (dict, list)):
                data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, bytes):
                data_bytes = data
            else:
                # Usar JSON em vez de pickle por segurança
                data_bytes = json.dumps(str(data), sort_keys=True, ensure_ascii=False).encode('utf-8')
                
            # Calcula hash baseado no algoritmo (apenas algoritmos seguros)
            if algorithm == IntegrityAlgorithm.SHA256:
                hash_obj = hashlib.sha256()
            elif algorithm == IntegrityAlgorithm.SHA512:
                hash_obj = hashlib.sha512()
            elif algorithm == IntegrityAlgorithm.BLAKE2B:
                hash_obj = hashlib.blake2b()
            elif algorithm == IntegrityAlgorithm.BLAKE2S:
                hash_obj = hashlib.blake2s()
            else:
                # Fallback para SHA256 se algoritmo não suportado
                hash_obj = hashlib.sha256()
                
            hash_obj.update(data_bytes)
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular hash: {str(e)}")
            raise
            
    def _calculate_hmac(self, data: Union[str, bytes, Dict, List], algorithm: IntegrityAlgorithm) -> str:
        """
        Calcula HMAC dos dados
        
        Args:
            data: Dados a serem processados
            algorithm: Algoritmo de hash para HMAC
            
        Returns:
            str: HMAC calculado
        """
        try:
            # Converte dados para bytes
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, (dict, list)):
                data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, bytes):
                data_bytes = data
            else:
                # Usar JSON em vez de pickle por segurança
                data_bytes = json.dumps(str(data), sort_keys=True, ensure_ascii=False).encode('utf-8')
                
            # Calcula HMAC (apenas algoritmos seguros)
            if algorithm == IntegrityAlgorithm.SHA256:
                hmac_obj = hmac.new(self.secret_key, data_bytes, hashlib.sha256)
            elif algorithm == IntegrityAlgorithm.SHA512:
                hmac_obj = hmac.new(self.secret_key, data_bytes, hashlib.sha512)
            else:
                # Fallback para SHA256
                hmac_obj = hmac.new(self.secret_key, data_bytes, hashlib.sha256)
                
            return hmac_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular HMAC: {str(e)}")
            raise

    def create_integrity_check(
        self,
        data_id: str,
        data_type: str,
        data: Union[str, bytes, Dict, List],
        level: IntegrityLevel = IntegrityLevel.STANDARD,
        algorithm: Optional[IntegrityAlgorithm] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IntegrityCheck:
        """
        Cria um novo check de integridade
        
        Args:
            data_id: ID único dos dados
            data_type: Tipo dos dados
            data: Dados a serem verificados
            level: Nível de integridade
            algorithm: Algoritmo de hash (opcional)
            metadata: Metadados adicionais
            
        Returns:
            IntegrityCheck: Check criado
        """
        try:
            # Gera ID único do check
            check_id = f"{data_type}_{data_id}_{int(time.time())}"
            
            # Determina algoritmo baseado no nível
            if algorithm is None:
                algorithm = self.level_configs[level]['algorithm']
                
            # Calcula hash original
            original_hash = self._calculate_hash(data, algorithm)
            
            # Se nível crítico, usa HMAC
            if level == IntegrityLevel.CRITICAL:
                original_hash = self._calculate_hmac(data, algorithm)
                
            # Cria check
            check = IntegrityCheck(
                check_id=check_id,
                data_type=data_type,
                data_id=data_id,
                algorithm=algorithm,
                level=level,
                original_hash=original_hash,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Salva check
            self.checks[check_id] = check
            self._save_checks()
            
            self.logger.info(f"Check de integridade criado: {check_id} (dados: {data_id})")
            return check
            
        except Exception as e:
            self.logger.error(f"Erro ao criar check de integridade: {str(e)}")
            raise
            
    def verify_data_integrity(
        self,
        data_id: str,
        data_type: str,
        data: Union[str, bytes, Dict, List],
        check_id: Optional[str] = None
    ) -> IntegrityResult:
        """
        Verifica integridade dos dados
        
        Args:
            data_id: ID dos dados
            data_type: Tipo dos dados
            data: Dados a serem verificados
            check_id: ID do check específico (opcional)
            
        Returns:
            IntegrityResult: Resultado da verificação
        """
        try:
            start_time = time.time()
            
            # Encontra check
            if check_id:
                check = self.checks.get(check_id)
            else:
                # Procura por data_id e data_type
                check = None
                for c in self.checks.values():
                    if c.data_id == data_id and c.data_type == data_type:
                        check = c
                        break
                        
            if not check:
                return IntegrityResult(
                    is_valid=False,
                    check_id="",
                    data_id=data_id,
                    algorithm=IntegrityAlgorithm.SHA256,
                    original_hash="",
                    current_hash="",
                    verification_time=datetime.utcnow(),
                    duration_ms=(time.time() - start_time) * 1000,
                    error_message="Check de integridade não encontrado"
                )
                
            # Calcula hash atual
            if check.level == IntegrityLevel.CRITICAL:
                current_hash = self._calculate_hmac(data, check.algorithm)
            else:
                current_hash = self._calculate_hash(data, check.algorithm)
                
            # Verifica integridade
            is_valid = current_hash == check.original_hash
            
            duration_ms = (time.time() - start_time) * 1000
            
            result = IntegrityResult(
                is_valid=is_valid,
                check_id=check.check_id,
                data_id=data_id,
                algorithm=check.algorithm,
                original_hash=check.original_hash,
                current_hash=current_hash,
                verification_time=datetime.utcnow(),
                duration_ms=duration_ms,
                details={
                    'data_type': data_type,
                    'level': check.level.value,
                    'verification_count': check.verification_count + 1
                }
            )
            
            # Atualiza estatísticas do check
            check.verification_count += 1
            check.last_verified = datetime.utcnow()
            
            if not is_valid:
                check.failed_attempts += 1
                result.error_message = "Hash não corresponde ao original"
            else:
                check.failed_attempts = 0
                
            self._save_checks()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar integridade: {str(e)}")
            return IntegrityResult(
                is_valid=False,
                check_id=check_id or "",
                data_id=data_id,
                algorithm=IntegrityAlgorithm.SHA256,
                original_hash="",
                current_hash="",
                verification_time=datetime.utcnow(),
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
            
    def verify_file_integrity(self, file_path: str, check_id: Optional[str] = None) -> IntegrityResult:
        """
        Verifica integridade de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            check_id: ID do check específico (opcional)
            
        Returns:
            IntegrityResult: Resultado da verificação
        """
        try:
            if not os.path.exists(file_path):
                return IntegrityResult(
                    is_valid=False,
                    check_id=check_id or "",
                    data_id=file_path,
                    algorithm=IntegrityAlgorithm.SHA256,
                    original_hash="",
                    current_hash="",
                    verification_time=datetime.utcnow(),
                    duration_ms=0,
                    error_message="Arquivo não encontrado"
                )
                
            # Lê arquivo
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # Verifica integridade
            return self.verify_data_integrity(
                data_id=file_path,
                data_type="file",
                data=file_data,
                check_id=check_id
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar arquivo: {str(e)}")
            return IntegrityResult(
                is_valid=False,
                check_id=check_id or "",
                data_id=file_path,
                algorithm=IntegrityAlgorithm.SHA256,
                original_hash="",
                current_hash="",
                verification_time=datetime.utcnow(),
                duration_ms=0,
                error_message=str(e)
            )
            
    def get_check(self, check_id: str) -> Optional[IntegrityCheck]:
        """
        Obtém um check de integridade
        
        Args:
            check_id: ID do check
            
        Returns:
            Optional[IntegrityCheck]: Check ou None
        """
        return self.checks.get(check_id)
        
    def get_checks_by_data_id(self, data_id: str) -> List[IntegrityCheck]:
        """
        Obtém checks por ID dos dados
        
        Args:
            data_id: ID dos dados
            
        Returns:
            List[IntegrityCheck]: Lista de checks
        """
        return [check for check in self.checks.values() if check.data_id == data_id]
        
    def get_checks_by_type(self, data_type: str) -> List[IntegrityCheck]:
        """
        Obtém checks por tipo de dados
        
        Args:
            data_type: Tipo de dados
            
        Returns:
            List[IntegrityCheck]: Lista de checks
        """
        return [check for check in self.checks.values() if check.data_type == data_type]
        
    def remove_check(self, check_id: str) -> bool:
        """
        Remove um check de integridade
        
        Args:
            check_id: ID do check
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            if check_id in self.checks:
                check = self.checks.pop(check_id)
                self._save_checks()
                self.logger.info(f"Check removido: {check_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao remover check: {str(e)}")
            return False
            
    def get_statistics(self) -> Dict:
        """
        Obtém estatísticas do sistema
        
        Returns:
            Dict: Estatísticas
        """
        try:
            total_checks = len(self.checks)
            valid_checks = len([c for c in self.checks.values() if c.failed_attempts == 0])
            failed_checks = total_checks - valid_checks
            
            # Estatísticas por nível
            level_stats = {}
            for level in IntegrityLevel:
                level_checks = [c for c in self.checks.values() if c.level == level]
                level_stats[level.value] = {
                    'total': len(level_checks),
                    'valid': len([c for c in level_checks if c.failed_attempts == 0]),
                    'failed': len([c for c in level_checks if c.failed_attempts > 0])
                }
                
            # Estatísticas por algoritmo
            algorithm_stats = {}
            for algorithm in IntegrityAlgorithm:
                algo_checks = [c for c in self.checks.values() if c.algorithm == algorithm]
                algorithm_stats[algorithm.value] = len(algo_checks)
                
            return {
                'total_checks': total_checks,
                'valid_checks': valid_checks,
                'failed_checks': failed_checks,
                'success_rate': (valid_checks / total_checks * 100) if total_checks > 0 else 0,
                'by_level': level_stats,
                'by_algorithm': algorithm_stats,
                'total_verifications': sum(c.verification_count for c in self.checks.values())
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
            
    def generate_integrity_report(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        Gera relatório de integridade
        
        Args:
            start_date: Data de início (opcional)
            end_date: Data de fim (opcional)
            
        Returns:
            Dict: Relatório
        """
        try:
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=7)
            if end_date is None:
                end_date = datetime.utcnow()
                
            # Filtra checks por período
            period_checks = [
                check for check in self.checks.values()
                if start_date <= check.created_at <= end_date
            ]
            
            # Análise de falhas
            failed_checks = [c for c in period_checks if c.failed_attempts > 0]
            
            # Análise por tipo de dados
            type_analysis = {}
            for check in period_checks:
                if check.data_type not in type_analysis:
                    type_analysis[check.data_type] = {
                        'total': 0,
                        'failed': 0,
                        'verifications': 0
                    }
                type_analysis[check.data_type]['total'] += 1
                type_analysis[check.data_type]['verifications'] += check.verification_count
                if check.failed_attempts > 0:
                    type_analysis[check.data_type]['failed'] += 1
                    
            return {
                'report_type': 'integrity_report',
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_checks': len(period_checks),
                    'failed_checks': len(failed_checks),
                    'success_rate': ((len(period_checks) - len(failed_checks)) / len(period_checks) * 100) if period_checks else 0
                },
                'failed_checks_details': [
                    {
                        'check_id': check.check_id,
                        'data_id': check.data_id,
                        'data_type': check.data_type,
                        'failed_attempts': check.failed_attempts,
                        'last_verified': check.last_verified.isoformat() if check.last_verified else None
                    }
                    for check in failed_checks
                ],
                'type_analysis': type_analysis,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {str(e)}")
            return {}
            
    def cleanup_old_checks(self, days: int = 30) -> int:
        """
        Remove checks antigos
        
        Args:
            days: Número de dias para manter
            
        Returns:
            int: Número de checks removidos
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            old_checks = [
                check_id for check_id, check in self.checks.items()
                if check.created_at < cutoff_date
            ]
            
            for check_id in old_checks:
                self.checks.pop(check_id)
                
            self._save_checks()
            self.logger.info(f"Checks antigos removidos: {len(old_checks)}")
            return len(old_checks)
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar checks antigos: {str(e)}")
            return 0
            
    def stop(self):
        """Para o validador"""
        self.running = False
        if self.verification_thread:
            self.verification_thread.join(timeout=5)

    def generate_hash(self, data: str, algorithm: IntegrityAlgorithm = IntegrityAlgorithm.SHA256) -> str:
        """Gera hash dos dados"""
        try:
            if algorithm == IntegrityAlgorithm.SHA256:
                hash_obj = hashlib.sha256()
            elif algorithm == IntegrityAlgorithm.SHA512:
                hash_obj = hashlib.sha512()
            elif algorithm == IntegrityAlgorithm.BLAKE2B:
                hash_obj = hashlib.blake2b()
            else:
                # Fallback para SHA256 se algoritmo não suportado
                hash_obj = hashlib.sha256()
            
            hash_obj.update(data.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao gerar hash: {e}")
            return ""

# Instância global do validador de integridade
integrity_validator = DataIntegrityValidator() 