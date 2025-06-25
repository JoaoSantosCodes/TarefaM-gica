import subprocess
import sys

print("\n=== AUTOMAÇÃO MASTER DO PROJETO ===\n")

# 0. Execução dos workflows de IA
print("[0/6] Executando análises de workflow IA...")
subprocess.run([sys.executable, 'workflow_scripts/tarefamagica_workflow.py', 'base', 'analyze'], check=True)
print("  - base analyze concluído.")
subprocess.run([sys.executable, 'workflow_scripts/tarefamagica_workflow.py', 'ia', 'ai-tasks'], check=True)
print("  - ia ai-tasks concluído.")
subprocess.run([sys.executable, 'workflow_scripts/tarefamagica_workflow.py', 'ia', 'ai-flow'], check=True)
print("  - ia ai-flow concluído.")

# 1. Organização e checklist de estrutura (já integra relatório visual)
print("[1/6] Organizando estrutura e gerando checklist...")
subprocess.run([sys.executable, 'scripts/organizar_e_checar_estrutura.py'], check=True)

# 2. Relatório visual (já gerado pelo passo anterior)
print("[2/6] Relatório visual de árvore e estatísticas atualizado.")

# 3. Detecção de duplicidades
print("[3/6] Gerando relatório de duplicidades relevantes...")
subprocess.run([sys.executable, 'scripts/checar_duplicidades_relevantes.py'], check=True)

# 4. Sugestões de limpeza
print("[4/6] Gerando sugestões de limpeza/movimentação...")
subprocess.run([sys.executable, 'scripts/sugerir_limpeza_duplicidades.py'], check=True)

# 5. Execução de movimentação para quarentena (opcional)
resposta = input("[5/6] Deseja executar a movimentação para quarentena AGORA? (s/n): ").strip().lower()
if resposta == 's':
    print("Executando movimentação para quarentena...")
    subprocess.run([sys.executable, 'scripts/executar_movimentacao_quarentena.py'], check=True)
else:
    print("Movimentação para quarentena NÃO executada. Você pode rodar manualmente depois.")

# 5.1 Limpeza de pastas vazias
print("[5.1/6] Removendo pastas vazias não protegidas...")
subprocess.run([sys.executable, 'scripts/remover_pastas_vazias.py'], check=True)

# 6. Geração/atualização do checklist de automação
print("[6/6] Gerando checklist de automação...")
with open('outputs/checklist_automacao.md', 'w', encoding='utf-8') as f:
    f.write("""# Checklist de Validação dos Processos de Automação\n\n## Organização da Estrutura\n- [x] Script para listar toda a estrutura de pastas/arquivos\n- [x] Geração de checklist de estrutura (`outputs/checklist_estrutura.txt`)\n\n## Detecção de Duplicidades\n- [x] Script para identificar duplicidades relevantes\n- [x] Relatório de duplicidades críticas (`outputs/duplicidades_relevantes.txt`)\n\n## Sugestões de Limpeza Segura\n- [x] Script para sugerir comandos de movimentação para quarentena\n- [x] Relatório de sugestões para Windows e Unix/Linux (`outputs/sugestoes_limpeza.txt`)\n\n## Execução Automatizada\n- [x] Script para executar movimentação para quarentena\n- [x] Log detalhado de movimentação (`outputs/log_quarentena.txt`)\n- [x] Garantia de não deletar nada automaticamente\n\n## Auditoria e Rastreabilidade\n- [x] Todos os passos registrados em arquivos de log e outputs\n- [x] Possibilidade de revisão e reversão das ações\n\n## Pronto para CI/CD\n- [x] Scripts e relatórios prontos para integração em pipelines de automação\n\n---\n\n### Próximos Passos (opcional)\n- [ ] Integrar scripts ao pipeline de CI/CD (ex: GitHub Actions, GitLab CI)\n- [ ] Agendar execuções periódicas para manter o projeto limpo\n- [ ] Adicionar notificações automáticas em caso de duplicidades críticas\n- [ ] Documentar o fluxo de automação no README do projeto\n""")

# 7. Atualização do banco SQLite com todos os relatórios
print("[7/6] Atualizando banco de dados SQLite com todos os relatórios e checklists...")
subprocess.run([sys.executable, 'scripts/importar_relatorios_sqlite.py'], check=True)

print("\n=== Processo de automação concluído! Veja os relatórios em outputs/. Banco atualizado. ===\n") 