#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Script para Abrir Android Studio - TarefaMágica
Abre o Android Studio diretamente no projeto para build manual
"""

import os
import subprocess
import sys
from pathlib import Path

def find_android_studio():
    """Encontra o Android Studio instalado"""
    print("[FIND] Procurando Android Studio...")
    
    possible_paths = [
        "C:\\Program Files\\Android\\Android Studio\\bin\\studio64.exe",
        "C:\\Program Files (x86)\\Android\\Android Studio\\bin\\studio64.exe",
        os.path.expanduser("~\\AppData\\Local\\Android\\Sdk\\tools\\studio64.exe")
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            print(f"[OK] Android Studio encontrado: {path}")
            return path
    
    print("[ERROR] Android Studio não encontrado")
    return None

def open_android_studio():
    """Abre o Android Studio"""
    studio_path = find_android_studio()
    if not studio_path:
        return False
    
    try:
        print("[OPEN] Abrindo Android Studio...")
        subprocess.Popen([studio_path])
        print("[SUCCESS] Android Studio iniciado!")
        return True
    except Exception as e:
        print(f"[ERROR] Erro ao abrir Android Studio: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Android Studio Launcher")
    print("=" * 60)
    
    if open_android_studio():
        print("\n[INFO] Android Studio foi aberto!")
        print("\n[NEXT] Próximos passos:")
        print("1. No Android Studio, vá em 'Tools' > 'AVD Manager'")
        print("2. Clique em 'Play' ao lado do AVD 'Medium_Phone_API_36.0'")
        print("3. Aguarde o emulador carregar completamente")
        print("4. Execute: python install_apk_automated.py")
        print("5. Ou instale manualmente a APK 'TarefaMagica-debug.apk'")
    else:
        print("\n[ERROR] Não foi possível abrir o Android Studio")
        print("[INFO] Instale o Android Studio primeiro:")
        print("  https://developer.android.com/studio")
    
    return True

if __name__ == "__main__":
    sys.exit(main()) 