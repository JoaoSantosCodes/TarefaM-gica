#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script de Automação - Setup Android Build TarefaMágica
Configura o ambiente e builda o projeto Android automaticamente
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import json
from pathlib import Path
import shutil
import winreg

class AndroidBuildSetup:
    """Configuração automática do ambiente Android"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.android_dir = self.project_root / "android"
        self.setup_status = {}
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Registra um passo da configuração"""
        self.setup_status[step] = {
            "status": status,
            "details": details,
            "timestamp": str(Path.cwd())
        }
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔄"
        print(f"{status_icon} {step}: {details}")
        
    def check_system(self):
        """Verifica o sistema operacional"""
        print("🔍 Verificando sistema operacional...")
        
        system = platform.system()
        if system == "Windows":
            self.log_step("Sistema", "SUCCESS", f"Windows detectado")
            return "windows"
        elif system == "Linux":
            self.log_step("Sistema", "SUCCESS", f"Linux detectado")
            return "linux"
        elif system == "Darwin":
            self.log_step("Sistema", "SUCCESS", f"macOS detectado")
            return "macos"
        else:
            self.log_step("Sistema", "FAILED", f"Sistema não suportado: {system}")
            return None
            
    def check_java(self):
        """Verifica se o Java está instalado"""
        print("\n☕ Verificando Java...")
        
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stderr.split('\n')[0]
                self.log_step("Java", "SUCCESS", f"Java encontrado: {version_line}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        self.log_step("Java", "FAILED", "Java não encontrado")
        return False
        
    def check_android_sdk(self):
        """Verifica se o Android SDK está instalado"""
        print("\n📱 Verificando Android SDK...")
        
        # Verificar variáveis de ambiente
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        
        if android_home and Path(android_home).exists():
            self.log_step("Android SDK", "SUCCESS", f"SDK encontrado em: {android_home}")
            return True
            
        # Verificar locais padrão
        default_locations = [
            Path.home() / "AppData/Local/Android/Sdk",  # Windows
            Path.home() / "Library/Android/sdk",        # macOS
            Path.home() / "Android/Sdk",                # Linux
        ]
        
        for location in default_locations:
            if location.exists():
                self.log_step("Android SDK", "SUCCESS", f"SDK encontrado em: {location}")
                return True
                
        self.log_step("Android SDK", "FAILED", "Android SDK não encontrado")
        return False
        
    def install_java_windows(self):
        """Instala Java no Windows usando Chocolatey"""
        print("\n☕ Instalando Java no Windows...")
        
        try:
            # Verificar se Chocolatey está instalado
            result = subprocess.run(["choco", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.log_step("Chocolatey", "FAILED", "Chocolatey não encontrado")
                return False
                
            # Instalar OpenJDK 17
            result = subprocess.run(["choco", "install", "openjdk17", "-y"], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_step("Java Install", "SUCCESS", "Java 17 instalado via Chocolatey")
                return True
            else:
                self.log_step("Java Install", "FAILED", f"Erro na instalação: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_step("Java Install", "FAILED", f"Erro: {str(e)}")
            return False
            
    def download_android_command_line_tools(self):
        """Baixa Android Command Line Tools"""
        print("\n📱 Baixando Android Command Line Tools...")
        
        system = platform.system().lower()
        if system == "windows":
            url = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
            filename = "commandlinetools-win-latest.zip"
        elif system == "darwin":
            url = "https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip"
            filename = "commandlinetools-mac-latest.zip"
        else:
            url = "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
            filename = "commandlinetools-linux-latest.zip"
            
        try:
            # Criar diretório para download
            download_dir = self.project_root / "temp_downloads"
            download_dir.mkdir(exist_ok=True)
            
            # Baixar arquivo
            file_path = download_dir / filename
            print(f"📥 Baixando de: {url}")
            
            urllib.request.urlretrieve(url, file_path)
            
            # Extrair
            extract_dir = self.project_root / "android_sdk"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            self.log_step("Android Tools", "SUCCESS", f"Tools extraídos em: {extract_dir}")
            return extract_dir
            
        except Exception as e:
            self.log_step("Android Tools", "FAILED", f"Erro no download: {str(e)}")
            return None
            
    def setup_environment_variables(self):
        """Configura variáveis de ambiente"""
        print("\n🔧 Configurando variáveis de ambiente...")
        
        try:
            # Encontrar Java
            java_home = None
            if platform.system() == "Windows":
                # Procurar Java em locais comuns
                java_locations = [
                    "C:\\Program Files\\Java\\jdk-17",
                    "C:\\Program Files\\Eclipse Adoptium\\jdk-17",
                    "C:\\Program Files\\OpenJDK\\jdk-17"
                ]
                
                for location in java_locations:
                    if Path(location).exists():
                        java_home = location
                        break
                        
            if java_home:
                os.environ['JAVA_HOME'] = java_home
                self.log_step("JAVA_HOME", "SUCCESS", f"Configurado: {java_home}")
            else:
                self.log_step("JAVA_HOME", "FAILED", "Java não encontrado")
                
            # Configurar Android SDK
            android_sdk = self.project_root / "android_sdk"
            if android_sdk.exists():
                os.environ['ANDROID_HOME'] = str(android_sdk)
                os.environ['ANDROID_SDK_ROOT'] = str(android_sdk)
                self.log_step("ANDROID_HOME", "SUCCESS", f"Configurado: {android_sdk}")
            else:
                self.log_step("ANDROID_HOME", "FAILED", "Android SDK não encontrado")
                
            return True
            
        except Exception as e:
            self.log_step("Environment", "FAILED", f"Erro na configuração: {str(e)}")
            return False
            
    def build_android_project(self):
        """Builda o projeto Android"""
        print("\n🔨 Buildando projeto Android...")
        
        try:
            # Navegar para o diretório Android
            os.chdir(self.android_dir)
            
            # Verificar se gradlew existe
            if not Path("gradlew.bat").exists():
                self.log_step("Gradle Wrapper", "FAILED", "gradlew.bat não encontrado")
                return False
                
            # Executar build
            print("🚀 Executando: .\\gradlew.bat assembleDebug")
            result = subprocess.run([".\\gradlew.bat", "assembleDebug"], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Verificar se o APK foi gerado
                apk_path = Path("app/build/outputs/apk/debug/app-debug.apk")
                if apk_path.exists():
                    size_mb = apk_path.stat().st_size / (1024 * 1024)
                    self.log_step("Build", "SUCCESS", f"APK gerado: {apk_path} ({size_mb:.1f} MB)")
                    return True
                else:
                    self.log_step("Build", "FAILED", "APK não encontrado após build")
                    return False
            else:
                self.log_step("Build", "FAILED", f"Erro no build: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_step("Build", "FAILED", f"Erro durante build: {str(e)}")
            return False
            
    def generate_setup_report(self):
        """Gera relatório da configuração"""
        print("\n📊 Gerando relatório de configuração...")
        
        report = {
            "timestamp": str(Path.cwd()),
            "system": platform.system(),
            "setup_steps": self.setup_status,
            "success_count": sum(1 for step in self.setup_status.values() if step["status"] == "SUCCESS"),
            "total_steps": len(self.setup_status)
        }
        
        # Salvar relatório
        report_file = self.project_root / "outputs" / "android_build_setup_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Relatório salvo em: {report_file}")
        
        # Mostrar resumo
        print(f"\n🎯 RESUMO DA CONFIGURAÇÃO:")
        print(f"✅ Passos bem-sucedidos: {report['success_count']}/{report['total_steps']}")
        
        for step, info in self.setup_status.items():
            status_icon = "✅" if info["status"] == "SUCCESS" else "❌"
            print(f"{status_icon} {step}: {info['details']}")
            
    def run_full_setup(self):
        """Executa a configuração completa"""
        print("🚀 INICIANDO CONFIGURAÇÃO AUTOMÁTICA DO ANDROID BUILD")
        print("=" * 60)
        
        # Verificar sistema
        system = self.check_system()
        if not system:
            return False
            
        # Verificar Java
        java_ok = self.check_java()
        if not java_ok:
            if system == "windows":
                java_ok = self.install_java_windows()
            else:
                print("❌ Instalação automática de Java não suportada neste sistema")
                print("💡 Instale manualmente: https://adoptium.net/")
                return False
                
        # Verificar Android SDK
        sdk_ok = self.check_android_sdk()
        if not sdk_ok:
            sdk_path = self.download_android_command_line_tools()
            if sdk_path:
                sdk_ok = True
                
        # Configurar variáveis de ambiente
        env_ok = self.setup_environment_variables()
        
        # Buildar projeto
        build_ok = False
        if java_ok and sdk_ok and env_ok:
            build_ok = self.build_android_project()
            
        # Gerar relatório
        self.generate_setup_report()
        
        if build_ok:
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            print("📱 APK gerado e pronto para instalação")
        else:
            print("\n⚠️ CONFIGURAÇÃO PARCIALMENTE CONCLUÍDA")
            print("🔧 Alguns passos podem precisar de intervenção manual")
            
        return build_ok

def download_file(url, filename):
    """Download de arquivo com barra de progresso"""
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

def setup_android_sdk():
    """Configura o Android SDK"""
    print("📱 Configurando Android SDK...")
    
    # Verifica se já está configurado
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and Path(android_home).exists():
        print(f"✅ Android SDK já configurado: {android_home}")
        return android_home
    
    # Cria diretório para Android SDK
    sdk_dir = Path.home() / "Android" / "Sdk"
    sdk_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Instalando Android SDK em: {sdk_dir}")
    
    # Download do Android Command Line Tools
    cmdline_tools_url = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    cmdline_tools_zip = "commandlinetools-win.zip"
    
    if not download_file(cmdline_tools_url, cmdline_tools_zip):
        return None
    
    # Extrai command line tools
    print("📦 Extraindo command line tools...")
    with zipfile.ZipFile(cmdline_tools_zip, 'r') as zip_ref:
        zip_ref.extractall(sdk_dir)
    
    # Remove arquivo zip
    os.remove(cmdline_tools_zip)
    
    # Configura estrutura de diretórios
    cmdline_tools_dir = sdk_dir / "cmdline-tools" / "latest"
    cmdline_tools_dir.mkdir(parents=True, exist_ok=True)
    
    # Move arquivos para o local correto
    extracted_dir = next(sdk_dir.glob("cmdline-tools-*"))
    if extracted_dir.exists():
        for item in extracted_dir.iterdir():
            shutil.move(str(item), str(cmdline_tools_dir))
        shutil.rmtree(extracted_dir)
    
    # Configura variáveis de ambiente
    os.environ['ANDROID_HOME'] = str(sdk_dir)
    os.environ['ANDROID_SDK_ROOT'] = str(sdk_dir)
    os.environ['PATH'] = f"{sdk_dir}/platform-tools;{sdk_dir}/cmdline-tools/latest/bin;{os.environ['PATH']}"
    
    print("✅ Android SDK instalado!")
    return str(sdk_dir)

def install_android_components(sdk_dir):
    """Instala componentes necessários do Android SDK"""
    print("🔧 Instalando componentes Android...")
    
    # Cria arquivo de licenças aceitas
    licenses_dir = Path(sdk_dir) / "licenses"
    licenses_dir.mkdir(exist_ok=True)
    
    # Aceita licenças
    license_files = [
        "android-sdk-license",
        "android-sdk-preview-license",
        "google-gdk-license",
        "intel-android-extra-license",
        "mips-android-sysimage-license"
    ]
    
    for license_file in license_files:
        license_path = licenses_dir / license_file
        if not license_path.exists():
            with open(license_path, 'w') as f:
                f.write("24333f8a63b6825ea9c5514f83c2829b004d1fee\n")
    
    # Instala componentes via sdkmanager
    sdkmanager = Path(sdk_dir) / "cmdline-tools" / "latest" / "bin" / "sdkmanager.bat"
    
    if sdkmanager.exists():
        components = [
            "platform-tools",
            "platforms;android-34",
            "build-tools;34.0.0",
            "system-images;android-34;google_apis;x86_64"
        ]
        
        for component in components:
            print(f"📦 Instalando {component}...")
            try:
                result = subprocess.run([str(sdkmanager), component, "--sdk_root=" + str(sdk_dir)], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"✅ {component} instalado!")
                else:
                    print(f"⚠️  {component} - {result.stderr}")
            except Exception as e:
                print(f"❌ Erro ao instalar {component}: {e}")
    else:
        print("❌ sdkmanager não encontrado")
        return False
    
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
        print("✅ Variáveis de ambiente configuradas!")
        return True
        
    except Exception as e:
        print(f"⚠️  Não foi possível configurar variáveis de ambiente automaticamente: {e}")
        print("💡 Configure manualmente:")
        print(f"   ANDROID_HOME = {sdk_dir}")
        print(f"   ANDROID_SDK_ROOT = {sdk_dir}")
        return False

def create_minimal_project():
    """Cria estrutura mínima do projeto se não existir"""
    print("📁 Verificando estrutura do projeto...")
    
    # Verifica se já existe estrutura básica
    if Path("android/app/build.gradle").exists():
        print("✅ Estrutura do projeto já existe")
        return True
    
    print("🔧 Criando estrutura mínima do projeto...")
    
    # Cria diretórios necessários
    android_dir = Path("android")
    app_dir = android_dir / "app" / "src" / "main"
    
    (app_dir / "java" / "com" / "tarefamagica" / "app").mkdir(parents=True, exist_ok=True)
    (app_dir / "res" / "values").mkdir(parents=True, exist_ok=True)
    (app_dir / "res" / "mipmap-hdpi").mkdir(parents=True, exist_ok=True)
    (app_dir / "res" / "xml").mkdir(parents=True, exist_ok=True)
    
    # Cria AndroidManifest.xml básico
    manifest_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.TarefaMagica"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.TarefaMagica">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>'''
    
    with open(app_dir / "AndroidManifest.xml", 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    # Cria MainActivity.kt básico
    main_activity_content = '''package com.tarefamagica.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TarefaMagicaTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting("TarefaMágica")
                }
            }
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    TarefaMagicaTheme {
        Greeting("TarefaMágica")
    }
}'''
    
    with open(app_dir / "java" / "com" / "tarefamagica" / "app" / "MainActivity.kt", 'w', encoding='utf-8') as f:
        f.write(main_activity_content)
    
    # Cria strings.xml
    strings_content = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">TarefaMágica</string>
</resources>'''
    
    with open(app_dir / "res" / "values" / "strings.xml", 'w', encoding='utf-8') as f:
        f.write(strings_content)
    
    # Cria ícone básico
    icon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82'
    
    icon_file = app_dir / "res" / "mipmap-hdpi" / "ic_launcher.png"
    with open(icon_file, 'wb') as f:
        f.write(icon_data)
    
    # Copia para outras densidades
    for density in ['mdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
        target_dir = app_dir / "res" / f"mipmap-{density}"
        target_dir.mkdir(exist_ok=True)
        shutil.copy2(icon_file, target_dir / "ic_launcher.png")
        shutil.copy2(icon_file, target_dir / "ic_launcher_round.png")
    
    print("✅ Estrutura mínima do projeto criada!")
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Android Build Environment Setup")
    print("=" * 60)
    
    try:
        # Passo 1: Configurar Android SDK
        sdk_dir = setup_android_sdk()
        if not sdk_dir:
            print("❌ Falha ao configurar Android SDK")
            return False
        
        # Passo 2: Instalar componentes
        if not install_android_components(sdk_dir):
            print("❌ Falha ao instalar componentes Android")
            return False
        
        # Passo 3: Configurar variáveis de ambiente
        setup_environment_variables(sdk_dir)
        
        # Passo 4: Criar estrutura do projeto
        if not create_minimal_project():
            print("❌ Falha ao criar estrutura do projeto")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Ambiente configurado com sucesso!")
        print("=" * 60)
        print("\n💡 Próximos passos:")
        print("1. Reinicie o terminal para carregar as variáveis de ambiente")
        print("2. Execute: python validate_build_environment.py")
        print("3. Execute: python create_minimal_apk.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 