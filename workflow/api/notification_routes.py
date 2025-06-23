#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 Rotas da API - Sistema de Notificações
Endpoints para gerenciamento de notificações
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from workflow.notification_system import notification_system, NotificationType, NotificationPriority

# Blueprint para notificações
notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/notifications/send', methods=['POST'])
def send_notification():
    """
    Envia notificação personalizada
    
    Body:
        user_id: ID do usuário
        type: Tipo de notificação
        title: Título da notificação
        message: Mensagem da notificação
        priority: Prioridade (low, normal, high, urgent)
        scheduled_for: Data/hora para envio (opcional)
        data: Dados adicionais (opcional)
        actions: Ações disponíveis (opcional)
        expires_at: Data de expiração (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        notification_type_str = data.get('type')
        title = data.get('title')
        message = data.get('message')
        priority_str = data.get('priority', 'normal')
        
        if not all([user_id, notification_type_str, title, message]):
            return jsonify({"error": "Campos obrigatórios: user_id, type, title, message"}), 400
            
        # Valida tipo de notificação
        try:
            notification_type = NotificationType(notification_type_str)
        except ValueError:
            return jsonify({"error": "Tipo de notificação inválido"}), 400
            
        # Valida prioridade
        try:
            priority = NotificationPriority(priority_str)
        except ValueError:
            return jsonify({"error": "Prioridade inválida"}), 400
            
        # Processa data agendada
        scheduled_for = None
        if data.get('scheduled_for'):
            try:
                scheduled_for = datetime.fromisoformat(data['scheduled_for'])
            except ValueError:
                return jsonify({"error": "Formato de data inválido para scheduled_for"}), 400
                
        # Processa data de expiração
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'])
            except ValueError:
                return jsonify({"error": "Formato de data inválido para expires_at"}), 400
                
        # Envia notificação
        notification_id = notification_system.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            scheduled_for=scheduled_for,
            data=data.get('data'),
            actions=data.get('actions'),
            expires_at=expires_at
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação enviada com sucesso"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/task-reminder', methods=['POST'])
def send_task_reminder():
    """
    Envia lembrete de tarefa
    
    Body:
        user_id: ID do usuário
        task_name: Nome da tarefa
        due_time: Horário de vencimento (ISO format)
        task_id: ID da tarefa (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        task_name = data.get('task_name')
        due_time_str = data.get('due_time')
        task_id = data.get('task_id')
        
        if not all([user_id, task_name, due_time_str]):
            return jsonify({"error": "Campos obrigatórios: user_id, task_name, due_time"}), 400
            
        # Processa horário de vencimento
        try:
            due_time = datetime.fromisoformat(due_time_str)
        except ValueError:
            return jsonify({"error": "Formato de data inválido para due_time"}), 400
            
        # Envia lembrete
        notification_id = notification_system.send_task_reminder(
            user_id=user_id,
            task_name=task_name,
            due_time=due_time,
            task_id=task_id
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar lembrete"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Lembrete de tarefa enviado"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar lembrete: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/achievement', methods=['POST'])
def send_achievement_notification():
    """
    Envia notificação de conquista
    
    Body:
        user_id: ID do usuário
        achievement_name: Nome da conquista
        achievement_type: Tipo da conquista
        points_earned: Pontos ganhos (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        achievement_name = data.get('achievement_name')
        achievement_type = data.get('achievement_type')
        points_earned = data.get('points_earned', 0)
        
        if not all([user_id, achievement_name, achievement_type]):
            return jsonify({"error": "Campos obrigatórios: user_id, achievement_name, achievement_type"}), 400
            
        # Envia notificação de conquista
        notification_id = notification_system.send_achievement_notification(
            user_id=user_id,
            achievement_name=achievement_name,
            achievement_type=achievement_type,
            points_earned=points_earned
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação de conquista"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação de conquista enviada"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação de conquista: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/reward', methods=['POST'])
def send_reward_notification():
    """
    Envia notificação de recompensa
    
    Body:
        user_id: ID do usuário
        reward_amount: Valor da recompensa
        reward_type: Tipo da recompensa
        task_name: Nome da tarefa (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        reward_amount = data.get('reward_amount')
        reward_type = data.get('reward_type')
        task_name = data.get('task_name')
        
        if not all([user_id, reward_amount, reward_type]):
            return jsonify({"error": "Campos obrigatórios: user_id, reward_amount, reward_type"}), 400
            
        # Envia notificação de recompensa
        notification_id = notification_system.send_reward_notification(
            user_id=user_id,
            reward_amount=reward_amount,
            reward_type=reward_type,
            task_name=task_name
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação de recompensa"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação de recompensa enviada"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação de recompensa: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/motivation', methods=['POST'])
def send_motivation_notification():
    """
    Envia notificação motivacional
    
    Body:
        user_id: ID do usuário
        motivation_type: Tipo de motivação (daily, streak, goal, encouragement)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        motivation_type = data.get('motivation_type', 'daily')
        
        if not user_id:
            return jsonify({"error": "user_id é obrigatório"}), 400
            
        # Envia notificação motivacional
        notification_id = notification_system.send_motivation_notification(
            user_id=user_id,
            motivation_type=motivation_type
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação motivacional"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação motivacional enviada"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação motivacional: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/parent-alert', methods=['POST'])
def send_parent_alert():
    """
    Envia alerta para os pais
    
    Body:
        user_id: ID do usuário
        alert_type: Tipo de alerta
        details: Detalhes do alerta
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        alert_type = data.get('alert_type')
        details = data.get('details', {})
        
        if not all([user_id, alert_type]):
            return jsonify({"error": "Campos obrigatórios: user_id, alert_type"}), 400
            
        # Envia alerta para os pais
        notification_id = notification_system.send_parent_alert(
            user_id=user_id,
            alert_type=alert_type,
            details=details
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar alerta para os pais"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Alerta para os pais enviado"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar alerta para os pais: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/financial', methods=['POST'])
def send_financial_notification():
    """
    Envia notificação financeira
    
    Body:
        user_id: ID do usuário
        financial_type: Tipo de notificação financeira
        amount: Valor (opcional)
        details: Detalhes adicionais (opcional)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        financial_type = data.get('financial_type')
        amount = data.get('amount')
        details = data.get('details', {})
        
        if not all([user_id, financial_type]):
            return jsonify({"error": "Campos obrigatórios: user_id, financial_type"}), 400
            
        # Envia notificação financeira
        notification_id = notification_system.send_financial_notification(
            user_id=user_id,
            financial_type=financial_type,
            amount=amount,
            details=details
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação financeira"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação financeira enviada"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação financeira: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/progress', methods=['POST'])
def send_progress_notification():
    """
    Envia notificação de progresso
    
    Body:
        user_id: ID do usuário
        progress_type: Tipo de progresso
        current_value: Valor atual
        target_value: Valor alvo
        metric_name: Nome da métrica
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        progress_type = data.get('progress_type')
        current_value = data.get('current_value')
        target_value = data.get('target_value')
        metric_name = data.get('metric_name')
        
        if not all([user_id, progress_type, current_value, target_value, metric_name]):
            return jsonify({"error": "Campos obrigatórios: user_id, progress_type, current_value, target_value, metric_name"}), 400
            
        # Envia notificação de progresso
        notification_id = notification_system.send_progress_notification(
            user_id=user_id,
            progress_type=progress_type,
            current_value=current_value,
            target_value=target_value,
            metric_name=metric_name
        )
        
        if not notification_id:
            return jsonify({"error": "Erro ao enviar notificação de progresso"}), 500
            
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notificação de progresso enviada"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação de progresso: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/user/<user_id>', methods=['GET'])
def get_user_notifications(user_id: str):
    """
    Obtém notificações do usuário
    
    Args:
        user_id: ID do usuário
        
    Query params:
        limit: Limite de notificações (padrão: 50)
        unread_only: Apenas não lidas (padrão: false)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = notification_system.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only
        )
        
        return jsonify({
            "success": True,
            "notifications": notifications,
            "total": len(notifications)
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter notificações: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id: str):
    """
    Marca notificação como lida
    
    Args:
        notification_id: ID da notificação
    """
    try:
        success = notification_system.mark_as_read(notification_id)
        
        if not success:
            return jsonify({"error": "Notificação não encontrada"}), 404
            
        return jsonify({
            "success": True,
            "message": "Notificação marcada como lida"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id: str):
    """
    Remove notificação
    
    Args:
        notification_id: ID da notificação
    """
    try:
        success = notification_system.delete_notification(notification_id)
        
        if not success:
            return jsonify({"error": "Notificação não encontrada"}), 404
            
        return jsonify({
            "success": True,
            "message": "Notificação removida"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao remover notificação: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/preferences/<user_id>', methods=['GET'])
def get_user_preferences(user_id: str):
    """
    Obtém preferências de notificação do usuário
    
    Args:
        user_id: ID do usuário
    """
    try:
        preferences = notification_system.get_user_preferences(user_id)
        
        return jsonify({
            "success": True,
            "preferences": preferences
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter preferências: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/preferences/<user_id>', methods=['PUT'])
def update_user_preferences(user_id: str):
    """
    Atualiza preferências de notificação do usuário
    
    Args:
        user_id: ID do usuário
        
    Body:
        preferences: Preferências de notificação
    """
    try:
        data = request.get_json()
        
        if not data or 'preferences' not in data:
            return jsonify({"error": "Preferências não fornecidas"}), 400
            
        preferences = data['preferences']
        
        success = notification_system.set_user_preferences(user_id, preferences)
        
        if not success:
            return jsonify({"error": "Erro ao atualizar preferências"}), 500
            
        return jsonify({
            "success": True,
            "message": "Preferências atualizadas"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao atualizar preferências: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@notification_bp.route('/notifications/stats/<user_id>', methods=['GET'])
def get_notification_stats(user_id: str):
    """
    Obtém estatísticas de notificação do usuário
    
    Args:
        user_id: ID do usuário
    """
    try:
        notifications = notification_system.get_user_notifications(user_id, limit=1000)
        
        # Calcula estatísticas
        total_notifications = len(notifications)
        unread_count = len([n for n in notifications if not n.get('read_at')])
        
        # Conta por tipo
        type_counts = {}
        for notification in notifications:
            notif_type = notification.get('type', 'unknown')
            type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
            
        # Conta por prioridade
        priority_counts = {}
        for notification in notifications:
            priority = notification.get('priority', 'normal')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        return jsonify({
            "success": True,
            "stats": {
                "total_notifications": total_notifications,
                "unread_count": unread_count,
                "read_count": total_notifications - unread_count,
                "type_counts": type_counts,
                "priority_counts": priority_counts
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500 