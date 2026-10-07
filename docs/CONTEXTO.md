# Diário de contexto do projeto

> **Para que serve:** é a memória do projeto. Quem pegar o trabalho (você, a dupla ou uma IA)
> lê isto primeiro e sabe onde parou, o que já foi decidido e o que vem a seguir.
>
> **Regra de uso:** ao **começar** uma sessão, leia as seções 1, 4 e 7. Ao **terminar**,
> atualize a seção 4 (estado atual), marque os ciclos na seção 7 e acrescente uma linha
> no registro de sessões (seção 10). Decisão nova vai na seção 3, com data.

Última atualização: **07/10/2026**

---

## 1. Resumo em 30 segundos

- **O quê:** sistema de estoque para um ateliê — materiais por cor, compras com vários itens,
  conversão de unidades, produções, uso/retorno de material e custos, sem reescrever histórico.
- **Para quê (agora):** atividade prática de **TDD** da disciplina Teste de Software
  (entrega no GitHub + apresentação de 15 min).
- **Como:** monorepo com `backend/` (Django + DRF + JWT, testes com pytest) e `app/`
  (Flutter celular + web, Riverpod + Drift + go_router, testes com flutter_test).
- **Por onde começa o TDD:** classes de domínio em Python puro no backend
  (ver [`requisitos.md`](requisitos.md)), depois services Django, depois Flutter.
- **Repositório:** https://github.com/GaeL-mdcr/atelie-estoque-tdd (público)

## 2. Documentos de origem (Google Drive)

Pasta do projeto: https://drive.google.com/drive/folders/1ji9REkLwkAdW36rDPC70bdfg2wJn1zXs

Valem as versões **mais recentes** abaixo. Em caso de conflito, a ordem de prioridade é:
decisões da seção 3 deste arquivo → Requisitos V3.2 → Lógico_1 / UML V4.8 → Arquitetura V3.1 → Interface V2.2.

