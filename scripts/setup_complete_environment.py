#!/usr/bin/env python3
"""
Script master para configurar ambiente completo e gerar APK
TarefaMágica - Complete Environment Setup & APK Builder
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_script(script_name, description):
    """Executa um script Python"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=1800)
        
        print(result.stdout)
        if result.stderr:
            print("⚠️  Avisos/Erros:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout ao executar {script_name}")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar {script_name}: {e}")
        return False

def check_java():
    """Verifica se o Java está instalado"""
    print("☕ Verificando Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Java encontrado!")
        return True
    except Exception as e:
        print(f"❌ Java não encontrado: {e}")
        return False

def check_android_sdk():
    """Verifica se o Android SDK está configurado"""
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and Path(android_home).exists():
        print(f"✅ Android SDK configurado: {android_home}")
        return True
    else:
        print("❌ Android SDK não configurado")
        return False

def main():
    """Função principal"""
    print("=" * 80)
    print("🚀 TarefaMágica - Complete Environment Setup & APK Builder")
    print("=" * 80)
    print("\nEste script irá:")
    print("1. ✅ Verificar Java")
    print("2. 📱 Instalar Android SDK (se necessário)")
    print("3. 📁 Configurar estrutura do projeto")
    print("4. 🔧 Configurar gradle.properties")
    print("5. 🎯 Gerar APK automaticamente")
    print("\n⏱️  Tempo estimado: 10-20 minutos")
    
    input("\nPressione ENTER para continuar...")
    
    # Passo 1: Verificar Java
    if not check_java():
        print("\n❌ Java é necessário para continuar")
        print("💡 Instale o Java 17 ou superior")
        return False
    
    # Passo 2: Verificar/Instalar Android SDK
    if not check_android_sdk():
        print("\n📱 Android SDK não encontrado. Instalando...")
        if not run_script("install_android_sdk_complete.py", "Instalando Android SDK"):
            print("\n❌ Falha na instalação do Android SDK")
            return False
    else:
        print("\n✅ Android SDK já configurado!")
    
    # Passo 3: Configurar estrutura do projeto
    if not run_script("setup_android_simple.py", "Configurando estrutura do projeto"):
        print("\n❌ Falha na configuração do projeto")
        return False
    
    # Passo 4: Gerar APK
    print("\n🎯 Gerando APK...")
    if run_script("build_apk_final.py", "Gerando APK"):
        print("\n" + "=" * 80)
        print("🎉 SUCESSO! APK GERADA COM SUCESSO!")
        print("=" * 80)
        
        # Verifica se a APK foi gerada
        apk_path = Path("outputs/TarefaMagica-debug.apk")
        if apk_path.exists():
            size_mb = apk_path.stat().st_size / (1024 * 1024)
            print(f"\n📱 APK gerada com sucesso!")
            print(f"📁 Localização: {apk_path.absolute()}")
            print(f"📏 Tamanho: {size_mb:.2f} MB")
            
            print("\n💡 Para instalar no dispositivo:")
            print("1. Conecte um dispositivo Android via USB")
            print("2. Ative a depuração USB no dispositivo")
            print("3. Execute: adb install outputs/TarefaMagica-debug.apk")
            
            return True
        else:
            print("\n⚠️  APK não encontrada no diretório outputs")
            return False
    else:
        print("\n❌ Falha na geração da APK")
        print("\n💡 Tente executar manualmente:")
        print("   python build_apk_final.py")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou. Verifique os erros acima.")
    
    input("\nPressione ENTER para sair...")
    sys.exit(0 if success else 1) 