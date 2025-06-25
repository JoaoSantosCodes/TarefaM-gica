#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Script de Build usando Android Studio - TarefaMágica
Usa o Android Studio instalado para buildar o projeto
"""

import os
import subprocess
import platform
import json
from pathlib import Path

class AndroidStudioBuild:
    """Build usando Android Studio"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.android_dir = self.project_root / "android"
        self.build_status = {}
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Registra um passo do build"""
        self.build_status[step] = {
            "status": status,
            "details": details
        }
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔄"
        print(f"{status_icon} {step}: {details}")
        
    def find_android_studio(self):
        """Encontra o Android Studio instalado"""
        print("🔍 Procurando Android Studio...")
        
        # Locais comuns do Android Studio no Windows
        studio_locations = [
            "C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe",
            "C:\\Program Files (x86)\\Android\\Android Studio\\bin\\studio64.exe",
            str(Path.home() / "AppData/Local/Android/Android Studio/bin/studio64.exe"),
            str(Path.home() / "AppData/Local/Android/Android Studio/bin/studio.exe")
        ]
        
        for location in studio_locations:
            if Path(location).exists():
                self.log_step("Android Studio", "SUCCESS", f"Encontrado em: {location}")
                return location
                
        self.log_step("Android Studio", "FAILED", "Android Studio não encontrado")
        return None
        
    def find_android_sdk(self):
        """Encontra o Android SDK"""
        print("📱 Procurando Android SDK...")
        
        # Verificar variáveis de ambiente
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        
        if android_home and Path(android_home).exists():
            self.log_step("Android SDK", "SUCCESS", f"Encontrado em: {android_home}")
            return android_home
            
        # Locais padrão
        default_locations = [
            Path.home() / "AppData/Local/Android/Sdk",
            Path.home() / "Library/Android/sdk",
            Path.home() / "Android/Sdk",
        ]
        
        for location in default_locations:
            if location.exists():
                self.log_step("Android SDK", "SUCCESS", f"Encontrado em: {location}")
                return str(location)
                
        self.log_step("Android SDK", "FAILED", "Android SDK não encontrado")
        return None
        
    def find_java(self):
        """Encontra o Java"""
        print("☕ Procurando Java...")
        
        # Verificar se java está no PATH
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stderr.split('\n')[0]
                self.log_step("Java", "SUCCESS", f"Encontrado: {version_line}")
                return True
        except:
            pass
            
        # Procurar em locais comuns
        java_locations = [
            "C:\\Program Files\\Java\\jdk-17\\bin\\java.exe",
            "C:\\Program Files\\Eclipse Adoptium\\jdk-17\\bin\\java.exe",
            "C:\\Program Files\\OpenJDK\\jdk-17\\bin\\java.exe",
            "C:\\Program Files\\Java\\jdk-11\\bin\\java.exe",
            "C:\\Program Files\\Java\\jdk-8\\bin\\java.exe"
        ]
        
        for location in java_locations:
            if Path(location).exists():
                self.log_step("Java", "SUCCESS", f"Encontrado em: {location}")
                return True
                
        self.log_step("Java", "FAILED", "Java não encontrado")
        return False
        
    def setup_environment(self):
        """Configura o ambiente"""
        print("🔧 Configurando ambiente...")
        
        # Configurar Android SDK
        sdk_path = self.find_android_sdk()
        if sdk_path:
            os.environ['ANDROID_HOME'] = sdk_path
            os.environ['ANDROID_SDK_ROOT'] = sdk_path
            self.log_step("Environment", "SUCCESS", f"ANDROID_HOME configurado: {sdk_path}")
            return True
        else:
            self.log_step("Environment", "FAILED", "Não foi possível configurar ANDROID_HOME")
            return False
            
    def build_with_gradle(self):
        """Build usando Gradle diretamente"""
        print("🔨 Buildando com Gradle...")
        
        try:
            # Navegar para o diretório Android
            os.chdir(self.android_dir)
            
            # Verificar se gradlew existe
            if not Path("gradlew.bat").exists():
                self.log_step("Gradle Wrapper", "FAILED", "gradlew.bat não encontrado")
                return False
                
            # Tentar build
            print("🚀 Executando build...")
            result = subprocess.run([".\\gradlew.bat", "assembleDebug", "--info"], 
                                  capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0:
                # Verificar APK
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
            
    def create_build_instructions(self):
        """Cria instruções para build manual"""
        print("📝 Criando instruções de build...")
        
        instructions = {
            "title": "Instruções para Build Manual - TarefaMágica",
            "steps": [
                {
                    "step": 1,
                    "title": "Instalar Java JDK",
                    "description": "Baixar e instalar Java JDK 17 de https://adoptium.net/",
                    "command": "java -version"
                },
                {
                    "step": 2,
                    "title": "Abrir Android Studio",
                    "description": "Abrir o projeto TarefaMágica no Android Studio",
                    "command": "File > Open > Selecionar pasta android/"
                },
                {
                    "step": 3,
                    "title": "Sincronizar Projeto",
                    "description": "Deixar o Android Studio sincronizar e baixar dependências",
                    "command": "Sync Now (quando aparecer)"
                },
                {
                    "step": 4,
                    "title": "Build APK",
                    "description": "Gerar o APK de debug",
                    "command": "Build > Build APK(s)"
                },
                {
                    "step": 5,
                    "title": "Localizar APK",
                    "description": "O APK estará em: android/app/build/outputs/apk/debug/app-debug.apk",
                    "command": "Navegar até o arquivo"
                }
            ],
            "troubleshooting": [
                "Se o Java não for encontrado, instale o JDK 17",
                "Se o Android SDK não for encontrado, instale o Android Studio",
                "Se houver erros de dependências, execute 'Sync Project with Gradle Files'",
                "Se houver problemas de permissão, execute como administrador"
            ]
        }
        
        # Salvar instruções
        instructions_file = self.project_root / "outputs" / "build_instructions.json"
        instructions_file.parent.mkdir(exist_ok=True)
        
        with open(instructions_file, 'w', encoding='utf-8') as f:
            json.dump(instructions, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Instruções salvas em: {instructions_file}")
        
        # Mostrar instruções
        print("\n📋 INSTRUÇÕES PARA BUILD MANUAL:")
        for step in instructions["steps"]:
            print(f"\n{step['step']}. {step['title']}")
            print(f"   {step['description']}")
            print(f"   Comando: {step['command']}")
            
    def generate_build_report(self):
        """Gera relatório do build"""
        print("\n📊 Gerando relatório de build...")
        
        report = {
            "timestamp": str(Path.cwd()),
            "system": platform.system(),
            "build_steps": self.build_status,
            "success_count": sum(1 for step in self.build_status.values() if step["status"] == "SUCCESS"),
            "total_steps": len(self.build_status)
        }
        
        # Salvar relatório
        report_file = self.project_root / "outputs" / "android_build_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Relatório salvo em: {report_file}")
        
        # Mostrar resumo
        print(f"\n🎯 RESUMO DO BUILD:")
        print(f"✅ Passos bem-sucedidos: {report['success_count']}/{report['total_steps']}")
        
        for step, info in self.build_status.items():
            status_icon = "✅" if info["status"] == "SUCCESS" else "❌"
            print(f"{status_icon} {step}: {info['details']}")
            
    def run_build(self):
        """Executa o processo de build"""
        print("🚀 INICIANDO BUILD DO PROJETO ANDROID")
        print("=" * 50)
        
        # Verificar componentes
        studio_path = self.find_android_studio()
        sdk_path = self.find_android_sdk()
        java_ok = self.find_java()
        
        # Configurar ambiente
        env_ok = self.setup_environment()
        
        # Tentar build
        build_ok = False
        if env_ok:
            build_ok = self.build_with_gradle()
            
        # Gerar relatório e instruções
        self.generate_build_report()
        self.create_build_instructions()
        
        if build_ok:
            print("\n🎉 BUILD CONCLUÍDO COM SUCESSO!")
            print("📱 APK gerado e pronto para instalação")
            print("📍 Localização: android/app/build/outputs/apk/debug/app-debug.apk")
        else:
            print("\n⚠️ BUILD NÃO CONCLUÍDO")
            print("📋 Consulte as instruções manuais geradas")
            
        return build_ok

def main():
    """Função principal"""
    builder = AndroidStudioBuild()
    success = builder.run_build()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Instalar o APK em um dispositivo Android")
        print("2. Testar as funcionalidades do app")
        print("3. Preparar para publicação na Google Play")
    else:
        print("\n🔧 SOLUÇÕES ALTERNATIVAS:")
        print("1. Seguir as instruções manuais geradas")
        print("2. Usar Android Studio para build visual")
        print("3. Configurar CI/CD para build automático")

if __name__ == "__main__":
    main() 