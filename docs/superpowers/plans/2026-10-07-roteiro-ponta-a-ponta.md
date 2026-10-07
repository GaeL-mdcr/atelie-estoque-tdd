# Roteiro de ponta a ponta — Sistema de Estoque para Ateliê

> Visão geral de **todo** o desenvolvimento, do domínio puro até o app Flutter sincronizando.
> Cada fase vira um plano detalhado próprio (passo a passo de TDD) quando chegar a vez dela,
> porque os nomes e tipos das fases seguintes dependem do que a anterior entregar.
>
> - Plano detalhado pronto: **Fase 1** → [`2026-10-07-fase1-dominio-backend.md`](2026-10-07-fase1-dominio-backend.md)
> - Contexto e decisões: [`docs/CONTEXTO.md`](../../CONTEXTO.md) · Requisitos da etapa 1: [`docs/requisitos.md`](../../requisitos.md)

## Visão das fases

| Fase | Entrega | Onde | Semana da atividade | Entra na nota do TDD? |
|---|---|---|---|---|
| 0 | Ambiente local verificado | máquina do Gabriel | 1 | setup |
| 1 | **Domínio do backend** (7 classes, Python puro) | `backend/apps/*/dominio.py` | 2 | **sim — núcleo** |
| 2 | Persistência: models, constraints, migrations | `backend/apps/*/models.py` | 3 | sim |
| 3 | Services transacionais (compra, uso, retorno, conclusão) | `backend/apps/*/services.py` | 3 | sim |
| 4 | Documentação da atividade (análise, README, slides) | `docs/`, `README.md` | 3–4 | sim |
| 5 | API REST + login JWT | `backend/apps/*/api.py` | depois | continuação |
| 6 | Sincronização PUSH/PULL idempotente | `backend/apps/sincronizacao/` | depois | continuação |
| 7 | App Flutter: domínio de prévia, banco local, fila, telas | `app/lib/src/` | depois | continuação |
| 8 | Vitrine pública | `backend/apps/vitrine/` | futuro | não |

A atividade cobra no mínimo 4 classes e 15 métodos testáveis: **a Fase 1 sozinha já entrega
7 classes e mais de 30 métodos**. As Fases 2–3 mostram TDD com banco e transação, o que
enriquece a apresentação. Da Fase 5 em diante é o projeto real do ateliê continuando, no
mesmo ritmo Red → Green → Refactor.

## Ordem de dependência

```
comum (Decimal, erros, arquivável)
  ├── conversoes ──► compras
  └── estoque ──► cadastros ──► producoes
                                   │
        models (Fase 2) ◄──────────┘
             │
        services (Fase 3) ──► API (Fase 5) ──► sync (Fase 6) ──► Flutter (Fase 7)
```

---

## Fase 0 — Ambiente local

- `pip install -r backend/requirements-dev.txt` e `pytest` dentro de `backend/` → 3 testes de configuração passando.
- `flutter create --platforms=android,web --project-name atelie .` em `app/`, apagar `test/widget_test.dart`, `flutter pub get`.
- Registrar no CONTEXTO as versões que o `pub get` resolveu.

## Fase 1 — Domínio do backend (Python puro)

Plano detalhado: [`2026-10-07-fase1-dominio-backend.md`](2026-10-07-fase1-dominio-backend.md).

