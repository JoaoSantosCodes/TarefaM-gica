#!/usr/bin/env python3
"""
Script para configurar emulador Android Studio AVD
TarefaMagica - Android Emulator Setup
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def check_android_studio():
    """Verifica se o Android Studio está instalado"""
    print("[CHECK] Verificando Android Studio...")
    
    # Possíveis locais de instalação
    possible_paths = [
        "C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe",
        "C:\\Program Files (x86)\\Android\\Android Studio\\bin\\studio64.exe",
        os.path.expanduser("~\\AppData\\Local\\Android\\Sdk\\emulator\\emulator.exe")
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            print(f"[OK] Android Studio encontrado em: {path}")
            return path
    
    print("[ERROR] Android Studio não encontrado")
    return None

def check_avd_manager():
    """Verifica se o AVD Manager está disponível"""
    print("[CHECK] Verificando AVD Manager...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    avd_manager = sdk_path / "cmdline-tools" / "bin" / "avdmanager.bat"
    
    if avd_manager.exists():
        print(f"[OK] AVD Manager encontrado: {avd_manager}")
        return str(avd_manager)
    
    print("[ERROR] AVD Manager não encontrado")
    return None

def list_available_avds():
    """Lista AVDs disponíveis"""
    print("[LIST] Listando AVDs disponíveis...")
    
    avd_manager = check_avd_manager()
    if not avd_manager:
        return []
    
    try:
        result = subprocess.run([avd_manager, "list", "avd"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            avds = []
            for line in lines:
                if line.strip() and 'Name:' in line:
                    name = line.split('Name:')[1].strip()
                    avds.append(name)
            
            print(f"[OK] {len(avds)} AVD(s) encontrado(s)")
            for avd in avds:
                print(f"  - {avd}")
            return avds
        else:
            print(f"[ERROR] Erro ao listar AVDs: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar AVDs: {e}")
        return []

def create_tarefamagica_avd():
    """Cria AVD específico para TarefaMágica"""
    print("[CREATE] Criando AVD TarefaMágica...")
    
    avd_manager = check_avd_manager()
    if not avd_manager:
        return False
    
    # Configurações do AVD
    avd_name = "TarefaMagica_AVD"
    device = "pixel_4"
    target = "android-30"  # Android 11
    abi = "x86_64"
    
    try:
        # Comando para criar AVD
        cmd = [
            avd_manager, "create", "avd",
            "--name", avd_name,
            "--device", device,
            "--target", target,
            "--abi", abi,
            "--force"  # Sobrescreve se já existir
        ]
        
        print(f"[CMD] Executando: {' '.join(cmd)}")
        
        # Executa com input automático (não para perguntas)
        result = subprocess.run(cmd, 
                              input=b"no\n",  # Não criar hardware profile customizado
                              capture_output=True, 
                              text=True, 
                              timeout=120)
        
        if result.returncode == 0:
            print(f"[SUCCESS] AVD '{avd_name}' criado com sucesso!")
            return True
        else:
            print(f"[ERROR] Erro ao criar AVD: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar AVD: {e}")
        return False

def start_emulator(avd_name="TarefaMagica_AVD"):
    """Inicia o emulador"""
    print(f"[START] Iniciando emulador: {avd_name}")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    emulator = sdk_path / "emulator" / "emulator.exe"
    
    if not emulator.exists():
        print("[ERROR] Emulador não encontrado")
        return False
    
    try:
        # Comando para iniciar emulador
        cmd = [
            str(emulator),
            "-avd", avd_name,
            "-no-snapshot-load",  # Não carregar snapshot
            "-gpu", "host",  # Usar GPU do host
            "-memory", "2048"  # 2GB RAM
        ]
        
        print(f"[CMD] Executando: {' '.join(cmd)}")
        print("[INFO] Emulador iniciando... (pode demorar alguns minutos)")
        
        # Inicia em background
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print(f"[OK] Emulador iniciado (PID: {process.pid})")
        print("[INFO] Aguarde o emulador carregar completamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar emulador: {e}")
        return False

def install_apk_on_emulator(apk_path):
    """Instala APK no emulador"""
    print(f"[INSTALL] Instalando APK: {apk_path}")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    adb = sdk_path / "platform-tools" / "adb.exe"
    
    if not adb.exists():
        print("[ERROR] ADB não encontrado")
        return False
    
    try:
        # Verifica se emulador está rodando
        result = subprocess.run([str(adb), "devices"], 
                              capture_output=True, text=True, timeout=30)
        
        if "emulator" not in result.stdout:
            print("[ERROR] Emulador não está rodando")
            return False
        
        # Instala APK
        install_cmd = [str(adb), "install", "-r", apk_path]
        result = subprocess.run(install_cmd, 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[SUCCESS] APK instalado com sucesso!")
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
    print("TarefaMágica - Configurador de Emulador Android")
    print("=" * 60)
    
    # Passo 1: Verificar Android Studio
    if not check_android_studio():
        print("\n[ERROR] Android Studio não encontrado!")
        print("[INFO] Instale o Android Studio primeiro:")
        print("  https://developer.android.com/studio")
        return False
    
    # Passo 2: Verificar AVD Manager
    if not check_avd_manager():
        print("\n[ERROR] AVD Manager não encontrado!")
        print("[INFO] Instale o Android SDK Command-line Tools")
        return False
    
    # Passo 3: Listar AVDs existentes
    existing_avds = list_available_avds()
    
    # Passo 4: Criar AVD se necessário
    avd_name = "TarefaMagica_AVD"
    if avd_name not in existing_avds:
        if not create_tarefamagica_avd():
            print("\n[ERROR] Falha ao criar AVD")
            return False
    else:
        print(f"[OK] AVD '{avd_name}' já existe")
    
    # Passo 5: Iniciar emulador
    print("\n[QUESTION] Deseja iniciar o emulador agora? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            if start_emulator(avd_name):
                print("\n[SUCCESS] Emulador iniciado!")
                print("[INFO] Aguarde o emulador carregar completamente")
                print("[INFO] Depois você pode instalar a APK manualmente")
            else:
                print("\n[ERROR] Falha ao iniciar emulador")
        else:
            print("\n[INFO] Emulador não iniciado")
            print("[INFO] Você pode iniciar manualmente depois")
    except KeyboardInterrupt:
        print("\n[INFO] Operação cancelada pelo usuário")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Configuração concluída!")
    print("=" * 60)
    print("\n[NEXT] Próximos passos:")
    print("1. Aguarde o emulador carregar completamente")
    print("2. Transfira a APK 'TarefaMagica-debug.apk' para o emulador")
    print("3. Instale a APK no emulador")
    print("4. Teste o app TarefaMágica!")
    
    return True

if __name__ == "__main__":
    main() 