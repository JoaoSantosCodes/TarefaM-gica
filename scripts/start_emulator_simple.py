#!/usr/bin/env python3
"""
Script simples para iniciar o emulador TarefaMagica_Simple
TarefaMagica - Simple Emulator Starter
"""

import os
import subprocess
import time
from pathlib import Path

def start_emulator():
    """Inicia o emulador TarefaMagica_Simple"""
    print("[START] Iniciando emulador TarefaMagica_Simple...")
    
    sdk_path = Path.home() / "Android" / "Sdk"
    emulator = sdk_path / "emulator" / "emulator.exe"
    
    if not emulator.exists():
        print(f"[ERROR] Emulador não encontrado: {emulator}")
        return False
    
    try:
        # Comando para iniciar emulador
        cmd = [
            str(emulator),
            "-avd", "TarefaMagica_Simple",
            "-no-snapshot-load",
            "-gpu", "host",
            "-memory", "2048"
        ]
        
        print(f"[CMD] Executando: {' '.join(cmd)}")
        print("[INFO] Emulador iniciando... (pode demorar alguns minutos)")
        print("[INFO] Uma janela do emulador será aberta")
        
        # Inicia em background
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print(f"[OK] Emulador iniciado (PID: {process.pid})")
        print("[INFO] Aguarde o emulador carregar completamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar emulador: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Iniciador Simples de Emulador")
    print("=" * 60)
    
    if start_emulator():
        print("\n[SUCCESS] Emulador iniciado!")
        print("\n[NEXT] Próximos passos:")
        print("1. Aguarde o emulador carregar completamente")
        print("2. Execute: python install_apk_automated.py")
        print("3. Ou instale manualmente a APK 'TarefaMagica-debug.apk'")
    else:
        print("\n[ERROR] Falha ao iniciar emulador")
    
    return True

if __name__ == "__main__":
    main() 