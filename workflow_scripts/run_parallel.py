import os
import sys
import threading
import subprocess
from datetime import datetime

def run_command(command, output_file=None):
    """Executa um comando e redireciona a saída para um arquivo."""
    try:
        # Configura o ambiente para UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Executa o comando
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE if output_file else None,
            stderr=subprocess.STDOUT if output_file else None,
            shell=True,
            env=env,
            text=True,
            encoding='utf-8'
        )
        
        # Se tiver arquivo de saída, redireciona
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in process.stdout:
                    f.write(line)
                    
        process.wait()
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ ERRO ao executar '{command}': {str(e)}")
        return False

def run_workflows():
    """Executa os workflows em paralelo."""
    print("\n🎯 EXECUÇÃO PARALELA - TarefaMágica")
    print("=" * 50)
    print(f"\n⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de comandos e seus arquivos de saída
    commands = [
        ("python tarefamagica_workflow.py base analyze", "base_output.txt"),
        ("python tarefamagica_workflow.py ia ai-tasks", "ia_tasks_output.txt"),
        ("python tarefamagica_workflow.py ia ai-flow", "ia_flow_output.txt")
    ]
    
    # Cria e inicia as threads
    threads = []
    for cmd, output in commands:
        thread = threading.Thread(
            target=run_command,
            args=(cmd, output)
        )
        threads.append(thread)
        thread.start()
        print(f"🚀 Iniciando: {cmd}")
    
    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 RESULTADOS:")
    print("=" * 50)
    
    # Verifica os resultados
    all_success = True
    for output_file in ["base_output.txt", "ia_tasks_output.txt", "ia_flow_output.txt"]:
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            if size > 0:
                print(f"✅ {output_file} gerado com sucesso ({size} bytes)")
            else:
                print(f"⚠️ {output_file} está vazio")
                all_success = False
        else:
            print(f"❌ {output_file} não foi gerado")
            all_success = False
    
    if all_success:
        print("\n🎉 Todos os workflows concluídos com sucesso!")
    else:
        print("\n⚠️ Alguns workflows podem ter falhado. Verifique os arquivos de saída.")

if __name__ == "__main__":
    # Configura encoding para Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Muda para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executa os workflows
    run_workflows() 