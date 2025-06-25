import os
from pathlib import Path
from datetime import datetime
import re

def read_file(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return f.read()
    return f"[Arquivo não encontrado: {path}]\n"

def extract_checklist_items(text):
    # Extrai itens marcados e não marcados
    checked = re.findall(r'- \[x\] (.+)', text)
    unchecked = re.findall(r'- \[ \] (.+)', text)
    return checked, unchecked

def checklist_area_report(area, filename):
    content = read_file(filename)
    checked, unchecked = extract_checklist_items(content)
    total = len(checked) + len(unchecked)
    pct = int(100 * len(checked) / total) if total else 0
    report = [f'# Relatório da Área: {area}\n']
    report.append(f'Progresso: {len(checked)}/{total} itens concluídos ({pct}%)\n')
    report.append('---\nItens Concluídos:\n')
    for item in checked:
        report.append(f'- [x] {item}')
    report.append('\nItens Pendentes:\n')
    for item in unchecked:
        report.append(f'- [ ] {item}')
    return '\n'.join(report), unchecked

def parse_checklist_progress(text):
    # Extrai blocos de prioridade e itens
    progress = {'Crítico': [], 'Importante': [], 'Nice-to-Have': []}
    current = None
    for line in text.splitlines():
        if 'CRÍTICO' in line.upper():
            current = 'Crítico'
        elif 'IMPORTANTE' in line.upper():
            current = 'Importante'
        elif 'NICE-TO-HAVE' in line.upper():
            current = 'Nice-to-Have'
        elif line.strip().startswith('|') and current:
            # Tabela de matriz de priorização
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) >= 4 and parts[0] != 'Checklist':
                status = parts[1]
                progresso = parts[2]
                acao = parts[3]
                progress[current].append({
                    'nome': parts[0],
                    'status': status,
                    'progresso': progresso,
                    'acao': acao
                })
    return progress

def checklist_percent(progress):
    # Calcula % concluído por prioridade
    def pct(lst):
        if not lst:
            return 0
        concl = sum(1 for i in lst if '100%' in i['progresso'] or '✅' in i['status'])
        return int(100 * concl / len(lst))
    return {k: pct(v) for k, v in progress.items()}

def principais_pendencias(progress):
    pend = []
    for k in ['Crítico', 'Importante', 'Nice-to-Have']:
        for i in progress[k]:
            if not ('100%' in i['progresso'] or '✅' in i['status']):
                pend.append(f"- [ ] {i['acao']} ({i['nome']} - {k})")
    return pend

def proximas_acoes(progress):
    # Lista as próximas ações recomendadas (primeiro as críticas)
    acoes = []
    for k in ['Crítico', 'Importante', 'Nice-to-Have']:
        for i in progress[k]:
            if not ('100%' in i['progresso'] or '✅' in i['status']):
                acoes.append(i['acao'])
    return acoes[:5]

# Caminhos dos arquivos
DOCS = {
    'visao_geral': 'docs/ia/README.md',
    'estrutura': 'docs/ia/STRUCTURE.md',
    'workflow': 'docs/ia/WORKFLOW.md',
    'exemplos': 'docs/ia/EXAMPLES.md',
    'contexto': 'docs/ia/CONTEXT.md',
    'checklist_geral': 'checklists/CHECKLIST_Geral_Validacao.md',
}

CHECKLISTS_AREAS = {
    'seguranca': 'checklists/CHECKLIST_Seguranca.md',
    'financeiro': 'checklists/CHECKLIST_Financeiro.md',
    'testes': 'checklists/CHECKLIST_Testes.md',
    'deploy': 'checklists/CHECKLIST_Deploy.md',
    'devops': 'checklists/CHECKLIST_DevOps.md',
}

OUTPUTS_DIR = 'outputs'
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Lê conteúdos
conteudo = {k: read_file(v) for k, v in DOCS.items()}

