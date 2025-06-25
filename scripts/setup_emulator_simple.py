#!/usr/bin/env python3
"""
Script simplificado para configurar emulador Android
TarefaMagica - Android Emulator Setup (Simple)
"""

import os
import subprocess
from pathlib import Path

def check_android_sdk():
    """Verifica se o Android SDK está configurado"""
    print("[CHECK] Verificando Android SDK...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    if sdk_path.exists():
        print(f"[OK] Android SDK encontrado: {sdk_path}")
        return str(sdk_path)
    
    print("[ERROR] Android SDK não encontrado")
    return None

def check_emulator():
    """Verifica se o emulador está disponível"""
    print("[CHECK] Verificando emulador...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    emulator = sdk_path / "emulator" / "emulator.exe"
    
    if emulator.exists():
        print(f"[OK] Emulador encontrado: {emulator}")
        return str(emulator)
    
    print("[ERROR] Emulador não encontrado")
    return None

def list_avds():
    """Lista AVDs disponíveis usando emulator"""
    print("[LIST] Listando AVDs disponíveis...")
    
    emulator = check_emulator()
    if not emulator:
        return []
    
    try:
        result = subprocess.run([emulator, "-list-avds"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            avds = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
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

def start_emulator(avd_name):
    """Inicia o emulador"""
    print(f"[START] Iniciando emulador: {avd_name}")
    
    emulator = check_emulator()
    if not emulator:
        return False
    
    try:
        # Comando para iniciar emulador
        cmd = [
            emulator,
            "-avd", avd_name,
            "-no-snapshot-load",
            "-gpu", "host",
            "-memory", "2048"
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

def install_apk(apk_path):
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
    print("TarefaMágica - Configurador de Emulador (Simples)")
    print("=" * 60)
    
    # Passo 1: Verificar Android SDK
    if not check_android_sdk():
        print("\n[ERROR] Android SDK não encontrado!")
        return False
    
    # Passo 2: Verificar emulador
    if not check_emulator():
        print("\n[ERROR] Emulador não encontrado!")
        print("[INFO] Instale o Android Emulator via Android Studio")
        return False
    
    # Passo 3: Listar AVDs existentes
    avds = list_avds()
    
    if not avds:
        print("\n[ERROR] Nenhum AVD encontrado!")
        print("[INFO] Crie um AVD via Android Studio:")
        print("  1. Abra Android Studio")
        print("  2. Vá em Tools > AVD Manager")
        print("  3. Clique em 'Create Virtual Device'")
        print("  4. Escolha Pixel 4 e Android 11 (API 30)")
        print("  5. Finalize a criação")
        return False
    
    # Passo 4: Escolher AVD
    print(f"\n[INFO] AVDs disponíveis:")
    for i, avd in enumerate(avds, 1):
        print(f"  {i}. {avd}")
    
    print("\n[QUESTION] Qual AVD você quer usar? (número): ", end="")
    try:
        choice = int(input().strip())
        if 1 <= choice <= len(avds):
            selected_avd = avds[choice - 1]
            print(f"[OK] AVD selecionado: {selected_avd}")
        else:
            print("[ERROR] Escolha inválida")
            return False
    except (ValueError, KeyboardInterrupt):
        print("[ERROR] Entrada inválida")
        return False
    
    # Passo 5: Iniciar emulador
    print(f"\n[QUESTION] Deseja iniciar o emulador '{selected_avd}' agora? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            if start_emulator(selected_avd):
                print("\n[SUCCESS] Emulador iniciado!")
                print("[INFO] Aguarde o emulador carregar completamente")
                
                # Passo 6: Instalar APK
                apk_path = "TarefaMagica-debug.apk"
                if Path(apk_path).exists():
                    print(f"\n[QUESTION] Deseja instalar a APK '{apk_path}' automaticamente? (s/n): ", end="")
                    try:
                        response = input().lower().strip()
                        if response in ['s', 'sim', 'y', 'yes']:
                            print("[INFO] Aguarde o emulador carregar completamente antes de instalar...")
                            print("[INFO] Pressione Enter quando o emulador estiver pronto...")
                            input()
                            install_apk(apk_path)
                        else:
                            print("[INFO] Você pode instalar a APK manualmente depois")
                    except KeyboardInterrupt:
                        print("\n[INFO] Instalação cancelada")
                else:
                    print(f"[WARNING] APK '{apk_path}' não encontrada")
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