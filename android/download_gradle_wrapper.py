#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para baixar o gradle-wrapper.jar
"""

import urllib.request
import os

def download_gradle_wrapper():
    """Baixa o gradle-wrapper.jar"""
    url = "https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar"
    output_path = "gradle/wrapper/gradle-wrapper.jar"
    
    print("📥 Baixando gradle-wrapper.jar...")
    
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ Gradle wrapper baixado com sucesso: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao baixar gradle wrapper: {e}")
        return False

if __name__ == "__main__":
    download_gradle_wrapper() 