# Relatórios por área e pendências críticas
pendencias_criticas = []
for area, filename in CHECKLISTS_AREAS.items():
    report, unchecked = checklist_area_report(area.capitalize(), filename)
    with open(os.path.join(OUTPUTS_DIR, f'relatorio_{area}.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
    # Notificação de pendências críticas: só as que aparecem em áreas críticas
    if area in ['seguranca', 'financeiro', 'testes']:
        for item in unchecked:
            pendencias_criticas.append(f'{area.capitalize()}: {item}')

with open(os.path.join(OUTPUTS_DIR, 'pendencias_criticas.txt'), 'w', encoding='utf-8') as f:
    if pendencias_criticas:
        f.write('\n'.join(pendencias_criticas))
    else:
        f.write('Nenhuma pendência crítica nas áreas principais!')

# Analisa progresso dos checklists gerais
progress = parse_checklist_progress(conteudo['checklist_geral'])
pct = checklist_percent(progress)
pendencias = principais_pendencias(progress)
acoes = proximas_acoes(progress)

datahora = datetime.now().strftime('%Y-%m-%d %H:%M')

# Gera o arquivo único consolidado
summary = []
summary.append(f'# Relatório Consolidado do Projeto TarefaMágica\nGerado em: {datahora}\n')
summary.append('---\n## Progresso Geral\n')
summary.append(f"- Itens críticos concluídos: {pct['Crítico']}%\n- Itens importantes concluídos: {pct['Importante']}%\n- Itens nice-to-have concluídos: {pct['Nice-to-Have']}%\n")
summary.append('---\n## Pendências Críticas por Área\n')
if pendencias_criticas:
    summary.extend([f'- {p}' for p in pendencias_criticas])
else:
    summary.append('Nenhuma pendência crítica nas áreas principais!')
summary.append('\n---\n## Principais Pendências Críticas (Matriz Geral)\n')
if pendencias:
    summary.extend(pendencias[:5])
else:
    summary.append('Nenhuma pendência crítica!')
summary.append('\n---\n## Próximas Ações Recomendadas\n')
if acoes:
    for i, ac in enumerate(acoes, 1):
        summary.append(f"{i}. {ac}")
else:
    summary.append('Nenhuma ação pendente!')
summary.append('\n---\n## Estrutura do Projeto\n')
summary.append(conteudo['estrutura'])
summary.append('\n---\n## Workflow e Fluxos\n')
summary.append(conteudo['workflow'])
summary.append('\n---\n## Exemplos Práticos\n')
summary.append(conteudo['exemplos'])
summary.append('\n---\n## Contexto e Diretrizes\n')
summary.append(conteudo['contexto'])

with open(os.path.join(OUTPUTS_DIR, 'project_summary.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary))

# Atualiza base_output.txt
base_output = []
base_output.append(f'=== Estado Geral do Projeto ===\nGerado em: {datahora}\n')
base_output.append(f"- Progresso Crítico: {pct['Crítico']}%\n- Progresso Importante: {pct['Importante']}%\n- Progresso Nice-to-Have: {pct['Nice-to-Have']}%\n")
base_output.append('\nPendências Críticas por Área:\n')
if pendencias_criticas:
    base_output.extend([f'- {p}' for p in pendencias_criticas])
else:
    base_output.append('Nenhuma pendência crítica nas áreas principais!')
base_output.append('\nPendências Críticas (Matriz Geral):\n')
base_output.extend(pendencias[:5])
base_output.append('\nPróximas Ações:\n')
for i, ac in enumerate(acoes, 1):
    base_output.append(f"{i}. {ac}")
base_output.append('\nResumo do Projeto:\n')
base_output.append(conteudo['visao_geral'])
with open(os.path.join(OUTPUTS_DIR, 'base_output.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(base_output))

# Atualiza ia_tasks_output.txt
ia_tasks_output = []
ia_tasks_output.append(f'=== Tarefas de IA Sugeridas ===\nGerado em: {datahora}\n')
ia_tasks_output.append(conteudo['exemplos'])
ia_tasks_output.append('\nContexto e Diretrizes para IA:\n')
ia_tasks_output.append(conteudo['contexto'])
with open(os.path.join(OUTPUTS_DIR, 'ia_tasks_output.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(ia_tasks_output))

# Atualiza ia_flow_output.txt
ia_flow_output = []
ia_flow_output.append(f'=== Fluxos e Workflow de IA ===\nGerado em: {datahora}\n')
ia_flow_output.append(conteudo['workflow'])
ia_flow_output.append('\nEstrutura do Projeto:\n')
ia_flow_output.append(conteudo['estrutura'])
with open(os.path.join(OUTPUTS_DIR, 'ia_flow_output.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(ia_flow_output))

print('Relatórios por área, pendências críticas e outputs detalhados gerados com sucesso!') 