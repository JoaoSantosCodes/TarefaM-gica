#!/usr/bin/env python3
"""
Script para instalar APK automaticamente no emulador
TarefaMagica - APK Auto Installer
"""

import os
import subprocess
import time
from pathlib import Path

def wait_for_emulator(max_wait=300):
    """Aguarda o emulador ficar disponível"""
    print("[WAIT] Aguardando emulador ficar disponível...")
    
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
                print("[OK] Emulador detectado!")
                return True
            
            print(f"[WAIT] Aguardando... ({int(time.time() - start_time)}s)")
            time.sleep(10)
            
        except Exception as e:
            print(f"[ERROR] Erro ao verificar emulador: {e}")
            time.sleep(10)
    
    print("[ERROR] Timeout aguardando emulador")
    return False

def install_apk(apk_path):
    """Instala APK no emulador"""
    print(f"[INSTALL] Instalando APK: {apk_path}")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    adb = sdk_path / "platform-tools" / "adb.exe"
    
    if not adb.exists():
        print("[ERROR] ADB não encontrado")
        return False
    
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
            print("[INFO] Você pode abrir o app TarefaMágica no emulador")
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
    print("TarefaMágica - Instalador Automático de APK")
    print("=" * 60)
    
    apk_path = "TarefaMagica-debug.apk"
    
    # Passo 1: Aguardar emulador
    if not wait_for_emulator():
        print("\n[ERROR] Emulador não ficou disponível")
        print("[INFO] Verifique se o emulador está rodando")
        return False
    
    # Passo 2: Instalar APK
    if not install_apk(apk_path):
        print("\n[ERROR] Falha ao instalar APK")
        return False
    
    # Passo 3: Abrir app
    print("\n[QUESTION] Deseja abrir o app TarefaMágica automaticamente? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            launch_app()
        else:
            print("[INFO] Você pode abrir o app manualmente no emulador")
    except KeyboardInterrupt:
        print("\n[INFO] Operação cancelada pelo usuário")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Instalação concluída!")
    print("=" * 60)
    print("\n[NEXT] Próximos passos:")
    print("1. O app TarefaMágica está instalado no emulador")
    print("2. Abra o app para testar as funcionalidades")
    print("3. Verifique se a interface está funcionando corretamente")
    print("4. Teste as funcionalidades básicas")
    
    return True

if __name__ == "__main__":
    main() 