# 🚀 TarefaMágica - APK Builder

Scripts automatizados para configurar o ambiente de desenvolvimento Android e gerar APKs do projeto TarefaMágica.

## 📋 Pré-requisitos

- **Java 17 ou superior** (já instalado ✅)
- **Python 3.7+** (já disponível ✅)
- **Windows 10/11** (sistema atual ✅)

## 🎯 Opções de Build

### Opção 1: Build Completo Automatizado (Recomendado)

Execute o script master que faz tudo automaticamente:

```bash
python setup_complete_environment.py
```

**O que este script faz:**
1. ✅ Verifica Java
2. 📱 Instala Android SDK automaticamente
3. 📁 Configura estrutura do projeto
4. 🔧 Configura gradle.properties
5. 🎯 Gera APK automaticamente

**⏱️ Tempo estimado:** 10-20 minutos

### Opção 2: Build Manual (Passo a Passo)

Se preferir executar cada etapa separadamente:

#### Passo 1: Instalar Android SDK
```bash
python install_android_sdk_complete.py
```

#### Passo 2: Configurar projeto
```bash
python setup_android_simple.py
```

#### Passo 3: Gerar APK
```bash
python build_apk_final.py
```

### Opção 3: Build Rápido (Se SDK já instalado)

Se você já tem o Android Studio instalado:

```bash
python build_apk_final.py
```

## 📁 Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `setup_complete_environment.py` | **Script master** - Faz tudo automaticamente |
| `install_android_sdk_complete.py` | Instala Android SDK completo |
| `setup_android_simple.py` | Configura estrutura do projeto |
| `build_apk_final.py` | Gera APK final |
| `validate_build_environment.py` | Valida ambiente de build |
| `quick_validate.py` | Validação rápida |
| `build_apk_automated.bat` | Script batch para Windows |

## 🔧 Configuração Manual (Alternativa)

Se os scripts automáticos não funcionarem:

### 1. Instalar Android Studio
- Baixe de: https://developer.android.com/studio
- Instale normalmente
- Abra o Android Studio
- Vá em **SDK Manager**
- Instale:
  - Android SDK Platform-Tools
  - Android SDK Build-Tools (34.0.0)
  - Android SDK Platform (API 34)

### 2. Configurar Variáveis de Ambiente
```
ANDROID_HOME = C:\Users\[seu_usuario]\AppData\Local\Android\Sdk
ANDROID_SDK_ROOT = C:\Users\[seu_usuario]\AppData\Local\Android\Sdk
```

### 3. Adicionar ao PATH
```
C:\Users\[seu_usuario]\AppData\Local\Android\Sdk\platform-tools
C:\Users\[seu_usuario]\AppData\Local\Android\Sdk\cmdline-tools\latest\bin
```

## 📱 Instalando a APK

Após gerar a APK:

1. **Conecte um dispositivo Android** via USB
2. **Ative a depuração USB** no dispositivo:
   - Configurações > Sobre o telefone > Toque 7x em "Número da versão"
   - Configurações > Opções do desenvolvedor > Depuração USB
3. **Instale a APK**:
   ```bash
   adb install outputs/TarefaMagica-debug.apk
   ```

## 🎯 Localização da APK

A APK será gerada em:
```
outputs/TarefaMagica-debug.apk
```

## 🔍 Solução de Problemas

### Erro: "Java não encontrado"
- Instale Java 17 ou superior
- Configure JAVA_HOME

### Erro: "Android SDK não configurado"
- Execute: `python install_android_sdk_complete.py`
- Ou instale Android Studio manualmente

### Erro: "Gradle não funcionando"
- Execute: `python setup_android_simple.py`
- Verifique se o gradle.properties está correto

### Erro: "Compilação Kotlin falhou"
- Normal sem Android SDK instalado
- Instale o Android SDK primeiro

### Erro: "Caracteres não-ASCII no caminho"
- Já configurado no gradle.properties
- Se persistir, mova o projeto para um diretório sem acentos

## 📊 Status do Ambiente

Para verificar o status atual:

```bash
python quick_validate.py
```

## 🎉 Sucesso!

Quando tudo estiver funcionando, você verá:

```
🎉 APK GERADA COM SUCESSO!
📁 Localização: C:\...\outputs\TarefaMagica-debug.apk
📏 Tamanho: XX.XX MB
```

## 📞 Suporte

Se encontrar problemas:

1. Execute `python quick_validate.py` para diagnóstico
2. Verifique se Java 17+ está instalado
3. Tente o script master: `python setup_complete_environment.py`
4. Se persistir, instale Android Studio manualmente

---

**🎯 Objetivo:** Gerar APK funcional do TarefaMágica para testes e desenvolvimento! 