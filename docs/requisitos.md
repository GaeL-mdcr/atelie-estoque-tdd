# Requisitos para o TDD — Etapa 1

> Documento da Etapa 1 da atividade. Ele recorta, dos requisitos completos do ateliê
> (Análise de Requisitos V3.2), **o que vai ser construído com TDD** e em que forma:
> classes, métodos, regras de negócio e cenários de erro.
>
> Versão 1.0 — 07/10/2026

## 1. Contexto

O sistema é para um ateliê de pequeno porte cuja dona trabalha pelo celular. Ela compra
materiais (tecidos, linhas, botões…) de fornecedores diferentes, em unidades comerciais
diferentes (rolo, pacote, metro) e em várias cores. O mesmo material existe em várias cores e
**cada cor tem saldo, estoque mínimo e custo médio próprios**. As compras podem ter vários
itens e precisam converter a unidade comprada para a unidade de estoque. Os materiais são
usados nas produções (as peças) e podem voltar ao estoque; nada disso pode reescrever o
histórico, porque é dele que sai o custo real de cada peça. As regras ficam no backend Django
(a fonte oficial) e o app Flutter mostra prévias e funciona offline.

## 2. Onde as regras moram

As regras de negócio são escritas como **classes de domínio em Python puro**, sem banco e sem
Django, dentro de cada módulo (`backend/apps/<modulo>/dominio.py`). Assim cada regra é testada
em milissegundos. Depois, os *services* do Django usam essas classes dentro de
`transaction.atomic()` para gravar no banco — e também nascem de testes.

Valores de dinheiro e quantidade são sempre `Decimal` (nunca `float`):
quantidades com 3 casas, dinheiro com 2 casas, fator de conversão com 6 casas,
arredondamento "meio para cima" (`ROUND_HALF_UP`).

## 3. Classes principais e responsabilidades

| # | Classe | Módulo | Responsabilidade | Tabela(s) do modelo |
|---|---|---|---|---|
| 1 | `Cor` | cadastros | Nome e código hexadecimal opcional de uma cor reutilizável. | Cor |
| 2 | `Material` | cadastros | Dados gerais do material, categoria do tipo Material, unidade de estoque, cores cadastradas e arquivamento. | Material, Material_Variante_Cor, Categoria |
| 3 | `ConversaoUnidade` | conversoes | Equivalência entre unidade de compra e unidade de estoque de **um** material; calcula fator e quantidade convertida. | Conversao_Unidade |
| 4 | `ItemCompra` | compras | Um item da compra: quantidade, preço, quantidade que entra no estoque (guardada como histórico) e custos. | Compra_Material |
| 5 | `Compra` | compras | Junta os itens, calcula o total e controla rascunho × confirmada. | Compra |
| 6 | `EstoqueVariante` | estoque | Saldo, custo médio ponderado e alerta de mínimo de **uma** combinação material + cor. | Material_Variante_Cor |
| 7 | `Producao` | producoes | Peça: usos e retornos de material, custos, conclusão, reabertura com histórico e publicação. | Producao, Uso_Material, Reabertura_Producao |

Objetos de apoio (sem regra própria relevante): `Categoria` (nome + tipo M/P),
`MovimentacaoMaterial` (um uso **U** ou retorno **R**) e `EventoReabertura`.

## 4. Métodos e comportamento esperado

### 4.1 `Cor`

| Assinatura | Comportamento esperado |
|---|---|
| `Cor(nome: str, codigo_hex: str \| None = None)` | Guarda o nome sem espaços nas pontas. Hex é opcional; se vier, precisa ser `#RRGGBB`. |
| `cor.rotulo() -> str` | Devolve o nome para exibir ao lado da amostra (a cor nunca é mostrada só pela bolinha). |

### 4.2 `Material`

