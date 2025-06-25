#!/usr/bin/env python3
"""
Script para fazer build da APK em diretório temporário sem caracteres especiais
TarefaMágica - Build Automation
"""

import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

def copy_project_to_temp():
    """Copia o projeto para um diretório temporário sem caracteres especiais"""
    print("📁 Copiando projeto para diretório temporário...")
    
    # Cria diretório temporário
    temp_dir = Path(tempfile.gettempdir()) / "TarefaMagica_Build"
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copia apenas os arquivos necessários para o build
    android_dir = Path("android")
    temp_android = temp_dir / "android"
    
    print(f"  📂 Copiando para: {temp_dir}")
    
    # Copia diretório android
    shutil.copytree(android_dir, temp_android)
    
    # Cria gradle.properties no diretório temporário
    gradle_props = temp_android / "gradle.properties"
    with open(gradle_props, 'w', encoding='utf-8') as f:
        f.write("android.overridePathCheck=true\n")
        f.write("android.useAndroidX=true\n")
        f.write("kotlin.code.style=official\n")
        f.write("android.nonTransitiveRClass=true\n")
        f.write("org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")
    
    print("✅ Projeto copiado com sucesso!")
    return temp_dir

def build_apk_in_temp(temp_dir):
    """Executa o build da APK no diretório temporário"""
    print("🚀 Iniciando build da APK...")
    
    # Muda para o diretório temporário
    os.chdir(temp_dir / "android")
    
    try:
        # Executa o build
        print("📦 Executando: gradlew.bat assembleDebug")
        result = subprocess.run(['gradlew.bat', 'assembleDebug'], 
                              capture_output=True, text=True, check=True)
        
        print("✅ Build concluído com sucesso!")
        
        # Verifica se a APK foi gerada
        apk_path = Path("app/build/outputs/apk/debug/app-debug.apk")
        if apk_path.exists():
            size_mb = apk_path.stat().st_size / (1024 * 1024)
            print(f"\n🎉 APK gerada com sucesso!")
            print(f"📁 Localização temporária: {apk_path.absolute()}")
            print(f"📏 Tamanho: {size_mb:.2f} MB")
            
            # Copia a APK para o diretório original
            original_apk_dir = Path("../../../outputs")
            original_apk_dir.mkdir(exist_ok=True)
            original_apk_path = original_apk_dir / "TarefaMagica-debug.apk"
            
            shutil.copy2(apk_path, original_apk_path)
            print(f"📁 APK copiada para: {original_apk_path.absolute()}")
            
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

def cleanup_temp_dir(temp_dir):
    """Remove o diretório temporário"""
    print("🧹 Limpando diretório temporário...")
    try:
        shutil.rmtree(temp_dir)
        print("✅ Diretório temporário removido!")
    except Exception as e:
        print(f"⚠️  Não foi possível remover diretório temporário: {e}")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Build Automation (Temp Directory)")
    print("=" * 60)
    
    # Verifica se estamos no diretório correto
    if not Path("android").exists():
        print("❌ Diretório 'android' não encontrado!")
        print("   Execute este script no diretório raiz do projeto.")
        return False
    
    temp_dir = None
    try:
        # Passo 1: Copiar projeto para diretório temporário
        temp_dir = copy_project_to_temp()
        
        # Passo 2: Build da APK
        success = build_apk_in_temp(temp_dir)
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 Processo concluído com sucesso!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ Falha no processo de build")
            print("=" * 60)
        
        return success
        
    finally:
        # Passo 3: Limpeza
        if temp_dir:
            cleanup_temp_dir(temp_dir)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 