#!/usr/bin/env python3
"""
Script para criar uma APK mínima e funcional do TarefaMágica
"""

import os
import subprocess
import shutil
from pathlib import Path
import zipfile
import tempfile

def create_minimal_project():
    """Cria um projeto Android mínimo e funcional"""
    print("[CREATE] Criando projeto Android mínimo...")
    
    # Cria diretório temporário
    temp_dir = Path(tempfile.mkdtemp())
    project_dir = temp_dir / "TarefaMagica"
    project_dir.mkdir()
    
    # Estrutura básica do projeto
    android_dir = project_dir / "android"
    android_dir.mkdir()
    
    app_dir = android_dir / "app"
    app_dir.mkdir()
    
    src_dir = app_dir / "src" / "main"
    src_dir.mkdir(parents=True)
    
    java_dir = src_dir / "java" / "com" / "tarefamagica" / "app"
    java_dir.mkdir(parents=True)
    
    res_dir = src_dir / "res"
    res_dir.mkdir()
    
    values_dir = res_dir / "values"
    values_dir.mkdir()
    
    # Arquivo build.gradle do projeto
    project_gradle = android_dir / "build.gradle"
    project_gradle.write_text("""
plugins {
    id 'com.android.application' version '8.1.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.0' apply false
}
""")
    
    # Arquivo settings.gradle
    settings_gradle = android_dir / "settings.gradle"
    settings_gradle.write_text("""
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "TarefaMagica"
include ':app'
""")
    
    # Arquivo gradle.properties
    gradle_props = android_dir / "gradle.properties"
    gradle_props.write_text("""
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
android.nonTransitiveRClass=true
""")
    
    # Arquivo build.gradle do app
    app_gradle = app_dir / "build.gradle"
    app_gradle.write_text("""
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.tarefamagica.app'
    compileSdk 34

    defaultConfig {
        applicationId "com.tarefamagica.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary true
        }
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = '1.8'
    }
    buildFeatures {
        compose true
    }
    composeOptions {
        kotlinCompilerExtensionVersion '1.5.1'
    }
    packaging {
        resources {
            excludes += '/META-INF/{AL2.0,LGPL2.1}'
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.2'
    implementation platform('androidx.compose:compose-bom:2023.08.00')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.ui:ui-graphics'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.compose.material3:material3'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    androidTestImplementation platform('androidx.compose:compose-bom:2023.08.00')
    androidTestImplementation 'androidx.compose.ui:ui-test-junit4'
    debugImplementation 'androidx.compose.ui:ui-tooling'
    debugImplementation 'androidx.compose.ui:ui-test-manifest'
}
""")
    
    # AndroidManifest.xml
    manifest_file = src_dir / "AndroidManifest.xml"
    manifest_file.write_text("""
<?xml version="1.0" encoding="utf-8"?>
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

</manifest>
""")
    
    # MainActivity.kt simplificado
    main_activity = java_dir / "MainActivity.kt"
    main_activity.write_text("""
package com.tarefamagica.app

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
}
""")
    
    # Tema simplificado
    theme_dir = java_dir / "theme"
    theme_dir.mkdir()
    
    theme_file = theme_dir / "Theme.kt"
    theme_file.write_text("""
package com.tarefamagica.app.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun TarefaMagicaTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
""")
    
    # Cores
    color_file = theme_dir / "Color.kt"
    color_file.write_text("""
package com.tarefamagica.app.theme

import androidx.compose.ui.graphics.Color

val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
""")
    
    # Tipografia
    type_file = theme_dir / "Type.kt"
    type_file.write_text("""
package com.tarefamagica.app.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    )
)
""")
    
    # Strings
    strings_file = values_dir / "strings.xml"
    strings_file.write_text("""
<resources>
    <string name="app_name">TarefaMágica</string>
</resources>
""")
    
    # Temas
    themes_file = values_dir / "themes.xml"
    themes_file.write_text("""
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.TarefaMagica" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
""")
    
    # Gradle wrapper
    gradle_wrapper_dir = android_dir / "gradle" / "wrapper"
    gradle_wrapper_dir.mkdir(parents=True)
    
    wrapper_props = gradle_wrapper_dir / "gradle-wrapper.properties"
    wrapper_props.write_text("""
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")
    
    # Gradle wrapper scripts
    gradlew = android_dir / "gradlew.bat"
    gradlew.write_text("""
@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar


@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
@rem End local scope for the variables with windows NT shell
if "%ERRORLEVEL%"=="0" goto mainEnd

:fail
rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd_ return code.
if not "" == "%GRADLE_EXIT_CONSOLE%" exit 1
exit /b 1

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
""")
    
    return project_dir

def build_apk(project_dir):
    """Compila a APK"""
    print("[BUILD] Compilando APK...")
    
    android_dir = project_dir / "android"
    
    # Configura variáveis de ambiente
    env = os.environ.copy()
    env['ANDROID_HOME'] = str(Path.home() / "Android" / "Sdk")
    env['ANDROID_SDK_ROOT'] = str(Path.home() / "Android" / "Sdk")
    
    try:
        # Executa o build
        result = subprocess.run(
            [str(android_dir / "gradlew.bat"), "assembleDebug"],
            cwd=android_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[SUCCESS] APK compilada com sucesso!")
            
            # Localiza a APK
            apk_path = android_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
            if apk_path.exists():
                # Copia para o diretório raiz
                output_path = Path.cwd() / "TarefaMagica.apk"
                shutil.copy2(apk_path, output_path)
                print(f"[APK] APK gerada: {output_path}")
                return True
            else:
                print("[ERROR] APK não encontrada")
                return False
        else:
            print(f"[ERROR] Erro na compilação: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout na compilação")
        return False
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TarefaMágica - Gerador de APK Mínima")
    print("=" * 60)
    
    try:
        # Passo 1: Criar projeto mínimo
        project_dir = create_minimal_project()
        print(f"[OK] Projeto criado em: {project_dir}")
        
        # Passo 2: Compilar APK
        if build_apk(project_dir):
            print("\n" + "=" * 60)
            print("[SUCCESS] APK gerada com sucesso!")
            print("=" * 60)
            print("\n[NEXT] Próximos passos:")
            print("1. Instale a APK no seu dispositivo Android")
            print("2. Teste a funcionalidade básica")
            print("3. A APK está pronta para desenvolvimento!")
        else:
            print("\n[ERROR] Falha na geração da APK")
            
    except Exception as e:
        print(f"[ERROR] Erro durante o processo: {e}")

if __name__ == "__main__":
    main() 