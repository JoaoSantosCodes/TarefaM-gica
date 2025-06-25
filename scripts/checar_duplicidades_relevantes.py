import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST_FILE = os.path.join(ROOT_DIR, 'outputs', 'checklist_estrutura.txt')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'outputs', 'duplicidades_relevantes.txt')

# Critérios de relevância por palavras-chave
RELEVANCIA = {
    'código-fonte': ['src', 'main', 'app', 'data', 'presentation', 'tasks', 'auth', 'api', 'repository', 'service', 'model', 'viewmodel'],
    'configuração': ['config', 'settings', 'gradle', 'properties', 'manifest', 'yaml', 'json', 'ini'],
    'documentação': ['docs', 'readme', 'doc', 'resumo', 'guide', 'manual'],
    'teste': ['test', 'tests', 'androidTest', 'unit', 'mock'],
    'backup': ['backup', '_backup'],
    'build': ['build', 'intermediates', 'tmp', 'output', 'apk', 'dex', 'kotlin', 'classes', 'jar', 'bin'],
    'scripts': ['scripts', 'py', 'sh', 'bat'],
}

# Função para classificar relevância
def classificar(paths):
    relevancias = set()
    for p in paths:
        p_lower = p.lower()
        for tipo, palavras in RELEVANCIA.items():
            if any(word in p_lower for word in palavras):
                relevancias.add(tipo)
    return list(relevancias) if relevancias else ['outro']

# Lê duplicidades do checklist
duplicidades = {}
with open(CHECKLIST_FILE, encoding='utf-8') as f:
    lines = f.readlines()

# Busca início das seções
for i, line in enumerate(lines):
    if line.strip() == 'Pastas Duplicadas:':
        start = i + 1
        break
else:
    start = len(lines)

# Extrai duplicidades
current = None
for line in lines[start:]:
    if line.startswith('- '):
        current = line[2:].split(':')[0].strip()
        duplicidades[current] = []
    elif line.startswith('    - '):
        duplicidades[current].append(line.strip()[2:])

# Classifica e destaca duplicidades relevantes
relatorio = []
relatorio.append('Relatório de Duplicidades Relevantes\n')
relatorio.append('='*40 + '\n')
for nome, paths in duplicidades.items():
    if not paths:
        continue
    relev = classificar(paths)
    critico = any(r in ['código-fonte', 'configuração', 'scripts'] for r in relev)
    relatorio.append(f"- {nome} ({', '.join(relev)}){' [CRÍTICO]' if critico else ''}:")
    for p in paths:
        relatorio.append(f"    - {p}")
    if critico:
        relatorio.append("    > Recomenda-se revisar e evitar múltiplas versões deste item no projeto principal!")
    relatorio.append('')

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    out.write('\n'.join(relatorio))

print(f"Relatório de duplicidades relevantes gerado em: {OUTPUT_FILE}") 