#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import io
import codecs

# Configura encoding para UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.platform == 'win32':
    os.system('chcp 65001')  # Força UTF-8 no terminal Windows

def setup_encoding():
    """Configura o encoding para UTF-8 em diferentes sistemas."""
    if sys.platform == 'win32':
        # Força UTF-8 no Windows
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        os.system('chcp 65001')  # Força UTF-8 no terminal Windows
    
    # Configura variáveis de ambiente
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Configura encoding antes de importar outros módulos
setup_encoding()

"""
WORKFLOW IA - TarefaMágica
==========================

WORKFLOW AUTOMATIZADO PARA IA SEGUIR:

1. Analisar atividades por grau de prioridade
2. Implementar funcionalidade/reparar/pensar solução
3. Atualizar checklists, README, roadmap e GitHub
4. Analisar pendências e próxima prioridade

COMO USAR:
python workflow_ia.py [comando]

COMANDOS:
- analyze    : Análise por prioridade
- next       : Próxima ação recomendada
- update     : Atualizar após tarefa
- docs       : Atualizar documentação
- github     : Preparar commit
- workflow   : Executar workflow completo
"""

import re
from datetime import datetime
from pathlib import Path
from checklist_analyzer import ChecklistAnalyzer

class WorkflowIA:
    def __init__(self):
        self.analyzer = ChecklistAnalyzer()
        self.tasks_output = []
        self.flow_output = []
        self.checklists_dir = Path("checklists")
        self.project_root = Path.cwd()
        self.checklists = {}
        
    def scan_checklists(self):
        """Escaneia checklists"""
        print("🔍 ESCANEANDO CHECKLISTS...")
        
        if not self.checklists_dir.exists():
            print("❌ Pasta checklists/ não encontrada!")
            return False
            
        for file_path in self.checklists_dir.glob("*.md"):
            if file_path.is_file():
                self.analyze_checklist(file_path)
        
        print(f"✅ {len(self.checklists)} checklists encontrados")
        return True
    
    def analyze_checklist(self, file_path):
        """Analisa checklist individual"""
        filename = file_path.name
        content = file_path.read_text(encoding='utf-8')
        
        self.checklists[filename] = {
            'filename': filename,
            'title': self.extract_title(content),
            'priority': self.extract_priority(content),
            'progress': self.calculate_progress(content),
            'total_items': self.count_items(content),
            'completed_items': self.count_completed(content),
            'pending_items': self.extract_pending(content)
        }
    
    def extract_title(self, content):
        """Extrai título"""
        for line in content.split('\n')[:10]:
            if line.startswith('# ') and 'CHECKLIST' in line:
                return re.sub(r'^#+\s*[^\w\s]*\s*', '', line).strip()
        return "Título não encontrado"
    
    def extract_priority(self, content):
        """Extrai prioridade"""
        if '🔥 **PRIORIDADE CRÍTICA**' in content:
            return "🔥 Crítico"
        elif '⚡ **PRIORIDADE MÉDIA**' in content:
            return "⚡ Importante"
        else:
            return "📈 Nice-to-have"
    
    def count_items(self, content):
        """Conta itens totais"""
        return len(re.findall(r'^\s*-\s*\[ \]', content, re.MULTILINE))
    
    def count_completed(self, content):
        """Conta itens completados"""
        return len(re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE))
    
    def extract_pending(self, content):
        """Extrai itens pendentes"""
        pending = []
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]') and any(keyword in line.lower() for keyword in ['crítico', 'pix', 'segurança', 'lgpd', 'teste']):
                pending.append(line.strip())
        return pending[:3]
    
    def calculate_progress(self, content):
        """Calcula progresso"""
        total = self.count_items(content)
        completed = self.count_completed(content)
        return round((completed / total) * 100, 1) if total > 0 else 0
    
    def analyze_by_priority(self):
        """1. ANALISA ATIVIDADES POR PRIORIDADE"""
        print("\n🔥 ANÁLISE POR PRIORIDADE")
        print("=" * 50)
        
        critical = []
        important = []
        nice = []
        
        for filename, data in self.checklists.items():
            if 'Crítico' in data['priority']:
                critical.append((filename, data))
            elif 'Importante' in data['priority']:
                important.append((filename, data))
            else:
                nice.append((filename, data))
        
        print("🔥 CHECKLISTS CRÍTICOS:")
        for filename, data in critical:
            print(f"  📋 {data['title']} ({data['progress']}%)")
            if data['pending_items']:
                print(f"     Próximo: {data['pending_items'][0]}")
        
        print("\n⚡ CHECKLISTS IMPORTANTES:")
        for filename, data in important:
            print(f"  📋 {data['title']} ({data['progress']}%)")
        
        return critical, important, nice
    
    def suggest_next_action(self):
        """2. SUGERE PRÓXIMA AÇÃO"""
        print("\n🎯 PRÓXIMA AÇÃO RECOMENDADA")
        print("=" * 50)
        
        critical, important, nice = self.analyze_by_priority()
        
        if critical:
            next_checklist = min(critical, key=lambda x: x[1]['progress'])
            filename, data = next_checklist
            
            print(f"🎯 CHECKLIST: {data['title']}")
            print(f"📊 PROGRESSO: {data['progress']}%")
            print(f"📝 PENDENTES: {data['total_items'] - data['completed_items']}")
            
            if data['pending_items']:
                print(f"🚀 PRÓXIMO ITEM:")
                print(f"   {data['pending_items'][0]}")
            
            print(f"\n💡 AÇÕES:")
            print(f"   1. Implementar o item acima")
            print(f"   2. Testar funcionalidade")
            print(f"   3. Executar: python workflow_ia.py update")
            
            return filename, data
        
        print("❌ Nenhum checklist crítico encontrado!")
        return None, None
    
    def update_after_task(self):
        """3. ATUALIZA APÓS TAREFA"""
        print("\n📝 ATUALIZAÇÃO APÓS TAREFA")
        print("=" * 50)
        
        print("📋 CHECKLISTS DISPONÍVEIS:")
        for i, (filename, data) in enumerate(self.checklists.items(), 1):
            print(f"   {i}. {data['title']} ({data['progress']}%)")
        
        try:
            choice = int(input("\nEscolha o checklist atualizado (0 para cancelar): "))
            if choice == 0:
                return
            checklist_name = list(self.checklists.keys())[choice - 1]
        except (ValueError, IndexError):
            print("❌ Escolha inválida!")
            return
        
        print(f"✅ Checklist {checklist_name} selecionado!")
        print("💡 Lembre-se de:")
        print("   - Marcar itens completados com [x]")
        print("   - Adicionar comentários se necessário")
        print("   - Salvar o arquivo")
        
        # Atualiza documentação
        self.update_documentation()
    
    def update_documentation(self):
        """3. ATUALIZA DOCUMENTAÇÃO"""
        print("\n📖 ATUALIZANDO DOCUMENTAÇÃO")
        print("=" * 50)
        
        # Atualiza README
        self.update_readme()
        
        # Atualiza roadmap
        self.update_roadmap()
        
        # Atualiza checklist geral
        self.update_general_checklist()
        
        print("✅ Documentação atualizada!")
    
    def update_readme(self):
        """Atualiza README"""
        readme_file = self.project_root / "README.md"
        if not readme_file.exists():
            return
        
        # Gera seção de status
        total = len(self.checklists)
        critical = sum(1 for c in self.checklists.values() if 'Crítico' in c['priority'])
        progress = sum(c['progress'] for c in self.checklists.values()) / total if total > 0 else 0
        
        status_section = f"""
## 📊 Status do Projeto

- **Checklists:** {total}
- **Críticos:** {critical}
- **Progresso:** {progress:.1f}%

*Atualizado em {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        print("📝 SEÇÃO PARA README:")
        print(status_section)
    
    def update_roadmap(self):
        """Atualiza roadmap"""
        critical, important, nice = self.analyze_by_priority()
        
        roadmap_content = f"""# 🗺️ ROADMAP - TarefaMágica

