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

**Semana 1 — Etapas 1 e 2.**

- [x] Repositório criado no GitHub (público)
- [x] Estrutura vazia do backend (módulos Django sem código de regra)
- [x] pytest / pytest-django / pytest-cov configurados (`backend/pytest.ini`, `.coveragerc`)
- [x] Casca do app Flutter (`pubspec.yaml`, `lib/main.dart`, pastas por funcionalidade)
- [x] README inicial
- [x] `docs/requisitos.md` (Etapa 1)
- [ ] **Rodar os testes de configuração na máquina local** (ver seção 6 — ainda não foram executados)
- [ ] Gerar pastas de plataforma do Flutter (`flutter create --platforms=android,web .`) e conferir `flutter pub get`
- [ ] Primeiro ciclo TDD: `ConversaoUnidade.fator()`

Código de produção existente: **nenhum** (só configuração).

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

- O ambiente de nuvem onde a estrutura foi montada **não tem acesso ao PyPI nem ao download
  do Flutter**. Por isso `pytest` e `flutter test` ainda **não foram executados**; o código
  Python foi checado só quanto à sintaxe. A execução real acontece na máquina do Gabriel (Windows).
- Versões do `pubspec.yaml` foram escritas sem rodar `pub get`. Se der conflito:
  `flutter pub upgrade --major-versions` e registrar aqui as versões que ficaram.
- O link do Figma só expõe a página do design system (*DS 10 • Components*); as telas são
  descritas pela Interface V2.2.

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
- Execução no ambiente de nuvem: só a Fase 1 roda lá (pytest 9 isolado em `/root/.local/bin/pytest`, sem Django).

**Backend — domínio (Python puro)**

- [ ] `ConversaoUnidade`: fator · converter · atende · equivalência ≤ 0 · converter ≤ 0
- [ ] `ItemCompra`: total · entrada sem conversão · entrada com conversão · custo de entrada · sem conversão → erro · conversão de outro material → erro · preço negativo → erro · entrada não muda se a conversão mudar
- [ ] `Compra`: adicionar · total · editar · remover · confirmar · confirmar vazia → erro · mexer depois de confirmada → erro · posição inexistente → erro
- [ ] `EstoqueVariante`: saldo inicial · entrada + média ponderada (exemplo 4,60) · saída devolve custo vigente · saída > saldo → erro com disponível · retorno + média · abaixo do mínimo · quantidade ≤ 0 → erro
- [ ] `Cor`: hex válido/opcional · hex inválido → erro · nome vazio → erro · rótulo
- [ ] `Material`: categoria M · categoria P → erro · adicionar cor · cor repetida → erro · arquivar/reativar
- [ ] `Producao`: uso com custo vigente · uso sem saldo → erro · retorno com origem e custo do uso · devolvível · retorno acima → erro · uso inexistente → erro · custos (11,50 / 71,50) · concluir bloqueia · reabrir com motivo e histórico · reabrir sem motivo → erro · publicar só concluída · dados públicos sem custo

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
