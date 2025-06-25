import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST = os.path.join(ROOT_DIR, 'outputs', 'checklist_estrutura.txt')
DUPLICIDADES = os.path.join(ROOT_DIR, 'outputs', 'duplicidades_relevantes.txt')
LOG_QUARENTENA = os.path.join(ROOT_DIR, 'outputs', 'log_quarentena.txt')
RELATORIO = os.path.join(ROOT_DIR, 'outputs', 'relatorio_validacao_organizacao.txt')

arquivos_soltos = []
pastas_vazias = []
duplicidades_criticas = []
sugestoes = []

# 1. Arquivos soltos na raiz
def checar_arquivos_soltos():
    with open(CHECKLIST, encoding='utf-8') as f:
        for line in f:
            if line.startswith('[FILE] '):
                path = line.split(' ', 1)[1].strip()
                if os.sep not in path and '/' not in path:
                    arquivos_soltos.append(path)

def checar_pastas_vazias():
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # Ignorar pastas internas do sistema/projeto
        rel = os.path.relpath(dirpath, ROOT_DIR)
        if rel == '.' or rel.startswith('outputs') or rel.startswith('.') or rel.startswith('_backup') or rel.startswith('build') or rel.startswith('quarentena_duplicidades'):
            continue
        if not dirnames and not filenames:
            pastas_vazias.append(rel)

def checar_duplicidades_criticas():
    with open(DUPLICIDADES, encoding='utf-8') as f:
        bloco = []
        critico = False
        for line in f:
            if '[CRÍTICO]' in line:
                critico = True
                bloco = [line.strip()]
            elif line.strip() == '' and critico:
                duplicidades_criticas.append('\n'.join(bloco))
                critico = False
                bloco = []
            elif critico:
                bloco.append(line.strip())

def gerar_sugestoes():
    if arquivos_soltos:
        sugestoes.append('Mover arquivos soltos na raiz para pastas temáticas apropriadas.')
    if pastas_vazias:
        sugestoes.append('Remover ou utilizar pastas vazias para evitar confusão.')
    if duplicidades_criticas:
        sugestoes.append('Resolver duplicidades críticas listadas abaixo.')
    if not (arquivos_soltos or pastas_vazias or duplicidades_criticas):
        sugestoes.append('Estrutura do projeto está bem organizada!')

def gerar_relatorio():
    with open(RELATORIO, 'w', encoding='utf-8') as f:
        f.write('Relatório de Validação da Organização do Projeto\n')
        f.write('='*50 + '\n\n')
        f.write('Arquivos soltos na raiz:\n')
        if arquivos_soltos:
            for a in arquivos_soltos:
                f.write(f'  - {a}\n')
        else:
            f.write('  Nenhum arquivo solto encontrado.\n')
        f.write('\nPastas vazias:\n')
        if pastas_vazias:
            for p in pastas_vazias:
                f.write(f'  - {p}\n')
        else:
            f.write('  Nenhuma pasta vazia encontrada.\n')
        f.write('\nDuplicidades críticas não resolvidas:\n')
        if duplicidades_criticas:
            for d in duplicidades_criticas:
                f.write(d + '\n\n')
        else:
            f.write('  Nenhuma duplicidade crítica não resolvida.\n')
        f.write('\nSugestões de melhoria:\n')
        for s in sugestoes:
            f.write(f'- {s}\n')

def resumo_terminal():
    print('\n==== Validação da Organização do Projeto ====')
    if arquivos_soltos:
        print(f"Arquivos soltos na raiz: {len(arquivos_soltos)} (veja relatório)")
    else:
        print("Nenhum arquivo solto na raiz.")
    if pastas_vazias:
        print(f"Pastas vazias: {len(pastas_vazias)} (veja relatório)")
    else:
        print("Nenhuma pasta vazia.")
    if duplicidades_criticas:
        print(f"Duplicidades críticas não resolvidas: {len(duplicidades_criticas)} (veja relatório)")
    else:
        print("Nenhuma duplicidade crítica não resolvida.")
    print('Sugestões principais:')
    for s in sugestoes:
        print(f'- {s}')
    print(f'\nRelatório completo: {RELATORIO}')

if __name__ == '__main__':
    checar_arquivos_soltos()
    checar_pastas_vazias()
    checar_duplicidades_criticas()
    gerar_sugestoes()
    gerar_relatorio()
    resumo_terminal() 