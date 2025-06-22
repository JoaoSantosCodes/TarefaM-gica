# 🤝 Guia de Contribuição - TarefaMágica

Obrigado por considerar contribuir com o **TarefaMágica**! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Índice

- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Solicitando Funcionalidades](#solicitando-funcionalidades)
- [Código de Conduta](#código-de-conduta)

---

## 🚀 Como Contribuir

### 📝 Tipos de Contribuição

- **🐛 Bug Reports** - Reportar problemas encontrados
- **✨ Feature Requests** - Sugerir novas funcionalidades
- **🔧 Code Contributions** - Contribuir com código
- **📚 Documentation** - Melhorar documentação
- **🧪 Testing** - Adicionar ou melhorar testes
- **🎨 Design** - Sugerir melhorias de UI/UX

### 🎯 Áreas de Foco

#### 🧒 **Experiência da Criança**
- Interface intuitiva e amigável
- Gamificação envolvente
- Feedback visual claro
- Acessibilidade

#### 👨‍👩‍👧 **Experiência dos Pais**
- Controle e monitoramento
- Relatórios claros
- Configurações flexíveis
- Segurança

#### 🔧 **Aspectos Técnicos**
- Performance otimizada
- Código limpo e bem documentado
- Testes abrangentes
- Segurança robusta

---

## 🛠️ Configuração do Ambiente

### 📋 Pré-requisitos

- **Flutter SDK** (versão estável)
- **Android Studio** ou **VS Code**
- **Git**
- **Conta Firebase** (para desenvolvimento)

### 🔧 Setup Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/JoaoSantosCodes/TarefaMágica.git
   cd TarefaMágica
   ```

2. **Instale as dependências**
   ```bash
   flutter pub get
   ```

3. **Configure o Firebase**
   - Crie um projeto no Firebase Console
   - Baixe os arquivos de configuração
   - Configure as credenciais

4. **Execute o projeto**
   ```bash
   flutter run
   ```

### 🧪 Executando Testes

```bash
# Testes unitários
flutter test

# Testes de integração
flutter test integration_test/

# Análise de código
flutter analyze
```

---

## 📝 Padrões de Código

### 🎨 **Convenções de Nomenclatura**

#### **Dart/Flutter**
```dart
// Classes: PascalCase
class TaskManager {}

// Variáveis e funções: camelCase
String taskTitle;
void createTask() {}

// Constantes: SCREAMING_SNAKE_CASE
const String APP_NAME = 'TarefaMágica';

// Arquivos: snake_case
task_manager.dart
user_profile_screen.dart
```

#### **Firebase**
```javascript
// Collections: camelCase
users, taskSubmissions, familyGroups

// Fields: camelCase
taskTitle, createdAt, isCompleted

// Functions: camelCase
createTask, approveSubmission, calculateReward
```

### 📁 **Estrutura de Arquivos**

```
lib/
├── main.dart
├── app/
│   ├── app.dart
│   └── routes.dart
├── core/
│   ├── constants/
│   ├── utils/
│   └── services/
├── features/
│   ├── auth/
│   ├── tasks/
│   ├── rewards/
│   └── gamification/
├── shared/
│   ├── widgets/
│   ├── models/
│   └── providers/
└── assets/
    ├── images/
    ├── fonts/
    └── icons/
```

### 🔍 **Comentários e Documentação**

```dart
/// Classe responsável por gerenciar as tarefas do usuário.
/// 
/// Esta classe fornece métodos para criar, atualizar e deletar tarefas,
/// além de gerenciar o estado das tarefas no aplicativo.
class TaskManager {
  /// Cria uma nova tarefa no sistema.
  /// 
  /// [title] - Título da tarefa
  /// [description] - Descrição detalhada da tarefa
  /// [reward] - Valor da recompensa em centavos
  /// 
  /// Retorna um [Future<Task>] com a tarefa criada.
  Future<Task> createTask({
    required String title,
    required String description,
    required int reward,
  }) async {
    // Implementação...
  }
}
```

### 🧪 **Testes**

```dart
// Teste unitário
test('should create task successfully', () async {
  // Arrange
  final taskManager = TaskManager();
  final taskData = TaskData(
    title: 'Arrumar a cama',
    description: 'Fazer a cama pela manhã',
    reward: 200, // R$2,00
  );

  // Act
  final task = await taskManager.createTask(taskData);

  // Assert
  expect(task.title, equals('Arrumar a cama'));
  expect(task.reward, equals(200));
  expect(task.isCompleted, isFalse);
});
```

---

## 🔄 Processo de Pull Request

### 📋 **Checklist Antes do PR**

- [ ] Código segue os padrões do projeto
- [ ] Testes passando localmente
- [ ] Documentação atualizada
- [ ] Screenshots adicionadas (se aplicável)
- [ ] Issue relacionada criada/linkada

### 🔄 **Workflow**

1. **Crie uma branch**
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Faça suas mudanças**
   - Siga os padrões de código
   - Adicione testes
   - Atualize documentação

3. **Commit suas mudanças**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade de gamificação"
   ```

4. **Push para o repositório**
   ```bash
   git push origin feature/nova-funcionalidade
   ```

5. **Crie o Pull Request**
   - Use o template fornecido
   - Descreva as mudanças claramente
   - Linke issues relacionadas

### 📝 **Convenções de Commit**

```
feat: nova funcionalidade
fix: correção de bug
docs: mudanças na documentação
style: formatação, ponto e vírgula, etc.
refactor: refatoração de código
test: adicionando ou corrigindo testes
chore: mudanças em build, configs, etc.
```

---

## 🐛 Reportando Bugs

### 📋 **Informações Necessárias**

- **Descrição clara** do problema
- **Passos para reproduzir**
- **Comportamento esperado**
- **Comportamento atual**
- **Informações do dispositivo**
- **Screenshots** (se aplicável)
- **Logs de erro**

### 📱 **Template de Bug Report**

Use o template `🐛 Bug Report` ao criar uma issue no GitHub.

---

## ✨ Solicitando Funcionalidades

### 💡 **Diretrizes**

- Descreva o problema que a funcionalidade resolveria
- Explique como a funcionalidade funcionaria
- Considere o impacto na experiência do usuário
- Avalie a complexidade técnica

### 🎯 **Template de Feature Request**

Use o template `✨ Feature Request` ao criar uma issue no GitHub.

---

## 🤝 Código de Conduta

### 📜 **Nossos Padrões**

- Seja respeitoso e inclusivo
- Use linguagem apropriada
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade

### 🚫 **Comportamento Inaceitável**

- Linguagem ofensiva ou discriminatória
- Trolling ou comentários insultuosos
- Assédio de qualquer forma
- Publicar informações privadas

### 📞 **Como Reportar**

Se você testemunhar ou sofrer comportamento inaceitável, entre em contato através de:
- Email: [seu-email@exemplo.com]
- GitHub Issues: [Crie uma issue privada]

---

## 🏆 Reconhecimento

### 🌟 **Contribuidores**

- Seu nome será adicionado ao README
- Você receberá crédito nos releases
- Suas contribuições serão reconhecidas

### 🎖️ **Níveis de Contribuição**

- **🥉 Bronze** - 1-5 contribuições
- **🥈 Prata** - 6-15 contribuições
- **🥇 Ouro** - 16+ contribuições
- **💎 Diamante** - Contribuições excepcionais

---

## 📞 Suporte

### 💬 **Canais de Comunicação**

- **GitHub Issues** - Para bugs e funcionalidades
- **GitHub Discussions** - Para perguntas e discussões
- **Email** - Para assuntos privados

### 📚 **Recursos Úteis**

- [Documentação Flutter](https://docs.flutter.dev/)
- [Documentação Firebase](https://firebase.google.com/docs)
- [Guia de Dart](https://dart.dev/guides)

---

## 🙏 Agradecimentos

Obrigado por contribuir com o **TarefaMágica**! Suas contribuições ajudam a criar uma experiência melhor para crianças e famílias em todo o mundo.

---

**Juntos, vamos tornar as tarefas domésticas mágicas! ✨🧒** 