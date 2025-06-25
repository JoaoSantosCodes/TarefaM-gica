#!/usr/bin/env python3
"""
Script automatizado para corrigir problemas do Gradle e gerar APK
TarefaMágica - Build Automation
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def fix_gradle_wrapper_properties():
    """Corrige o arquivo gradle-wrapper.properties removendo espaços em branco"""
    gradle_wrapper_path = Path("android/gradle/wrapper/gradle-wrapper.properties")
    
    if not gradle_wrapper_path.exists():
        print("❌ Arquivo gradle-wrapper.properties não encontrado!")
        return False
    
    print("🔧 Corrigindo gradle-wrapper.properties...")
    
    # Lê o arquivo
    with open(gradle_wrapper_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Corrige a linha zipStorePath
    fixed_lines = []
    for line in lines:
        if line.strip().startswith('zipStorePath='):
            # Remove espaços em branco e caracteres invisíveis
            fixed_line = 'zipStorePath=wrapper/dists\n'
            print(f"  ✅ Corrigindo: '{line.strip()}' -> '{fixed_line.strip()}'")
        else:
            fixed_line = line
        fixed_lines.append(fixed_line)
    
    # Escreve o arquivo corrigido
    with open(gradle_wrapper_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ gradle-wrapper.properties corrigido!")
    return True

def clean_gradle_cache():
    """Limpa o cache do Gradle para evitar problemas"""
    print("🧹 Limpando cache do Gradle...")
    
    # Remove diretório .gradle se existir
    gradle_cache = Path.home() / ".gradle"
    if gradle_cache.exists():
        try:
            shutil.rmtree(gradle_cache)
            print("✅ Cache do Gradle removido!")
        except Exception as e:
            print(f"⚠️  Não foi possível remover cache: {e}")
    
    # Remove diretório .gradle do projeto
    project_gradle = Path("android/.gradle")
    if project_gradle.exists():
        try:
            shutil.rmtree(project_gradle)
            print("✅ Cache do projeto removido!")
        except Exception as e:
            print(f"⚠️  Não foi possível remover cache do projeto: {e}")

def check_java_version():
    """Verifica se o Java 17 ou superior está instalado e configurado"""
    print("☕ Verificando versão do Java...")
    
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        if 'version "17' in result.stderr or 'version "18' in result.stderr or 'version "19' in result.stderr or 'version "20' in result.stderr or 'version "21' in result.stderr:
            print("✅ Java compatível encontrado!")
            print(result.stderr.strip())
            return True
        else:
            print("❌ Java 17+ não encontrado. Versão atual:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar Java: {e}")
        return False

def check_android_sdk():
    """Verifica se o Android SDK está configurado"""
    print("📱 Verificando Android SDK...")
    
    # Verifica variáveis de ambiente
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home:
        print(f"✅ ANDROID_HOME encontrado: {android_home}")
        return True
    else:
        print("⚠️  ANDROID_HOME não configurado")
        return False

def build_apk():
    """Executa o build da APK"""
    print("🚀 Iniciando build da APK...")
    
    # Muda para o diretório android
    os.chdir("android")
    
    try:
        # Executa o build (usa gradlew.bat no Windows)
        print("📦 Executando: gradlew.bat assembleDebug")
        result = subprocess.run(['gradlew.bat', 'assembleDebug'], 
                              capture_output=True, text=True, check=True)
        
        print("✅ Build concluído com sucesso!")
        print("\n📋 Log do build:")
        print(result.stdout)
        
        # Verifica se a APK foi gerada
        apk_path = Path("app/build/outputs/apk/debug/app-debug.apk")
        if apk_path.exists():
            size_mb = apk_path.stat().st_size / (1024 * 1024)
            print(f"\n🎉 APK gerada com sucesso!")
            print(f"📁 Localização: {apk_path.absolute()}")
            print(f"📏 Tamanho: {size_mb:.2f} MB")
        else:
            print("❌ APK não encontrada no local esperado")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        print("\n📋 Log de erro:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Build Automation")
    print("=" * 60)
    
    # Verifica se estamos no diretório correto
    if not Path("android").exists():
        print("❌ Diretório 'android' não encontrado!")
        print("   Execute este script no diretório raiz do projeto.")
        return False
    
    # Passo 1: Verificar Java
    if not check_java_version():
        print("\n💡 Instale o Java 17 e configure JAVA_HOME")
        return False
    
    # Passo 2: Verificar Android SDK
    check_android_sdk()
    
    # Passo 3: Corrigir gradle-wrapper.properties
    if not fix_gradle_wrapper_properties():
        return False
    
    # Passo 4: Limpar cache
    clean_gradle_cache()
    
    # Passo 5: Build da APK
    success = build_apk()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Processo concluído com sucesso!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Falha no processo de build")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 