#!/usr/bin/env python3
"""
Script completo para instalar Android SDK automaticamente
TarefaMágica - Complete Android SDK Installer
"""

import os
import subprocess
import sys
import shutil
import zipfile
import urllib.request
import winreg
from pathlib import Path
import time

def download_with_progress(url, filename):
    """Download com barra de progresso"""
    print(f"📥 Baixando {filename}...")
    
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            print(f"\r  Progresso: {percent}%", end='', flush=True)
    
    try:
        urllib.request.urlretrieve(url, filename, progress_hook)
        print(f"\n✅ {filename} baixado com sucesso!")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao baixar {filename}: {e}")
        return False

def install_android_sdk():
    """Instala o Android SDK completo"""
    print("📱 Instalando Android SDK...")
    
    # Verifica se já está instalado
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and Path(android_home).exists():
        print(f"✅ Android SDK já instalado: {android_home}")
        return android_home
    
    # Cria diretório para Android SDK
    sdk_dir = Path.home() / "Android" / "Sdk"
    sdk_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Instalando em: {sdk_dir}")
    
    # Download do Android Command Line Tools
    cmdline_tools_url = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    cmdline_tools_zip = "commandlinetools-win.zip"
    
    if not download_with_progress(cmdline_tools_url, cmdline_tools_zip):
        return None
    
    # Extrai command line tools
    print("📦 Extraindo command line tools...")
    try:
        with zipfile.ZipFile(cmdline_tools_zip, 'r') as zip_ref:
            zip_ref.extractall(sdk_dir)
        print("✅ Extração concluída!")
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        return None
    
    # Remove arquivo zip
    os.remove(cmdline_tools_zip)
    
    # Configura estrutura de diretórios
    cmdline_tools_dir = sdk_dir / "cmdline-tools" / "latest"
    cmdline_tools_dir.mkdir(parents=True, exist_ok=True)
    
    # Move arquivos para o local correto
    extracted_dirs = list(sdk_dir.glob("cmdline-tools-*"))
    if extracted_dirs:
        extracted_dir = extracted_dirs[0]
        if extracted_dir.exists():
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(cmdline_tools_dir))
            shutil.rmtree(extracted_dir)
            print("✅ Estrutura de diretórios configurada!")
    
    return str(sdk_dir)

def accept_licenses(sdk_dir):
    """Aceita as licenças do Android SDK"""
    print("📋 Aceitando licenças...")
    
    licenses_dir = Path(sdk_dir) / "licenses"
    licenses_dir.mkdir(exist_ok=True)
    
    # Licenças necessárias
    license_files = {
        "android-sdk-license": "24333f8a63b6825ea9c5514f83c2829b004d1fee",
        "android-sdk-preview-license": "84831b9409646a918e30573bab4c9c91346d8abd",
        "google-gdk-license": "33b6a2b64607f11b759f320ef9dff4ae5c47d97a",
        "intel-android-extra-license": "d975f751698a77b662f1254ddbeed3901e976f5a",
        "mips-android-sysimage-license": "e9acab5b5fbb560a72cfaecce8946896ff6aab9d"
    }
    
    for license_file, license_hash in license_files.items():
        license_path = licenses_dir / license_file
        if not license_path.exists():
            with open(license_path, 'w') as f:
                f.write(license_hash + "\n")
    
    print("✅ Licenças aceitas!")

