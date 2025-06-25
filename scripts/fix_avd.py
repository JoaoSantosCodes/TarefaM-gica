#!/usr/bin/env python3
"""
Script para corrigir o problema do AVD
TarefaMagica - AVD Fixer
"""

import os
import subprocess
import shutil
from pathlib import Path

def delete_broken_avd():
    """Deleta o AVD quebrado"""
    print("[DELETE] Deletando AVD quebrado...")
    
    avd_home = Path.home() / ".android" / "avd"
    broken_avd = avd_home / "Medium_Phone.avd"
    
    if broken_avd.exists():
        try:
            shutil.rmtree(broken_avd)
            print(f"[OK] AVD deletado: {broken_avd}")
            return True
        except Exception as e:
            print(f"[ERROR] Erro ao deletar AVD: {e}")
            return False
    else:
        print("[INFO] AVD não encontrado para deletar")
        return True

def create_simple_avd():
    """Cria um AVD simples e funcional"""
    print("[CREATE] Criando AVD simples...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    avd_manager = sdk_path / "cmdline-tools" / "bin" / "avdmanager.bat"
    
    if not avd_manager.exists():
        print(f"[ERROR] AVD Manager não encontrado: {avd_manager}")
        return False
    
    # Configurações do AVD simples
    avd_name = "TarefaMagica_Simple"
    device = "pixel_2"  # Dispositivo mais simples
    target = "android-30"  # Android 11 (mais estável)
    abi = "x86_64"
    
    try:
        # Comando para criar AVD
        cmd = [
            str(avd_manager), "create", "avd",
            "--name", avd_name,
            "--package", f"system-images;{target};google_apis;{abi}",
            "--device", device,
            "--force"
        ]
        
        print(f"[CMD] Executando: {' '.join(cmd)}")
        
        # Executa com input automático
        result = subprocess.run(cmd, 
                              input="no\n",  # Não criar hardware profile customizado
                              capture_output=True, 
                              text=True, 
                              timeout=120)
        
        if result.returncode == 0:
            print(f"[SUCCESS] AVD '{avd_name}' criado com sucesso!")
            return True
        else:
            print(f"[ERROR] Erro ao criar AVD: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar AVD: {e}")
        return False

def test_avd():
    """Testa se o AVD funciona"""
    print("[TEST] Testando AVD...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    emulator = sdk_path / "emulator" / "emulator.exe"
    
    if not emulator.exists():
        print(f"[ERROR] Emulador não encontrado: {emulator}")
        return False
    
    try:
        # Lista AVDs disponíveis
        result = subprocess.run([str(emulator), "-list-avds"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            avds = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            print(f"[OK] AVDs disponíveis: {avds}")
            return len(avds) > 0
        else:
            print(f"[ERROR] Erro ao listar AVDs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao testar AVD: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Corretor de AVD")
    print("=" * 60)
    
    # Passo 1: Deletar AVD quebrado
    if not delete_broken_avd():
        print("[ERROR] Falha ao deletar AVD quebrado")
        return False
    
    # Passo 2: Criar AVD simples
    if not create_simple_avd():
        print("[ERROR] Falha ao criar AVD simples")
        return False
    
    # Passo 3: Testar AVD
    if not test_avd():
        print("[ERROR] Falha ao testar AVD")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] AVD corrigido com sucesso!")
    print("=" * 60)
    print("\n[NEXT] Próximos passos:")
    print("1. Execute: python start_emulator_simple.py")
    print("2. Ou use o Android Studio para iniciar o emulador")
    print("3. Depois execute: python install_apk_automated.py")
    
    return True

if __name__ == "__main__":
    main() 