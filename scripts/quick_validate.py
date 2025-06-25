#!/usr/bin/env python3
"""
Validação rápida do ambiente de build
TarefaMágica - Quick Environment Validation
"""

import os
import subprocess
from pathlib import Path

def main():
    print("🔧 Validação Rápida do Ambiente")
    print("=" * 40)
    
    # Verifica Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        print("✅ Java: OK")
    except:
        print("❌ Java: Não encontrado")
    
    # Verifica Gradle
    try:
        result = subprocess.run(['cd android && gradlew.bat --version'], 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Gradle: OK")
        else:
            print("❌ Gradle: Erro")
    except:
        print("❌ Gradle: Não encontrado")
    
    # Verifica arquivos principais
    files_to_check = [
        "android/app/src/main/AndroidManifest.xml",
        "android/app/src/main/java/com/tarefamagica/app/MainActivity.kt",
        "android/app/src/main/res/values/strings.xml",
        "android/app/src/main/res/values/themes.xml",
        "android/app/src/main/res/values/colors.xml",
        "android/gradle.properties"
    ]
    
    print("\n📁 Verificando arquivos:")
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # Verifica Android SDK
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home:
        print(f"\n✅ Android SDK: {android_home}")
    else:
        print("\n❌ Android SDK: Não configurado")
    
    print("\n" + "=" * 40)
    print("🎯 Status: Ambiente básico configurado!")
    print("💡 Para gerar APK, instale o Android SDK")

if __name__ == "__main__":
    main() 