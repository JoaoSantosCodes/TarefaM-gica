#!/usr/bin/env python3
"""
Script robusto para iniciar o emulador Android
TarefaMagica - Robust Emulator Starter
"""

import os
import subprocess
import time
import signal
import sys
from pathlib import Path

def check_emulator_process():
    """Verifica se há processo do emulador rodando"""
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq emulator.exe"], 
                              capture_output=True, text=True, timeout=10)
        return "emulator.exe" in result.stdout
    except:
        return False

def kill_emulator_processes():
    """Mata processos do emulador se existirem"""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "emulator.exe"], 
                      capture_output=True, timeout=10)
        print("[KILL] Processos do emulador finalizados")
        time.sleep(2)
    except:
        pass

def start_emulator(avd_name):
    """Inicia o emulador de forma robusta"""
    print(f"[START] Iniciando emulador: {avd_name}")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    emulator = sdk_path / "emulator" / "emulator.exe"
    
    if not emulator.exists():
        print(f"[ERROR] Emulador não encontrado: {emulator}")
        return False
    
    # Mata processos existentes
    kill_emulator_processes()
    
    try:
        # Comando para iniciar emulador
        cmd = [
            str(emulator),
            "-avd", avd_name,
            "-no-snapshot-load",
            "-gpu", "host",
            "-memory", "2048",
            "-no-audio",  # Desabilita áudio para acelerar
            "-no-boot-anim"  # Desabilita animação de boot
        ]
        
        print(f"[CMD] Executando: {' '.join(cmd)}")
        print("[INFO] Emulador iniciando... (pode demorar alguns minutos)")
        
        # Inicia em background
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print(f"[OK] Emulador iniciado (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar emulador: {e}")
        return None

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

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Iniciador Robusto de Emulador")
    print("=" * 60)
    
    avd_name = "Medium_Phone_API_36.0"
    apk_path = "TarefaMagica-debug.apk"
    
    # Passo 1: Verificar se emulador já está rodando
    if check_emulator_process():
        print("[INFO] Emulador já está rodando")
    else:
        # Passo 2: Iniciar emulador
        process = start_emulator(avd_name)
        if not process:
            print("[ERROR] Falha ao iniciar emulador")
            return False
    
    # Passo 3: Aguardar emulador ficar disponível
    if not wait_for_emulator():
        print("[ERROR] Emulador não ficou disponível")
        return False
    
    # Passo 4: Instalar APK
    print("\n[QUESTION] Deseja instalar a APK automaticamente? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            if install_apk(apk_path):
                print("\n[SUCCESS] TarefaMágica instalado com sucesso!")
                print("[INFO] Abra o app no emulador para testar")
            else:
                print("\n[ERROR] Falha ao instalar APK")
        else:
            print("[INFO] Você pode instalar a APK manualmente")
    except KeyboardInterrupt:
        print("\n[INFO] Operação cancelada pelo usuário")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Emulador configurado!")
    print("=" * 60)
    print("\n[NEXT] Próximos passos:")
    print("1. O emulador está rodando")
    print("2. Instale a APK 'TarefaMagica-debug.apk' se ainda não instalou")
    print("3. Abra o app TarefaMágica no emulador")
    print("4. Teste as funcionalidades básicas")
    
    return True

if __name__ == "__main__":
    main() 