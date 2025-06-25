import os
import sqlite3
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs')
DB_PATH = os.path.join(OUTPUTS_DIR, 'relatorios_projeto.db')
SQL_EXEMPLO = os.path.join(OUTPUTS_DIR, 'consultas_exemplo.sql')

IGNORAR = {'relatorios_projeto.db', 'consultas_exemplo.sql'}
TIPOS = {
    '.md': 'checklist',
    '.txt': 'relatorio',
    '.log': 'log',
    '.json': 'json',
    '.csv': 'csv',
    '.xml': 'xml',
}

def detectar_tipo(nome):
    ext = os.path.splitext(nome)[1].lower()
    if ext in TIPOS:
        return TIPOS[ext]
    if 'checklist' in nome:
        return 'checklist'
    if 'log' in nome:
        return 'log'
    if 'estatistica' in nome:
        return 'estatistica'
    if 'duplicidade' in nome:
        return 'duplicidade'
    if 'arvore' in nome:
        return 'estrutura'
    return 'outro'

def criar_tabela(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        tipo TEXT,
        data TEXT,
        conteudo TEXT,
        origem TEXT
    )''')
    conn.commit()

def importar_todos(conn):
    arquivos = [f for f in os.listdir(OUTPUTS_DIR) if os.path.isfile(os.path.join(OUTPUTS_DIR, f)) and f not in IGNORAR]
    for nome in arquivos:
        path = os.path.join(OUTPUTS_DIR, nome)
        with open(path, encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
        data = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
        tipo = detectar_tipo(nome)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO documentos (nome, tipo, data, conteudo, origem) VALUES (?, ?, ?, ?, ?)''',
                  (nome, tipo, data, conteudo, 'outputs'))
        print(f"Importado: {nome} ({tipo})")
    conn.commit()

def gerar_consultas_exemplo():
    with open(SQL_EXEMPLO, 'w', encoding='utf-8') as f:
        f.write('-- Exemplos de consultas para relatorios_projeto.db\n')
        f.write('SELECT nome, tipo, data FROM documentos ORDER BY data DESC LIMIT 10;\n')
        f.write('SELECT nome, data FROM documentos WHERE tipo = "checklist" ORDER BY data DESC;\n')
        f.write('SELECT nome, data FROM documentos WHERE tipo = "relatorio" ORDER BY data DESC;\n')
        f.write('SELECT COUNT(*) FROM documentos WHERE tipo = "log";\n')
        f.write('SELECT * FROM documentos WHERE nome LIKE "%duplicidade%";\n')

def main():
    conn = sqlite3.connect(DB_PATH)
    criar_tabela(conn)
    importar_todos(conn)
    conn.close()
    gerar_consultas_exemplo()
    print(f"\nBanco atualizado: {DB_PATH}")
    print(f"Consultas de exemplo em: {SQL_EXEMPLO}")

if __name__ == '__main__':
    main() 