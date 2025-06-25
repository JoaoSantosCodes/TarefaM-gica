import os
import shutil
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUGESTOES_FILE = os.path.join(ROOT_DIR, 'outputs', 'sugestoes_limpeza.txt')
LOG_FILE = os.path.join(ROOT_DIR, 'outputs', 'log_quarentena.txt')
QUARENTENA = os.path.join(ROOT_DIR, 'quarentena_duplicidades')

if not os.path.exists(QUARENTENA):
    os.makedirs(QUARENTENA)

is_windows = os.name == 'nt'

with open(SUGESTOES_FILE, encoding='utf-8') as f:
    lines = f.readlines()

executando = False
for line in lines:
    line = line.strip()
    if is_windows and line.startswith('--- Windows ---'):
        executando = True
        continue
    elif not is_windows and line.startswith('--- Unix/Linux ---'):
        executando = True
        continue
    elif line.startswith('---'):
        executando = False
        continue
    if executando and line and not line.startswith('#'):
        # Extrai origem e destino do comando
        if is_windows:
            if line.startswith('move '):
                partes = line.split('move ')[1].split('&&')[0].strip().split('"')
                origem = partes[1]
                destino = partes[3]
            else:
                continue
        else:
            if line.startswith('mv '):
                partes = line.split('mv ')[1].split('&&')[0].strip().split('"')
                origem = partes[1]
                destino = partes[3]
            else:
                continue
        abs_origem = os.path.join(ROOT_DIR, origem)
        abs_destino = os.path.join(ROOT_DIR, destino)
        tipo = 'pasta' if os.path.isdir(abs_origem) else 'arquivo'
        try:
            shutil.move(abs_origem, abs_destino)
            msg = f"[{datetime.now().isoformat()}] {tipo.upper()} | {origem} -> {destino} | SUCESSO"
            print(f"Movido: {origem} -> {destino}")
        except Exception as e:
            msg = f"[{datetime.now().isoformat()}] {tipo.upper()} | {origem} -> {destino} | ERRO: {e}"
            print(f"ERRO ao mover {origem}: {e}")
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(msg + '\n') 