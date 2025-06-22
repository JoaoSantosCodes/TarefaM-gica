# 📚 Guia de Uso - Workflow Automático

Este guia explica como usar o Workflow Automático para análise e automação de projetos.

## 🚀 Início Rápido

1. Instale o pacote:
```bash
pip install workflow-automatico
```

2. Importe as classes necessárias:
```python
from workflow import BaseAnalyzer, IAAnalyzer, DiagramGenerator
```

3. Execute uma análise básica:
```python
analyzer = BaseAnalyzer()
results = analyzer.analyze_project("./meu_projeto")
analyzer.generate_report()
```

## 💡 Conceitos Básicos

### Análise Base
- Verifica checklists
- Calcula prioridades
- Coleta métricas
- Gera relatórios

### Análise IA
- Identifica padrões
- Analisa dependências
- Sugere melhorias
- Otimiza fluxos

### Diagramas
- Estrutura do projeto
- Fluxos de trabalho
- Execução
- Roadmap

## 🔧 Configuração

### Arquivo base_config.json
```json
{
    "checklist_patterns": ["*.md"],
    "output_directory": "outputs",
    "priorities": {
        "critical": "🔥",
        "important": "⚡",
        "normal": "📈"
    }
}
```

### Arquivo ia_config.json
```json
{
    "analysis": {
        "patterns": {
            "enabled": true,
            "min_occurrences": 2
        }
    }
}
```

### Arquivo diagram_config.json
```json
{
    "structure": {
        "enabled": true,
        "format": "mermaid"
    }
}
```

## 📋 Checklists

### Estrutura Básica
```markdown
# Nome do Checklist

## Informações
- Título
- Descrição
- Versão

## Seções
- [ ] Item 1
- [ ] Item 2
```

### Prioridades
- 🔥 Crítica
- ⚡ Importante
- 📈 Normal

## 📊 Relatórios

### Análise Base
```
=== WORKFLOW AUTOMÁTICO ===
2024-02-22 10:00

## CHECKLISTS
- Total: 5
- Completos: 2
- Pendentes: 3
```

### Análise IA
```
## PADRÕES
- Padrão 1
- Padrão 2

## SUGESTÕES
- Sugestão 1
- Sugestão 2
```

## 🔄 Fluxo de Trabalho

1. **Preparação**
   - Configure o ambiente
   - Defina checklists
   - Ajuste configurações

2. **Análise**
   - Execute análise base
   - Execute análise IA
   - Gere diagramas

3. **Resultados**
   - Verifique relatórios
   - Implemente sugestões
   - Atualize documentação

## 🎯 Exemplos

### Análise Completa
```python
# Inicializa analisadores
base = BaseAnalyzer()
ia = IAAnalyzer()
diagrams = DiagramGenerator()

# Executa análises
base_results = base.analyze_project("./")
ia_tasks = ia.analyze_tasks("./")
ia_flow = ia.analyze_flow()

# Gera diagramas
structure = diagrams.generate_structure_diagram("./")
workflow = diagrams.generate_workflow_diagram(ia_flow)

# Gera relatórios
base.generate_report("base_output.txt")
ia.generate_report("ia_output.txt")
```

### Análise Customizada
```python
analyzer = BaseAnalyzer("custom_config.json")
analyzer.analyze_project("./")
analyzer.generate_report("custom_output.txt")
```

## 📌 Dicas

1. **Organização**
   - Mantenha checklists atualizados
   - Use nomes descritivos
   - Siga a estrutura padrão

2. **Análise**
   - Execute regularmente
   - Verifique sugestões
   - Implemente melhorias

3. **Manutenção**
   - Atualize configurações
   - Revise prioridades
   - Mantenha documentação

## ❓ Solução de Problemas

### Erros Comuns

1. **Arquivo não encontrado**
   ```
   ⚠️ Arquivo não encontrado: config.json
   ```
   - Verifique o caminho do arquivo
   - Crie o arquivo se necessário

2. **Erro de encoding**
   ```
   UnicodeEncodeError: 'charmap' codec can't encode character
   ```
   - Use UTF-8 em todos os arquivos
   - Configure encoding no Windows

### Dicas de Debug

1. Ative logs detalhados:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Verifique arquivos de saída:
```python
analyzer.generate_report(debug=True)
```

## 📚 Recursos Adicionais

- [Documentação Completa](docs/README.md)
- [Exemplos](docs/examples/)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Licença](LICENSE) 