## 🔥 Fase 1 - Crítico
"""
        
        for filename, data in critical:
            roadmap_content += f"- [ ] {data['title']} ({data['progress']}%)\n"
        
        roadmap_content += "\n## ⚡ Fase 2 - Importante\n"
        
        for filename, data in important:
            roadmap_content += f"- [ ] {data['title']} ({data['progress']}%)\n"
        
        # Salva roadmap
        roadmap_file = self.project_root / "ROADMAP.md"
        roadmap_file.write_text(roadmap_content, encoding='utf-8')
        
        print("✅ ROADMAP.md atualizado!")
    
    def update_general_checklist(self):
        """Atualiza checklist geral"""
        general_file = self.checklists_dir / "CHECKLIST_Geral_Validacao.md"
        if not general_file.exists():
            return
        
        content = general_file.read_text(encoding='utf-8')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if '🔄 Última Atualização:' not in content:
            content = content.replace(
                '**📅 Data de Criação:** [Data Atual]',
                f'**📅 Data de Criação:** [Data Atual]\n**🔄 Última Atualização:** {timestamp}'
            )
        else:
            content = re.sub(r'🔄 Última Atualização:.*', f'🔄 Última Atualização: {timestamp}', content)
        
        general_file.write_text(content, encoding='utf-8')
        print("✅ Checklist geral atualizado!")
    
    def prepare_github(self):
        """3. PREPARA GITHUB"""
        print("\n🐙 PREPARANDO GITHUB")
        print("=" * 50)
        
        if not (self.project_root / ".git").exists():
            print("❌ Não é repositório Git!")
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        progress = sum(c['progress'] for c in self.checklists.values()) / len(self.checklists)
        
        commit_message = f"""📊 Atualização de checklists - {timestamp}

