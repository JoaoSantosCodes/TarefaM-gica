import os
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARVORE_FILE = os.path.join(ROOT_DIR, 'outputs', 'arvore_projeto.md')
ESTAT_FILE = os.path.join(ROOT_DIR, 'outputs', 'estatisticas_projeto.txt')
IGNORAR = {'.git', 'outputs', '__pycache__', '.idea', '.gradle', '.DS_Store', '.vscode', 'build', '_backup', 'quarentena_duplicidades'}

# Árvore de diretórios em Markdown
def gerar_arvore():
    linhas = ['# Árvore de Diretórios do Projeto\n']
    def listar(path, prefixo=''):
        itens = sorted([i for i in os.listdir(path) if i not in IGNORAR])
        for i, nome in enumerate(itens):
            caminho = os.path.join(path, nome)
            marcador = '└── ' if i == len(itens)-1 else '├── '
            linhas.append(f"{prefixo}{marcador}{nome}")
            if os.path.isdir(caminho):
                novo_prefixo = prefixo + ('    ' if i == len(itens)-1 else '│   ')
                listar(caminho, novo_prefixo)
    linhas.append(os.path.basename(ROOT_DIR) + '/')
    listar(ROOT_DIR)
    with open(ARVORE_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))

# Estatísticas de arquivos
def gerar_estatisticas():
    total_arquivos = 0
    total_pastas = 0
    por_ext = defaultdict(int)
    por_pasta = defaultdict(int)
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # Ignorar pastas indesejadas
        dirnames[:] = [d for d in dirnames if d not in IGNORAR]
        rel_dir = os.path.relpath(dirpath, ROOT_DIR)
        if rel_dir == '.':
            rel_dir = os.path.basename(ROOT_DIR)
        else:
            rel_dir = rel_dir.split(os.sep)[0]
        total_pastas += 1
        for f in filenames:
            ext = os.path.splitext(f)[1].lower() or '[sem extensão]'
            por_ext[ext] += 1
            por_pasta[rel_dir] += 1
            total_arquivos += 1
    with open(ESTAT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Total de arquivos: {total_arquivos}\n")
        f.write(f"Total de pastas: {total_pastas}\n\n")
        f.write("Arquivos por extensão:\n")
        for ext, qtd in sorted(por_ext.items(), key=lambda x: -x[1]):
            f.write(f"  {ext}: {qtd}\n")
        f.write("\nArquivos por pasta principal:\n")
        for pasta, qtd in sorted(por_pasta.items(), key=lambda x: -x[1]):
            f.write(f"  {pasta}: {qtd}\n")

if __name__ == '__main__':
    gerar_arvore()
    gerar_estatisticas()
    print(f"Relatórios gerados em: {ARVORE_FILE} e {ESTAT_FILE}") 