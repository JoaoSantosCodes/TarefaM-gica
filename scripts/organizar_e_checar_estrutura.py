import os
from collections import defaultdict
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, 'outputs', 'checklist_estrutura.txt')
IGNORED_DIRS = {'.git', 'outputs', '__pycache__', '.idea', '.gradle', '.DS_Store', '.vscode'}

# Dicionários para checagem de duplicidade
file_names = defaultdict(list)
dir_names = defaultdict(list)

checklist = []

for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
    # Ignorar diretórios indesejados
    dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
    rel_dir = os.path.relpath(dirpath, ROOT_DIR)
    if rel_dir == '.':
        rel_dir = ''
    # Listar diretórios
    for d in dirnames:
        dir_names[d].append(os.path.join(rel_dir, d))
        checklist.append(f"[DIR]  {os.path.join(rel_dir, d)}")
    # Listar arquivos
    for f in filenames:
        file_names[f].append(os.path.join(rel_dir, f))
        checklist.append(f"[FILE] {os.path.join(rel_dir, f)}")

# Checar duplicidades
duplicated_files = {k: v for k, v in file_names.items() if len(v) > 1}
duplicated_dirs = {k: v for k, v in dir_names.items() if len(v) > 1}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    out.write("Checklist de Estrutura do Projeto\n")
    out.write("="*40 + "\n\n")
    out.write("Pastas e Arquivos:\n")
    for item in checklist:
        out.write(item + '\n')
    out.write("\nArquivos Duplicados:\n")
    if duplicated_files:
        for name, paths in duplicated_files.items():
            out.write(f"- {name}:\n")
            for p in paths:
                out.write(f"    - {p}\n")
    else:
        out.write("Nenhum arquivo duplicado encontrado.\n")
    out.write("\nPastas Duplicadas:\n")
    if duplicated_dirs:
        for name, paths in duplicated_dirs.items():
            out.write(f"- {name}:\n")
            for p in paths:
                out.write(f"    - {p}\n")
    else:
        out.write("Nenhuma pasta duplicada encontrada.\n")

print(f"Checklist de estrutura gerado em: {OUTPUT_FILE}")

# Ao final, gerar árvore de diretórios e estatísticas
subprocess.run(['python', 'scripts/relatorio_visual_estrutura.py'], check=False) 