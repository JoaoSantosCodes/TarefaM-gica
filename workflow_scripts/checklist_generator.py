#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKLIST GENERATOR - TarefaMágica
=================================

Gera checklists automaticamente baseado no resumo do projeto.
Foco em:
- Funcionalidades principais
- Sistema de gamificação
- Interface
- Stack de desenvolvimento
- Roadmap
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class ChecklistGenerator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        
    def generate_checklists(self):
        """Gera os checklists baseados no resumo do projeto."""
        # Cria diretório de checklists se não existir
        checklists_dir = self.project_root / 'checklists'
        checklists_dir.mkdir(exist_ok=True)
        
        # Gera os checklists específicos do TarefaMágica
        self._generate_features_checklist(checklists_dir)
        self._generate_gamification_checklist(checklists_dir)
        self._generate_interface_checklist(checklists_dir)
        self._generate_technical_checklist(checklists_dir)
        self._generate_deployment_checklist(checklists_dir)
        
        print(f"\n✅ Checklists gerados com sucesso em {checklists_dir}")

    def _generate_features_checklist(self, output_dir):
        """Gera checklist de funcionalidades principais."""
        content = f"""# CHECKLIST DE FUNCIONALIDADES

**📅 Data de Criação:** {datetime.now().strftime('%Y-%m-%d')}

## 👨‍👩‍👧 Perfil Familiar - Admin (Pais)
- [ ] Criar tarefas com descrição
- [ ] Definir valor por tarefa (limite R$10)
- [ ] Sistema de aprovação de tarefas
- [ ] Histórico de tarefas realizadas
- [ ] Controle de saldo e recompensas
- [ ] Gerenciamento de perfis de crianças

## 🧒 Perfil Familiar - Criança
- [ ] Visualização de tarefas disponíveis
- [ ] Upload de foto/vídeo da tarefa
- [ ] Marcação de tarefa como concluída
- [ ] Visualização de progresso
- [ ] Acompanhamento de saldo
- [ ] Personalização de avatar

## 📱 Funcionalidades Extras
- [ ] Notificações push
- [ ] Lembretes mágicos
- [ ] Estatísticas para pais
- [ ] Modo mascote ajudante
- [ ] Sistema de dicas e elogios
- [ ] Tarefas recorrentes

## 🎯 Prioridade: 1
"""
        
        output_file = output_dir / 'CHECKLIST_Funcionalidades.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_gamification_checklist(self, output_dir):
        """Gera checklist do sistema de gamificação."""
        content = f"""# CHECKLIST DE GAMIFICAÇÃO

**📅 Data de Criação:** {datetime.now().strftime('%Y-%m-%d')}

## 🎮 Sistema de Níveis
- [ ] Sistema de XP por tarefa
- [ ] Progressão de níveis
- [ ] Desbloqueio de itens por nível
- [ ] Sistema de conquistas
- [ ] Badges/medalhas especiais
- [ ] Ranking entre irmãos (opcional)

## 💰 Sistema de Moedas
- [ ] Conversão R$ para moedas (1:1)
- [ ] Sistema de carteira virtual
- [ ] Loja de itens cosméticos
- [ ] Sistema de preços dinâmicos
- [ ] Histórico de transações
- [ ] Integração com PIX (futuro)

## 🎨 Customização
- [ ] Sistema de avatares
- [ ] Roupas desbloqueáveis
- [ ] Fundos personalizados
- [ ] Adesivos digitais
- [ ] Frases mágicas
- [ ] Temas especiais

## 🎯 Prioridade: 2
"""
        
        output_file = output_dir / 'CHECKLIST_Gamificacao.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_interface_checklist(self, output_dir):
        """Gera checklist da interface."""
        content = f"""# CHECKLIST DE INTERFACE

**📅 Data de Criação:** {datetime.now().strftime('%Y-%m-%d')}

## 🎨 Design Visual
- [ ] Paleta de cores alegre
- [ ] Elementos mágicos (varinhas, estrelas)
- [ ] Mascotes animados
- [ ] Ícones ilustrados para tarefas
- [ ] Botões grandes e claros
- [ ] Fontes legíveis para crianças

## 🌓 Temas
- [ ] Modo claro implementado
- [ ] Modo escuro implementado
- [ ] Transição suave entre temas
- [ ] Temas sazonais
- [ ] Temas desbloqueáveis
- [ ] Persistência da preferência

## 📱 Responsividade
- [ ] Layout adaptativo
- [ ] Suporte a diferentes telas
- [ ] Orientação retrato/paisagem
- [ ] Animações fluidas
- [ ] Feedback tátil
- [ ] Gestos intuitivos

## 🎯 Prioridade: 1
"""
        
        output_file = output_dir / 'CHECKLIST_Interface.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_technical_checklist(self, output_dir):
        """Gera checklist técnico."""
        content = f"""# CHECKLIST TÉCNICO

**📅 Data de Criação:** {datetime.now().strftime('%Y-%m-%d')}

## 📱 Frontend (Flutter)
- [ ] Setup do projeto Flutter
- [ ] Configuração do Material Design
- [ ] Integração com Firebase
- [ ] Sistema de rotas
- [ ] Gerenciamento de estado
- [ ] Widgets personalizados

## ⚙️ Backend (Firebase)
- [ ] Configuração do Firestore
- [ ] Esquema do banco de dados
- [ ] Regras de segurança
- [ ] Autenticação de usuários
- [ ] Cloud Functions
- [ ] Storage para mídias

## 🔐 Segurança
- [ ] Autenticação segura
- [ ] Controle de acesso
- [ ] Proteção de dados
- [ ] Backup automático
- [ ] Logs de atividade
- [ ] Conformidade LGPD

## 🎯 Prioridade: 1
"""
        
        output_file = output_dir / 'CHECKLIST_Tecnico.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_deployment_checklist(self, output_dir):
        """Gera checklist de deploy e testes."""
        content = f"""# CHECKLIST DE DEPLOY

**📅 Data de Criação:** {datetime.now().strftime('%Y-%m-%d')}

## 🧪 Testes
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes de UI
- [ ] Testes de usabilidade
- [ ] Beta testing com famílias
- [ ] Feedback de usuários

## 📱 Google Play
- [ ] Conta de desenvolvedor
- [ ] Screenshots do app
- [ ] Descrição e metadata
- [ ] Políticas de privacidade
- [ ] Termos de uso
- [ ] Release beta

## 🚀 Lançamento
- [ ] Correção de bugs
- [ ] Otimização de performance
- [ ] Marketing inicial
- [ ] Suporte ao usuário
- [ ] Monitoramento
- [ ] Atualizações planejadas

## 🎯 Prioridade: 3
"""
        
        output_file = output_dir / 'CHECKLIST_Deploy.md'
        output_file.write_text(content, encoding='utf-8')

def main():
    """Função principal."""
    try:
        print("\n🎯 GERADOR DE CHECKLISTS - TarefaMágica")
        print("=" * 50)
        
        # Usa o diretório atual ou o passado como argumento
        project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
        
        generator = ChecklistGenerator(project_dir)
        generator.generate_checklists()
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar checklists: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 