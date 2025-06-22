#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA DOCS GENERATOR - TarefaMágica
===============================

Gera documentação específica para IAs entenderem o projeto.
Analisa o resumo e gera:
- Estrutura base
- Fluxo de análise
- Exemplos
- Contexto
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class IADocsGenerator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.resumo_file = self.project_root / 'resumo' / 'Resumo ChatGPT.txt'
        self.docs_dir = self.project_root / 'docs' / 'ia'
        
    def generate_docs(self):
        """Gera a documentação para IAs."""
        # Cria diretório se não existir
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera os diferentes tipos de documentação
        self._generate_overview()
        self._generate_structure()
        self._generate_workflow()
        self._generate_examples()
        self._generate_context()
        
        print(f"\n✅ Documentação para IAs gerada em {self.docs_dir}")
        
    def _generate_overview(self):
        """Gera visão geral do projeto para IAs."""
        content = """# TarefaMágica - Documentação para IA 🤖

## O Que é o TarefaMágica?

O TarefaMágica é um aplicativo educativo e gamificado que:
- 🎯 Incentiva crianças (11-12 anos) a realizarem tarefas domésticas
- 🎮 Usa gamificação para motivar
- 💰 Integra recompensas reais (até R$10) e virtuais
- 🧠 Usa IA para análise e otimização

## Por Que é Único?

1. **Abordagem Híbrida**
   - Combina tarefas reais com elementos virtuais
   - Integra recompensas monetárias com gamificação
   - Une educação com diversão

2. **Sistema Inteligente**
   - Análise automática de progresso
   - Sugestões personalizadas
   - Adaptação ao perfil da criança

3. **Arquitetura Modular**
   - Sistema de checklists em Markdown
   - Análise por IA
   - Geração automática de relatórios
   - Workflows personalizados

## Como a IA Deve Interpretar

1. **Entenda o Contexto**
   - Público-alvo: crianças de 11-12 anos
   - Ambiente: doméstico/familiar
   - Objetivo: educação + motivação

2. **Analise as Estruturas**
   - Checklists são a base
   - Prioridades são importantes
   - Gamificação é essencial

3. **Considere o Fluxo**
   - Tarefas → Verificação → Recompensa
   - Progresso → Níveis → Desbloqueios
   - Análise → Relatórios → Sugestões
"""
        
        output_file = self.docs_dir / 'README.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_structure(self):
        """Gera documentação da estrutura do projeto."""
        content = """# Estrutura do TarefaMágica para IA 🏗️

## Componentes Principais

### 1. Sistema de Usuários 👥
```yaml
Perfis:
  Admin (Pais):
    - Criar tarefas
    - Definir valores
    - Aprovar conclusões
    - Gerenciar recompensas
  
  Criança:
    - Ver tarefas
    - Marcar conclusões
    - Personalizar avatar
    - Acompanhar progresso
```

### 2. Sistema de Tarefas 📋
```yaml
Tarefa:
  - Descrição
  - Valor (R$)
  - Moedas virtuais
  - Status
  - Evidência (foto/vídeo)
  - Aprovação
```

### 3. Sistema de Gamificação 🎮
```yaml
Elementos:
  - Níveis
  - Pontos XP
  - Moedas virtuais
  - Itens desbloqueáveis
  - Conquistas
  - Rankings
```

### 4. Sistema de Recompensas 🎁
```yaml
Tipos:
  Reais:
    - Dinheiro (até R$10)
    - Baseado em tarefas
  
  Virtuais:
    - Moedas do app
    - Itens cosméticos
    - Adesivos
    - Temas
```

## Como Processar Esta Estrutura

1. **Análise de Dados**
   - Usar estruturas hierárquicas
   - Manter relações entre sistemas
   - Preservar metadados

2. **Processamento**
   - Validar regras de negócio
   - Verificar dependências
   - Manter consistência

3. **Geração**
   - Relatórios estruturados
   - Sugestões contextuais
   - Análises preditivas
"""
        
        output_file = self.docs_dir / 'STRUCTURE.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_workflow(self):
        """Gera documentação do workflow para IAs."""
        content = """# Workflow do TarefaMágica para IA 🔄

## Fluxos Principais

### 1. Fluxo de Tarefas
```mermaid
graph TD
    A[Criar Tarefa] --> B[Definir Valor]
    B --> C[Criança Executa]
    C --> D[Upload Evidência]
    D --> E[Pais Aprovam]
    E --> F[Recompensa Liberada]
```

### 2. Fluxo de Gamificação
```mermaid
graph TD
    A[Completar Tarefa] --> B[Ganhar XP]
    B --> C[Subir Nível]
    C --> D[Desbloquear Itens]
    D --> E[Personalizar Avatar]
```

### 3. Fluxo de Análise
```mermaid
graph TD
    A[Coletar Dados] --> B[Analisar Padrões]
    B --> C[Gerar Insights]
    C --> D[Sugerir Ações]
    D --> E[Atualizar Sistema]
```

## Como a IA Deve Processar

1. **Entrada de Dados**
   - Ler checklists
   - Validar formatos
   - Verificar integridade

2. **Processamento**
   - Analisar prioridades
   - Identificar padrões
   - Calcular métricas

3. **Saída**
   - Gerar relatórios
   - Sugerir ações
   - Atualizar status

## Pontos de Atenção

1. **Validações**
   - Valores dentro do limite
   - Evidências adequadas
   - Aprovações corretas

2. **Consistência**
   - Dados sincronizados
   - Estados coerentes
   - Histórico preservado

3. **Otimização**
   - Performance
   - Recursos
   - Experiência
"""
        
        output_file = self.docs_dir / 'WORKFLOW.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_examples(self):
        """Gera exemplos práticos para IAs."""
        content = """# Exemplos Práticos para IA 📝

## 1. Exemplo de Checklist
```markdown
# Tarefas Domésticas

## 🏠 Quarto
- [ ] Arrumar a cama (R$2 | 🪙2)
- [ ] Organizar brinquedos (R$1 | 🪙1)
- [ ] Limpar escrivaninha (R$3 | 🪙3)

## 🍽️ Cozinha
- [ ] Lavar louça (R$5 | 🪙5)
- [ ] Ajudar no jantar (R$4 | 🪙4)
- [ ] Guardar compras (R$3 | 🪙3)
```

## 2. Exemplo de Análise
```python
# Como a IA deve processar
def analisar_checklist(checklist):
    tarefas = extrair_tarefas(checklist)
    prioridades = calcular_prioridades(tarefas)
    valor_total = sum(tarefa.valor for tarefa in tarefas)
    progresso = calcular_progresso(tarefas)
    return {
        'total_tarefas': len(tarefas),
        'valor_total': valor_total,
        'progresso': progresso,
        'prioridades': prioridades
    }
```

## 3. Exemplo de Gamificação
```yaml
Tarefa:
  nome: "Arrumar a cama"
  recompensas:
    dinheiro: 2.00
    moedas: 2
    xp: 50
  desbloqueios:
    nivel_1:
      - "Adesivo de cama arrumada"
      - "+10% moedas por 1 dia"
    nivel_2:
      - "Título: Mestre da Organização"
      - "Tema especial para o quarto"
```

## 4. Exemplo de Relatório
```markdown
# Relatório Semanal

## 📊 Estatísticas
- Tarefas Concluídas: 15/20
- Valor Total: R$45,00
- Moedas Ganhas: 🪙45
- XP Acumulado: 750

## 🎯 Conquistas
- Nível Alcançado: 5
- Novos Itens: 3
- Recordes: 2

## 📈 Progresso
- Segunda: 4 tarefas
- Terça: 3 tarefas
- Quarta: 2 tarefas
- Quinta: 3 tarefas
- Sexta: 3 tarefas
```

## Como Usar os Exemplos

1. **Identificação de Padrões**
   - Estrutura consistente
   - Formatos padronizados
   - Relações claras

2. **Processamento**
   - Extração de dados
   - Cálculos e análises
   - Geração de insights

3. **Aplicação**
   - Sugestões contextuais
   - Recomendações personalizadas
   - Relatórios adaptados
"""
        
        output_file = self.docs_dir / 'EXAMPLES.md'
        output_file.write_text(content, encoding='utf-8')

    def _generate_context(self):
        """Gera documentação de contexto para IAs."""
        content = """# Contexto do TarefaMágica para IA 🌟

## 1. Objetivo Principal

O TarefaMágica visa resolver um desafio comum:
- Motivar crianças a fazerem tarefas domésticas
- Ensinar responsabilidade financeira
- Criar hábitos positivos
- Gamificar atividades cotidianas

## 2. Público-Alvo

### Crianças (11-12 anos)
```yaml
Características:
  - Interesse em jogos
  - Familiaridade com tecnologia
  - Busca por independência
  - Desenvolvimento de responsabilidade
```

### Pais/Responsáveis
```yaml
Necessidades:
  - Ferramenta educativa
  - Controle financeiro
  - Acompanhamento de progresso
  - Incentivo positivo
```

## 3. Aspectos Psicológicos

### Motivação
- Recompensas imediatas
- Progresso visível
- Reconhecimento
- Autonomia

### Gamificação
- Desafios adequados
- Recompensas equilibradas
- Feedback constante
- Progressão clara

## 4. Considerações Técnicas

### Segurança
```yaml
Aspectos:
  - Controle parental
  - Proteção de dados
  - Limites de valores
  - Aprovações necessárias
```

### Usabilidade
```yaml
Prioridades:
  - Interface intuitiva
  - Feedback claro
  - Navegação simples
  - Experiência divertida
```

## Como a IA Deve Interpretar

1. **Análise Contextual**
   - Considerar idade do usuário
   - Avaliar complexidade adequada
   - Manter linguagem apropriada

2. **Processamento Adaptativo**
   - Ajustar sugestões ao perfil
   - Personalizar recompensas
   - Adaptar dificuldade

3. **Geração de Conteúdo**
   - Usar linguagem amigável
   - Manter tom positivo
   - Incluir elementos lúdicos

## Diretrizes de Processamento

1. **Análise de Dados**
   - Priorizar segurança
   - Manter privacidade
   - Respeitar limites

2. **Geração de Sugestões**
   - Considerar contexto familiar
   - Respeitar valores definidos
   - Manter equilíbrio educativo

3. **Feedback e Relatórios**
   - Linguagem adequada à idade
   - Visualização clara
   - Métricas relevantes
"""
        
        output_file = self.docs_dir / 'CONTEXT.md'
        output_file.write_text(content, encoding='utf-8')

def main():
    """Função principal."""
    try:
        print("\n🤖 GERADOR DE DOCUMENTAÇÃO PARA IA - TarefaMágica")
        print("=" * 50)
        
        # Usa o diretório atual ou o passado como argumento
        project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
        
        generator = IADocsGenerator(project_dir)
        generator.generate_docs()
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar documentação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 