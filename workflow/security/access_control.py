"""
Módulo de Controle de Acesso - TarefaMágica
Implementa controle de acesso baseado em roles e permissões
"""

import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    CHILD = "child"
    PARENT = "parent"
    ADMIN = "admin"
    MODERATOR = "moderator"

class Permission(Enum):
    # Permissões de dados
    READ_OWN_DATA = "read_own_data"
    WRITE_OWN_DATA = "write_own_data"
    READ_CHILD_DATA = "read_child_data"
    WRITE_CHILD_DATA = "write_child_data"
    
    # Permissões financeiras
    CREATE_TRANSACTION = "create_transaction"
    APPROVE_TRANSACTION = "approve_transaction"
    VIEW_TRANSACTION_HISTORY = "view_transaction_history"
    
    # Permissões de consentimento
    MANAGE_CONSENT = "manage_consent"
    VIEW_CONSENT_HISTORY = "view_consent_history"
    
    # Permissões administrativas
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    MANAGE_SYSTEM = "manage_system"

@dataclass
class User:
    user_id: str
    role: UserRole
    parent_id: Optional[str] = None
    child_id: Optional[str] = None
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    permissions: Set[Permission] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.permissions is None:
            self.permissions = set()

@dataclass
class AccessLog:
    log_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Optional[str] = None

