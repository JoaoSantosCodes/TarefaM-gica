# 🧒 TarefaMágica – Ajude em Casa e Ganhe Recompensas!

<div align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter">
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase">
  <img src="https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white" alt="Dart">
  <br>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue" alt="Status">
  <img src="https://img.shields.io/badge/Version-1.0.0-green" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</div>

## 📱 Sobre o Projeto

**TarefaMágica** é um aplicativo educativo e gamificado que incentiva crianças de 11 e 12 anos a realizarem tarefas domésticas de forma natural, com recompensas simbólicas (até R$10 por tarefa).

### 🎯 Objetivo
Transformar tarefas domésticas em uma experiência divertida e recompensadora, desenvolvendo responsabilidade e bons hábitos nas crianças através da gamificação.

---

## ✨ Funcionalidades Principais

### 👨‍👩‍👧 **Perfil Familiar**
- **Pais/Responsáveis:**
  - Criar e gerenciar tarefas
  - Definir valores por tarefa (até R$10)
  - Aprovar ou rejeitar tarefas realizadas
  - Acompanhar histórico e saldo de recompensas

- **Crianças:**
  - Visualizar tarefas disponíveis
  - Marcar tarefas como concluídas
  - Enviar fotos/vídeos como prova
  - Acompanhar progresso e saldo
  - Personalizar avatar

### 🎮 **Sistema de Gamificação**
- **Níveis e Pontos:** Cada tarefa concede XP e moedas
- **Avatar Personalizável:** Roupinhas e acessórios desbloqueáveis
- **Conquistas:** Badges e missões especiais
- **Loja Interna:** Compras com moedas virtuais

### 💰 **Sistema de Recompensas**
- **Moedas Virtuais:** 1 moeda = R$1 ganho
- **Pagamento Real:** Integração PIX para transferências
- **Histórico:** Rastreamento completo de transações

---

## 🛠️ Stack Tecnológica

### 📱 **Frontend**
- **Framework:** Flutter (Android e iOS)
- **Design:** Material Design 3
- **Estado:** Provider/Riverpod
- **Navegação:** GoRouter
- **Animações:** Flutter Animations

### 🔧 **Backend**
- **Plataforma:** Firebase
- **Banco de Dados:** Firestore (tempo real)
- **Autenticação:** Firebase Auth
- **Storage:** Firebase Storage (mídia)
- **Funções:** Firebase Functions
- **Notificações:** Firebase Cloud Messaging

### 💳 **Pagamentos**
- **API:** PIX (Banco Central)
- **Segurança:** Criptografia e validação
- **Webhooks:** Processamento automático

---

## 📋 Exemplos de Tarefas e Recompensas

| Tarefa | Valor | Moedas |
|--------|-------|--------|
| Arrumar a cama | R$2 | 🪙2 |
| Lavar a louça do almoço | R$5 | 🪙5 |
| Guardar os brinquedos | R$1 | 🪙1 |
| Ajudar a colocar a mesa | R$3 | 🪙3 |
| Regar as plantas | R$2 | 🪙2 |
| Cuidar do pet | R$4 | 🪙4 |

---

## 🚀 Roadmap de Desenvolvimento

### 🟢 **Fase 1 – MVP (1 mês)**
- [x] Documentação e planejamento
- [ ] Cadastro de pais e filhos
- [ ] Adição de tarefas com valor
- [ ] Marcação e aprovação de tarefas
- [ ] Sistema de pontos e saldo
- [ ] Interface básica gamificada

### 🔵 **Fase 2 – Gamificação (2-3 meses)**
- [ ] Sistema de níveis e conquistas
- [ ] Loja interna de itens estéticos
- [ ] Personalização de avatar
- [ ] Missões especiais

### 🟣 **Fase 3 – Expansão**
- [ ] Tarefas recorrentes e lembretes
- [ ] Integração PIX para pagamentos
- [ ] Rankings entre irmãos
- [ ] Missões semanais com bônus

---

## 📁 Estrutura do Projeto

