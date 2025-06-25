#!/usr/bin/env python3
"""
Script para validar o ambiente de build do Android
TarefaMágica - Build Environment Validator
"""

import os
import subprocess
import sys
from pathlib import Path

def check_java():
    """Verifica se o Java está instalado e configurado"""
    print("☕ Verificando Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Java encontrado:")
        print(result.stderr.strip())
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar Java: {e}")
        return False

def check_android_sdk():
    """Verifica se o Android SDK está configurado"""
    print("\n📱 Verificando Android SDK...")
    
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home:
        print(f"✅ ANDROID_HOME: {android_home}")
        
        # Verifica se o diretório existe
        if Path(android_home).exists():
            print("✅ Diretório Android SDK existe")
        else:
            print("❌ Diretório Android SDK não existe")
            return False
            
        return True
    else:
        print("⚠️  ANDROID_HOME não configurado")
        return False

def check_gradle():
    """Verifica se o Gradle está funcionando"""
    print("\n📦 Verificando Gradle...")
    
    if not Path("android").exists():
        print("❌ Diretório 'android' não encontrado")
        return False
    
    if not Path("android/gradlew.bat").exists():
        print("❌ gradlew.bat não encontrado")
        return False
    
    try:
        os.chdir("android")
        result = subprocess.run(['gradlew.bat', '--version'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Gradle funcionando corretamente")
            version_line = result.stdout.split('Gradle')[1].split('\n')[0].strip()
            print(f"Versão: {version_line}")
            return True
        else:
            print("❌ Gradle não funcionando")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar Gradle: {e}")
        return False

def check_project_structure():
    """Verifica a estrutura do projeto"""
    print("\n📁 Verificando estrutura do projeto...")
    
    required_files = [
        "android/app/src/main/AndroidManifest.xml",
        "android/app/src/main/java/com/tarefamagica/app/MainActivity.kt",
        "android/app/src/main/res/values/strings.xml",
        "android/app/src/main/res/values/themes.xml",
        "android/app/src/main/res/values/colors.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} arquivos necessários não encontrados")
        return False
    else:
        print("✅ Estrutura do projeto OK")
        return True

def check_gradle_properties():
    """Verifica se o gradle.properties está configurado corretamente"""
    print("\n⚙️  Verificando gradle.properties...")
    
    gradle_props = Path("android/gradle.properties")
    if gradle_props.exists():
        with open(gradle_props, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_props = [
            "android.overridePathCheck=true",
            "android.useAndroidX=true"
        ]
        
        for prop in required_props:
            if prop in content:
                print(f"✅ {prop}")
            else:
                print(f"❌ {prop} - não encontrado")
                return False
        
        print("✅ gradle.properties configurado corretamente")
        return True
    else:
        print("❌ gradle.properties não encontrado")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Build Environment Validator")
    print("=" * 60)
    
    checks = [
        ("Java", check_java),
        ("Android SDK", check_android_sdk),
        ("Gradle", check_gradle),
        ("Estrutura do Projeto", check_project_structure),
        ("Gradle Properties", check_gradle_properties)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro ao verificar {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} verificações passaram")
    
    if passed == len(results):
        print("\n🎉 Ambiente configurado corretamente!")
        print("💡 Você pode tentar gerar a APK agora.")
    else:
        print(f"\n⚠️  {len(results) - passed} problema(s) encontrado(s)")
        print("💡 Corrija os problemas antes de tentar gerar a APK.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 