class AccessControl:
    def __init__(self, storage_path: str = "data/access"):
        """
        Inicializa o sistema de controle de acesso
        
        Args:
            storage_path: Caminho para armazenamento dos dados de acesso
        """
        self.storage_path = storage_path
        self._setup_storage()
        self._setup_logging()
        self._load_role_permissions()
        
    def _setup_storage(self):
        """Configura diretório de armazenamento"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "users"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "logs"), exist_ok=True)
        
    def _setup_logging(self):
        """Configura logging para auditoria de acesso"""
        log_path = os.path.join(self.storage_path, "logs", "access_audit.log")
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_role_permissions(self):
        """Carrega permissões padrão para cada role"""
        self.role_permissions = {
            UserRole.CHILD: {
                Permission.READ_OWN_DATA,
                Permission.WRITE_OWN_DATA
            },
            UserRole.PARENT: {
                Permission.READ_OWN_DATA,
                Permission.WRITE_OWN_DATA,
                Permission.READ_CHILD_DATA,
                Permission.WRITE_CHILD_DATA,
                Permission.CREATE_TRANSACTION,
                Permission.APPROVE_TRANSACTION,
                Permission.VIEW_TRANSACTION_HISTORY,
                Permission.MANAGE_CONSENT,
                Permission.VIEW_CONSENT_HISTORY
            },
            UserRole.MODERATOR: {
                Permission.READ_OWN_DATA,
                Permission.WRITE_OWN_DATA,
                Permission.VIEW_LOGS,
                Permission.MANAGE_USERS
            },
            UserRole.ADMIN: {
                Permission.READ_OWN_DATA,
                Permission.WRITE_OWN_DATA,
                Permission.READ_CHILD_DATA,
                Permission.WRITE_CHILD_DATA,
                Permission.CREATE_TRANSACTION,
                Permission.APPROVE_TRANSACTION,
                Permission.VIEW_TRANSACTION_HISTORY,
                Permission.MANAGE_CONSENT,
                Permission.VIEW_CONSENT_HISTORY,
                Permission.MANAGE_USERS,
                Permission.VIEW_LOGS,
                Permission.MANAGE_SYSTEM
            }
        }
        
    def create_user(
        self,
        user_id: str,
        role: UserRole,
        parent_id: Optional[str] = None,
        child_id: Optional[str] = None
    ) -> User:
        """
        Cria um novo usuário com permissões baseadas no role
        
        Args:
            user_id: ID único do usuário
            role: Role do usuário
            parent_id: ID do responsável (se aplicável)
            child_id: ID da criança (se aplicável)
            
        Returns:
            User: Usuário criado
        """
        try:
            # Verifica se usuário já existe
            if self._user_exists(user_id):
                raise ValueError(f"Usuário {user_id} já existe")
                
            # Cria usuário com permissões padrão do role
            permissions = self.role_permissions.get(role, set()).copy()
            
            user = User(
                user_id=user_id,
                role=role,
                parent_id=parent_id,
                child_id=child_id,
                permissions=permissions
            )
            
            # Salva usuário
            self._save_user(user)
            
            # Log da criação
            self._log_access(
                user_id=user_id,
                action="user_created",
                resource="user",
                success=True,
                details=f"Role: {role.value}"
            )
            
            logging.info(f"Usuário criado: {user_id} com role {role.value}")
            return user
            
        except Exception as e:
            logging.error(f"Erro ao criar usuário: {str(e)}")
            raise
            
    def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Verifica se usuário tem permissão para uma ação
        
        Args:
            user_id: ID do usuário
            permission: Permissão necessária
            resource_id: ID do recurso (para verificações específicas)
            
        Returns:
            bool: True se tem permissão
        """
        try:
            user = self._load_user(user_id)
            if not user or not user.is_active:
                return False
                
            # Verifica se tem a permissão básica
            if permission not in user.permissions:
                return False
                
            # Verificações específicas por permissão
            if permission == Permission.READ_CHILD_DATA:
                return self._can_access_child_data(user, resource_id)
            elif permission == Permission.WRITE_CHILD_DATA:
                return self._can_access_child_data(user, resource_id)
            elif permission == Permission.APPROVE_TRANSACTION:
                return self._can_approve_transaction(user, resource_id)
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao verificar permissão: {str(e)}")
            return False
            
    def _can_access_child_data(self, user: User, child_id: str) -> bool:
        """Verifica se usuário pode acessar dados da criança"""
        if user.role == UserRole.ADMIN:
            return True
            
        if user.role == UserRole.PARENT and user.child_id == child_id:
            return True
            
        return False
        
    def _can_approve_transaction(self, user: User, transaction_id: str) -> bool:
        """Verifica se usuário pode aprovar transação"""
        if user.role == UserRole.ADMIN:
            return True
            
        if user.role == UserRole.PARENT:
            # Aqui implementaríamos verificação se a transação pertence ao filho
            return True
            
        return False
        
    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Concede permissão adicional a um usuário
        
        Args:
            user_id: ID do usuário
            permission: Permissão a ser concedida
            
        Returns:
            bool: True se concedida com sucesso
        """
        try:
            user = self._load_user(user_id)
            if not user:
                return False
                
            user.permissions.add(permission)
            self._save_user(user)
            
            self._log_access(
                user_id=user_id,
                action="permission_granted",
                resource="permission",
                success=True,
                details=f"Permission: {permission.value}"
            )
            
            logging.info(f"Permissão concedida: {permission.value} para {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao conceder permissão: {str(e)}")
            return False
            
    def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Revoga permissão de um usuário
        
        Args:
            user_id: ID do usuário
            permission: Permissão a ser revogada
            
        Returns:
            bool: True se revogada com sucesso
        """
        try:
            user = self._load_user(user_id)
            if not user:
                return False
                
            user.permissions.discard(permission)
            self._save_user(user)
            
            self._log_access(
                user_id=user_id,
                action="permission_revoked",
                resource="permission",
                success=True,
                details=f"Permission: {permission.value}"
            )
            
            logging.info(f"Permissão revogada: {permission.value} de {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao revogar permissão: {str(e)}")
            return False
            
    def deactivate_user(self, user_id: str) -> bool:
        """
        Desativa um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se desativado com sucesso
        """
        try:
            user = self._load_user(user_id)
            if not user:
                return False
                
            user.is_active = False
            self._save_user(user)
            
            self._log_access(
                user_id=user_id,
                action="user_deactivated",
                resource="user",
                success=True
            )
            
            logging.info(f"Usuário desativado: {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao desativar usuário: {str(e)}")
            return False
            
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        Obtém todas as permissões de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Set[Permission]: Conjunto de permissões
        """
        try:
            user = self._load_user(user_id)
            if not user:
                return set()
                
            return user.permissions.copy()
            
        except Exception as e:
            logging.error(f"Erro ao obter permissões: {str(e)}")
            return set()
            
    def get_access_logs(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> List[AccessLog]:
        """
        Obtém logs de acesso
        
        Args:
            user_id: ID do usuário (opcional)
            days: Número de dias para buscar
            
        Returns:
            List[AccessLog]: Lista de logs
        """
        try:
            logs = []
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Busca logs no período
            for filename in os.listdir(os.path.join(self.storage_path, "logs")):
                if filename.endswith(".json"):
                    log = self._load_log_from_file(filename)
                    if log and log.timestamp >= cutoff_date:
                        if user_id is None or log.user_id == user_id:
                            logs.append(log)
                            
            # Ordena por timestamp
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            return logs
            
        except Exception as e:
            logging.error(f"Erro ao obter logs: {str(e)}")
            return []
            
    def _save_user(self, user: User):
        """Salva usuário em arquivo"""
        filename = f"{user.user_id}.json"
        filepath = os.path.join(self.storage_path, "users", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._user_to_dict(user), f, indent=2, default=str)
            
    def _load_user(self, user_id: str) -> Optional[User]:
        """Carrega usuário por ID"""
        filename = f"{user_id}.json"
        filepath = os.path.join(self.storage_path, "users", filename)
        
        try:
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return self._dict_to_user(data)
            
        except Exception as e:
            logging.error(f"Erro ao carregar usuário: {str(e)}")
            return None
            
    def _user_exists(self, user_id: str) -> bool:
        """Verifica se usuário existe"""
        filename = f"{user_id}.json"
        filepath = os.path.join(self.storage_path, "users", filename)
        return os.path.exists(filepath)
        
    def _user_to_dict(self, user: User) -> Dict:
        """Converte usuário para dicionário"""
        return {
            "user_id": user.user_id,
            "role": user.role.value,
            "parent_id": user.parent_id,
            "child_id": user.child_id,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
            "permissions": [p.value for p in user.permissions]
        }
        
    def _dict_to_user(self, data: Dict) -> User:
        """Converte dicionário para usuário"""
        return User(
            user_id=data["user_id"],
            role=UserRole(data["role"]),
            parent_id=data.get("parent_id"),
            child_id=data.get("child_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data["last_login"] else None,
            is_active=data["is_active"],
            permissions={Permission(p) for p in data["permissions"]}
        )
        
    def _log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool = True,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Registra log de acesso"""
        try:
            log_id = f"log_{int(time.time())}_{secrets.token_hex(4)}"
            
            log = AccessLog(
                log_id=log_id,
                user_id=user_id,
                action=action,
                resource=resource,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details
            )
            
            # Salva log
            filename = f"{log_id}.json"
            filepath = os.path.join(self.storage_path, "logs", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._log_to_dict(log), f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Erro ao registrar log: {str(e)}")
            
    def _load_log_from_file(self, filename: str) -> Optional[AccessLog]:
        """Carrega log de arquivo"""
        try:
            filepath = os.path.join(self.storage_path, "logs", filename)
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return self._dict_to_log(data)
            
        except Exception as e:
            logging.error(f"Erro ao carregar log: {str(e)}")
            return None
            
    def _log_to_dict(self, log: AccessLog) -> Dict:
        """Converte log para dicionário"""
        return {
            "log_id": log.log_id,
            "user_id": log.user_id,
            "action": log.action,
            "resource": log.resource,
            "timestamp": log.timestamp.isoformat(),
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "success": log.success,
            "details": log.details
        }
        
    def _dict_to_log(self, data: Dict) -> AccessLog:
        """Converte dicionário para log"""
        return AccessLog(
            log_id=data["log_id"],
            user_id=data["user_id"],
            action=data["action"],
            resource=data["resource"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            success=data["success"],
            details=data.get("details")
        ) 