| Assinatura | Comportamento esperado |
|---|---|
| `Material(nome: str, categoria: Categoria, unidade_estoque_id: int)` | Cria o material ativo. A categoria precisa ser do tipo **M**. |
| `material.adicionar_cor(cor: Cor, qtd_estoque_minimo=0, qtd_inicial=0, vl_unitario_inicial=0) -> EstoqueVariante` | Cria a variante daquela cor com saldo inicial, mínimo e custo inicial. |
| `material.cores() -> list[str]` | Nomes das cores já cadastradas para o material. |
| `material.arquivar()` / `material.reativar()` | Liga/desliga `ativo`. Arquivado some das listas de escolha, mas o histórico continua. |

### 4.3 `ConversaoUnidade`

| Assinatura | Comportamento esperado |
|---|---|
| `ConversaoUnidade(material_id, unidade_compra_id, qtd_equivalente_compra, qtd_equivalente_estoque)` | Exemplo: `(material 1, rolo, 1, 50)` → 1 rolo = 50 m. |
| `conversao.fator() -> Decimal` | `qtd_equivalente_estoque ÷ qtd_equivalente_compra`, 6 casas. |
| `conversao.converter(qtd_compra) -> Decimal` | `qtd_compra × fator`, 3 casas. 2 rolos → 100 m. |
| `conversao.atende(material_id, unidade_compra_id) -> bool` | Só vale para o mesmo material e a mesma unidade de compra. |

### 4.4 `ItemCompra`

| Assinatura | Comportamento esperado |
|---|---|
| `ItemCompra(variante_id, material_id, unidade_compra_id, unidade_estoque_id, qtd_compra, vl_unitario_compra, conversao=None)` | Unidades iguais → entra a mesma quantidade. Unidades diferentes → exige conversão compatível. |
| `item.qtd_entrada_estoque` | Calculada **uma vez** na criação e guardada; mudar a conversão depois não altera o item. |
| `item.total() -> Decimal` | `qtd_compra × vl_unitario_compra`, 2 casas. |
| `item.custo_unitario_entrada() -> Decimal` | `total ÷ qtd_entrada_estoque`, 2 casas. Ex.: 2 rolos × R$ 80 = R$ 160 ÷ 100 m = R$ 1,60/m. |

### 4.5 `Compra`

| Assinatura | Comportamento esperado |
|---|---|
| `Compra(fornecedor_id, usuario_id, data, observacoes="")` | Nasce como rascunho, sem itens. |
| `compra.adicionar_item(item)` | Inclui o item no rascunho. |
| `compra.editar_item(posicao, item)` | Troca o item daquela posição. |
| `compra.remover_item(posicao)` | Tira o item e o total se ajusta. |
| `compra.total() -> Decimal` | Soma dos totais dos itens (nunca digitado). |
| `compra.confirmar()` | Fecha a compra. Daí em diante não aceita mais mudanças. |

### 4.6 `EstoqueVariante`

| Assinatura | Comportamento esperado |
|---|---|
| `EstoqueVariante(qtd_inicial=0, vl_unitario_inicial=0, qtd_estoque_minimo=0)` | Saldo começa no inicial e o custo médio no valor inicial. |
| `estoque.saldo` / `estoque.custo_medio` | Somente leitura: não existe "editar saldo". |
| `estoque.registrar_entrada(qtd, custo_total)` | Soma no saldo e recalcula a média ponderada: `(saldo×média + custo_total) ÷ (saldo + qtd)`. |
| `estoque.registrar_saida(qtd) -> Decimal` | Tira do saldo e devolve o custo médio vigente (que fica gravado no uso). Média não muda. |
| `estoque.registrar_retorno(qtd, custo_unitario)` | Devolve ao saldo e recalcula a média ponderada com o custo do uso de origem. |
| `estoque.abaixo_do_minimo() -> bool` | `True` quando `saldo < mínimo`. |

### 4.7 `Producao`

