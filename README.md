# Ateliê — Sistema de Estoque feito com TDD

Trabalho da disciplina **Teste de Software** (atividade prática de Test-Driven Development).

O projeto é um sistema real para um ateliê de pequeno porte: a dona do ateliê trabalha pelo
celular, compra materiais de fornecedores diferentes, em unidades diferentes (rolo, metro,
pacote) e em várias cores. O sistema organiza **materiais por cor, compras com vários itens,
estoque, conversão de unidades, produções, uso e retorno de materiais e custos**, sem nunca
reescrever o histórico.

Todo o código de produção nasce de um teste que falhou antes (ciclo **Red → Green → Refactor**),
e o histórico de commits mostra isso.

> Status: **Semana 1 — estrutura e requisitos.** Ainda não existe código de produção.

## Arquitetura

App **Flutter** (celular + web) com **SQLite local** para funcionar offline, conversando com uma
**API Django** que é a fonte oficial das regras e do banco. O site **vitrine** fica reservado
para depois.

```
celular / navegador (Flutter + SQLite local)
        │  fila de operações pendentes
        ▼  HTTPS + JWT
API Django (DRF) ── valida, recalcula e confirma ──► banco oficial (SQLite no MVP)
        │
        └─► vitrine pública (futuro, só peças publicadas)
```

## Estrutura de pastas

```
atelie-estoque-tdd/
├── backend/                  # API Django — onde começam os ciclos TDD
│   ├── config/               # settings, urls, wsgi/asgi
│   ├── apps/
│   │   ├── contas/           # usuário e login (JWT)
│   │   ├── cadastros/        # material, cor, variante material+cor, categoria, unidade, fornecedor
│   │   ├── conversoes/       # 1 rolo = 50 m, etc.
│   │   ├── compras/          # compra com vários itens, tudo ou nada
│   │   ├── estoque/          # saldo e custo médio por material e cor
│   │   ├── producoes/        # peças, pastas, imagens, conclusão, reabertura, publicação
│   │   ├── movimentacoes/    # uso (U) e retorno (R) de material
│   │   ├── sincronizacao/    # PUSH/PULL com o celular, sem duplicar
│   │   └── vitrine/          # reservado para o site público (futuro)
│   │   (cada módulo tem sua pasta tests/)
│   ├── tests/                # testes do ambiente/configuração
│   ├── requirements.txt      # dependências de produção
│   ├── requirements-dev.txt  # + pytest, pytest-django, pytest-cov
│   └── pytest.ini
├── app/                      # app Flutter (celular + web)
│   ├── lib/src/              # core, features/*, sincronizacao
│   └── test/                 # espelha lib/src
└── docs/
    ├── requisitos.md         # Etapa 1: classes, métodos, regras de negócio
    └── CONTEXTO.md           # diário de bordo: decisões, estado atual e próximos passos
```

## Como rodar os testes

### Backend (Python 3.12+)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt

pytest                                   # roda tudo
pytest --cov --cov-report=term-missing   # com cobertura
```

### App Flutter

Veja [`app/README.md`](app/README.md) para gerar as pastas de plataforma na primeira vez. Depois:

```bash
cd app
flutter test --coverage
```

## Resultados

| Métrica | Backend | App |
| --- | --- | --- |
| Testes | — | — |
| Cobertura | — | — |

(Atualizado ao fim de cada semana.)

## Integrantes

- Gabriel Mallezan da Costa Ribeiro



