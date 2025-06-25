#!/usr/bin/env python3
"""
Script master para configurar ambiente completo e gerar APK
TarefaMagica - Complete Environment Setup & APK Builder
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_script(script_name, description):
    """Executa um script Python"""
    print(f"\n{'='*60}")
    print(f"[SETUP] {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=1800)
        
        print(result.stdout)
        if result.stderr:
            print("[WARNING] Avisos/Erros:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout ao executar {script_name}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro ao executar {script_name}: {e}")
        return False

def check_java():
    """Verifica se o Java esta instalado"""
    print("[CHECK] Verificando Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        print("[OK] Java encontrado!")
        return True
    except Exception as e:
        print(f"[ERROR] Java nao encontrado: {e}")
        return False

def check_android_sdk():
    """Verifica se o Android SDK esta configurado"""
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and Path(android_home).exists():
        print(f"[OK] Android SDK configurado: {android_home}")
        return True
    else:
        print("[ERROR] Android SDK nao configurado")
        return False

def main():
    """Funcao principal"""
    print("=" * 80)
    print("TarefaMagica - Complete Environment Setup & APK Builder")
    print("=" * 80)
    print("\nEste script ira:")
    print("1. [CHECK] Verificar Java")
    print("2. [SDK] Instalar Android SDK (se necessario)")
    print("3. [PROJECT] Configurar estrutura do projeto")
    print("4. [GRADLE] Configurar gradle.properties")
    print("5. [BUILD] Gerar APK automaticamente")
    print("\nTempo estimado: 10-20 minutos")
    
    input("\nPressione ENTER para continuar...")
    
    # Passo 1: Verificar Java
    if not check_java():
        print("\n[ERROR] Java e necessario para continuar")
        print("[INFO] Instale o Java 17 ou superior")
        return False
    
    # Passo 2: Verificar/Instalar Android SDK
    if not check_android_sdk():
        print("\n[SDK] Android SDK nao encontrado. Instalando...")
        if not run_script("install_android_sdk_simple.py", "Instalando Android SDK"):
            print("\n[ERROR] Falha na instalacao do Android SDK")
            return False
    else:
        print("\n[OK] Android SDK ja configurado!")
    
    # Passo 3: Configurar estrutura do projeto
    if not run_script("setup_android_simple.py", "Configurando estrutura do projeto"):
        print("\n[ERROR] Falha na configuracao do projeto")
        return False
    
    # Passo 4: Gerar APK
    print("\n[BUILD] Gerando APK...")
    if run_script("build_apk_final.py", "Gerando APK"):
        print("\n" + "=" * 80)
        print("SUCESSO! APK GERADA COM SUCESSO!")
        print("=" * 80)
        
        # Verifica se a APK foi gerada
        apk_path = Path("outputs/TarefaMagica-debug.apk")
        if apk_path.exists():
            size_mb = apk_path.stat().st_size / (1024 * 1024)
            print(f"\n[APK] APK gerada com sucesso!")
            print(f"[PATH] Localizacao: {apk_path.absolute()}")
            print(f"[SIZE] Tamanho: {size_mb:.2f} MB")
            
            print("\n[INSTALL] Para instalar no dispositivo:")
            print("1. Conecte um dispositivo Android via USB")
            print("2. Ative a depuracao USB no dispositivo")
            print("3. Execute: adb install outputs/TarefaMagica-debug.apk")
            
            return True
        else:
            print("\n[WARNING] APK nao encontrada no diretorio outputs")
            return False
    else:
        print("\n[ERROR] Falha na geracao da APK")
        print("\n[INFO] Tente executar manualmente:")
        print("   python build_apk_final.py")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[SUCCESS] Processo concluido com sucesso!")
    else:
        print("\n[ERROR] Processo falhou. Verifique os erros acima.")
    
    input("\nPressione ENTER para sair...")
    sys.exit(0 if success else 1) 