| Assinatura | Comportamento esperado |
|---|---|
| `Producao(nome_peca, categoria: Categoria, usuario_id, vl_mao_obra=0, vl_venda=0, pasta_id=None)` | Pasta é opcional. Categoria precisa ser do tipo **P**. |
| `producao.registrar_uso(variante_id, estoque, qtd, quando) -> MovimentacaoMaterial` | Cria um **U** com o custo médio vigente da cor; o estoque daquela cor diminui. |
| `producao.quantidade_devolvivel(id_uso) -> Decimal` | `quantidade usada − retornos já feitos daquele uso`. |
| `producao.registrar_retorno(id_uso_origem, estoque, qtd, quando) -> MovimentacaoMaterial` | Cria um **R** apontando para o uso de origem, com o custo daquele uso. O uso original não é apagado. |
| `producao.custo_materiais() -> Decimal` | `Σ (qtd × custo) dos U − Σ (qtd × custo) dos R`. |
| `producao.custo_total() -> Decimal` | `custo_materiais + mão de obra`. |
| `producao.concluir(data)` | Marca a data de finalização. Daí em diante usos e retornos ficam bloqueados. |
| `producao.reabrir(motivo, usuario_id, quando) -> EventoReabertura` | Volta a ficar em andamento e registra **quem, quando e por quê** no histórico. |
| `producao.historico_reaberturas() -> list[EventoReabertura]` | Lista as reaberturas em ordem. |
| `producao.publicar_na_vitrine()` / `producao.retirar_da_vitrine()` | Publicação manual, só de peça concluída. |
| `producao.dados_publicos() -> dict` | Só nome, categoria, descrição, valor de venda e imagens — nada de custo, fornecedor ou estoque. |

**Total: 7 classes e 33 métodos/propriedades testáveis**, fora os 7 construtores, que também
validam dados (mínimo exigido: 4 classes e 15 métodos).

## 5. Regras de negócio que os testes vão validar

| Código | Regra | Classe | Origem |
|---|---|---|---|
| RN-T01 | Quantidade e valor nunca negativos; quantidades de movimento e de compra maiores que zero. | todas | RN20 |
| RN-T02 | A mesma cor não pode ser cadastrada duas vezes no mesmo material. | Material | RN02 |
| RN-T03 | Categoria de material é do tipo M; categoria de produção é do tipo P. | Material, Producao | RN02 |
| RN-T04 | Fator = estoque ÷ compra, com denominador maior que zero. | ConversaoUnidade | RN05 |
| RN-T05 | Unidade de compra diferente da de estoque exige conversão do **mesmo** material e da **mesma** unidade. | ItemCompra | RN13, RN20 |
| RN-T06 | A quantidade que entrou no estoque é histórica: mudar a conversão não muda compra antiga. | ItemCompra | RN09 |
| RN-T07 | Total do item = qtd × preço; total da compra = soma dos itens; custo de entrada = total ÷ entrada. | ItemCompra, Compra | RN07, RN08 |
| RN-T08 | Compra sem itens não pode ser confirmada; compra confirmada não muda. | Compra | RN04, RF15, RF16 |
| RN-T09 | Saldo = inicial + entradas − usos + retornos, nunca editado à mão. | EstoqueVariante | RN10, RN22 |
| RN-T10 | Custo médio ponderado móvel por cor; uma cor não afeta a outra. | EstoqueVariante | RN11, RF21 |
| RN-T11 | Uso não pode passar do saldo. | EstoqueVariante, Producao | RN13 |
| RN-T12 | Uso grava o custo médio vigente; compras posteriores não mudam esse custo. | Producao | RN14 |
| RN-T13 | Retorno aponta para o uso de origem, usa o custo daquele uso e não passa do que ainda pode voltar. | Producao | RN13, RN14 (fechada em 07/10) |
| RN-T14 | Custo de materiais = usos − retornos; custo total = materiais + mão de obra. | Producao | RN15 |
| RN-T15 | Produção concluída não aceita uso nem retorno. | Producao | RF30 |
| RN-T16 | Reabertura exige motivo e fica registrada com usuário e data. | Producao | RF30 (fechada em 07/10) |
| RN-T17 | Só produção concluída pode ser publicada; a vitrine só recebe dados públicos. | Producao | RN18, RF31, RF35 |
| RN-T18 | Material arquivado continua com histórico, só sai das listas de escolha. | Material | RN19 (fechada em 07/10) |

