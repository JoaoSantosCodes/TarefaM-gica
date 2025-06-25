@echo off
echo ========================================
echo    Fix Gradle - Solucao Completa
echo ========================================
echo.

echo [1/6] Parando todos os processos do Gradle...
taskkill /f /im java.exe 2>nul
taskkill /f /im gradle.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/6] Removendo completamente a pasta .gradle...
if exist "%USERPROFILE%\.gradle" (
    echo Removendo: %USERPROFILE%\.gradle
    rmdir /s /q "%USERPROFILE%\.gradle" 2>nul
    if errorlevel 1 (
        echo Tentando forcar remocao...
        rd /s /q "%USERPROFILE%\.gradle" 2>nul
    )
)

echo [3/6] Criando nova estrutura .gradle...
mkdir "%USERPROFILE%\.gradle" 2>nul
mkdir "%USERPROFILE%\.gradle\wrapper" 2>nul
mkdir "%USERPROFILE%\.gradle\wrapper\dists" 2>nul

echo [4/6] Configurando permissoes completas...
icacls "%USERPROFILE%\.gradle" /grant "%USERNAME%":(OI)(CI)F /T >nul 2>&1
icacls "%USERPROFILE%\.gradle\wrapper" /grant "%USERNAME%":(OI)(CI)F /T >nul 2>&1
icacls "%USERPROFILE%\.gradle\wrapper\dists" /grant "%USERNAME%":(OI)(CI)F /T >nul 2>&1

echo [5/6] Verificando estrutura criada...
dir "%USERPROFILE%\.gradle\wrapper\dists"

echo [6/6] Configurando Java 17...
set JAVA_HOME=C:\Java17\jdk-17.0.10+7
set PATH=C:\Java17\jdk-17.0.10+7\bin;%PATH%

echo.
echo ========================================
echo    Configuracao concluida!
echo ========================================
echo.
echo Agora tente executar:
echo gradlew.bat assembleDebug
echo.
echo Se ainda der erro, reinicie o computador
echo e tente novamente.
echo.
pause 