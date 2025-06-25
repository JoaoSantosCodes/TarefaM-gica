#!/usr/bin/env python3
"""
Script final para aguardar emulador e instalar APK
TarefaMagica - Final Setup
"""

import os
import subprocess
import time
from pathlib import Path

def wait_for_emulator(max_wait=600):
    """Aguarda o emulador ficar disponível (10 minutos)"""
    print("[WAIT] Aguardando emulador ficar disponível...")
    print("[INFO] Isso pode demorar até 10 minutos na primeira inicialização")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    adb = sdk_path / "platform-tools" / "adb.exe"
    
    if not adb.exists():
        print("[ERROR] ADB não encontrado")
        return False
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            result = subprocess.run([str(adb), "devices"], 
                                  capture_output=True, text=True, timeout=10)
            
            if "emulator" in result.stdout:
                print("[SUCCESS] Emulador detectado!")
                print(f"[INFO] Dispositivos: {result.stdout.strip()}")
                return True
            
            elapsed = int(time.time() - start_time)
            print(f"[WAIT] Aguardando... ({elapsed}s / {max_wait}s)")
            time.sleep(30)  # Verifica a cada 30 segundos
            
        except Exception as e:
            print(f"[ERROR] Erro ao verificar emulador: {e}")
            time.sleep(30)
    
    print("[ERROR] Timeout aguardando emulador")
    print("[INFO] O emulador pode estar demorando mais do que o esperado")
    print("[INFO] Verifique se a janela do emulador apareceu")
    return False

def install_apk(apk_path):
    """Instala APK no emulador"""
    print(f"[INSTALL] Instalando APK: {apk_path}")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    adb = sdk_path / "platform-tools" / "adb.exe"
    
    if not Path(apk_path).exists():
        print(f"[ERROR] APK não encontrada: {apk_path}")
        return False
    
    try:
        # Instala APK
        install_cmd = [str(adb), "install", "-r", apk_path]
        result = subprocess.run(install_cmd, 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[SUCCESS] APK instalada com sucesso!")
            return True
        else:
            print(f"[ERROR] Erro ao instalar APK: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao instalar APK: {e}")
        return False

def launch_app():
    """Abre o app TarefaMágica"""
    print("[LAUNCH] Abrindo app TarefaMágica...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    adb = sdk_path / "platform-tools" / "adb.exe"
    
    try:
        # Comando para abrir o app
        launch_cmd = [
            str(adb), "shell", "am", "start", 
            "-n", "com.tarefamagica.app/.MainActivity"
        ]
        
        result = subprocess.run(launch_cmd, 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[SUCCESS] App TarefaMágica aberto!")
            return True
        else:
            print(f"[ERROR] Erro ao abrir app: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao abrir app: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Setup Final")
    print("=" * 60)
    
    apk_path = "TarefaMagica-debug.apk"
    
    # Passo 1: Aguardar emulador
    print("\n[STEP 1] Aguardando emulador...")
    if not wait_for_emulator():
        print("\n[ERROR] Emulador não ficou disponível")
        print("[INFO] Verifique se:")
        print("  1. A janela do emulador apareceu")
        print("  2. O emulador carregou completamente")
        print("  3. A tela inicial do Android está visível")
        return False
    
    # Passo 2: Instalar APK
    print("\n[STEP 2] Instalando APK...")
    if not install_apk(apk_path):
        print("\n[ERROR] Falha ao instalar APK")
        return False
    
    # Passo 3: Abrir app
    print("\n[STEP 3] Abrindo app...")
    if not launch_app():
        print("\n[WARNING] Não foi possível abrir o app automaticamente")
        print("[INFO] Abra o app manualmente no emulador")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] TarefaMágica configurado com sucesso!")
    print("=" * 60)
    print("\n[CELEBRATION] 🎉 Parabéns! O app está funcionando!")
    print("\n[NEXT] Próximos passos:")
    print("1. O app TarefaMágica está instalado e aberto")
    print("2. Teste as funcionalidades básicas")
    print("3. Verifique se a interface está funcionando")
    print("4. Explore o app no emulador")
    
    return True

if __name__ == "__main__":
    main() 