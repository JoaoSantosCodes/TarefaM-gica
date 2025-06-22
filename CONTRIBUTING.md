# �� Contribuindo com o Workflow Automático

Obrigado por considerar contribuir com o Workflow Automático! Este documento fornece as diretrizes para contribuir com o projeto.

## 📋 Processo de Contribuição

1. Fork o repositório
2. Clone seu fork localmente
3. Crie uma branch para sua feature/correção
4. Faça suas alterações
5. Execute os testes
6. Commit suas alterações
7. Push para seu fork
8. Abra um Pull Request

## 🔧 Ambiente de Desenvolvimento

1. Clone o repositório:
```bash
git clone https://github.com/JoaoSantosCodes/Workflow-Automatico.git
cd Workflow-Automatico
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate     # Windows
```

3. Instale as dependências de desenvolvimento:
```bash
pip install -r requirements.txt
```

## ✅ Testes

Execute os testes antes de submeter alterações:

```bash
pytest tests/
```

Para verificar a cobertura de código:

```bash
pytest --cov=workflow tests/
```

## 📝 Estilo de Código

Usamos as seguintes ferramentas para manter a qualidade do código:

- Black para formatação
- Flake8 para linting
- isort para ordenação de imports

Execute antes de commitar:

```bash
black .
flake8 .
isort .
```

## 📚 Documentação

- Mantenha a documentação atualizada
- Adicione docstrings para novas funções/classes
- Atualize o README.md se necessário
- Inclua exemplos de uso

## 🏷️ Commits

Use mensagens de commit claras e descritivas:

- feat: Nova funcionalidade
- fix: Correção de bug
- docs: Atualização de documentação
- test: Adição/modificação de testes
- refactor: Refatoração de código
- style: Formatação, ponto e vírgula, etc
- chore: Tarefas de manutenção

## 🔍 Pull Requests

1. Descreva claramente o propósito
2. Referencie issues relacionadas
3. Inclua testes para novas funcionalidades
4. Mantenha o PR focado em uma única alteração
5. Atualize a documentação se necessário

## 📌 Notas Importantes

- Não quebre a compatibilidade com versões anteriores
- Mantenha a cobertura de testes
- Siga as convenções de código existentes
- Documente alterações significativas

## 🚫 O que evitar

- Alterações não relacionadas ao escopo do PR
- Commits grandes e não relacionados
- Código não testado
- Breaking changes sem discussão prévia

## 📬 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto. 