```
TarefaMágica/
├── 📁 checklists/                    # 📋 TODOS OS CHECKLISTS
│   ├── 🎯 CHECKLIST_Geral_Validacao.md     # Master checklist
│   ├── 📋 CHECKLIST_TarefaMágica.md        # Checklist geral
│   ├── 📱 CHECKLIST_Frontend.md            # Checklist Flutter
│   ├── 🔧 CHECKLIST_Backend.md             # Checklist Firebase
│   ├── 🐙 CHECKLIST_GitHub.md              # Checklist GitHub
│   ├── 🤖 CHECKLIST_IA_Validacao.md        # Checklist IA
│   └── 🔍 CHECKLIST_Validacao_Completa.md  # Validação de cobertura
├── 📄 Resumo ChatGPT.txt            # Resumo inicial
├── 📖 README.md                     # Este arquivo
├── 🤝 CONTRIBUTING.md               # Guia de contribuição
├── 🔒 .gitignore                    # Configuração Git
├── 📄 LICENSE                       # Licença MIT
└── 📁 .github/                      # Templates GitHub
    ├── 📝 ISSUE_TEMPLATE/
    │   ├── 🐛 bug_report.md
    │   └── ✨ feature_request.md
    └── 🔄 pull_request_template.md
```

---

## 📊 Status dos Checklists

### ✅ **Checklists Criados (6/11 - 55%)**
- [x] **CHECKLIST_TarefaMágica.md** - Visão geral do projeto
- [x] **CHECKLIST_Frontend.md** - Desenvolvimento Flutter
- [x] **CHECKLIST_Backend.md** - Desenvolvimento Firebase
- [x] **CHECKLIST_GitHub.md** - Gestão do repositório
- [x] **CHECKLIST_IA_Validacao.md** - Validação por IA
- [x] **CHECKLIST_Geral_Validacao.md** - Master checklist

### 🚨 **Checklists Faltando (5/11 - 45%)**
- [ ] **CHECKLIST_Seguranca.md** - 🔥 **CRÍTICO** (LGPD, proteção de dados)
- [ ] **CHECKLIST_Testes.md** - ⚡ **ALTA** (Qualidade, testes)
- [ ] **CHECKLIST_Financeiro.md** - ⚡ **ALTA** (Custos, PIX, viabilidade)
- [ ] **CHECKLIST_Deploy.md** - 📈 **MÉDIA** (App Store, Google Play)
- [ ] **CHECKLIST_DevOps.md** - 📈 **MÉDIA** (CI/CD, automação)

### 📈 **Cobertura por Prioridade**
- **Crítico:** 6/7 (86%) ✅
- **Alta:** 6/9 (67%) ⚠️
- **Média:** 6/9 (67%) ⚠️
- **Geral:** 6/11 (55%) ⚠️

---

## 🛠️ Como Contribuir

### 📋 Pré-requisitos
- Flutter SDK (versão estável)
- Android Studio / VS Code
- Conta Firebase
- Git

### 🔧 Configuração do Ambiente
```bash
# Clone o repositório
git clone https://github.com/JoaoSantosCodes/TarefaMágica.git
cd TarefaMágica

# Instale as dependências
flutter pub get

# Execute o projeto
flutter run
```

### 📝 Processo de Contribuição
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 🧪 Testes

### 📱 Testes de Interface
- Testes de usabilidade com crianças reais
- Testes de acessibilidade
- Testes de performance
- Testes de navegação

### 🔧 Testes de Backend
- Testes unitários das Functions
- Testes de integração
- Testes de segurança
- Testes de carga

---

## 📊 Métricas de Sucesso

- **Engajamento:** Número de tarefas completadas por semana
- **Retenção:** Tempo médio de uso do app
- **Satisfação:** Feedback positivo dos pais
- **Crescimento:** Número de famílias ativas

---

## 🔒 Segurança e Privacidade

### 🛡️ Proteção de Dados
- Criptografia em trânsito e repouso
- Conformidade com LGPD
- Dados de crianças protegidos
- Logs de auditoria

### 💳 Segurança de Pagamentos
- Integração segura com PIX
- Validação de transações
- Monitoramento de fraudes
- Backup de dados

---

## 📞 Suporte

- **Email:** [seu-email@exemplo.com]
- **Issues:** [GitHub Issues](https://github.com/JoaoSantosCodes/TarefaMágica/issues)
- **Documentação:** [Wiki do Projeto](https://github.com/JoaoSantosCodes/TarefaMágica/wiki)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **João Santos** - *Desenvolvimento inicial* - [JoaoSantosCodes](https://github.com/JoaoSantosCodes)

---

## 🙏 Agradecimentos

- ChatGPT pela concepção inicial do projeto
- Comunidade Flutter pelo suporte
- Famílias beta testers pela validação

---

<div align="center">
  <p>Feito com ❤️ para incentivar responsabilidade nas crianças</p>
  <p>⭐ Se este projeto te ajudou, considere dar uma estrela!</p>
</div> 