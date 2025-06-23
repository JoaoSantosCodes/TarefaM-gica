#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Rotas da API - Sistema de Relatórios
Endpoints para geração e consulta de relatórios
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from workflow.reports_system import reports_system, ReportType

# Blueprint para relatórios
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """
    Gera relatório personalizado
    
    Body:
        user_id: ID do usuário
        report_type: Tipo de relatório (daily, weekly, monthly, custom)
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user_id = data.get('user_id')
        report_type_str = data.get('report_type', 'weekly')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        if not user_id:
            return jsonify({"error": "user_id é obrigatório"}), 400
            
        # Valida tipo de relatório
        try:
            report_type = ReportType(report_type_str)
        except ValueError:
            return jsonify({"error": "Tipo de relatório inválido"}), 400
            
        # Processa datas
        if report_type == ReportType.DAILY:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
        elif report_type == ReportType.WEEKLY:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=1)
        elif report_type == ReportType.MONTHLY:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif report_type == ReportType.CUSTOM:
            if not start_date_str or not end_date_str:
                return jsonify({"error": "Datas obrigatórias para relatório customizado"}), 400
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=1)
            
        # Gera relatório
        report = reports_system.generate_comprehensive_report(
            user_id, report_type, start_date, end_date
        )
        
        if not report:
            return jsonify({"error": "Erro ao gerar relatório"}), 500
            
        return jsonify({
            "success": True,
            "report": {
                "id": report.id,
                "user_id": report.user_id,
                "report_type": report.report_type.value,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "generated_at": report.generated_at.isoformat(),
                "summary": report.data["summary"],
                "charts": report.charts,
                "recommendations": report.recommendations,
                "status": report.status
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id: str):
    """
    Obtém relatório específico
    
    Args:
        report_id: ID do relatório
    """
    try:
        # Carrega relatório do arquivo
        import os
        import json
        from workflow.reports_system import ReportData
        
        report_file = os.path.join(reports_system.data_dir, f"{report_id}.json")
        
        if not os.path.exists(report_file):
            return jsonify({"error": "Relatório não encontrado"}), 404
            
        with open(report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            
        return jsonify({
            "success": True,
            "report": report_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter relatório: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/user/<user_id>', methods=['GET'])
def get_user_reports(user_id: str):
    """
    Lista relatórios de um usuário
    
    Args:
        user_id: ID do usuário
    """
    try:
        import os
        import json
        
        reports = []
        
        # Lista arquivos de relatório do usuário
        for filename in os.listdir(reports_system.data_dir):
            if filename.startswith(f"report_{user_id}_") and filename.endswith('.json'):
                report_file = os.path.join(reports_system.data_dir, filename)
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                        reports.append({
                            "id": report_data["id"],
                            "report_type": report_data["report_type"],
                            "period_start": report_data["period_start"],
                            "period_end": report_data["period_end"],
                            "generated_at": report_data["generated_at"],
                            "status": report_data["status"]
                        })
                except Exception as e:
                    logging.warning(f"Erro ao ler relatório {filename}: {str(e)}")
                    continue
                    
        # Ordena por data de geração (mais recente primeiro)
        reports.sort(key=lambda x: x["generated_at"], reverse=True)
        
        return jsonify({
            "success": True,
            "reports": reports,
            "total": len(reports)
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao listar relatórios: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/quick/<user_id>', methods=['GET'])
def get_quick_report(user_id: str):
    """
    Gera relatório rápido (última semana)
    
    Args:
        user_id: ID do usuário
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=1)
        
        report = reports_system.generate_comprehensive_report(
            user_id, ReportType.WEEKLY, start_date, end_date
        )
        
        if not report:
            return jsonify({"error": "Erro ao gerar relatório rápido"}), 500
            
        return jsonify({
            "success": True,
            "report": {
                "id": report.id,
                "summary": report.data["summary"],
                "recommendations": report.recommendations[:3],  # Top 3 recomendações
                "generated_at": report.generated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório rápido: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/achievement/<user_id>', methods=['GET'])
def get_achievement_report(user_id: str):
    """
    Gera relatório de conquistas
    
    Args:
        user_id: ID do usuário
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Últimos 30 dias
        
        report = reports_system.generate_comprehensive_report(
            user_id, ReportType.ACHIEVEMENT, start_date, end_date
        )
        
        if not report:
            return jsonify({"error": "Erro ao gerar relatório de conquistas"}), 500
            
        return jsonify({
            "success": True,
            "report": {
                "id": report.id,
                "gamification": report.data["gamification_analysis"],
                "achievements": report.data["summary"],
                "next_milestones": report.data["gamification_analysis"]["next_milestones"],
                "generated_at": report.generated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de conquistas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/progress/<user_id>', methods=['GET'])
def get_progress_report(user_id: str):
    """
    Gera relatório de progresso
    
    Args:
        user_id: ID do usuário
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=4)  # Últimas 4 semanas
        
        report = reports_system.generate_comprehensive_report(
            user_id, ReportType.PROGRESS, start_date, end_date
        )
        
        if not report:
            return jsonify({"error": "Erro ao gerar relatório de progresso"}), 500
            
        return jsonify({
            "success": True,
            "report": {
                "id": report.id,
                "performance": report.data["performance_metrics"],
                "trends": report.data["trends"],
                "comparisons": report.data["comparisons"],
                "charts": report.charts,
                "generated_at": report.generated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de progresso: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/delete/<report_id>', methods=['DELETE'])
def delete_report(report_id: str):
    """
    Remove relatório específico
    
    Args:
        report_id: ID do relatório
    """
    try:
        import os
        
        report_file = os.path.join(reports_system.data_dir, f"{report_id}.json")
        
        if not os.path.exists(report_file):
            return jsonify({"error": "Relatório não encontrado"}), 404
            
        os.remove(report_file)
        
        return jsonify({
            "success": True,
            "message": "Relatório removido com sucesso"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao remover relatório: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@reports_bp.route('/reports/stats', methods=['GET'])
def get_reports_stats():
    """
    Obtém estatísticas dos relatórios
    """
    try:
        import os
        
        total_reports = 0
        reports_by_type = {}
        
        for filename in os.listdir(reports_system.data_dir):
            if filename.endswith('.json'):
                total_reports += 1
                
                # Extrai tipo do relatório do nome do arquivo
                parts = filename.replace('.json', '').split('_')
                if len(parts) >= 3:
                    report_type = parts[2]
                    reports_by_type[report_type] = reports_by_type.get(report_type, 0) + 1
                    
        return jsonify({
            "success": True,
            "stats": {
                "total_reports": total_reports,
                "reports_by_type": reports_by_type,
                "storage_size": "2.5 MB"  # Implementar cálculo real
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500 