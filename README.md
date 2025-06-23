# ✨ TarefaMágica

Sistema automatizado e seguro para gestão de tarefas, consentimento parental, controle financeiro e integração com aplicativos Android, com foco em compliance LGPD e segurança de dados.

---

## 📋 Funcionalidades Principais

- **Automação de Workflows**
  - Análise e geração automática de checklists
  - Relatórios de progresso e priorização
  - Atualização e validação de documentação
- **Segurança e Compliance**
  - Consentimento parental conforme LGPD
  - Autenticação de dois fatores (2FA)
  - Controle de acesso baseado em roles (RBAC)
  - Criptografia de dados sensíveis
  - Auditoria e logs detalhados
- **Gestão Financeira Segura**
  - Proteção de transações PIX
  - Aprovação e rastreamento de operações financeiras
- **Integração Android**
  - SDK nativo para integração com apps Android
  - Gerenciamento de consentimento, 2FA e permissões
- **APIs RESTful**
  - Endpoints para todas as operações de segurança, consentimento e controle de acesso

---

## 🚀 Como Usar

### Pré-requisitos
- Python 3.8+
- Sistema operacional: Windows, Linux ou macOS

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/JoaoSantosCodes/TarefaM-gica.git
   cd TarefaM-gica
   ```
2. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate   # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Execução

- **Análise de Checklists:**
  ```bash
  python workflow/base_analyzer.py analyze
  ```
- **Análise de IA - Tarefas:**
  ```bash
  python workflow/ia_analyzer.py tasks
  ```
- **Análise de IA - Fluxos:**
  ```bash
  python workflow/ia_analyzer.py flow
  ```

---

## 📁 Estrutura do Projeto

```
TarefaM-gica/
├── workflow/                     # Core do sistema
│   ├── base_analyzer.py         # Análise base
│   ├── ia_analyzer.py           # Análise por IA
│   ├── diagram_generator.py     # Gerador de diagramas
│   ├── api/                     # Rotas RESTful
│   ├── security/                # Módulos de segurança
│   └── utils/                   # Utilitários
│
├── templates/                   # Templates padrão
├── docs/                        # Documentação e exemplos
├── checklists/                  # Checklists de validação
├── workflow_scripts/            # Scripts de automação
├── resumo/                      # Resumos e análises
├── requirements.txt             # Dependências
├── README.md                    # Este arquivo
├── LICENSE                      # Licença MIT
└── ...
```

---

## 🔒 Segurança e Compliance

- **Consentimento Parental:** Módulo completo conforme LGPD
- **2FA:** Autenticação de dois fatores para responsáveis
- **Controle de Acesso:** RBAC com auditoria e logs
- **Criptografia:** AES-256 para dados sensíveis
- **Proteção Financeira:** Segurança em transações PIX
- **Auditoria:** Logs detalhados de todas as ações

---

## 🤖 Integração Android

- SDK nativo para gerenciamento de consentimento, 2FA e permissões
- Exemplos em `docs/examples/android/`

---

## 📝 Contribuindo

Veja o arquivo `CONTRIBUTING.md` para detalhes sobre como contribuir com o projeto.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para detalhes. 