| Classe | Métodos testáveis |
|---|---|
| `comum.numeros` | `decimal_de`, `quantidade`, `dinheiro`, `fator`, `exigir_positivo`, `exigir_nao_negativo` |
| `comum.Arquivavel` | `ativo`, `arquivar()`, `reativar()` |
| `ConversaoUnidade` | `fator()`, `converter(qtd)`, `atende(material_id, unidade_id)`, `alterar(compra, estoque)` |
| `ItemCompra` | `qtd_entrada_estoque`, `total()`, `custo_unitario_entrada()` |
| `Compra` | `adicionar_item`, `editar_item`, `remover_item`, `itens`, `total()`, `confirmar()` |
| `EstoqueVariante` | `saldo`, `custo_medio`, `registrar_entrada`, `registrar_saida`, `registrar_retorno`, `abaixo_do_minimo()` |
| `Cor` / `Categoria` | construtores com validação, `rotulo()`, arquivar/reativar |
| `Material` | `adicionar_cor`, `cores()`, `estoque_da_cor`, arquivar/reativar |
| `Producao` | `registrar_uso`, `registrar_retorno`, `quantidade_devolvivel`, `movimentacoes()`, `custo_materiais()`, `custo_total()`, `concluir`, `reabrir`, `historico_reaberturas()`, `publicar_na_vitrine`, `retirar_da_vitrine`, `dados_publicos()` |

## Fase 2 — Persistência (models + migrations)

Testes com `@pytest.mark.django_db`. Cada constraint nasce de um teste que tenta gravar o dado proibido.

| Model | Testes que guiam |
|---|---|
| `contas.Usuario` (`AUTH_USER_MODEL`, login por e-mail) | cria usuário com e-mail único; senha guardada em hash, nunca em texto |
| `Categoria` | `UNIQUE(tipo, nome)` sem diferenciar maiúsculas; tipo só M/P |
| `UnidadeMedida`, `Cor`, `Fornecedor` | nome único; `ativo` padrão `True`; hex `#RRGGBB` |
| `Material` | FK categoria tipo M; FK unidade de estoque; `ativo` |
| `MaterialVarianteCor` | `UNIQUE(material, cor)`; saldo/custo ≥ 0; `para_dominio()` devolve `EstoqueVariante` |
| `ConversaoUnidade` | `UNIQUE(material, unidade)`; equivalências > 0; `para_dominio()` |
| `Compra` / `CompraMaterial` | `qtd_entrada_estoque` guardada; total da compra por consulta |
| `PastaProducao` / `Producao` | apagar pasta deixa produção sem pasta (`SET_NULL`) |
| `UsoMaterial` | tipo U/R; `uso_origem` obrigatório só em R; `PROTECT` na produção e na variante |
| `ReaberturaProducao` (nova) | produção, usuário, motivo obrigatório, data |
| `ImagemProducao` | no máximo uma principal por produção (constraint condicional) |
| Exclusões | apagar material/fornecedor/cor com histórico → `ProtectedError` |

## Fase 3 — Services transacionais

Funções do Guia do Programador V3.1, cada uma em `transaction.atomic()`, usando o domínio da Fase 1.

| Função | Testes que guiam |
|---|---|
| `cadastros.criar_material_com_categoria(dados, usuario)` | categoria M criada só ao salvar; repetir não duplica (get_or_create por nome+tipo) |
| `cadastros.criar_variante(material, cor, dados)` | segunda criação da mesma cor falha sem gravar nada |
| `conversoes.registrar_equivalencia(material, unidade, compra, estoque)` | fator calculado; mudar depois não altera compra antiga |
| `compras.registrar_compra(dados, usuario)` | 2 itens gravados juntos; **erro no 2º item desfaz tudo**; saldo e custo médio da variante atualizados |
| `estoque.consultar_saldo(variante)` / `estoque.extrato(variante)` | saldo do extrato = saldo consolidado; ordem cronológica; rótulos "Compra registrada", "Material utilizado", "Material retornado" |
| `estoque.abaixo_do_minimo()` | lista só as cores abaixo do mínimo |
| `movimentacoes.registrar_uso(producao, variante, qtd, usuario)` | baixa condicional `UPDATE … WHERE saldo >= qtd`; sem saldo → erro e nada gravado |
| `movimentacoes.registrar_retorno(uso_origem, qtd, usuario)` | limite do devolvível no banco; custo do uso de origem |
| `producoes.concluir / reabrir / publicar / retirar` | grava `ReaberturaProducao`; reabrir tira da vitrine |
| `vitrine.pecas_publicadas()` | só concluídas e publicadas; sem custos |