## 6. Cenários de exceção (pelo menos um por classe)

Os erros são exceções próprias, com mensagem em português que a tela pode mostrar.

| Classe | Situação | Exceção esperada |
|---|---|---|
| Cor | Hex fora do formato `#RRGGBB` (ex.: `azul`, `#12345`) | `CorInvalidaError` |
| Cor | Nome vazio | `ValorObrigatorioError` |
| Material | Mesma cor adicionada duas vezes | `VarianteDuplicadaError` |
| Material | Categoria do tipo P | `CategoriaIncompativelError` |
| ConversaoUnidade | Equivalência zero ou negativa | `QuantidadeInvalidaError` |
| ConversaoUnidade | Converter quantidade zero ou negativa | `QuantidadeInvalidaError` |
| ItemCompra | Unidades diferentes sem conversão | `ConversaoAusenteError` |
| ItemCompra | Conversão de outro material ou outra unidade | `ConversaoIncompativelError` |
| ItemCompra | Preço negativo | `ValorInvalidoError` |
| Compra | Confirmar sem itens | `CompraSemItensError` |
| Compra | Mexer em itens depois de confirmada | `CompraConfirmadaError` |
| Compra | Editar/remover posição que não existe | `ItemNaoEncontradoError` |
| EstoqueVariante | Saída maior que o saldo (mensagem traz o disponível) | `SaldoInsuficienteError` |
| EstoqueVariante | Entrada/saída/retorno com quantidade ≤ 0 | `QuantidadeInvalidaError` |
| Producao | Retorno maior que o devolvível daquele uso | `RetornoExcedeUsoError` |
| Producao | Retorno de um uso que não existe nessa produção | `UsoNaoEncontradoError` |
| Producao | Uso ou retorno com a produção concluída | `ProducaoConcluidaError` |
| Producao | Reabrir sem motivo | `ValorObrigatorioError` |
| Producao | Reabrir produção que não está concluída | `ProducaoNaoConcluidaError` |
| Producao | Publicar produção não concluída | `ProducaoNaoConcluidaError` |

## 7. Ordem planejada dos ciclos TDD

Do mais simples ao mais dependente (caminho feliz primeiro, depois bordas e erros):

1. `ConversaoUnidade` — fator, converter, atende, erros de quantidade
2. `ItemCompra` — total, entrada com e sem conversão, custo de entrada, erros de conversão
3. `Compra` — adicionar, total, editar, remover, confirmar, erros de rascunho
4. `EstoqueVariante` — saldo, entrada com média ponderada, saída, retorno, mínimo, saldo insuficiente
5. `Cor` e `Material` — validações, adicionar cor, duplicidade, arquivamento
6. `Producao` — uso, retorno com origem, custos, conclusão, reabertura, publicação
7. Services Django (`registrar_compra`, `registrar_uso`, `registrar_retorno`…) com banco e transação
8. Lado Flutter — prévias de compra e repositórios com fakes

## 8. Exemplos numéricos que viram testes

Tirados da Referência SQL V3.1, para os testes terem números conferíveis à mão:

- Tecido Oxford Azul começa com 10 m a R$ 7,00/m.
- Compra de 2 rolos a R$ 80,00 com 1 rolo = 20 m → entram 40 m, item de R$ 160,00, custo de entrada R$ 4,00/m.
- Custo médio depois da compra: (10 × 7 + 160) ÷ (10 + 40) = **R$ 4,60/m**, saldo **50 m**.
- Saia midi usa 3 m → custo do uso R$ 4,60/m, saldo 47 m.
- Retorno de 0,5 m desse uso → saldo **47,5 m**; custo de materiais (3 × 4,60 − 0,5 × 4,60) = **R$ 11,50**;
  com mão de obra de R$ 60,00, custo total **R$ 71,50**.
