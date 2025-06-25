import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUPLICIDADES_FILE = os.path.join(ROOT_DIR, 'outputs', 'duplicidades_relevantes.txt')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'outputs', 'sugestoes_limpeza.txt')
LOG_FILE = os.path.join(ROOT_DIR, 'outputs', 'log_quarentena.txt')
QUARENTENA = os.path.join(ROOT_DIR, 'quarentena_duplicidades')

# Palavras-chave para ignorar sugestões de limpeza
IGNORAR = [
    'build', 'intermediates', 'tmp', 'output', 'apk', 'dex', 'kotlin', 'classes', 'jar', 'bin',
    'test', 'tests', 'androidTest', 'unit', 'mock',
    'backup', '_backup',
    'docs', 'doc', 'resumo', 'guide', 'manual',
    'scripts', 'script',
    'README', 'readme',
    'template', 'example',
    'outputs',
]

# Função para decidir se deve sugerir limpeza
def deve_sugerir(path):
    p = path.lower()
    return not any(word in p for word in IGNORAR)

def tipo_arquivo_ou_pasta(path):
    abs_path = os.path.join(ROOT_DIR, path)
    if os.path.isdir(abs_path):
        return 'pasta'
    elif os.path.isfile(abs_path):
        return 'arquivo'
    else:
        # Se não existe, tentar inferir pelo sufixo
        return 'arquivo' if '.' in os.path.basename(path) else 'pasta'

def log_movimentacao(origem, destino, tipo):
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now().isoformat()}] {tipo.upper()} | {origem} -> {destino}\n")

sugestoes_win = []
sugestoes_unix = []
with open(DUPLICIDADES_FILE, encoding='utf-8') as f:
    lines = f.readlines()

current = None
for line in lines:
    if line.startswith('- '):
        current = line[2:].split('(')[0].strip()
        paths = []
    elif line.startswith('    - '):
        path = line.strip()[2:]
        if deve_sugerir(path):
            paths.append(path)
    elif line.strip().startswith('> Recomenda-se') and paths:
        for p in paths[1:]:
            tipo = tipo_arquivo_ou_pasta(p)
            # Windows
            dest_win = os.path.join('quarentena_duplicidades', os.path.normpath(p).replace(os.sep, '_'))
            if tipo == 'pasta':
                cmd_win = f'move "{p}" "{dest_win}" && echo Pasta movida: {p} -> {dest_win} || echo ERRO ao mover pasta: {p}'
            else:
                cmd_win = f'move "{p}" "{dest_win}" && echo Arquivo movido: {p} -> {dest_win} || echo ERRO ao mover arquivo: {p}'
            sugestoes_win.append(f'# {current}: Mover {tipo} para quarentena (Windows). Revise antes de executar!')
            sugestoes_win.append(cmd_win)
            # Unix/Linux
            dest_unix = f'quarentena_duplicidades/{p.replace(os.sep, "_")}'
            if tipo == 'pasta':
                cmd_unix = f'mv "{p}" "{dest_unix}" && echo "Pasta movida: {p} -> {dest_unix}" || echo "ERRO ao mover pasta: {p}"'
            else:
                cmd_unix = f'mv "{p}" "{dest_unix}" && echo "Arquivo movido: {p} -> {dest_unix}" || echo "ERRO ao mover arquivo: {p}"'
            sugestoes_unix.append(f'# {current}: Mover {tipo} para quarentena (Unix/Linux). Revise antes de executar!')
            sugestoes_unix.append(cmd_unix)
            # Log sugerido
            log_movimentacao(p, dest_win, tipo)
        paths = []

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    out.write('''INSTRUÇÕES:
- Estas sugestões movem duplicidades manuais para a pasta "quarentena_duplicidades" (NÃO DELETAM nada).
- Revise cada comando antes de executar.
- Execute apenas se tiver certeza de que não perderá dados importantes.
- Todos os comandos geram saída de sucesso/erro para facilitar integração em CI/CD.
- Um log de movimentação sugerida é salvo em outputs/log_quarentena.txt.
- Crie a pasta "quarentena_duplicidades" na raiz do projeto antes de executar.

''')
    out.write('--- Windows ---\n')
    if sugestoes_win:
        out.write('\n'.join(sugestoes_win))
    else:
        out.write('Nenhuma sugestão para Windows.\n')
    out.write('\n\n--- Unix/Linux ---\n')
    if sugestoes_unix:
        out.write('\n'.join(sugestoes_unix))
    else:
        out.write('Nenhuma sugestão para Unix/Linux.\n')

print(f'Sugestões de limpeza/movimentação geradas em: {OUTPUT_FILE}') 