# 🎯 Workflow Automático

Sistema modular de análise e automação de workflows para projetos de software.

## 📋 Funcionalidades

- **Análise Base**
  - Escaneamento de checklists
  - Relatórios de progresso
  - Análise por prioridade
  - Atualização de documentação
  - Lista de pendências
  - Preparação de commits

- **Análise por IA**
  - Análise de tarefas
  - Análise de fluxos de trabalho
  - Identificação de dependências
  - Sugestões de priorização

## 🚀 Como Usar

### Pré-requisitos

- Python 3.8+
- Sistema operacional: Windows, Linux ou macOS

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/JoaoSantosCodes/Workflow-Automatico.git
cd Workflow-Automatico
```

2. (Opcional) Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Execução

1. Análise básica:
```bash
python workflow/base_analyzer.py analyze
```

2. Análise de IA - Tarefas:
```bash
python workflow/ia_analyzer.py tasks
```

3. Análise de IA - Fluxos:
```bash
python workflow/ia_analyzer.py flow
```

## 📁 Estrutura do Projeto

```
Workflow-Automatico/
├── workflow/                     # Core do sistema
│   ├── __init__.py             
│   ├── base_analyzer.py         # Análise base
│   ├── ia_analyzer.py           # Análise por IA
│   ├── diagram_generator.py     # Gerador de diagramas
│   └── utils/                   # Utilitários
│       ├── __init__.py
│       ├── file_handler.py      # Manipulação de arquivos
│       └── output_formatter.py  # Formatação de saída
│
├── templates/                    # Templates padrão
│   ├── checklists/             
│   │   ├── base.md             # Checklist base
│   │   └── examples/           # Exemplos de checklists
│   └── outputs/                 # Templates de saída
│
├── docs/                        # Documentação
│   ├── USAGE.md                # Guia de uso
│   ├── INTEGRATION.md          # Guia de integração
│   └── examples/               # Exemplos de uso
│
├── tests/                       # Testes
│   ├── __init__.py
│   ├── test_base_analyzer.py
│   └── test_ia_analyzer.py
│
├── LICENSE                      # Licença MIT
├── README.md                    # Este arquivo
├── CONTRIBUTING.md             # Guia de contribuição
└── requirements.txt            # Dependências
```

## 🔧 Configuração

O sistema é altamente configurável através de arquivos de configuração:

1. `config/base_config.json`: Configurações da análise base
2. `config/ia_config.json`: Configurações da análise por IA
3. `config/output_config.json`: Configurações de saída

## 📊 Exemplos de Uso

### Análise Base
```python
from workflow.base_analyzer import BaseAnalyzer

analyzer = BaseAnalyzer()
analyzer.analyze_project("./meu_projeto")
analyzer.generate_report()
```

### Análise IA
```python
from workflow.ia_analyzer import IAAnalyzer

analyzer = IAAnalyzer()
analyzer.analyze_tasks("./meu_projeto")
analyzer.analyze_flow()
analyzer.generate_suggestions()
```

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre como contribuir com o projeto.

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 