| Documento | Versão | Link | O que tem |
|---|---|---|---|
| Análise de Requisitos | **V3.2** (07/10/2026) | [docx](https://drive.google.com/file/d/1M02lmsAwkAs8cUZC3HXWqncEuH9vcJ1r/view) | RF01–RF35, RN01–RN22, RNF01–RNF12, casos de uso, rastreabilidade |
| Proposta de Banco de Dados | **V4.8** (21/09) | [docx](https://drive.google.com/file/d/1CgN0DlgiEETwXmW8Z51llko585WEkVWh/view) | Funcionalidades, restrições, 14 tabelas, valores calculados |
| Modelo de Entidades UML | **V4.8** (21/09) | [doc](https://docs.google.com/document/d/11CYbU1-2fqgl4WyeAF7CCrnCpTys9NelwUfZ_8lwbm4/edit) | PlantUML das 14 entidades e cardinalidades |
| 01 Mapa da Arquitetura | **V3.1** | [docx](https://drive.google.com/file/d/1ihDvC6YNfW9BiBqTvy5zyr_ndPAvBU7v/view) | Quem fala com quem, ADRs, decisões abertas |
| 02 Guia do Programador | **V3.1** | [docx](https://drive.google.com/file/d/1RqQd0exzgRI9_eiSq_n3fWAEGAJKLQ2-/view) | Módulos, funções propostas, ordem de implementação |
| 03 Referência SQL e Códigos | **V3.1** | [docx](https://drive.google.com/file/d/151cDlHtVZWvLO6zlGzCIQAOv8HeHyOE7/view) | Lógico_1, DDL SQLite adaptado, regras em Decimal, exemplos numéricos |
| Diagramas de Sequência UML | V4.8 | [docx](https://drive.google.com/file/d/1zu5_-r0xrIZOS-HNvHb24cYzMb_jwXNq/view) | Cadastro, compra, uso/retorno, sync, conclusão/vitrine |
| Descritivo da Interface | **V2.2** | [doc](https://docs.google.com/document/d/1rDEcibiQe59lxU1FpKnKlXHUMObQooupYKiltsPYByE/edit) | Telas, textos, dropdown "Adicionar novo…", fluxo de teste |
| Figma (design system) | — | [figma](https://www.figma.com/design/pDIBceda9E1kBKdqTFcAyw/Projeto-atelie---Aplica%25C3%25A7%25C3%25A3o-Mobile) | Página *DS 10 • Components*: botões, ações, campos, chips, navegação, cards, feedback, ícones, padrões |

**Superado — não usar:** "Modelo Lógico e DDL **V4.4**" (raiz do Drive, 14/09). Usa
`Material_Cor`, `descricao_categoria`, endereço/link de fornecedor e `descricao_pasta`, que
foram removidos. O nome vigente é **`Material_Variante_Cor`** (PK `id_material_cor`).

## 3. Decisões tomadas

Origem: **Doc** = já estava nos documentos; **07/10** = fechada na conversa de 07/10/2026.

| # | Decisão | Origem |
|---|---|---|
| D01 | App em **Flutter** para celular (Android) e web; **Django** é o backend e o canal de sincronização com o SQLite do aparelho. | Doc + 07/10 |
| D02 | **Vitrine** não é implementada agora, mas tem módulo reservado (`apps/vitrine`) e as regras já separam dados públicos de internos. | 07/10 |
| D03 | **Monorepo** (`backend/` + `app/`). Ciclos TDD começam no **backend** (Django é a fonte oficial). | 07/10 |
| D04 | Testes: **pytest + pytest-django + pytest-cov** no backend; **flutter_test** no app. A atividade aceita outra linguagem além de Java. | 07/10 |
| D05 | **Retorno** guarda o **id do uso de origem**. O uso grava o **custo médio ponderado vigente**; o retorno volta com o **custo daquele uso**, e o custo médio da cor é recalculado por **média ponderada**. Limite do retorno = usado − já devolvido daquele uso. | 07/10 |
| D06 | **Reabertura com histórico agora**: tabela própria de reaberturas (produção, usuário, motivo, data). Motivo obrigatório. | 07/10 |
| D07 | **Arquivamento**: campo `ativo` em Material, Cor e Fornecedor; arquivar só esconde das listas. **Exclusão de quem tem histórico é recusada** (RESTRICT no lugar dos CASCADE do Lógico_1). | 07/10 |
| D08 | Flutter com **Riverpod + Drift + go_router** desde a configuração (Drift roda no celular e na web). | 07/10 |
| D09 | API com **Django REST Framework + JWT** (`djangorestframework-simplejwt`); serializer da vitrine separado do interno. | 07/10 |
| D10 | Banco do servidor: **SQLite no MVP**; código sem depender de `select_for_update` (usar `UPDATE … WHERE saldo >= qtd` com `F()`). PostgreSQL continua alternativa. | Doc |
| D11 | Dinheiro e quantidade sempre em **`Decimal`**: qtd 3 casas, dinheiro 2, fator 6, `ROUND_HALF_UP`. | Doc |
| D12 | Usuário do sistema será um **modelo de usuário próprio** (`apps.contas`) criado **antes da primeira migration**. | 07/10 (consequência de D09) |
| D13 | Commits e comentários **em português, simples e humanizados**, com prefixo `[RED]`, `[GREEN]` ou `[REFACTOR]` nos ciclos. Autor sempre o Gabriel; **sem** linha `Co-Authored-By` ou de sessão (o histórico foi regravado em 07/10 para tirar essas linhas). | 07/10 |
| D15 | Reabrir uma produção publicada **tira da vitrine** automaticamente (peça em andamento não está concluída). | 07/10 |
| D14 | Repositório público `atelie-estoque-tdd`; integrante: Gabriel (dupla a definir). | 07/10 |

## 4. Estado atual

**Semana 2 — Fase 1 concluída** (branch `claude/codespaces-fase1-deuu9l`, PR para `main`).

- [x] Repositório criado no GitHub (público)
- [x] Estrutura vazia do backend (módulos Django sem código de regra)
- [x] pytest / pytest-django / pytest-cov configurados (`backend/pytest.ini`, `.coveragerc`)
- [x] Casca do app Flutter (`pubspec.yaml`, `lib/main.dart`, pastas por funcionalidade)
- [x] README inicial
- [x] `docs/requisitos.md` (Etapa 1)
- [x] Testes de configuração rodados: **3 passando** (Python 3.13, Django 5.2.18, pytest 9.1.1)
- [x] Pastas de plataforma do Flutter geradas (`android/`, `web/`) e `flutter pub get` sem conflito
- [x] Ambiente do **GitHub Codespaces** (`.devcontainer/`): Python 3.12 + Flutter stable
- [x] **Fase 1 — domínio do backend:** 7 classes em `apps/*/dominio.py` + `apps/comum`,
      **92 testes passando, 100% de cobertura** do código de domínio
- [ ] Plano detalhado da Fase 2 (models + migrations)

Código de produção existente: só o domínio em Python puro (`apps/comum/*.py` e `apps/*/dominio.py`),
sem nenhuma importação de Django.

## 5. Mudanças no modelo em relação ao Lógico_1

Quando os *models* Django forem criados (sempre a partir de testes), aplicar:

| Tabela | Mudança | Por quê |
|---|---|---|
| Material_Variante_Cor | `UNIQUE(material, cor)` | RN02; não existia no SQL exportado |
| Uso_Material | `fk_uso_origem` (opcional, só no tipo R) → Uso_Material | D05 |
| **Reabertura_Producao** (nova) | `id`, `fk_producao`, `fk_usuario`, `motivo`, `dt_reabertura` | D06 |
| Material, Cor, Fornecedor | `ativo BOOLEAN DEFAULT TRUE` | D07 |
| Todas as FKs históricas | `ON DELETE RESTRICT` no lugar de `CASCADE`; Producao → Pasta continua `SET NULL` | D07, RN16, RN19 |
| FKs e datas | FK inteira (não SERIAL); `DATETIME` → `DateTimeField` | Lógico_1 é export do brModelo |
| Categoria | `UNIQUE(tipo, nome)` sem diferenciar maiúscula/minúscula | RN21 |
| Imagem_Producao | No máximo uma principal por produção (constraint condicional) | RN17 |
| Valores derivados | `fator`, totais, custos de produção: **calculados**, não colunas editáveis; `qtd_entrada_estoque` e custo do uso: **guardados** (histórico); saldo e custo médio: consolidados só por transação | Proposta V4.8 §7 |
| Sincronização | Tabelas técnicas `sync_operacao` / `sync_evento` fora das 14 entidades | Referência SQL V3.1 |

## 6. Ambiente e limitações conhecidas

- **GitHub Codespaces** (desde 07/10): `.devcontainer/devcontainer.json` usa a imagem
  `mcr.microsoft.com/devcontainers/python:3.12-bookworm`; o `pos-criacao.sh` cria o venv do
  backend, clona o Flutter stable em `~/flutter` e roda o `pub get` do app. Portas 8000 (Django)
  e 8080 (Flutter web) já ficam encaminhadas.
- O ambiente de nuvem do Claude Code agora acessa o PyPI e o download do Flutter: a Fase 0 e a
  Fase 1 rodaram lá de verdade (Python 3.13.16, Django 5.2.18, pytest 9.1.1, Flutter 3.47.6 / Dart 3.13.5).
- Versões que o `pub get` resolveu: flutter_riverpod 3.4.3 · drift 2.31.0 · drift_flutter 0.2.8 ·
  go_router 16.3.0 · drift_dev 2.31.0 · build_runner 2.15.1 · flutter_lints 6.0.0. O `pubspec.lock` está no repositório.
- O link do Figma só expõe a página do design system (*DS 10 • Components*); as telas são
  descritas pela Interface V2.2.
- O `CLAUDE.md` foi apagado pelo site no commit `7535c83`; as regras dele continuam valendo
  (estão neste diário e na seção 8).

Comandos:

```bash
# backend
cd backend && python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
pytest
pytest --cov --cov-report=term-missing

# app
cd app && flutter create --platforms=android,web --project-name atelie .
# apagar test/widget_test.dart gerado
flutter pub get && flutter test --coverage
```

## 7. Plano de ciclos TDD

Cada linha = um ou mais ciclos Red → Green (→ Refactor), cada um com seu commit.
Detalhes de assinatura e erros em [`requisitos.md`](requisitos.md).

Planos:
- Roteiro de todas as fases: [`superpowers/plans/2026-10-07-roteiro-ponta-a-ponta.md`](superpowers/plans/2026-10-07-roteiro-ponta-a-ponta.md)
- Passo a passo da Fase 1 (domínio): [`superpowers/plans/2026-10-07-fase1-dominio-backend.md`](superpowers/plans/2026-10-07-fase1-dominio-backend.md)
- Execução: Fase 1 feita no ambiente de nuvem com o venv completo (Django incluso); dá para repetir no Codespaces.

**Backend — domínio (Python puro)**

- [x] `ConversaoUnidade`: fator · converter · atende · equivalência ≤ 0 · converter ≤ 0
- [x] `ItemCompra`: total · entrada sem conversão · entrada com conversão · custo de entrada · sem conversão → erro · conversão de outro material → erro · preço negativo → erro · entrada não muda se a conversão mudar
- [x] `Compra`: adicionar · total · editar · remover · confirmar · confirmar vazia → erro · mexer depois de confirmada → erro · posição inexistente → erro
- [x] `EstoqueVariante`: saldo inicial · entrada + média ponderada (exemplo 4,60) · saída devolve custo vigente · saída > saldo → erro com disponível · retorno + média · abaixo do mínimo · quantidade ≤ 0 → erro
- [x] `Cor`: hex válido/opcional · hex inválido → erro · nome vazio → erro · rótulo
- [x] `Material`: categoria M · categoria P → erro · adicionar cor · cor repetida → erro · arquivar/reativar
- [x] `Producao`: uso com custo vigente · uso sem saldo → erro · retorno com origem e custo do uso · devolvível · retorno acima → erro · uso inexistente → erro · custos (11,50 / 71,50) · concluir bloqueia · reabrir com motivo e histórico · reabrir sem motivo → erro · publicar só concluída · dados públicos sem custo

**O que a Fase 1 ensinou (material para a `analise-beneficios.md`)**

Bugs que os testes pegaram antes de chegar no banco:

1. **Quantidade que arredonda para zero.** `0,0001 m` passava no `exigir_positivo`, virava `0,000`
   depois do arredondamento de 3 casas e, num estoque vazio, a média ponderada dividia por zero.
   Correção: arredondar primeiro e validar depois (ciclo extra na Tarefa 5).
2. **O mesmo no item de compra:** `0,001 rolo` com "3 rolos = 1 m" entrava como `0,000 m` e o custo
   de entrada dividia por zero. Agora o item exige que a entrada no estoque seja maior que zero.
3. **Hex com quebra de linha.** A regex `^#…$` aceitava `"#315A81\n"`, porque o `$` do Python casa
   antes da quebra de linha final. Trocado por `fullmatch`.
4. **Mão de obra negativa na produção** (lacuna do plano): RN-T01 não tinha teste na `Producao`;
   uma mão de obra de −60 baixaria o custo total. Ciclo extra na Tarefa 9.

Testes que já nasceram verdes (o comportamento veio de um ciclo anterior; commitados como
`[GREEN] teste confirma …`, sem `[RED]`, como teste de regressão):
fator fracionado (T2), entrada histórica da compra (T3), entrada em estoque vazio (T5), saída do
saldo inteiro (T5), arquivar material sem perder cores (T7), custo do uso congelado (T8), retorno
com dois custos diferentes, média R$ 7,13 (T8), custo só de mão de obra (T9).

Números da fase: 67 commits `[RED]`, 75 `[GREEN]` (8 deles de testes que já passavam), 9 `[REFACTOR]`.

**Backend — Django**

- [ ] `contas.Usuario` (antes da 1ª migration)
- [ ] Models + migrations com as mudanças da seção 5
- [ ] `compras.registrar_compra` atômico (falha no 2º item desfaz tudo)
- [ ] `movimentacoes.registrar_uso` / `registrar_retorno` sem saldo negativo
- [ ] `producoes.concluir` / `reabrir` / `publicar`
- [ ] Endpoints DRF + JWT
- [ ] `sincronizacao.push` idempotente / `pull` com cursor

**App Flutter**

- [ ] Prévia de compra (total, entrada convertida) com testes de unidade
- [ ] Repositórios com fakes + Riverpod
- [ ] Banco Drift local e fila de operações pendentes

## 8. Convenções

- **Commits:** português, frase simples, como se explicasse para a dupla.
  `[RED] …` (teste falhando), `[GREEN] …` (mínimo para passar), `[REFACTOR] …` (melhoria sem mudar comportamento).
  Commits de configuração/documentação sem prefixo.
- **Testes:** `deve_<acao>_quando_<condicao>` / `nao_deve_<acao>_quando_<condicao>` (o `pytest.ini` já reconhece esses nomes).
- **Comentários:** explicam o *porquê* com palavras do ateliê ("1 rolo = 50 m"), não repetem o código.
- **Domínio:** `apps/<modulo>/dominio.py`; erros em português, herdando de uma exceção base do projeto.
- **Interface:** textos da Interface V2.2 ("Material e cor", "Quantidade no estoque", "Retirar da vitrine"), nunca nomes de tabela.

## 9. Cronograma da atividade

| Semana | O que | Entrega |
|---|---|---|
| 1 | Etapas 1 e 2: requisitos e setup | repositório + `docs/requisitos.md` |
| 2 | TDD das primeiras classes | commits RED/GREEN/REFACTOR |
| 3 | TDD completo + análise | código + `docs/analise-beneficios.md` |
| 4 | README final + slides | README com cobertura e nº de testes |
| depois | Apresentação (5 min contexto · 7 min demo ao vivo · 3 min benefícios) | — |

Critério que mais pesa (3,0): **evidência do ciclo TDD nos commits**. Escrever código de
produção antes do teste custa 3 pontos.

## 10. Registro de sessões

| Data | O que foi feito | Próximo passo |
|---|---|---|
| 07/10/2026 | Leitura dos documentos (Drive + Figma); decisões D01–D14 fechadas; repositório criado; estrutura vazia + README (commit 1); requisitos e este diário (commit 2). | Rodar `pytest` localmente; começar `ConversaoUnidade` com o primeiro `[RED]`. |
| 07/10/2026 | Roteiro ponta a ponta (8 fases) e plano detalhado da Fase 1 (10 tarefas, 71 ciclos). Requisitos ajustados: `registrar_uso(estoque, qtd, quando)`, `alterar`, `estoque_da_cor`, `chave`, `VarianteDiferenteError`, reabrir tira da vitrine (confirmado, D15). | Gabriel revisar o plano e escolher como executar. |
| 07/10/2026 | Histórico regravado sem a linha de coautoria do Claude (autor continua o Gabriel). D15 confirmada. | Executar a Fase 1. |
| 07/10/2026 | Codespaces configurado (`.devcontainer/`). Fase 0 verificada (3 testes, `pub get`, pastas Android/web). **Fase 1 completa** em ciclos RED/GREEN/REFACTOR: 92 testes, 100% de cobertura do domínio, 4 bugs pegos pelos testes (seção 7). | Revisar e fazer o merge do PR; escrever o plano detalhado da Fase 2 (models + migrations). |
