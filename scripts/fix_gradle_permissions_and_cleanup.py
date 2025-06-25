import os
import shutil
import getpass
import ctypes
from pathlib import Path

# Função para apagar a pasta gradle-8.4-bin

def delete_gradle_bin():
    gradle_bin = Path.home() / ".gradle" / "wrapper" / "dists" / "gradle-8.4-bin"
    if gradle_bin.exists():
        try:
            shutil.rmtree(gradle_bin)
            print(f"✅ Pasta removida: {gradle_bin}")
        except Exception as e:
            print(f"❌ Erro ao remover {gradle_bin}: {e}")
    else:
        print(f"ℹ️ Pasta não existe: {gradle_bin}")

# Função para garantir permissão total na pasta .gradle (Windows)
def set_permissions_windows():
    gradle_path = str(Path.home() / ".gradle")
    user = os.getlogin()
    print(f"🔒 Garantindo permissão total para o usuário {user} em {gradle_path} ...")
    try:
        # Executa icacls para permissão total recursiva
        os.system(f'icacls "{gradle_path}" /grant "{user}:(OI)(CI)F" /T')
        print("✅ Permissões aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao aplicar permissões: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    print("=== Fix Gradle Permissions and Cleanup ===\n")
    if os.name != 'nt':
        print("❌ Este script só funciona no Windows.")
        return
    if not is_admin():
        print("⚠️  Execute este script como administrador!")
        return
    delete_gradle_bin()
    set_permissions_windows()
    print("\n🎯 Agora abra o Android Studio como administrador e tente sincronizar/buildar novamente.")
    print("Se o erro persistir, tente mudar o diretório do Gradle Home nas configurações do Android Studio.")

if __name__ == "__main__":
    main() 