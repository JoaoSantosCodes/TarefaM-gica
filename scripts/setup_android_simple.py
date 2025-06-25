#!/usr/bin/env python3
"""
Script simples para configurar ambiente de build Android
TarefaMágica - Simple Android Build Setup
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def check_java():
    """Verifica se o Java está instalado"""
    print("☕ Verificando Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Java encontrado!")
        print(result.stderr.strip())
        return True
    except Exception as e:
        print(f"❌ Java não encontrado: {e}")
        return False

def setup_android_sdk_manual():
    """Configura Android SDK manualmente"""
    print("📱 Configurando Android SDK...")
    
    # Verifica se já está configurado
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and Path(android_home).exists():
        print(f"✅ Android SDK já configurado: {android_home}")
        return android_home
    
    print("⚠️  Android SDK não encontrado!")
    print("\n💡 Para instalar o Android SDK:")
    print("1. Baixe o Android Studio de: https://developer.android.com/studio")
    print("2. Instale o Android Studio")
    print("3. Abra o Android Studio e vá em 'SDK Manager'")
    print("4. Instale os seguintes componentes:")
    print("   - Android SDK Platform-Tools")
    print("   - Android SDK Build-Tools (versão 34.0.0)")
    print("   - Android SDK Platform (API 34)")
    print("5. Configure as variáveis de ambiente:")
    print("   ANDROID_HOME = C:\\Users\\[seu_usuario]\\AppData\\Local\\Android\\Sdk")
    print("   ANDROID_SDK_ROOT = C:\\Users\\[seu_usuario]\\AppData\\Local\\Android\\Sdk")
    
    return None

def create_minimal_project():
    """Cria estrutura mínima do projeto"""
    print("📁 Criando estrutura mínima do projeto...")
    
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
    
    # Cria themes.xml
    themes_content = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.TarefaMagica" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
    </style>
</resources>'''
    
    with open(app_dir / "res" / "values" / "themes.xml", 'w', encoding='utf-8') as f:
        f.write(themes_content)
    
    # Cria colors.xml
    colors_content = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>'''
    
    with open(app_dir / "res" / "values" / "colors.xml", 'w', encoding='utf-8') as f:
        f.write(colors_content)
    
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
    
    # Cria arquivos XML necessários
    xml_files = {
        "data_extraction_rules.xml": '''<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="root" />
    </cloud-backup>
</data-extraction-rules>''',
        
        "backup_rules.xml": '''<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <exclude domain="root" />
</full-backup-content>''',
        
        "file_paths.xml": '''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-path name="external_files" path="."/>
</paths>'''
    }
    
    for filename, content in xml_files.items():
        with open(app_dir / "res" / "xml" / filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Estrutura mínima do projeto criada!")
    return True

def setup_gradle_properties():
    """Configura gradle.properties"""
    print("⚙️  Configurando gradle.properties...")
    
    gradle_props = Path("android/gradle.properties")
    with open(gradle_props, 'w', encoding='utf-8') as f:
        f.write("android.overridePathCheck=true\n")
        f.write("android.useAndroidX=true\n")
        f.write("kotlin.code.style=official\n")
        f.write("android.nonTransitiveRClass=true\n")
        f.write("org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")
    
    print("✅ gradle.properties configurado!")
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 TarefaMágica - Simple Android Build Setup")
    print("=" * 60)
    
    # Passo 1: Verificar Java
    if not check_java():
        print("❌ Java é necessário para continuar")
        return False
    
    # Passo 2: Configurar Android SDK
    sdk_dir = setup_android_sdk_manual()
    
    # Passo 3: Criar estrutura do projeto
    if not create_minimal_project():
        print("❌ Falha ao criar estrutura do projeto")
        return False
    
    # Passo 4: Configurar gradle.properties
    if not setup_gradle_properties():
        print("❌ Falha ao configurar gradle.properties")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Configuração básica concluída!")
    print("=" * 60)
    
    if sdk_dir:
        print("\n✅ Ambiente completo configurado!")
        print("💡 Próximos passos:")
        print("1. Execute: python validate_build_environment.py")
        print("2. Execute: python create_minimal_apk.py")
    else:
        print("\n⚠️  Configuração parcial concluída!")
        print("💡 Para completar a configuração:")
        print("1. Instale o Android Studio")
        print("2. Configure o Android SDK")
        print("3. Configure as variáveis de ambiente")
        print("4. Execute: python validate_build_environment.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 