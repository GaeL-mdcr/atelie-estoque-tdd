# Instruções para o Claude neste projeto

Projeto: sistema de estoque do ateliê (Flutter + Django) feito com **TDD** para a disciplina
Teste de Software. Leia o diário e os requisitos antes de qualquer coisa:

@docs/CONTEXTO.md
@docs/requisitos.md

O plano que está sendo executado fica em `docs/superpowers/plans/` (roteiro geral + plano da fase atual).
Abra o da fase atual antes de começar um ciclo.

## Regras que não podem ser quebradas

- **TDD de verdade:** escrever só o teste → rodar e ver falhar → commit `[RED] …` →
  mínimo de código → rodar e ver passar → commit `[GREEN] …` → refatorar se precisar → commit `[REFACTOR] …`.
  Nunca escrever código de produção que nenhum teste pediu. Um commit por etapa do ciclo.
- **Commits só no nome do Gabriel:** nunca adicionar `Co-Authored-By`, link de sessão nem
  "Generated with Claude Code" em commit ou pull request.
- Commits, comentários e mensagens de erro **em português, simples e humanizados**.
- `dominio.py` e `apps/comum/` não importam Django. Dinheiro e quantidade só em `Decimal`, nunca `float`.
- Ao terminar uma sessão, atualizar as seções 4, 7 e 10 de `docs/CONTEXTO.md`.

## Comandos

```bash
cd backend
.venv\Scripts\activate          # Windows (criar antes com: python -m venv .venv)
pip install -r requirements-dev.txt
pytest                           # todos os testes
pytest apps/conversoes -v        # um módulo
pytest --cov --cov-report=term-missing

cd app
flutter test --coverage
```
