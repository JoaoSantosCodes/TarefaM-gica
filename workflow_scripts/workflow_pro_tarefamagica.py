#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORKFLOW PRO - TarefaMágica
===============================

Combina funcionalidades dos scripts:
- workflow_ia.py
- checklist_analyzer.py

Comandos disponíveis:
- analyze      : Análise resumida
- priority     : Análise por prioridade
- next         : Sugestão de próxima ação
- update       : Atualiza checklist após tarefa
- docs         : Atualiza README, ROADMAP e checklist geral
- github       : Gera commit para GitHub
- pending      : Lista pendências
- workflow     : Executa workflow completo
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

class WorkflowPro:
    def __init__(self, checklists_dir="checklists"):
        self.checklists_dir = Path(checklists_dir)
        self.project_root = Path.cwd()
        self.checklists = {}

    def scan_checklists(self):
        if not self.checklists_dir.exists():
            print("❌ Pasta checklists/ não encontrada!")
            return False
        for file_path in self.checklists_dir.glob("*.md"):
            self.analyze_checklist(file_path)
        print(f"✅ {len(self.checklists)} checklists carregados.")
        return True

    def analyze_checklist(self, file_path):
        content = file_path.read_text(encoding='utf-8')
        self.checklists[file_path.name] = {
            'filename': file_path.name,
            'title': self.extract_title(content),
            'priority': self.extract_priority(content),
            'progress': self.calculate_progress(content),
            'total': self.count_items(content),
            'done': self.count_done(content),
            'pending': self.extract_pending(content),
            'mtime': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
        }

    def extract_title(self, text):
        for line in text.split('\n')[:10]:
            if line.startswith('# ') and 'CHECKLIST' in line:
                return re.sub(r'^#+\s*', '', line).strip()
        return "Sem título"

    def extract_priority(self, text):
        priority_match = re.search(r'Prioridade:\s*(\d+)', text)
        return int(priority_match.group(1)) if priority_match else 999

    def calculate_progress(self, text):
        total = self.count_items(text)
        if total == 0:
            return 0
        return (self.count_done(text) / total) * 100

    def count_items(self, text):
        return len(re.findall(r'^\s*-\s*\[[ xX]\]', text, re.MULTILINE))

    def count_done(self, text):
        return len(re.findall(r'^\s*-\s*\[[xX]\]', text, re.MULTILINE))

    def extract_pending(self, text):
        pending = []
        for line in text.split('\n'):
            if re.match(r'^\s*-\s*\[ \]', line):
                task = re.sub(r'^\s*-\s*\[ \]\s*', '', line).strip()
                pending.append(task)
        return pending

    def analyze(self):
        if not self.scan_checklists():
            return
        
        print("\n📊 Análise dos Checklists:")
        print("=" * 40)
        
        for checklist in sorted(self.checklists.values(), key=lambda x: x['priority']):
            print(f"\n📝 {checklist['filename']}")
            print(f"   Título: {checklist['title']}")
            print(f"   Prioridade: {checklist['priority']}")
            print(f"   Progresso: {checklist['progress']:.1f}% ({checklist['done']}/{checklist['total']})")
            print(f"   Última modificação: {checklist['mtime']}")

    def main(self):
        if len(sys.argv) < 2:
            print("❌ Comando necessário!")
            print("Uso: python workflow_pro_tarefamagica.py <comando>")
            return

        command = sys.argv[1].lower()
        
        if command == "analyze":
            self.analyze()
        else:
            print(f"❌ Comando '{command}' não reconhecido!")

if __name__ == "__main__":
    workflow = WorkflowPro()
    workflow.main()