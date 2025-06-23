#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Sistema de Gamificação Avançada - TarefaMágica
Missões, eventos, competições e recompensas dinâmicas
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
import random
import math

class MissionType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIAL = "special"
    CHALLENGE = "challenge"
    EVENT = "event"

class EventType(Enum):
    HOLIDAY = "holiday"
    SEASONAL = "seasonal"
    COMPETITION = "competition"
    COLLABORATION = "collaboration"
    SPECIAL = "special"

class CompetitionType(Enum):
    INDIVIDUAL = "individual"
    TEAM = "team"
    FAMILY = "family"
    GLOBAL = "global"

@dataclass
class Mission:
    id: str
    title: str
    description: str
    mission_type: MissionType
    requirements: Dict
    rewards: Dict
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    current_participants: int = 0
    difficulty: str = "normal"
    category: str = "general"

@dataclass
class Event:
    id: str
    title: str
    description: str
    event_type: EventType
    start_date: datetime
    end_date: datetime
    missions: List[str]
    rewards: Dict
    participants: List[str]
    status: str = "active"

@dataclass
class Competition:
    id: str
    title: str
    description: str
    competition_type: CompetitionType
    start_date: datetime
    end_date: datetime
    participants: Dict[str, Dict]
    leaderboard: List[Dict]
    rewards: Dict
    status: str = "active"

