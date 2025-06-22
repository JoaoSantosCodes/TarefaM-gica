# Exemplos Práticos para IA 📝

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