## Fase 4 — Documentação da atividade

- `docs/analise-beneficios.md`: evolução do design guiada pelos testes, bugs pegos antes da integração (anotados durante as Fases 1–3 no CONTEXTO), comparativo com/sem TDD, lições aprendidas.
- README: número de testes, cobertura (`pytest --cov`), comando exato, integrantes.
- Slides: 5 min contexto, 7 min demonstração ao vivo (histórico de commits + execução + um ciclo explicado), 3 min benefícios.
- Ciclo sugerido para a demonstração ao vivo: **retorno acima do devolvível** (Fase 1, Tarefa 8) — é curto, tem número conferível e mostra uma regra que só o teste pegaria.

## Fase 5 — API REST + JWT

| Rota | Testes que guiam |
|---|---|
| `POST /api/v1/auth/token` e `/refresh` | login por e-mail; sem token → 401 |
| `GET/POST /api/v1/materiais`, `/cores`, `/unidades`, `/fornecedores`, `/categorias` | arquivados fora das listas; "Adicionar novo…" é responsabilidade do app |
| `POST /api/v1/conversoes` | equivalência ≤ 0 → 422 com mensagem |
| `POST /api/v1/compras` | totais recalculados no servidor (ignora total enviado); 201 só depois do commit |
| `GET /api/v1/estoque`, `/estoque/{id}/extrato` | filtros por material, cor, abaixo do mínimo |
| `POST /api/v1/producoes`, `/producoes/{id}/usos`, `/usos/{id}/retornos` | saldo insuficiente → **409** "Saldo disponível: 1,5 m" |
| `POST /api/v1/producoes/{id}/concluir`, `/reabrir`, `/publicar`, `/retirar` | reabrir sem motivo → 422 |
| `GET /vitrine/pecas` (sem login) | serializer público separado; nenhum campo de custo |

## Fase 6 — Sincronização

| Peça | Testes que guiam |
|---|---|
| `sync_operacao` (UUID do cliente, hash do payload, resposta guardada) | mesmo UUID reenviado devolve a mesma resposta e não duplica; mesmo UUID com payload diferente → 409 |
| `sync_evento` (sequência) | gravado na mesma transação da operação |
| `POST /api/v1/sync/push` | lote com operação rejeitada não derruba as aceitas; resposta por operação |
| `GET /api/v1/sync/pull?cursor=` | página fixa; `proximo_cursor` = último evento enviado; cursor inválido → 400 |

## Fase 7 — App Flutter

| Camada | Testes que guiam |
|---|---|
| `core/dinheiro.dart`, `core/quantidade.dart` | formatação "R$ 1.234,56" e "47,5 m"; sem `double` para dinheiro |
| `features/compras/previa_compra.dart` | mesmo cálculo do backend (entrada convertida, total, custo de entrada) — mesmos números da Fase 1 |
| Banco Drift (`AppDatabase`) | tabelas espelho + `operacoes_pendentes`; testes com banco em memória |
| Repositórios + Riverpod | `observarEstoque()` emite ao gravar; fakes nos testes de widget |
| `SyncService.enviarPendentes()` / `buscarAtualizacoes(cursor)` | reenvio usa o mesmo UUID; lote do PULL aplicado em transação; cursor salvo junto |
| Telas (widget tests) | Nova compra mantém o total visível; dropdown com "＋ Adicionar novo…" primeiro; erro de saldo mantém o formulário preenchido; produção concluída sem ações de uso/retorno |
| Rotas (`go_router`) | Início, Materiais, Produções, Estoque |

## Fase 8 — Vitrine (futuro)

Templates Django em `apps/vitrine/` lendo `vitrine.pecas_publicadas()` da Fase 3.
Nada novo de regra: o domínio (`dados_publicos()`) e o serializer público já existem.

## Fora do escopo por enquanto

Hospedagem (Google Cloud ou AWS), PostgreSQL, perfis de acesso detalhados, relatórios, lucro/margem.