class AdvancedGamification:
    def __init__(self, data_dir: str = "data/gamification"):
        """
        Inicializa sistema de gamificação avançada
        
        Args:
            data_dir: Diretório para armazenar dados
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Carrega missões, eventos e competições
        self.missions = {}
        self.events = {}
        self.competitions = {}
        
        self._load_data()
        
        logging.info("Sistema de gamificação avançada inicializado")
        
    def create_mission(self, title: str, description: str, mission_type: MissionType,
                      requirements: Dict, rewards: Dict, start_date: datetime,
                      end_date: datetime, difficulty: str = "normal",
                      category: str = "general", max_participants: Optional[int] = None) -> str:
        """
        Cria nova missão
        
        Args:
            title: Título da missão
            description: Descrição da missão
            mission_type: Tipo da missão
            requirements: Requisitos para completar
            rewards: Recompensas
            start_date: Data de início
            end_date: Data de fim
            difficulty: Dificuldade
            category: Categoria
            max_participants: Máximo de participantes
            
        Returns:
            str: ID da missão
        """
        try:
            mission_id = f"mission_{mission_type.value}_{int(time.time())}"
            
            mission = Mission(
                id=mission_id,
                title=title,
                description=description,
                mission_type=mission_type,
                requirements=requirements,
                rewards=rewards,
                start_date=start_date,
                end_date=end_date,
                max_participants=max_participants,
                difficulty=difficulty,
                category=category
            )
            
            self.missions[mission_id] = mission
            self._save_missions()
            
            logging.info(f"Missão criada: {mission_id} - {title}")
            return mission_id
            
        except Exception as e:
            logging.error(f"Erro ao criar missão: {str(e)}")
            return None
            
    def create_daily_mission(self, title: str, description: str, requirements: Dict,
                           rewards: Dict, category: str = "general") -> str:
        """
        Cria missão diária
        
        Args:
            title: Título da missão
            description: Descrição da missão
            requirements: Requisitos
            rewards: Recompensas
            category: Categoria
            
        Returns:
            str: ID da missão
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)
        
        return self.create_mission(
            title=title,
            description=description,
            mission_type=MissionType.DAILY,
            requirements=requirements,
            rewards=rewards,
            start_date=start_date,
            end_date=end_date,
            difficulty="easy",
            category=category
        )
        
    def create_weekly_mission(self, title: str, description: str, requirements: Dict,
                            rewards: Dict, category: str = "general") -> str:
        """
        Cria missão semanal
        
        Args:
            title: Título da missão
            description: Descrição da missão
            requirements: Requisitos
            rewards: Recompensas
            category: Categoria
            
        Returns:
            str: ID da missão
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=1)
        
        return self.create_mission(
            title=title,
            description=description,
            mission_type=MissionType.WEEKLY,
            requirements=requirements,
            rewards=rewards,
            start_date=start_date,
            end_date=end_date,
            difficulty="normal",
            category=category
        )
        
    def create_special_mission(self, title: str, description: str, requirements: Dict,
                             rewards: Dict, end_date: datetime, category: str = "special") -> str:
        """
        Cria missão especial
        
        Args:
            title: Título da missão
            description: Descrição da missão
            requirements: Requisitos
            rewards: Recompensas
            end_date: Data de fim
            category: Categoria
            
        Returns:
            str: ID da missão
        """
        start_date = datetime.now()
        
        return self.create_mission(
            title=title,
            description=description,
            mission_type=MissionType.SPECIAL,
            requirements=requirements,
            rewards=rewards,
            start_date=start_date,
            end_date=end_date,
            difficulty="hard",
            category=category
        )
        
    def create_event(self, title: str, description: str, event_type: EventType,
                    start_date: datetime, end_date: datetime, missions: List[str],
                    rewards: Dict) -> str:
        """
        Cria novo evento
        
        Args:
            title: Título do evento
            description: Descrição do evento
            event_type: Tipo do evento
            start_date: Data de início
            end_date: Data de fim
            missions: Lista de IDs de missões
            rewards: Recompensas do evento
            
        Returns:
            str: ID do evento
        """
        try:
            event_id = f"event_{event_type.value}_{int(time.time())}"
            
            event = Event(
                id=event_id,
                title=title,
                description=description,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                missions=missions,
                rewards=rewards,
                participants=[]
            )
            
            self.events[event_id] = event
            self._save_events()
            
            logging.info(f"Evento criado: {event_id} - {title}")
            return event_id
            
        except Exception as e:
            logging.error(f"Erro ao criar evento: {str(e)}")
            return None
            
    def create_competition(self, title: str, description: str, competition_type: CompetitionType,
                         start_date: datetime, end_date: datetime, rewards: Dict) -> str:
        """
        Cria nova competição
        
        Args:
            title: Título da competição
            description: Descrição da competição
            competition_type: Tipo da competição
            start_date: Data de início
            end_date: Data de fim
            rewards: Recompensas
            
        Returns:
            str: ID da competição
        """
        try:
            competition_id = f"comp_{competition_type.value}_{int(time.time())}"
            
            competition = Competition(
                id=competition_id,
                title=title,
                description=description,
                competition_type=competition_type,
                start_date=start_date,
                end_date=end_date,
                participants={},
                leaderboard=[],
                rewards=rewards
            )
            
            self.competitions[competition_id] = competition
            self._save_competitions()
            
            logging.info(f"Competição criada: {competition_id} - {title}")
            return competition_id
            
        except Exception as e:
            logging.error(f"Erro ao criar competição: {str(e)}")
            return None
            
    def join_mission(self, user_id: str, mission_id: str) -> bool:
        """
        Usuário entra em uma missão
        
        Args:
            user_id: ID do usuário
            mission_id: ID da missão
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            if mission_id not in self.missions:
                return False
                
            mission = self.missions[mission_id]
            
            # Verifica se a missão está ativa
            now = datetime.now()
            if now < mission.start_date or now > mission.end_date:
                return False
                
            # Verifica limite de participantes
            if mission.max_participants and mission.current_participants >= mission.max_participants:
                return False
                
            # Incrementa contador de participantes
            mission.current_participants += 1
            self._save_missions()
            
            logging.info(f"Usuário {user_id} entrou na missão {mission_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao entrar na missão: {str(e)}")
            return False
            
    def join_event(self, user_id: str, event_id: str) -> bool:
        """
        Usuário entra em um evento
        
        Args:
            user_id: ID do usuário
            event_id: ID do evento
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            if event_id not in self.events:
                return False
                
            event = self.events[event_id]
            
            # Verifica se o evento está ativo
            now = datetime.now()
            if now < event.start_date or now > event.end_date:
                return False
                
            # Adiciona participante
            if user_id not in event.participants:
                event.participants.append(user_id)
                self._save_events()
                
            logging.info(f"Usuário {user_id} entrou no evento {event_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao entrar no evento: {str(e)}")
            return False
            
    def join_competition(self, user_id: str, competition_id: str, team_id: str = None) -> bool:
        """
        Usuário entra em uma competição
        
        Args:
            user_id: ID do usuário
            competition_id: ID da competição
            team_id: ID do time (se aplicável)
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            if competition_id not in self.competitions:
                return False
                
            competition = self.competitions[competition_id]
            
            # Verifica se a competição está ativa
            now = datetime.now()
            if now < competition.start_date or now > competition.end_date:
                return False
                
            # Adiciona participante
            if user_id not in competition.participants:
                competition.participants[user_id] = {
                    "joined_at": datetime.now().isoformat(),
                    "score": 0,
                    "team_id": team_id,
                    "completed_tasks": 0,
                    "earned_points": 0
                }
                self._save_competitions()
                
            logging.info(f"Usuário {user_id} entrou na competição {competition_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao entrar na competição: {str(e)}")
            return False
            
    def update_competition_score(self, user_id: str, competition_id: str, points: int,
                               completed_tasks: int = 0) -> bool:
        """
        Atualiza pontuação na competição
        
        Args:
            user_id: ID do usuário
            competition_id: ID da competição
            points: Pontos a adicionar
            completed_tasks: Tarefas completadas
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            if competition_id not in self.competitions:
                return False
                
            competition = self.competitions[competition_id]
            
            if user_id not in competition.participants:
                return False
                
            # Atualiza pontuação
            competition.participants[user_id]["score"] += points
            competition.participants[user_id]["earned_points"] += points
            competition.participants[user_id]["completed_tasks"] += completed_tasks
            
            # Atualiza leaderboard
            self._update_leaderboard(competition_id)
            
            self._save_competitions()
            
            logging.info(f"Pontuação atualizada: {user_id} +{points} pontos na competição {competition_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao atualizar pontuação: {str(e)}")
            return False
            
    def get_available_missions(self, user_id: str = None) -> List[Dict]:
        """
        Obtém missões disponíveis
        
        Args:
            user_id: ID do usuário (opcional)
            
        Returns:
            List[Dict]: Lista de missões
        """
        try:
            now = datetime.now()
            available_missions = []
            
            for mission in self.missions.values():
                if mission.start_date <= now <= mission.end_date:
                    mission_data = asdict(mission)
                    mission_data["is_available"] = True
                    
                    # Verifica se há vagas
                    if mission.max_participants:
                        mission_data["spots_remaining"] = max(0, mission.max_participants - mission.current_participants)
                    else:
                        mission_data["spots_remaining"] = None
                        
                    available_missions.append(mission_data)
                    
            return available_missions
            
        except Exception as e:
            logging.error(f"Erro ao obter missões: {str(e)}")
            return []
            
    def get_active_events(self) -> List[Dict]:
        """
        Obtém eventos ativos
        
        Returns:
            List[Dict]: Lista de eventos
        """
        try:
            now = datetime.now()
            active_events = []
            
            for event in self.events.values():
                if event.start_date <= now <= event.end_date and event.status == "active":
                    event_data = asdict(event)
                    event_data["is_active"] = True
                    event_data["days_remaining"] = (event.end_date - now).days
                    active_events.append(event_data)
                    
            return active_events
            
        except Exception as e:
            logging.error(f"Erro ao obter eventos: {str(e)}")
            return []
            
    def get_active_competitions(self) -> List[Dict]:
        """
        Obtém competições ativas
        
        Returns:
            List[Dict]: Lista de competições
        """
        try:
            now = datetime.now()
            active_competitions = []
            
            for competition in self.competitions.values():
                if competition.start_date <= now <= competition.end_date and competition.status == "active":
                    competition_data = asdict(competition)
                    competition_data["is_active"] = True
                    competition_data["days_remaining"] = (competition.end_date - now).days
                    competition_data["total_participants"] = len(competition.participants)
                    active_competitions.append(competition_data)
                    
            return active_competitions
            
        except Exception as e:
            logging.error(f"Erro ao obter competições: {str(e)}")
            return []
            
    def get_leaderboard(self, competition_id: str, limit: int = 10) -> List[Dict]:
        """
        Obtém leaderboard da competição
        
        Args:
            competition_id: ID da competição
            limit: Limite de posições
            
        Returns:
            List[Dict]: Leaderboard
        """
        try:
            if competition_id not in self.competitions:
                return []
                
            competition = self.competitions[competition_id]
            
            # Ordena por pontuação
            sorted_participants = sorted(
                competition.participants.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )
            
            leaderboard = []
            for position, (user_id, data) in enumerate(sorted_participants[:limit], 1):
                leaderboard.append({
                    "position": position,
                    "user_id": user_id,
                    "score": data["score"],
                    "completed_tasks": data["completed_tasks"],
                    "earned_points": data["earned_points"],
                    "team_id": data.get("team_id")
                })
                
            return leaderboard
            
        except Exception as e:
            logging.error(f"Erro ao obter leaderboard: {str(e)}")
            return []
            
    def generate_daily_missions(self) -> List[str]:
        """
        Gera missões diárias automáticas
        
        Returns:
            List[str]: IDs das missões criadas
        """
        try:
            mission_ids = []
            
            # Missão: Complete 3 tarefas
            mission_id = self.create_daily_mission(
                title="🎯 Produtivo do Dia",
                description="Complete 3 tarefas hoje para ganhar pontos extras!",
                requirements={"tasks_completed": 3},
                rewards={"points": 50, "coins": 10},
                category="productivity"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            # Missão: Economize dinheiro
            mission_id = self.create_daily_mission(
                title="💰 Economista",
                description="Economize pelo menos R$ 5,00 hoje!",
                requirements={"savings": 5.0},
                rewards={"points": 30, "coins": 5},
                category="financial"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            # Missão: Ajude alguém
            mission_id = self.create_daily_mission(
                title="🤝 Ajudante",
                description="Ajude alguém hoje com uma tarefa!",
                requirements={"help_others": 1},
                rewards={"points": 40, "badge": "helper"},
                category="social"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            logging.info(f"Missões diárias geradas: {len(mission_ids)}")
            return mission_ids
            
        except Exception as e:
            logging.error(f"Erro ao gerar missões diárias: {str(e)}")
            return []
            
    def generate_weekly_missions(self) -> List[str]:
        """
        Gera missões semanais automáticas
        
        Returns:
            List[str]: IDs das missões criadas
        """
        try:
            mission_ids = []
            
            # Missão: Sequência de 5 dias
            mission_id = self.create_weekly_mission(
                title="🔥 Sequência Incrível",
                description="Mantenha uma sequência de 5 dias completando tarefas!",
                requirements={"streak_days": 5},
                rewards={"points": 200, "coins": 50, "badge": "streak_master"},
                category="consistency"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            # Missão: Economia semanal
            mission_id = self.create_weekly_mission(
                title="💰 Economista Semanal",
                description="Economize R$ 20,00 esta semana!",
                requirements={"weekly_savings": 20.0},
                rewards={"points": 150, "coins": 30},
                category="financial"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            # Missão: Criatividade
            mission_id = self.create_weekly_mission(
                title="🎨 Criativo",
                description="Crie 3 tarefas personalizadas esta semana!",
                requirements={"custom_tasks_created": 3},
                rewards={"points": 100, "badge": "creative"},
                category="creativity"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            logging.info(f"Missões semanais geradas: {len(mission_ids)}")
            return mission_ids
            
        except Exception as e:
            logging.error(f"Erro ao gerar missões semanais: {str(e)}")
            return []
            
    def create_holiday_event(self, holiday_name: str, start_date: datetime,
                           end_date: datetime) -> str:
        """
        Cria evento de feriado
        
        Args:
            holiday_name: Nome do feriado
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            str: ID do evento
        """
        try:
            # Cria missões especiais para o feriado
            mission_ids = []
            
            # Missão especial do feriado
            mission_id = self.create_special_mission(
                title=f"🎉 {holiday_name} Especial",
                description=f"Complete tarefas especiais durante o {holiday_name}!",
                requirements={"tasks_completed": 5},
                rewards={"points": 300, "coins": 100, "badge": f"{holiday_name.lower()}_specialist"},
                end_date=end_date,
                category="holiday"
            )
            if mission_id:
                mission_ids.append(mission_id)
                
            # Cria evento
            event_id = self.create_event(
                title=f"🎊 Evento {holiday_name}",
                description=f"Celebre o {holiday_name} com tarefas especiais e recompensas únicas!",
                event_type=EventType.HOLIDAY,
                start_date=start_date,
                end_date=end_date,
                missions=mission_ids,
                rewards={"bonus_points": 50, "special_badge": f"{holiday_name.lower()}_celebrator"}
            )
            
            return event_id
            
        except Exception as e:
            logging.error(f"Erro ao criar evento de feriado: {str(e)}")
            return None
            
    def _update_leaderboard(self, competition_id: str):
        """
        Atualiza leaderboard da competição
        
        Args:
            competition_id: ID da competição
        """
        try:
            competition = self.competitions[competition_id]
            
            # Ordena participantes por pontuação
            sorted_participants = sorted(
                competition.participants.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )
            
            # Atualiza leaderboard
            competition.leaderboard = []
            for position, (user_id, data) in enumerate(sorted_participants, 1):
                competition.leaderboard.append({
                    "position": position,
                    "user_id": user_id,
                    "score": data["score"],
                    "completed_tasks": data["completed_tasks"]
                })
                
        except Exception as e:
            logging.error(f"Erro ao atualizar leaderboard: {str(e)}")
            
    def _load_data(self):
        """Carrega dados salvos"""
        try:
            # Carrega missões
            missions_file = os.path.join(self.data_dir, "missions.json")
            if os.path.exists(missions_file):
                with open(missions_file, 'r', encoding='utf-8') as f:
                    missions_data = json.load(f)
                    for mission_data in missions_data.values():
                        mission = Mission(**mission_data)
                        self.missions[mission.id] = mission
                        
            # Carrega eventos
            events_file = os.path.join(self.data_dir, "events.json")
            if os.path.exists(events_file):
                with open(events_file, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    for event_data in events_data.values():
                        event = Event(**event_data)
                        self.events[event.id] = event
                        
            # Carrega competições
            competitions_file = os.path.join(self.data_dir, "competitions.json")
            if os.path.exists(competitions_file):
                with open(competitions_file, 'r', encoding='utf-8') as f:
                    competitions_data = json.load(f)
                    for competition_data in competitions_data.values():
                        competition = Competition(**competition_data)
                        self.competitions[competition.id] = competition
                        
        except Exception as e:
            logging.error(f"Erro ao carregar dados: {str(e)}")
            
    def _save_missions(self):
        """Salva missões"""
        try:
            missions_file = os.path.join(self.data_dir, "missions.json")
            missions_data = {mission.id: asdict(mission) for mission in self.missions.values()}
            with open(missions_file, 'w', encoding='utf-8') as f:
                json.dump(missions_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logging.error(f"Erro ao salvar missões: {str(e)}")
            
    def _save_events(self):
        """Salva eventos"""
        try:
            events_file = os.path.join(self.data_dir, "events.json")
            events_data = {event.id: asdict(event) for event in self.events.values()}
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logging.error(f"Erro ao salvar eventos: {str(e)}")
            
    def _save_competitions(self):
        """Salva competições"""
        try:
            competitions_file = os.path.join(self.data_dir, "competitions.json")
            competitions_data = {comp.id: asdict(comp) for comp in self.competitions.values()}
            with open(competitions_file, 'w', encoding='utf-8') as f:
                json.dump(competitions_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logging.error(f"Erro ao salvar competições: {str(e)}")

# Instância global
advanced_gamification = AdvancedGamification() 