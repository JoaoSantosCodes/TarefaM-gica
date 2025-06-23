#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CHECKLIST ANALYZER - TarefaMágica
================================

Sistema unificado de análise e gestão de checklists.
Base principal para automação do projeto TarefaMágica.

FUNCIONALIDADES:
1. Análise de checklists
   - Prioridades
   - Progresso
   - Pendências
   
2. Gestão de tarefas
   - Sugestão de próximas ações
   - Atualização de status
   - Tracking de progresso

3. Documentação
   - README
   - ROADMAP
   - Relatórios

4. Integração
   - GitHub
   - Workflows
   - Automação

COMO USAR:
python checklist_analyzer.py [comando] [opções]

COMANDOS:
- analyze    : Análise completa (padrão)
- priority   : Análise por prioridade
- next       : Próxima ação sugerida
- update     : Atualiza após tarefa
- docs       : Atualiza documentação
- github     : Prepara commit
- pending    : Lista pendências
- workflow   : Workflow completo
- report     : Gera relatório
"""

import os
import re
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import glob
import codecs
import json
import logging

# Configura encoding para UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.platform == 'win32':
    os.system('chcp 65001')  # Força UTF-8 no terminal Windows

class ChecklistAnalyzer:
    """
    Classe base para análise e gestão de checklists
    """
    
    def __init__(self, checklists_dir: str = "checklists"):
        """
        Inicializa o analisador
        Args:
            checklists_dir (str): Nome da pasta com os checklists
        """
        self.checklists_dir = checklists_dir
        self.checklists = []
        self.total_items = 0
        self.completed_items = 0
        self.critical_checklists = []
        self.important_checklists = []
        self.nice_to_have_checklists = []
        self.project_root = Path.cwd()
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        sys.stdout.reconfigure(encoding='utf-8')
        
    def scan_checklists(self) -> bool:
        """
        Escaneia todos os arquivos .md na pasta checklists
        Returns:
            bool: True se encontrou checklists, False se não
        """
        print("🔍 ESCANEANDO CHECKLISTS...")
        print("=" * 50)
        
        if not os.path.exists(self.checklists_dir):
            print("❌ ERRO: Pasta 'checklists' não encontrada!")
            print("💡 DICA: Certifique-se de que este script está na raiz do projeto")
            return False
            
        checklist_files = glob.glob(os.path.join(self.checklists_dir, "CHECKLIST_*.md"))
        
        if not checklist_files:
            print(f"❌ ERRO: Nenhum arquivo .md encontrado em '{self.checklists_dir}'")
            return False
        
        for file_path in checklist_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extrai informações básicas
                title_match = re.search(r'# (.*)', content)
                title = title_match.group(1) if title_match else os.path.basename(file_path)
                
                # Conta itens totais e completos
                total = len(re.findall(r'- \[[ x]\]', content))
                completed = len(re.findall(r'- \[x\]', content))
                
                # Determina prioridade
                priority = "📈"  # Nice-to-have por padrão
                if "🔥" in content or "CRÍTICO" in content:
                    priority = "🔥"  # Crítico
                elif "⚡" in content or "IMPORTANTE" in content:
                    priority = "⚡"  # Importante
                
                # Calcula progresso
                progress = (completed / total * 100) if total > 0 else 0
                
                # Adiciona à lista apropriada
                checklist = {
                    'file': os.path.basename(file_path),
                    'title': title,
                    'priority': priority,
                    'total': total,
                    'completed': completed,
                    'progress': progress
                }
                
                self.checklists.append(checklist)
                
                # Atualiza contadores
                self.total_items += total
                self.completed_items += completed
                
                # Classifica por prioridade
                if priority == "🔥":
                    self.critical_checklists.append(checklist)
                elif priority == "⚡":
                    self.important_checklists.append(checklist)
                else:
                    self.nice_to_have_checklists.append(checklist)
                
                # Exibe informações
                print(f"  📋 {checklist['file']}")
                print(f"     Título: {checklist['title']}")
                print(f"     Prioridade: {checklist['priority']}")
                print(f"     Progresso: {checklist['progress']:.1f}% ({completed}/{total} itens)\n")
        
        print(f"✅ SUCESSO: Encontrados {len(self.checklists)} checklists")
        return True
    
    def analyze_checklist(self, file_path: Path) -> None:
        """
        Analisa um checklist individual
        Args:
            file_path (Path): Caminho para o arquivo .md
        """
        filename = file_path.name
        content = file_path.read_text(encoding='utf-8')
        
        metadata = {
            'filename': filename,
            'title': self.extract_title(content),
            'priority': self.extract_priority(content),
            'priority_level': self.get_priority_level(content),
            'progress': self.calculate_progress(content),
            'total_items': self.count_checklist_items(content),
            'completed_items': self.count_completed_items(content),
            'pending_items': self.extract_pending_items(content),
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d'),
            'size_kb': round(file_path.stat().st_size / 1024, 1),
            'content': content
        }
        
        self.checklists[filename] = metadata
        
        print(f"  📋 {filename}")
        print(f"     Título: {metadata['title']}")
        print(f"     Prioridade: {metadata['priority']} ({metadata['priority_level']})")
        print(f"     Progresso: {metadata['progress']}% ({metadata['completed_items']}/{metadata['total_items']} itens)")
        print()
    
    def extract_title(self, content: str) -> str:
        """
        Extrai o título do checklist
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            str: Título extraído
        """
        for line in content.split('\n')[:10]:
            if line.startswith('# ') and 'CHECKLIST' in line:
                return re.sub(r'^#+\s*[^\w\s]*\s*', '', line).strip()
        return "Título não encontrado"
    
    def extract_priority(self, content: str) -> str:
        """
        Extrai indicador de prioridade
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            str: Emoji de prioridade
        """
        if '🔥 **PRIORIDADE CRÍTICA**' in content:
            return "🔥"
        elif '⚡ **PRIORIDADE MÉDIA**' in content:
            return "⚡"
        return "📈"
    
    def get_priority_level(self, content: str) -> str:
        """
        Obtém nível de prioridade em texto
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            str: Nível de prioridade
        """
        if '🔥 **PRIORIDADE CRÍTICA**' in content:
            return "Crítico"
        elif '⚡ **PRIORIDADE MÉDIA**' in content:
            return "Importante"
        return "Nice-to-have"
    
    def count_checklist_items(self, content: str) -> int:
        """
        Conta total de itens
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            int: Total de itens
        """
        return len(re.findall(r'^\s*-\s*\[[ xX]\]', content, re.MULTILINE))
    
    def count_completed_items(self, content: str) -> int:
        """
        Conta itens completados
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            int: Número de itens completados
        """
        return len(re.findall(r'^\s*-\s*\[[xX]\]', content, re.MULTILINE))
    
    def extract_pending_items(self, content: str) -> List[str]:
        """
        Extrai itens pendentes importantes
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            List[str]: Lista de itens pendentes
        """
        pending = []
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]'):
                if any(keyword in line.lower() for keyword in ['crítico', 'importante', 'urgente', 'pix', 'segurança', 'lgpd']):
                    pending.append(line.strip())
        return pending[:5]
    
    def calculate_progress(self, content: str) -> float:
        """
        Calcula progresso em porcentagem
        Args:
            content (str): Conteúdo do arquivo
        Returns:
            float: Progresso em %
        """
        total = self.count_checklist_items(content)
        completed = self.count_completed_items(content)
        return round((completed / total) * 100, 1) if total > 0 else 0.0
    
    def analyze_by_priority(self):
        """Analisa os checklists por prioridade."""
        print("\n🔥 ANÁLISE POR PRIORIDADE")
        print("=" * 50)
        
        if self.critical_checklists:
            print("\n🔥 CHECKLISTS CRÍTICOS:")
            for checklist in self.critical_checklists:
                print(f"\n  📋 {checklist['title']} ({checklist['progress']:.1f}%)")
                print(f"     Próximo: {self.get_next_task(checklist['file'])}")
        
        if self.important_checklists:
            print("\n⚡ CHECKLISTS IMPORTANTES:")
            for checklist in self.important_checklists:
                print(f"\n  📋 {checklist['title']} ({checklist['progress']:.1f}%)")
                print(f"     Próximo: {self.get_next_task(checklist['file'])}")
        
        if self.nice_to_have_checklists:
            print("\n📈 CHECKLISTS NICE-TO-HAVE:")
            for checklist in self.nice_to_have_checklists:
                print(f"\n  📋 {checklist['title']} ({checklist['progress']:.1f}%)")
                print(f"     Próximo: {self.get_next_task(checklist['file'])}")
    
    def suggest_next_action(self) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Sugere próxima ação a ser implementada
        Returns:
            Tuple[str, Dict]: Nome do arquivo e dados do checklist, ou (None, None)
        """
        print("\n🎯 PRÓXIMA AÇÃO RECOMENDADA")
        print("=" * 50)
        
        critical, important, nice = self.analyze_by_priority()
        
        if critical:
            next_checklist = min(critical, key=lambda x: x[1]['progress'])
            filename, data = next_checklist
            
            print(f"🎯 CHECKLIST: {data['title']}")
            print(f"📊 PROGRESSO ATUAL: {data['progress']}%")
            print(f"📝 ITENS PENDENTES: {data['total_items'] - data['completed_items']}")
            
            if data['pending_items']:
                print(f"\n🚀 PRÓXIMO ITEM A IMPLEMENTAR:")
                print(f"   {data['pending_items'][0]}")
            
            print(f"\n💡 AÇÕES RECOMENDADAS:")
            print(f"   1. Implementar: {data['pending_items'][0] if data['pending_items'] else 'Próximo item do checklist'}")
            print(f"   2. Testar funcionalidade")
            print(f"   3. Atualizar checklist")
            print(f"   4. Executar: python checklist_analyzer.py update")
            
            return filename, data
            
        print("❌ Nenhum checklist crítico encontrado!")
        return None, None
    
    def update_checklist_after_task(self, checklist_name: Optional[str] = None) -> None:
        """
        Atualiza checklist após conclusão de tarefa
        Args:
            checklist_name (str): Nome do arquivo do checklist
        """
        print("\n📝 ATUALIZAÇÃO DE CHECKLIST")
        print("=" * 50)
        
        if not checklist_name:
            print("📋 CHECKLISTS DISPONÍVEIS:")
            for i, (filename, data) in enumerate(self.checklists.items(), 1):
                print(f"   {i}. {data['title']} ({data['progress']}%)")
            
            try:
                choice = int(input("\nEscolha o número do checklist (0 para cancelar): "))
                if choice == 0:
                    return
                checklist_name = list(self.checklists.keys())[choice - 1]
            except (ValueError, IndexError):
                print("❌ Escolha inválida!")
                return
        
        checklist_file = self.checklists_dir / checklist_name
        if not checklist_file.exists():
            print(f"❌ Checklist {checklist_name} não encontrado!")
            return
        
        print(f"\n📝 ATUALIZANDO: {checklist_name}")
        print("💡 INSTRUÇÕES:")
        print("   1. Abra o arquivo do checklist")
        print("   2. Marque os itens completados com [x]")
        print("   3. Adicione comentários se necessário")
        print("   4. Salve o arquivo")
        print("   5. Execute: python checklist_analyzer.py update")
        
        self.update_general_checklist()
    
    def update_documentation(self):
        """Atualiza a documentação do projeto."""
        print("\n📖 ATUALIZAÇÃO DE DOCUMENTAÇÃO")
        print("=" * 50)
        
        # Gera seção para o README
        print("\n📝 SEÇÃO GERADA PARA README:")
        print("\n## 📊 Status do Projeto")
        print("\n### ✅ Cobertura de Checklists")
        print(f"- **Total de Checklists:** {len(self.checklists)}")
        print(f"- **Críticos:** {len(self.critical_checklists)}")
        print(f"- **Importantes:** {len(self.important_checklists)}")
        
        total_progress = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        print(f"- **Progresso Médio:** {total_progress:.1f}%")
        
        if self.critical_checklists:
            print("\n### 🔥 Próximas Prioridades")
            for checklist in self.critical_checklists[:1]:
                print(f"- {checklist['title']} ({checklist['progress']:.1f}%)")
                next_task = self.get_next_task(checklist['file'])
                if next_task != "Nenhuma tarefa pendente":
                    print(f"  - Próximo: {next_task}")
        
        print(f"\n*Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        print("\n💡 COPIAR ESTA SEÇÃO PARA O README.md")
    
    def update_readme(self) -> None:
        """Atualiza README do projeto"""
        readme_file = self.project_root / "README.md"
        if not readme_file.exists():
            print("❌ README.md não encontrado!")
            return
        
        total = len(self.checklists)
        critical = sum(1 for c in self.checklists.values() if c['priority_level'] == 'Crítico')
        important = sum(1 for c in self.checklists.values() if c['priority_level'] == 'Importante')
        progress = sum(c['progress'] for c in self.checklists.values()) / total if total > 0 else 0
        
        status_section = f"""
## 📊 Status do Projeto

### ✅ Cobertura de Checklists
- **Total de Checklists:** {total}
- **Críticos:** {critical}
- **Importantes:** {important}
- **Progresso Médio:** {progress:.1f}%

### 🔥 Próximas Prioridades
"""
        
        critical, important, nice = self.analyze_by_priority()
        if critical:
            status_section += f"- {critical[0][1]['title']} ({critical[0][1]['progress']}%)\n"
        if important:
            status_section += f"- {important[0][1]['title']} ({important[0][1]['progress']}%)\n"
        
        status_section += f"\n*Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        print("📝 SEÇÃO GERADA PARA README:")
        print(status_section)
        print("\n💡 COPIAR ESTA SEÇÃO PARA O README.md")
    
    def update_roadmap(self) -> None:
        """Atualiza ROADMAP do projeto"""
        print("\n🗺️ ATUALIZAÇÃO DO ROADMAP")
        print("=" * 50)
        
        critical, important, nice = self.analyze_by_priority()
        
        roadmap_content = f"""# 🗺️ ROADMAP - TarefaMágica

## 📅 Cronograma Atualizado
*Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}*

### 🔥 Fase 1 - Crítico (Atual)
"""
        
        for filename, data in critical:
            roadmap_content += f"- [ ] {data['title']} ({data['progress']}%)\n"
            if data['pending_items']:
                roadmap_content += f"      Próximo: {data['pending_items'][0]}\n"
        
        roadmap_content += "\n### ⚡ Fase 2 - Importante\n"
        for filename, data in important:
            roadmap_content += f"- [ ] {data['title']} ({data['progress']}%)\n"
        
        roadmap_content += "\n### 📈 Fase 3 - Nice-to-have\n"
        for filename, data in nice:
            roadmap_content += f"- [ ] {data['title']} ({data['progress']}%)\n"
        
        roadmap_file = self.project_root / "ROADMAP.md"
        roadmap_file.write_text(roadmap_content, encoding='utf-8')
        
        print("✅ ROADMAP.md atualizado!")
    
    def update_general_checklist(self) -> None:
        """Atualiza checklist geral com timestamp"""
        general_file = os.path.join(self.checklists_dir, "CHECKLIST_Geral_Validacao.md")
        
        if not os.path.exists(general_file):
            print("❌ CHECKLIST_Geral_Validacao.md não encontrado!")
            return
        
        try:
            content = open(general_file, 'r', encoding='utf-8').read()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if '🔄 Última Atualização:' not in content:
                content = content.replace(
                    '**📅 Data de Criação:** [Data Atual]',
                    f'**📅 Data de Criação:** [Data Atual]\n**🔄 Última Atualização:** {timestamp}'
                )
            else:
                content = re.sub(
                    r'🔄 Última Atualização:.*',
                    f'🔄 Última Atualização: {timestamp}',
                    content
                )
            
            open(general_file, 'w', encoding='utf-8').write(content)
            print("✅ Checklist geral atualizado!")
            
        except Exception as e:
            print(f"❌ ERRO ao atualizar arquivo: {e}")
    
    def prepare_github_commit(self) -> None:
        """Prepara commit para GitHub"""
        print("\n🐙 PREPARAÇÃO PARA GITHUB")
        print("=" * 50)
        
        if not (self.project_root / ".git").exists():
            print("❌ Não é um repositório Git!")
            print("💡 Execute: git init")
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        progress = sum(c['progress'] for c in self.checklists.values()) / len(self.checklists)
        
        commit_message = f"""📊 Atualização de checklists - {timestamp}

✅ Análise automática de progresso
📋 Atualização de checklists
📖 Atualização de documentação
🗺️ Atualização de roadmap

Progresso médio: {progress:.1f}%
"""
        
        print("📝 MENSAGEM DE COMMIT GERADA:")
        print("=" * 30)
        print(commit_message)
        print("=" * 30)
        
        print("\n💡 COMANDOS PARA EXECUTAR:")
        print("git add .")
        print("git commit -m \"[MENSAGEM ACIMA]\"")
        print("git push origin main")
    
    def analyze_pending_items(self) -> None:
        """Analisa pendências e próxima prioridade"""
        print("\n🔍 ANÁLISE DE PENDÊNCIAS")
        print("=" * 50)
        
        all_pending = []
        for filename, data in self.checklists.items():
            if data['pending_items']:
                all_pending.append({
                    'checklist': data['title'],
                    'priority': data['priority'],
                    'priority_level': data['priority_level'],
                    'items': data['pending_items']
                })
        
        if not all_pending:
            print("🎉 Nenhuma pendência encontrada!")
            return
        
        print("📋 PENDÊNCIAS IDENTIFICADAS:")
        for pending in all_pending:
            print(f"\n📄 {pending['checklist']} ({pending['priority']} {pending['priority_level']})")
            for item in pending['items']:
                print(f"   • {item}")
        
        if all_pending:
            next_action = all_pending[0]
            print(f"\n🎯 PRÓXIMA AÇÃO RECOMENDADA:")
            print(f"   Checklist: {next_action['checklist']}")
            print(f"   Prioridade: {next_action['priority']} {next_action['priority_level']}")
            print(f"   Item: {next_action['items'][0]}")
    
    def execute_workflow(self) -> None:
        """Executa workflow completo"""
        print("🔄 EXECUTANDO WORKFLOW COMPLETO")
        print("=" * 50)
        
        print("1️⃣ ANALISANDO POR PRIORIDADE...")
        critical, important, nice = self.analyze_by_priority()
        
        print("\n2️⃣ SUGERINDO PRÓXIMA AÇÃO...")
        next_checklist, next_data = self.suggest_next_action()
        
        print("\n3️⃣ ATUALIZANDO DOCUMENTAÇÃO...")
        self.update_documentation()
        
        print("\n4️⃣ ANALISANDO PENDÊNCIAS...")
        self.analyze_pending_items()
        
        print("\n5️⃣ PREPARANDO GITHUB...")
        self.prepare_github_commit()
        
        print("\n🎉 WORKFLOW COMPLETO EXECUTADO!")
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Implementar a próxima ação sugerida")
        print("   2. Atualizar checklists conforme necessário")
        print("   3. Executar: python checklist_analyzer.py workflow")
    
    def generate_summary_report(self) -> None:
        """Gera relatório resumido"""
        print("\n📊 RELATÓRIO RESUMIDO")
        print("=" * 50)
        
        print(f"\n📋 TOTAL DE CHECKLISTS: {len(self.checklists)}")
        print(f"🔥 CRÍTICOS: {len(self.critical_checklists)}")
        print(f"⚡ IMPORTANTES: {len(self.important_checklists)}")
        print(f"📈 NICE-TO-HAVE: {len(self.nice_to_have_checklists)}")
        
        total_progress = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        print(f"\n📊 PROGRESSO MÉDIO: {total_progress:.1f}%")
        
        if self.critical_checklists:
            print("\n🔥 CHECKLISTS CRÍTICOS:")
            for checklist in self.critical_checklists:
                print(f"  • {checklist['title']} ({checklist['progress']:.1f}%)")
        
        if self.important_checklists:
            print("\n⚡ CHECKLISTS IMPORTANTES:")
            for checklist in self.important_checklists:
                print(f"  • {checklist['title']} ({checklist['progress']:.1f}%)")
        
        if self.nice_to_have_checklists:
            print("\n📈 CHECKLISTS NICE-TO-HAVE:")
            for checklist in self.nice_to_have_checklists:
                print(f"  • {checklist['title']} ({checklist['progress']:.1f}%)")

    def get_next_task(self, checklist_file):
        """Retorna a próxima tarefa não concluída do checklist."""
        try:
            with open(os.path.join(self.checklists_dir, checklist_file), 'r', encoding='utf-8') as f:
                content = f.readlines()
                for line in content:
                    if '- [ ]' in line:
                        return line.strip()
            return "Nenhuma tarefa pendente"
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    def list_pending(self):
        """Lista todas as tarefas pendentes."""
        print("\n📋 TAREFAS PENDENTES")
        print("=" * 50)
        
        for checklist in self.checklists:
            try:
                with open(os.path.join(self.checklists_dir, checklist['file']), 'r', encoding='utf-8') as f:
                    content = f.readlines()
                    pending = [line.strip() for line in content if '- [ ]' in line]
                    if pending:
                        print(f"\n📋 {checklist['title']}")
                        for task in pending:
                            print(f"  • {task}")
            except Exception as e:
                print(f"❌ Erro ao ler {checklist['file']}: {str(e)}")

    def prepare_commit(self):
        """Prepara mensagem de commit."""
        print("\n📝 PREPARANDO COMMIT")
        print("=" * 50)
        
        # Gera mensagem de commit
        msg = "📋 Atualização de Checklists\n\n"
        msg += f"- Total: {len(self.checklists)} checklists\n"
        msg += f"- Críticos: {len(self.critical_checklists)}\n"
        
        total_progress = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        msg += f"- Progresso: {total_progress:.1f}%\n"
        
        print("\n💡 MENSAGEM DE COMMIT:")
        print(msg)

    def save_output(self, content, filename):
        """Salva output com encoding correto."""
        if sys.platform == 'win32':
            # No Windows, usa UTF-8-SIG (UTF-8 com BOM)
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(content)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

def main():
    """Função principal"""
    print("🎯 CHECKLIST ANALYZER - TarefaMágica")
    print("🔄 WORKFLOW AUTOMATIZADO")
    print("=" * 50)
    print("📝 DESCRIÇÃO: Analisa checklists e gera relatórios")
    print("📁 PASTA: checklists/")
    print("=" * 50)
    
    command = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    
    analyzer = ChecklistAnalyzer()
    
    if not analyzer.scan_checklists():
        return
    
    if command == "analyze":
        analyzer.generate_summary_report()
        analyzer.update_general_checklist()
    elif command == "priority":
        analyzer.analyze_by_priority()
    elif command == "next":
        analyzer.suggest_next_action()
    elif command == "update":
        analyzer.update_checklist_after_task()
    elif command == "docs":
        analyzer.update_documentation()
    elif command == "github":
        analyzer.prepare_github_commit()
    elif command == "pending":
        analyzer.analyze_pending_items()
    elif command == "workflow":
        analyzer.execute_workflow()
    else:
        print(f"❌ Comando '{command}' não reconhecido!")
        print("💡 Comandos: analyze, priority, next, update, docs, github, pending, workflow")
    
    print(f"\n🎉 Análise concluída!")

if __name__ == "__main__":
    main() 