✅ Análise automática de progresso
📋 Atualização de checklists
📖 Atualização de documentação
🗺️ Atualização de roadmap

Progresso: {progress:.1f}%
"""
        
        print("📝 MENSAGEM DE COMMIT:")
        print("=" * 30)
        print(commit_message)
        print("=" * 30)
        
        print("\n💡 COMANDOS:")
        print("git add .")
        print("git commit -m \"[MENSAGEM ACIMA]\"")
        print("git push origin main")
    
    def analyze_pending(self):
        """4. ANALISA PENDÊNCIAS"""
        print("\n🔍 ANÁLISE DE PENDÊNCIAS")
        print("=" * 50)
        
        all_pending = []
        for filename, data in self.checklists.items():
            if data['pending_items']:
                all_pending.append({
                    'checklist': data['title'],
                    'priority': data['priority'],
                    'items': data['pending_items']
                })
        
        if not all_pending:
            print("🎉 Nenhuma pendência!")
            return
        
        print("📋 PENDÊNCIAS:")
        for pending in all_pending:
            print(f"\n📄 {pending['checklist']} ({pending['priority']})")
            for item in pending['items']:
                print(f"   • {item}")
        
        # Próxima ação
        if all_pending:
            next_action = all_pending[0]
            print(f"\n🎯 PRÓXIMA AÇÃO:")
            print(f"   {next_action['checklist']}")
            print(f"   {next_action['items'][0]}")
    
    def execute_workflow(self):
        """EXECUTA WORKFLOW COMPLETO"""
        print("🔄 WORKFLOW COMPLETO")
        print("=" * 50)
        
        # 1. Análise por prioridade
        print("1️⃣ ANALISANDO PRIORIDADES...")
        self.analyze_by_priority()
        
        # 2. Próxima ação
        print("\n2️⃣ SUGERINDO PRÓXIMA AÇÃO...")
        self.suggest_next_action()
        
        # 3. Atualiza documentação
        print("\n3️⃣ ATUALIZANDO DOCUMENTAÇÃO...")
        self.update_documentation()
        
        # 4. Analisa pendências
        print("\n4️⃣ ANALISANDO PENDÊNCIAS...")
        self.analyze_pending()
        
        # 5. GitHub
        print("\n5️⃣ PREPARANDO GITHUB...")
        self.prepare_github()
        
        print("\n🎉 WORKFLOW COMPLETO!")
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Implementar ação sugerida")
        print("   2. Atualizar checklists")
        print("   3. Executar: python workflow_ia.py workflow")

    def analyze_checklists(self):
        """Analisa os checklists e extrai informações relevantes."""
        print("🤖 INICIANDO ANÁLISE DE IA")
        print("=" * 50)
        
        if not self.analyzer.scan_checklists():
            return False
            
        # Analisa checklists críticos primeiro
        for checklist in self.analyzer.critical_checklists:
            self._analyze_checklist_tasks(checklist)
            self._analyze_checklist_flow(checklist)
            
        # Depois os importantes
        for checklist in self.analyzer.important_checklists:
            self._analyze_checklist_tasks(checklist)
            self._analyze_checklist_flow(checklist)
            
        return True

    def _analyze_checklist_tasks(self, checklist):
        """Analisa as tarefas de um checklist específico."""
        with open(os.path.join(self.analyzer.checklists_dir, checklist['file']), 'r', encoding='utf-8') as f:
            content = f.readlines()
            
            current_section = None
            for line in content:
                # Identifica seções
                if line.startswith('#'):
                    current_section = line.strip('#').strip()
                    continue
                    
                # Analisa tarefas
                if '- [ ]' in line:  # Tarefa pendente
                    task = {
                        'checklist': checklist['title'],
                        'section': current_section,
                        'description': line.replace('- [ ]', '').strip(),
                        'priority': checklist['priority'],
                        'status': 'pending'
                    }
                    self.tasks_output.append(task)

    def _analyze_checklist_flow(self, checklist):
        """Analisa o fluxo de trabalho de um checklist."""
        with open(os.path.join(self.analyzer.checklists_dir, checklist['file']), 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Identifica padrões de fluxo
            sections = content.split('#')[1:]  # Ignora o conteúdo antes do primeiro #
            
            for section in sections:
                if not section.strip():
                    continue
                    
                # Extrai título e conteúdo
                lines = section.strip().split('\n')
                title = lines[0].strip()
                content = '\n'.join(lines[1:]).strip()
                
                flow = {
                    'checklist': checklist['title'],
                    'section': title,
                    'content': content,
                    'priority': checklist['priority'],
                    'dependencies': self._extract_dependencies(content)
                }
                self.flow_output.append(flow)

    def _extract_dependencies(self, content):
        """Extrai dependências do conteúdo."""
        dependencies = []
        
        # Procura por referências a outros checklists/tarefas
        lines = content.split('\n')
        for line in lines:
            if 'Ver:' in line or 'Ref:' in line or 'Relacionado:' in line:
                dep = line.split(':')[1].strip()
                dependencies.append(dep)
                
        return dependencies

    def save_tasks_analysis(self, output_file='ia_tasks_output.txt'):
        """Salva a análise de tarefas em um arquivo."""
        print(f"\n💾 SALVANDO ANÁLISE DE TAREFAS EM {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("🤖 ANÁLISE DE TAREFAS POR IA\n")
            f.write("=" * 50 + "\n\n")
            
            # Agrupa por prioridade
            for priority in ["🔥", "⚡", "📈"]:
                tasks = [t for t in self.tasks_output if t['priority'] == priority]
                if tasks:
                    f.write(f"\n{priority} TAREFAS {priority}\n")
                    f.write("-" * 30 + "\n")
                    
                    for task in tasks:
                        f.write(f"\n📋 {task['checklist']}")
                        f.write(f"\n   Seção: {task['section']}")
                        f.write(f"\n   Tarefa: {task['description']}\n")
            
            f.write(f"\n\n*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    def save_flow_analysis(self, output_file='ia_flow_output.txt'):
        """Salva a análise de fluxo em um arquivo."""
        print(f"\n💾 SALVANDO ANÁLISE DE FLUXO EM {output_file}")
        
        content = "🤖 ANÁLISE DE FLUXO POR IA\n"
        content += "=" * 50 + "\n\n"
        
        # Agrupa por prioridade
        for priority in ["🔥", "⚡", "📈"]:
            flows = [flow for flow in self.flow_output if flow['priority'] == priority]
            if flows:
                content += f"\n{priority} FLUXOS {priority}\n"
                content += "-" * 30 + "\n"
                
                for flow in flows:
                    content += f"\n📋 {flow['checklist']}"
                    content += f"\n   Seção: {flow['section']}"
                    if flow['dependencies']:
                        content += "\n   Dependências:"
                        for dep in flow['dependencies']:
                            content += f"\n    - {dep}"
                    content += "\n"
        
        content += f"\n\n*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        self.save_output(content, output_file)

    def run_ai_workflow(self, mode=None):
        """Executa o workflow de IA completo."""
        if not self.analyze_checklists():
            return False
            
        if mode == 'ai-tasks' or mode is None:
            self.save_tasks_analysis()
            
        if mode == 'ai-flow' or mode is None:
            self.save_flow_analysis()
            
        print("\n🎉 Análise de IA concluída!")
        return True

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
    print("🎯 WORKFLOW IA - TarefaMágica")
    print("=" * 50)
    
    command = sys.argv[1] if len(sys.argv) > 1 else "workflow"
    
    workflow = WorkflowIA()
    
    if not workflow.scan_checklists():
        return
    
    if command == "analyze":
        workflow.analyze_by_priority()
    elif command == "next":
        workflow.suggest_next_action()
    elif command == "update":
        workflow.update_after_task()
    elif command == "docs":
        workflow.update_documentation()
    elif command == "github":
        workflow.prepare_github()
    elif command == "pending":
        workflow.analyze_pending()
    elif command == "workflow":
        workflow.execute_workflow()
    else:
        print(f"❌ Comando '{command}' não reconhecido!")
        print("💡 Comandos: analyze, next, update, docs, github, pending, workflow")
    
    print(f"\n🎉 Concluído!")

if __name__ == "__main__":
    main() 