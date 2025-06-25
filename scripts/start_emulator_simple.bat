@echo off
echo ============================================================
echo TarefaMagica - Iniciador Simples de Emulador
echo ============================================================

set ANDROID_HOME=C:\Users\joaoc\Android\Sdk
set ANDROID_SDK_ROOT=C:\Users\joaoc\Android\Sdk
set PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\emulator;%PATH%

echo [INFO] Configurando ambiente...
echo [INFO] ANDROID_HOME=%ANDROID_HOME%

echo.
echo [START] Iniciando emulador Medium_Phone_API_36.0...
echo [INFO] Aguarde o emulador carregar (pode demorar 5-10 minutos)
echo [INFO] Uma janela do emulador será aberta
echo.

"%ANDROID_HOME%\emulator\emulator.exe" -avd Medium_Phone_API_36.0

echo.
echo [INFO] Emulador iniciado!
echo [INFO] Quando o emulador carregar, execute:
echo [INFO] python install_apk_automated.py
echo.
pause 