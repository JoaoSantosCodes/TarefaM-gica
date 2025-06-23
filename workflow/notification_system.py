#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 Sistema de Notificações Inteligentes - TarefaMágica
Notificações personalizadas com agendamento e inteligência
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
import threading
from queue import Queue
import re

class NotificationType(Enum):
    TASK_REMINDER = "task_reminder"
    ACHIEVEMENT = "achievement"
    REWARD = "reward"
    MOTIVATION = "motivation"
    SYSTEM = "system"
    PARENT_ALERT = "parent_alert"
    FINANCIAL = "financial"
    PROGRESS = "progress"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    data: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    expires_at: Optional[datetime] = None

class NotificationSystem:
    def __init__(self, data_dir: str = "data/notifications"):
        """
        Inicializa sistema de notificações
        
        Args:
            data_dir: Diretório para armazenar notificações
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Fila de notificações para processamento
        self.notification_queue = Queue()
        
        # Thread para processamento de notificações agendadas
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        # Configurações de notificação por usuário
        self.user_preferences = {}
        
        logging.info("Sistema de notificações inicializado")
        
    def send_notification(self, user_id: str, notification_type: NotificationType,
                         title: str, message: str, priority: NotificationPriority = NotificationPriority.NORMAL,
                         scheduled_for: Optional[datetime] = None, data: Optional[Dict] = None,
                         actions: Optional[List[Dict]] = None, expires_at: Optional[datetime] = None) -> str:
        """
        Envia notificação
        
        Args:
            user_id: ID do usuário
            notification_type: Tipo de notificação
            title: Título da notificação
            message: Mensagem da notificação
            priority: Prioridade da notificação
            scheduled_for: Data/hora para envio (None = imediato)
            data: Dados adicionais
            actions: Ações disponíveis
            expires_at: Data de expiração
            
        Returns:
            str: ID da notificação
        """
        try:
            # Verifica preferências do usuário
            if not self._should_send_notification(user_id, notification_type):
                logging.info(f"Notificação bloqueada para usuário {user_id}, tipo {notification_type.value}")
                return None
                
            # Cria notificação
            notification_id = f"notif_{user_id}_{int(time.time())}_{notification_type.value}"
            
            notification = Notification(
                id=notification_id,
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                priority=priority,
                created_at=datetime.utcnow(),
                scheduled_for=scheduled_for,
                data=data,
                actions=actions,
                expires_at=expires_at
            )
            
            # Salva notificação
            self._save_notification(notification)
            
            # Processa notificação
            if scheduled_for:
                # Adiciona à fila de agendamento
                self.notification_queue.put(notification)
                logging.info(f"Notificação agendada: {notification_id} para {scheduled_for}")
            else:
                # Envia imediatamente
                self._send_immediate_notification(notification)
                
            return notification_id
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação: {str(e)}")
            return None
            
    def send_task_reminder(self, user_id: str, task_name: str, due_time: datetime,
                          task_id: str = None) -> str:
        """
        Envia lembrete de tarefa
        
        Args:
            user_id: ID do usuário
            task_name: Nome da tarefa
            due_time: Horário de vencimento
            task_id: ID da tarefa
            
        Returns:
            str: ID da notificação
        """
        title = "⏰ Lembrete de Tarefa"
        message = f"Você tem a tarefa '{task_name}' para fazer agora!"
        
        actions = [
            {"label": "Ver Tarefa", "action": "view_task", "data": {"task_id": task_id}},
            {"label": "Marcar como Feita", "action": "complete_task", "data": {"task_id": task_id}},
            {"label": "Adiar 15 min", "action": "snooze", "data": {"minutes": 15}}
        ]
        
        data = {
            "task_name": task_name,
            "task_id": task_id,
            "due_time": due_time.isoformat(),
            "reminder_type": "task_due"
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.TASK_REMINDER,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH,
            data=data,
            actions=actions,
            expires_at=due_time + timedelta(hours=1)
        )
        
    def send_achievement_notification(self, user_id: str, achievement_name: str,
                                    achievement_type: str, points_earned: int = 0) -> str:
        """
        Envia notificação de conquista
        
        Args:
            user_id: ID do usuário
            achievement_name: Nome da conquista
            achievement_type: Tipo da conquista
            points_earned: Pontos ganhos
            
        Returns:
            str: ID da notificação
        """
        title = "🏆 Nova Conquista!"
        message = f"Parabéns! Você conquistou '{achievement_name}'!"
        
        if points_earned > 0:
            message += f" +{points_earned} pontos"
            
        actions = [
            {"label": "Ver Conquistas", "action": "view_achievements"},
            {"label": "Compartilhar", "action": "share_achievement"}
        ]
        
        data = {
            "achievement_name": achievement_name,
            "achievement_type": achievement_type,
            "points_earned": points_earned
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.ACHIEVEMENT,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH,
            data=data,
            actions=actions
        )
        
    def send_reward_notification(self, user_id: str, reward_amount: float,
                               reward_type: str, task_name: str = None) -> str:
        """
        Envia notificação de recompensa
        
        Args:
            user_id: ID do usuário
            reward_amount: Valor da recompensa
            reward_type: Tipo da recompensa
            task_name: Nome da tarefa (se aplicável)
            
        Returns:
            str: ID da notificação
        """
        title = "💰 Recompensa Ganha!"
        
        if task_name:
            message = f"Você ganhou R$ {reward_amount:.2f} por completar '{task_name}'!"
        else:
            message = f"Você ganhou R$ {reward_amount:.2f}!"
            
        actions = [
            {"label": "Ver Saldo", "action": "view_balance"},
            {"label": "Ver Histórico", "action": "view_history"}
        ]
        
        data = {
            "reward_amount": reward_amount,
            "reward_type": reward_type,
            "task_name": task_name
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.REWARD,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH,
            data=data,
            actions=actions
        )
        
    def send_motivation_notification(self, user_id: str, motivation_type: str = "daily") -> str:
        """
        Envia notificação motivacional
        
        Args:
            user_id: ID do usuário
            motivation_type: Tipo de motivação
            
        Returns:
            str: ID da notificação
        """
        motivations = {
            "daily": {
                "title": "🌟 Bom dia!",
                "message": "Que tal começar o dia com uma tarefa? Você consegue! 💪"
            },
            "streak": {
                "title": "🔥 Sequência Incrível!",
                "message": "Você está mantendo uma sequência incrível! Continue assim!"
            },
            "goal": {
                "title": "🎯 Meta Próxima!",
                "message": "Você está muito perto de alcançar sua meta! Vamos lá!"
            },
            "encouragement": {
                "title": "💪 Você Pode!",
                "message": "Mesmo que seja difícil, você é capaz de completar essa tarefa!"
            }
        }
        
        motivation = motivations.get(motivation_type, motivations["daily"])
        
        actions = [
            {"label": "Ver Tarefas", "action": "view_tasks"},
            {"label": "Definir Meta", "action": "set_goal"}
        ]
        
        data = {
            "motivation_type": motivation_type,
            "sentiment": "positive"
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.MOTIVATION,
            title=motivation["title"],
            message=motivation["message"],
            priority=NotificationPriority.NORMAL,
            data=data,
            actions=actions
        )
        
    def send_parent_alert(self, user_id: str, alert_type: str, details: Dict) -> str:
        """
        Envia alerta para os pais
        
        Args:
            user_id: ID do usuário
            alert_type: Tipo de alerta
            details: Detalhes do alerta
            
        Returns:
            str: ID da notificação
        """
        alert_templates = {
            "large_transaction": {
                "title": "⚠️ Transação Importante",
                "message": f"Transação de R$ {details.get('amount', 0):.2f} realizada."
            },
            "inactive_period": {
                "title": "📱 Período Inativo",
                "message": "Seu filho não completou tarefas nos últimos 3 dias."
            },
            "achievement_milestone": {
                "title": "🎉 Marco Alcançado!",
                "message": f"Seu filho alcançou {details.get('milestone', '')}!"
            }
        }
        
        template = alert_templates.get(alert_type, {
            "title": "📋 Alerta",
            "message": "Novo alerta disponível."
        })
        
        actions = [
            {"label": "Ver Detalhes", "action": "view_details"},
            {"label": "Configurar", "action": "configure_alerts"}
        ]
        
        data = {
            "alert_type": alert_type,
            "details": details,
            "child_id": user_id
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PARENT_ALERT,
            title=template["title"],
            message=template["message"],
            priority=NotificationPriority.HIGH,
            data=data,
            actions=actions
        )
        
    def send_financial_notification(self, user_id: str, financial_type: str,
                                  amount: float = None, details: Dict = None) -> str:
        """
        Envia notificação financeira
        
        Args:
            user_id: ID do usuário
            financial_type: Tipo de notificação financeira
            amount: Valor (se aplicável)
            details: Detalhes adicionais
            
        Returns:
            str: ID da notificação
        """
        templates = {
            "savings_goal": {
                "title": "💰 Meta de Economia!",
                "message": f"Você economizou R$ {amount:.2f}! Meta alcançada!"
            },
            "spending_limit": {
                "title": "⚠️ Limite de Gastos",
                "message": "Você está próximo do limite de gastos do dia."
            },
            "investment_opportunity": {
                "title": "📈 Oportunidade de Investimento",
                "message": "Que tal investir parte do seu dinheiro?"
            }
        }
        
        template = templates.get(financial_type, {
            "title": "💳 Atividade Financeira",
            "message": "Nova atividade financeira registrada."
        })
        
        actions = [
            {"label": "Ver Saldo", "action": "view_balance"},
            {"label": "Ver Histórico", "action": "view_history"}
        ]
        
        data = {
            "financial_type": financial_type,
            "amount": amount,
            "details": details or {}
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.FINANCIAL,
            title=template["title"],
            message=template["message"],
            priority=NotificationPriority.NORMAL,
            data=data,
            actions=actions
        )
        
    def send_progress_notification(self, user_id: str, progress_type: str,
                                 current_value: int, target_value: int,
                                 metric_name: str) -> str:
        """
        Envia notificação de progresso
        
        Args:
            user_id: ID do usuário
            progress_type: Tipo de progresso
            current_value: Valor atual
            target_value: Valor alvo
            metric_name: Nome da métrica
            
        Returns:
            str: ID da notificação
        """
        percentage = (current_value / target_value) * 100 if target_value > 0 else 0
        
        if percentage >= 100:
            title = "🎯 Meta Alcançada!"
            message = f"Você alcançou 100% da meta de {metric_name}!"
        elif percentage >= 75:
            title = "📈 Quase Lá!"
            message = f"Você está a {target_value - current_value} de alcançar a meta de {metric_name}!"
        else:
            title = "📊 Progresso Atualizado"
            message = f"Seu progresso em {metric_name}: {current_value}/{target_value} ({percentage:.1f}%)"
            
        actions = [
            {"label": "Ver Progresso", "action": "view_progress"},
            {"label": "Definir Meta", "action": "set_goal"}
        ]
        
        data = {
            "progress_type": progress_type,
            "current_value": current_value,
            "target_value": target_value,
            "percentage": percentage,
            "metric_name": metric_name
        }
        
        return self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PROGRESS,
            title=title,
            message=message,
            priority=NotificationPriority.NORMAL,
            data=data,
            actions=actions
        )
        
    def get_user_notifications(self, user_id: str, limit: int = 50,
                             unread_only: bool = False) -> List[Dict]:
        """
        Obtém notificações do usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de notificações
            unread_only: Apenas não lidas
            
        Returns:
            List[Dict]: Lista de notificações
        """
        try:
            notifications = []
            
            # Lista arquivos de notificação do usuário
            for filename in os.listdir(self.data_dir):
                if filename.startswith(f"notif_{user_id}_") and filename.endswith('.json'):
                    notification_file = os.path.join(self.data_dir, filename)
                    try:
                        with open(notification_file, 'r', encoding='utf-8') as f:
                            notification_data = json.load(f)
                            
                            # Filtra por não lidas se solicitado
                            if unread_only and notification_data.get("read_at"):
                                continue
                                
                            # Verifica expiração
                            if notification_data.get("expires_at"):
                                expires_at = datetime.fromisoformat(notification_data["expires_at"])
                                if datetime.utcnow() > expires_at:
                                    continue
                                    
                            notifications.append(notification_data)
                            
                    except Exception as e:
                        logging.warning(f"Erro ao ler notificação {filename}: {str(e)}")
                        continue
                        
            # Ordena por data de criação (mais recente primeiro)
            notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return notifications[:limit]
            
        except Exception as e:
            logging.error(f"Erro ao obter notificações: {str(e)}")
            return []
            
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Marca notificação como lida
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            notification_file = os.path.join(self.data_dir, f"{notification_id}.json")
            
            if not os.path.exists(notification_file):
                return False
                
            with open(notification_file, 'r', encoding='utf-8') as f:
                notification_data = json.load(f)
                
            notification_data["read_at"] = datetime.utcnow().isoformat()
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao marcar notificação como lida: {str(e)}")
            return False
            
    def delete_notification(self, notification_id: str) -> bool:
        """
        Remove notificação
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            notification_file = os.path.join(self.data_dir, f"{notification_id}.json")
            
            if os.path.exists(notification_file):
                os.remove(notification_file)
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Erro ao remover notificação: {str(e)}")
            return False
            
    def set_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Define preferências de notificação do usuário
        
        Args:
            user_id: ID do usuário
            preferences: Preferências
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            self.user_preferences[user_id] = preferences
            
            # Salva preferências
            prefs_file = os.path.join(self.data_dir, f"prefs_{user_id}.json")
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao definir preferências: {str(e)}")
            return False
            
    def get_user_preferences(self, user_id: str) -> Dict:
        """
        Obtém preferências do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict: Preferências
        """
        try:
            if user_id in self.user_preferences:
                return self.user_preferences[user_id]
                
            # Carrega do arquivo
            prefs_file = os.path.join(self.data_dir, f"prefs_{user_id}.json")
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    self.user_preferences[user_id] = preferences
                    return preferences
                    
            # Preferências padrão
            default_prefs = {
                "task_reminders": True,
                "achievements": True,
                "rewards": True,
                "motivation": True,
                "parent_alerts": True,
                "financial": True,
                "progress": True,
                "quiet_hours": {
                    "start": "22:00",
                    "end": "08:00"
                },
                "max_daily": 10
            }
            
            return default_prefs
            
        except Exception as e:
            logging.error(f"Erro ao obter preferências: {str(e)}")
            return {}
            
    def _should_send_notification(self, user_id: str, notification_type: NotificationType) -> bool:
        """
        Verifica se deve enviar notificação
        
        Args:
            user_id: ID do usuário
            notification_type: Tipo de notificação
            
        Returns:
            bool: Deve enviar
        """
        try:
            preferences = self.get_user_preferences(user_id)
            
            # Verifica se o tipo está habilitado
            type_key = notification_type.value
            if not preferences.get(type_key, True):
                return False
                
            # Verifica horário silencioso
            current_time = datetime.now().time()
            quiet_hours = preferences.get("quiet_hours", {})
            
            if quiet_hours:
                start_time = datetime.strptime(quiet_hours["start"], "%H:%M").time()
                end_time = datetime.strptime(quiet_hours["end"], "%H:%M").time()
                
                if start_time <= current_time <= end_time:
                    return False
                    
            # Verifica limite diário
            daily_count = self._get_daily_notification_count(user_id)
            max_daily = preferences.get("max_daily", 10)
            
            if daily_count >= max_daily:
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Erro ao verificar preferências: {str(e)}")
            return True
            
    def _get_daily_notification_count(self, user_id: str) -> int:
        """
        Obtém contagem de notificações do dia
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Contagem
        """
        try:
            today = datetime.now().date()
            count = 0
            
            for filename in os.listdir(self.data_dir):
                if filename.startswith(f"notif_{user_id}_") and filename.endswith('.json'):
                    notification_file = os.path.join(self.data_dir, filename)
                    try:
                        with open(notification_file, 'r', encoding='utf-8') as f:
                            notification_data = json.load(f)
                            created_at = datetime.fromisoformat(notification_data["created_at"])
                            if created_at.date() == today:
                                count += 1
                    except:
                        continue
                        
            return count
            
        except Exception as e:
            logging.error(f"Erro ao contar notificações: {str(e)}")
            return 0
            
    def _send_immediate_notification(self, notification: Notification):
        """
        Envia notificação imediata
        
        Args:
            notification: Notificação
        """
        try:
            # Marca como enviada
            notification.sent_at = datetime.utcnow()
            self._save_notification(notification)
            
            # Aqui você implementaria o envio real (push, email, etc.)
            logging.info(f"Notificação enviada: {notification.id} - {notification.title}")
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação: {str(e)}")
            
    def _scheduler_worker(self):
        """
        Worker para processar notificações agendadas
        """
        while True:
            try:
                # Processa notificações na fila
                while not self.notification_queue.empty():
                    notification = self.notification_queue.get()
                    
                    if notification.scheduled_for and datetime.utcnow() >= notification.scheduled_for:
                        self._send_immediate_notification(notification)
                    else:
                        # Recoloca na fila se ainda não é hora
                        self.notification_queue.put(notification)
                        
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                logging.error(f"Erro no scheduler: {str(e)}")
                time.sleep(60)
                
    def _save_notification(self, notification: Notification):
        """
        Salva notificação
        
        Args:
            notification: Notificação
        """
        try:
            notification_file = os.path.join(self.data_dir, f"{notification.id}.json")
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(notification), f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logging.error(f"Erro ao salvar notificação: {str(e)}")

# Instância global
notification_system = NotificationSystem() 