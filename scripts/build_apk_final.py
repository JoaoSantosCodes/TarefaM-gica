#!/usr/bin/env python3
"""
Script final para gerar APK
TarefaMágica - Final APK Builder
"""

import os
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """Verifica o ambiente atual"""
    print("🔧 Verificando ambiente...")
    
    # Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        print("✅ Java: OK")
    except:
        print("❌ Java: Não encontrado")
        return False
    
    # Gradle
    if Path("android/gradlew.bat").exists():
        print("✅ Gradle Wrapper: OK")
    else:
        print("❌ Gradle Wrapper: Não encontrado")
        return False
    
    # Arquivos do projeto
    required_files = [
        "android/app/src/main/AndroidManifest.xml",
        "android/app/src/main/java/com/tarefamagica/app/MainActivity.kt",
        "android/gradle.properties"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            return False
    
    return True

def build_apk():
    """Tenta gerar a APK"""
    print("\n🚀 Tentando gerar APK...")
    
    # Muda para o diretório android
    os.chdir("android")
    
    try:
        # Executa o build
        print("📦 Executando: gradlew.bat assembleDebug")
        result = subprocess.run(['gradlew.bat', 'assembleDebug'], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Build concluído com sucesso!")
            
            # Verifica se a APK foi gerada
            apk_path = Path("app/build/outputs/apk/debug/app-debug.apk")
            if apk_path.exists():
                size_mb = apk_path.stat().st_size / (1024 * 1024)
                print(f"\n🎉 APK gerada com sucesso!")
                print(f"📁 Localização: {apk_path.absolute()}")
                print(f"📏 Tamanho: {size_mb:.2f} MB")
                
                # Copia para outputs
                outputs_dir = Path("../outputs")
                outputs_dir.mkdir(exist_ok=True)
                final_apk = outputs_dir / "TarefaMagica-debug.apk"
                shutil.copy2(apk_path, final_apk)
                print(f"📁 APK copiada para: {final_apk.absolute()}")
                
                return True
            else:
                print("❌ APK não encontrada no local esperado")
                return False
        else:
            print(f"❌ Erro no build: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout no build (10 minutos)")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 TarefaMágica - Final APK Builder")
    print("=" * 60)
    
    # Verifica ambiente
    if not check_environment():
        print("\n❌ Ambiente não está pronto")
        print("💡 Execute: python setup_android_simple.py")
        return False
    
    # Tenta gerar APK
    success = build_apk()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 APK GERADA COM SUCESSO!")
        print("=" * 60)
        print("\n📱 Para instalar no dispositivo:")
        print("1. Conecte um dispositivo Android via USB")
        print("2. Ative a depuração USB no dispositivo")
        print("3. Execute: adb install outputs/TarefaMagica-debug.apk")
    else:
        print("\n" + "=" * 60)
        print("❌ Falha na geração da APK")
        print("=" * 60)
        print("\n💡 Possíveis soluções:")
        print("1. Instale o Android Studio")
        print("2. Configure o Android SDK")
        print("3. Configure ANDROID_HOME")
        print("4. Tente novamente")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 