def install_sdk_components(sdk_dir):
    """Instala componentes do Android SDK"""
    print("🔧 Instalando componentes Android...")
    
    sdkmanager = Path(sdk_dir) / "cmdline-tools" / "latest" / "bin" / "sdkmanager.bat"
    
    if not sdkmanager.exists():
        print("❌ sdkmanager não encontrado")
        return False
    
    # Componentes necessários
    components = [
        "platform-tools",
        "platforms;android-34",
        "build-tools;34.0.0",
        "system-images;android-34;google_apis;x86_64"
    ]
    
    for component in components:
        print(f"📦 Instalando {component}...")
        try:
            cmd = [str(sdkmanager), component, "--sdk_root=" + str(sdk_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {component} instalado!")
            else:
                print(f"⚠️  {component} - {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {component} - Timeout")
        except Exception as e:
            print(f"❌ Erro ao instalar {component}: {e}")
    
    return True

def setup_environment_variables(sdk_dir):
    """Configura variáveis de ambiente permanentemente"""
    print("⚙️  Configurando variáveis de ambiente...")
    
    try:
        # Abre o registro do Windows
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        
        # Configura ANDROID_HOME
        winreg.SetValueEx(key, "ANDROID_HOME", 0, winreg.REG_EXPAND_SZ, str(sdk_dir))
        winreg.SetValueEx(key, "ANDROID_SDK_ROOT", 0, winreg.REG_EXPAND_SZ, str(sdk_dir))
        
        # Adiciona ao PATH
        try:
            current_path = winreg.QueryValueEx(key, "Path")[0]
        except:
            current_path = ""
        
        new_paths = [
            str(sdk_dir / "platform-tools"),
            str(sdk_dir / "cmdline-tools" / "latest" / "bin")
        ]
        
        for new_path in new_paths:
            if new_path not in current_path:
                current_path = f"{new_path};{current_path}" if current_path else new_path
        
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, current_path)
        
        winreg.CloseKey(key)
        
        # Atualiza variáveis de ambiente na sessão atual
        os.environ['ANDROID_HOME'] = str(sdk_dir)
        os.environ['ANDROID_SDK_ROOT'] = str(sdk_dir)
        os.environ['PATH'] = f"{sdk_dir}/platform-tools;{sdk_dir}/cmdline-tools/latest/bin;{os.environ['PATH']}"
        
        print("✅ Variáveis de ambiente configuradas!")
        return True
        
    except Exception as e:
        print(f"⚠️  Não foi possível configurar automaticamente: {e}")
        print("💡 Configure manualmente:")
        print(f"   ANDROID_HOME = {sdk_dir}")
        print(f"   ANDROID_SDK_ROOT = {sdk_dir}")
        return False

def verify_installation(sdk_dir):
    """Verifica se a instalação foi bem-sucedida"""
    print("🔍 Verificando instalação...")
    
    # Verifica se os diretórios existem
    required_dirs = [
        sdk_dir / "platform-tools",
        sdk_dir / "platforms" / "android-34",
        sdk_dir / "build-tools" / "34.0.0",
        sdk_dir / "cmdline-tools" / "latest" / "bin"
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.name}")
        else:
            print(f"❌ {dir_path.name}")
            return False
    
    # Verifica se adb funciona
    try:
        adb_path = sdk_dir / "platform-tools" / "adb.exe"
        if adb_path.exists():
            result = subprocess.run([str(adb_path), "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ ADB funcionando")
            else:
                print("⚠️  ADB com problemas")
        else:
            print("❌ ADB não encontrado")
    except Exception as e:
        print(f"⚠️  Erro ao testar ADB: {e}")
    
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Complete Android SDK Installer")
    print("=" * 60)
    
    try:
        # Passo 1: Instalar Android SDK
        sdk_dir = install_android_sdk()
        if not sdk_dir:
            print("❌ Falha ao instalar Android SDK")
            return False
        
        # Passo 2: Aceitar licenças
        accept_licenses(sdk_dir)
        
        # Passo 3: Instalar componentes
        if not install_sdk_components(sdk_dir):
            print("❌ Falha ao instalar componentes")
            return False
        
        # Passo 4: Configurar variáveis de ambiente
        setup_environment_variables(sdk_dir)
        
        # Passo 5: Verificar instalação
        if not verify_installation(sdk_dir):
            print("❌ Falha na verificação")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Android SDK instalado com sucesso!")
        print("=" * 60)
        print(f"\n📂 Localização: {sdk_dir}")
        print("\n💡 Próximos passos:")
        print("1. Reinicie o terminal para carregar as variáveis")
        print("2. Execute: python build_apk_final.py")
        print("3. A APK será gerada automaticamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a instalação: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 