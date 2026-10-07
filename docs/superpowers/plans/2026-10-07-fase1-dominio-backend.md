# Fase 1 — Domínio do backend: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir com TDD as regras de negócio do ateliê em Python puro: conversão de unidades, compra com itens, estoque por cor com custo médio ponderado, cadastros de material/cor e produção com uso, retorno, custos, conclusão, reabertura e publicação.

**Architecture:** Cada módulo Django ganha um `dominio.py` sem nenhuma importação de Django, com classes pequenas e exceções próprias. As Fases 2–3 vão envolver estas classes em models e services transacionais. Valores sempre `Decimal`, criados por funções de `apps/comum/numeros.py`.

**Tech Stack:** Python 3.12+, `decimal`, `dataclasses`, `uuid`, pytest (sem Django nesta fase).

**Spec:** [`docs/requisitos.md`](../../requisitos.md) + decisões D05–D07, D11, D13 de [`docs/CONTEXTO.md`](../../CONTEXTO.md). Roteiro geral: [`2026-10-07-roteiro-ponta-a-ponta.md`](2026-10-07-roteiro-ponta-a-ponta.md).

## Global Constraints

- **Protocolo de cada ciclo** (é o que a nota de 3,0 pontos avalia):
  1. escrever **só** o teste do ciclo → 2. rodar e ver **FALHAR** (erro de import conta como falha) →
  3. `git commit` só do arquivo de teste com `[RED] …` → 4. escrever o **mínimo** de código para passar →
  5. rodar o arquivo de teste inteiro e ver **PASSAR** → 6. `git commit` com `[GREEN] …` →
  7. se houver duplicação ou nome ruim, refatorar, rodar de novo e commitar `[REFACTOR] …`.
  Nunca escrever código de produção que nenhum teste pediu ainda.
- Mensagens de commit e comentários **em português, simples e humanizados** (ex.: `[RED] teste do fator: 1 rolo tem que virar 50 metros`). Autor de todos os commits: **Gabriel Mallezan da Costa Ribeiro**. **Nenhuma** linha de coautoria (`Co-Authored-By`) ou de sessão em mensagem nenhuma.
- `dominio.py` e `apps/comum/*` **não importam Django**.
- Nada de `float`: toda entrada numérica passa por `decimal_de()`; `float` e `bool` são recusados.
- Arredondamento `ROUND_HALF_UP`: quantidade **3** casas, dinheiro **2**, fator **6**.
- Toda exceção de regra herda de `ErroDeNegocio` e tem mensagem em português que a tela pode mostrar.
- Nomes de teste: `deve_<acao>_quando_<condicao>` ou `nao_deve_<acao>_quando_<condicao>` (o `pytest.ini` já coleta esses nomes).
- Testes de cada módulo em `backend/apps/<modulo>/tests/test_dominio.py` (o de `comum` em `test_numeros.py` e `test_arquivavel.py`).
- Comandos rodam de dentro de `backend/`: `pytest apps/<modulo>/tests/<arquivo>.py -v`.
  No ambiente de nuvem (sem Django instalado), use `/root/.local/bin/pytest -p no:cacheprovider apps/<modulo>/tests/<arquivo>.py -v`; o aviso sobre `DJANGO_SETTINGS_MODULE` é esperado.
- Números de referência (Referência SQL V3.1): Tecido Oxford Azul 10 m a R$ 7,00 · compra 2 rolos × R$ 80 com 1 rolo = 20 m → +40 m, custo médio **R$ 4,60**, saldo **50 m** · Saia midi usa 3 m, devolve 0,5 m → saldo **47,5 m**, materiais **R$ 11,50**, com mão de obra R$ 60 → total **R$ 71,50**.

## Review Focus

1. **`float` chegando do JSON** (`0.1`): tem que ser recusado com `ValorInvalidoError`, não virar `0.1000000000000000055…` — teste na Tarefa 1, ciclo 2.
2. **Dois retornos do mesmo uso que, somados, passam do usado**: o segundo é recusado e o estoque não muda — teste na Tarefa 8, ciclo 7.
3. **Posição negativa em `remover_item(-1)`**: em Python isso apagaria o último item sem aviso; tem que dar `ItemNaoEncontradoError` — teste na Tarefa 4, ciclo 8.
4. **Estoque zerado** recebendo entrada ou retorno: sem divisão por zero, o custo médio vira o custo que entrou — testes na Tarefa 5, ciclos 3 e 7.
5. **Mesma cor escrita diferente** (`"Azul"` e `" azul "`): é a mesma cor, segunda inclusão recusada — teste na Tarefa 7, ciclo 4.

**Decisão D15 (confirmada pelo Gabriel em 07/10):** reabrir uma produção **publicada** tira a peça da vitrine automaticamente, porque peça em andamento não é peça concluída (Tarefa 9, ciclo 8).

---

### Tarefa 1: Base comum — números, erros e arquivável

**Files:**
- Create: `backend/apps/comum/__init__.py`, `backend/apps/comum/erros.py`, `backend/apps/comum/numeros.py`, `backend/apps/comum/arquivavel.py`
- Create: `backend/apps/comum/tests/__init__.py`, `backend/apps/comum/tests/test_numeros.py`, `backend/apps/comum/tests/test_arquivavel.py`
- Modify: `backend/requirements-dev.txt` (`pytest>=8,<10`, porque a versão atual já é a 9)

`comum` é só um pacote Python: **não** entra em `INSTALLED_APPS`.

**Interfaces:**
- Produces:
  - `erros.ErroDeNegocio(Exception)`; subclasses `ValorObrigatorioError`, `ValorInvalidoError`, `QuantidadeInvalidaError`. `str(erro)` é a mensagem.
  - `numeros.decimal_de(valor: Decimal | int | str) -> Decimal`
  - `numeros.quantidade(valor) -> Decimal` (3 casas) · `numeros.dinheiro(valor) -> Decimal` (2 casas) · `numeros.fator(valor) -> Decimal` (6 casas)
  - `numeros.exigir_positivo(valor, campo: str) -> Decimal` → `QuantidadeInvalidaError` se ≤ 0
  - `numeros.exigir_nao_negativo(valor, campo: str) -> Decimal` → `ValorInvalidoError` se < 0
  - `numeros.texto_obrigatorio(texto: str | None, campo: str) -> str` → devolve sem espaços nas pontas; vazio → `ValorObrigatorioError`
  - `arquivavel.Arquivavel` (mixin): atributo `ativo: bool`, `arquivar()`, `reativar()`; quem herda chama `self.ativo = True` no `__init__`.

- [x] **Ciclo 1 — decimal a partir de texto e inteiro**
```python
def deve_converter_texto_e_inteiro_para_decimal():
    assert decimal_de("1.5") == Decimal("1.5")
    assert decimal_de(2) == Decimal("2")
    assert decimal_de(Decimal("3.25")) == Decimal("3.25")
```
Implementar `decimal_de` em `numeros.py`. Commits: `[RED] teste do decimal_de com texto, inteiro e Decimal` / `[GREEN] decimal_de convertendo texto e inteiro`.

- [x] **Ciclo 2 — recusar float e bool** (Review Focus 1)
```python
@pytest.mark.parametrize("valor", [0.1, 2.0, True])
def nao_deve_aceitar_float_nem_bool(valor):
    with pytest.raises(ValorInvalidoError):
        decimal_de(valor)
```
Cria `erros.py` com `ErroDeNegocio` e `ValorInvalidoError`. `bool` é checado antes de `int` (porque `True` é `int` em Python).

- [x] **Ciclo 3 — recusar texto que não é número**
```python
@pytest.mark.parametrize("valor", ["abc", "", None, "NaN", "Infinity"])
def nao_deve_aceitar_valor_que_nao_e_numero(valor):
    with pytest.raises(ValorInvalidoError):
        decimal_de(valor)
```
`NaN` e `Infinity` são `Decimal` válidos para o Python, mas não para o ateliê: recusar com `is_finite()`.

- [x] **Ciclo 4 — arredondamento meio para cima**
```python
def deve_arredondar_meio_para_cima_em_cada_escala():
    assert dinheiro("2.345") == Decimal("2.35")
    assert dinheiro("2") == Decimal("2.00")
    assert quantidade("1.2345") == Decimal("1.235")
    assert fator("0.3333335") == Decimal("0.333334")
```
`quantize` com `ROUND_HALF_UP` sobre `decimal_de(valor)`.

- [x] **Ciclo 5 — exigir positivo / não negativo / texto obrigatório**
```python
def deve_validar_positivo_nao_negativo_e_texto():
    assert exigir_positivo("0.001", "quantidade") == Decimal("0.001")
    assert exigir_nao_negativo("0", "preço") == Decimal("0")
    assert texto_obrigatorio("  Azul ", "nome") == "Azul"
    with pytest.raises(QuantidadeInvalidaError, match="quantidade"):
        exigir_positivo("0", "quantidade")
    with pytest.raises(ValorInvalidoError, match="preço"):
        exigir_nao_negativo("-0.01", "preço")
    with pytest.raises(ValorObrigatorioError, match="nome"):
        texto_obrigatorio("   ", "nome")
    assert issubclass(QuantidadeInvalidaError, ErroDeNegocio)
```
A mensagem cita o campo (ex.: `"A quantidade precisa ser maior que zero."`).

- [x] **Ciclo 6 — arquivável** (em `test_arquivavel.py`)
```python
class Coisa(Arquivavel):
    def __init__(self):
        self.ativo = True

def deve_arquivar_e_reativar():
    coisa = Coisa()
    coisa.arquivar()
    assert coisa.ativo is False
    coisa.reativar()
    assert coisa.ativo is True
```

- [x] **Fechamento:** `pytest apps/comum -v` → 6 testes de função (com parametrizações, mais casos) passando. Ajustar `requirements-dev.txt` num commit próprio: `Atualiza o pytest para aceitar a versão 9`.

---

### Tarefa 2: `ConversaoUnidade`

**Files:**
- Create: `backend/apps/conversoes/dominio.py`, `backend/apps/conversoes/tests/test_dominio.py`

**Interfaces:**
- Consumes: `decimal_de`, `fator`, `quantidade`, `exigir_positivo` (Tarefa 1)
- Produces: `ConversaoUnidade(material_id: int, unidade_compra_id: int, qtd_equivalente_compra, qtd_equivalente_estoque)` com `material_id`, `unidade_compra_id`, `fator() -> Decimal`, `converter(qtd_compra) -> Decimal`, `atende(material_id: int, unidade_compra_id: int) -> bool`, `alterar(qtd_equivalente_compra, qtd_equivalente_estoque) -> None`

Nos testes: `ROLO = 2`, `METRO = 1`, `TECIDO = 1`.

- [x] **Ciclo 1 — fator inteiro**
```python
def deve_calcular_fator_quando_um_rolo_vale_cinquenta_metros():
    assert ConversaoUnidade(TECIDO, ROLO, "1", "50").fator() == Decimal("50.000000")
```
- [x] **Ciclo 2 — fator fracionado**
```python
def deve_calcular_fator_quando_tres_unidades_valem_uma():
    assert ConversaoUnidade(TECIDO, ROLO, "3", "1").fator() == Decimal("0.333333")
```
- [x] **Ciclo 3 — converter**
```python
def deve_converter_quantidade_comprada_para_unidade_de_estoque():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "50")
    assert rolo.converter("2") == Decimal("100.000")
    assert rolo.converter("1.5") == Decimal("75.000")
    assert ConversaoUnidade(TECIDO, ROLO, "3", "1").converter("3") == Decimal("1.000")
```
`quantidade(decimal_de(qtd) * self.fator())` — o último caso (0,999999 → 1,000) garante o arredondamento de 3 casas.
- [x] **Ciclo 4 — só vale para o mesmo material e unidade**
```python
def deve_atender_somente_o_mesmo_material_e_a_mesma_unidade():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "50")
    assert rolo.atende(TECIDO, ROLO) is True
    assert rolo.atende(TECIDO, 3) is False
    assert rolo.atende(9, ROLO) is False
```
- [x] **Ciclo 5 — equivalência inválida**
```python
@pytest.mark.parametrize("compra,estoque", [("0", "50"), ("1", "0"), ("-1", "50")])
def nao_deve_aceitar_equivalencia_zero_ou_negativa(compra, estoque):
    with pytest.raises(QuantidadeInvalidaError):
        ConversaoUnidade(TECIDO, ROLO, compra, estoque)
```
- [x] **Ciclo 6 — converter quantidade inválida**
```python
@pytest.mark.parametrize("qtd", ["0", "-2"])
def nao_deve_converter_quantidade_zero_ou_negativa(qtd):
    with pytest.raises(QuantidadeInvalidaError):
        ConversaoUnidade(TECIDO, ROLO, "1", "50").converter(qtd)
```
- [x] **Ciclo 7 — alterar a equivalência com a mesma validação**
```python
def deve_alterar_equivalencia_validando_de_novo():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "50")
    rolo.alterar("1", "25")
    assert rolo.fator() == Decimal("25.000000")
    with pytest.raises(QuantidadeInvalidaError):
        rolo.alterar("0", "25")
    assert rolo.fator() == Decimal("25.000000")
```
- [x] **Refactor provável:** construtor e `alterar` validando no mesmo método privado. Commit `[REFACTOR] construtor e alterar usam a mesma validação`.

---

### Tarefa 3: `ItemCompra`

**Files:**
- Create: `backend/apps/compras/dominio.py`, `backend/apps/compras/tests/test_dominio.py`

**Interfaces:**
- Consumes: `ConversaoUnidade` (Tarefa 2), `quantidade`, `dinheiro`, `exigir_positivo`, `exigir_nao_negativo`
- Produces: `ItemCompra(variante_id: int, material_id: int, unidade_compra_id: int, unidade_estoque_id: int, qtd_compra, vl_unitario_compra, conversao: ConversaoUnidade | None = None)` com atributos `variante_id`, `qtd_compra` (3 casas), `vl_unitario_compra` (2 casas), `qtd_entrada_estoque` (3 casas, calculado **uma vez** no construtor) e métodos `total() -> Decimal`, `custo_unitario_entrada() -> Decimal`. Exceções `ConversaoAusenteError`, `ConversaoIncompativelError`.

Nos testes: `AZUL = 10` (variante), `TECIDO = 1`, `METRO = 1`, `ROLO = 2`, fábrica `item_em_metro(qtd, preco)` (unidades iguais) e `item_em_rolo(qtd, preco, conversao)`.

- [x] **Ciclo 1 — total do item**
```python
def deve_calcular_total_do_item():
    assert item_em_metro("3", "7.50").total() == Decimal("22.50")
```
- [x] **Ciclo 2 — entrada igual à compra quando a unidade é a mesma**
```python
def deve_entrar_a_mesma_quantidade_quando_unidades_sao_iguais():
    assert item_em_metro("3", "7.50").qtd_entrada_estoque == Decimal("3.000")
```
- [x] **Ciclo 3 — entrada convertida**
```python
def deve_converter_a_entrada_quando_comprou_em_rolo():
    item = item_em_rolo("2", "80", ConversaoUnidade(TECIDO, ROLO, "1", "20"))
    assert item.qtd_entrada_estoque == Decimal("40.000")
    assert item.total() == Decimal("160.00")
```
- [x] **Ciclo 4 — custo unitário de entrada**
```python
def deve_calcular_custo_por_metro_que_entrou():
    item = item_em_rolo("2", "80", ConversaoUnidade(TECIDO, ROLO, "1", "20"))
    assert item.custo_unitario_entrada() == Decimal("4.00")
```
- [x] **Ciclo 5 — histórico não muda**
```python
def nao_deve_mudar_a_entrada_quando_a_conversao_muda_depois():
    rolo = ConversaoUnidade(TECIDO, ROLO, "1", "20")
    item = item_em_rolo("2", "80", rolo)
    rolo.alterar("1", "25")
    assert item.qtd_entrada_estoque == Decimal("40.000")
```
Este passa logo de cara se a entrada já é guardada no construtor: rodar e **confirmar que passa**, commitar como `[GREEN] teste confirma que a compra antiga não muda com a conversão nova` (sem RED, porque o comportamento já existia — registrar isso no diário como exemplo de teste de regressão).
- [x] **Ciclo 6 — falta conversão**
```python
def nao_deve_aceitar_unidade_diferente_sem_conversao():
    with pytest.raises(ConversaoAusenteError):
        item_em_rolo("2", "80", None)
```
- [x] **Ciclo 7 — conversão de outro material ou unidade**
```python
@pytest.mark.parametrize("conversao", [
    ConversaoUnidade(9, ROLO, "1", "20"),
    ConversaoUnidade(TECIDO, 3, "1", "20"),
])
def nao_deve_aceitar_conversao_que_nao_e_deste_material_e_unidade(conversao):
    with pytest.raises(ConversaoIncompativelError):
        item_em_rolo("2", "80", conversao)
```
- [x] **Ciclo 8 — quantidade e preço**
```python
def nao_deve_aceitar_preco_negativo_nem_quantidade_zero():
    with pytest.raises(ValorInvalidoError):
        item_em_metro("1", "-1")
    with pytest.raises(QuantidadeInvalidaError):
        item_em_metro("0", "5")
    assert item_em_metro("2", "0").custo_unitario_entrada() == Decimal("0.00")
```
Preço zero é permitido (brinde do fornecedor).

---

### Tarefa 4: `Compra`

**Files:**
- Modify: `backend/apps/compras/dominio.py`
- Modify: `backend/apps/compras/tests/test_dominio.py`

**Interfaces:**
- Consumes: `ItemCompra` (Tarefa 3), `dinheiro`
- Produces: `Compra(fornecedor_id: int, usuario_id: int, data: datetime, observacoes: str = "")` com `confirmada: bool`, `itens -> tuple[ItemCompra, ...]` (property, cópia), `adicionar_item(item)`, `editar_item(posicao: int, item)`, `remover_item(posicao: int)`, `total() -> Decimal`, `confirmar()`. Exceções `CompraSemItensError`, `CompraConfirmadaError`, `ItemNaoEncontradoError`.

Nos testes: fixture `compra()` com `fornecedor_id=1, usuario_id=1, data=datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)`.

- [x] **Ciclo 1** `deve_comecar_como_rascunho_sem_itens`: `confirmada is False`, `itens == ()`, `total() == Decimal("0.00")`.
- [x] **Ciclo 2** `deve_somar_os_totais_dos_itens`: itens de R$ 160,00 e R$ 22,50 → `total() == Decimal("182.50")`, `len(itens) == 2`.
- [x] **Ciclo 3** `deve_editar_o_item_na_posicao`: `editar_item(0, item_em_metro("1", "10"))` → `itens[0]` é o novo; `total() == Decimal("32.50")`.
- [x] **Ciclo 4** `deve_remover_item_e_ajustar_o_total`: com os dois itens, `remover_item(1)` → `total() == Decimal("160.00")`.
- [x] **Ciclo 5** `deve_confirmar_compra_com_itens`: `confirmar()` → `confirmada is True`.
- [x] **Ciclo 6** `nao_deve_confirmar_compra_sem_itens` → `CompraSemItensError`.
- [x] **Ciclo 7** `nao_deve_mexer_em_compra_confirmada`: depois de confirmar, `adicionar_item`, `editar_item(0, …)`, `remover_item(0)` e `confirmar()` levantam `CompraConfirmadaError`; `total()` continua o mesmo.
- [x] **Ciclo 8** `nao_deve_aceitar_posicao_que_nao_existe` (Review Focus 3):
```python
@pytest.mark.parametrize("posicao", [5, -1])
def nao_deve_aceitar_posicao_que_nao_existe(compra, posicao):
    compra.adicionar_item(item_em_metro("1", "10"))
    with pytest.raises(ItemNaoEncontradoError):
        compra.remover_item(posicao)
    with pytest.raises(ItemNaoEncontradoError):
        compra.editar_item(posicao, item_em_metro("1", "10"))
    assert len(compra.itens) == 1
```
- [x] **Refactor provável:** `_exigir_rascunho()` e `_exigir_posicao(posicao)` privados.

---

### Tarefa 5: `EstoqueVariante`

**Files:**
- Create: `backend/apps/estoque/dominio.py`, `backend/apps/estoque/tests/test_dominio.py`

**Interfaces:**
- Consumes: `quantidade`, `dinheiro`, `exigir_positivo`, `exigir_nao_negativo`
- Produces: `EstoqueVariante(qtd_inicial="0", vl_unitario_inicial="0", qtd_estoque_minimo="0", *, variante_id: int | None = None)` com propriedades **somente leitura** `saldo` (3 casas), `custo_medio` (2 casas), `qtd_estoque_minimo`, `variante_id`; métodos `registrar_entrada(qtd, custo_total) -> None`, `registrar_saida(qtd) -> Decimal` (custo médio vigente), `registrar_retorno(qtd, custo_unitario) -> None`, `abaixo_do_minimo() -> bool`. Exceção `SaldoInsuficienteError` com atributo `disponivel: Decimal`.

Média ponderada (entrada e retorno): `dinheiro((saldo × custo_medio + valor_que_entra) ÷ (saldo + qtd))`, onde `valor_que_entra` é `custo_total` na entrada e `qtd × custo_unitario` no retorno.

- [x] **Ciclo 1** `deve_comecar_com_saldo_e_custo_iniciais`:
```python
estoque = EstoqueVariante("10", "7", "5")
assert estoque.saldo == Decimal("10.000")
assert estoque.custo_medio == Decimal("7.00")
with pytest.raises(AttributeError):
    estoque.saldo = Decimal("99")
```
- [x] **Ciclo 2** `deve_recalcular_media_ponderada_quando_entra_compra`: `EstoqueVariante("10", "7")`, `registrar_entrada("40", "160")` → `saldo == Decimal("50.000")`, `custo_medio == Decimal("4.60")`.
- [x] **Ciclo 3** `deve_usar_o_custo_da_compra_quando_estoque_estava_vazio` (Review Focus 4): `EstoqueVariante()`, `registrar_entrada("40", "160")` → `custo_medio == Decimal("4.00")`.
- [x] **Ciclo 4** `deve_baixar_saldo_e_devolver_custo_vigente_na_saida`: `EstoqueVariante("50", "4.60").registrar_saida("3") == Decimal("4.60")`; `saldo == Decimal("47.000")`; `custo_medio == Decimal("4.60")`.
- [x] **Ciclo 5** `nao_deve_sair_mais_que_o_saldo`:
```python
estoque = EstoqueVariante("2", "5")
with pytest.raises(SaldoInsuficienteError) as erro:
    estoque.registrar_saida("2.5")
assert erro.value.disponivel == Decimal("2.000")
assert estoque.saldo == Decimal("2.000")
```
- [x] **Ciclo 6** `deve_permitir_sair_todo_o_saldo`: `EstoqueVariante("2", "5").registrar_saida("2")` → `saldo == Decimal("0.000")`.
- [x] **Ciclo 7** `deve_devolver_ao_saldo_e_recalcular_media_no_retorno` (Review Focus 4):
```python
estoque = EstoqueVariante("47", "4.60")
estoque.registrar_retorno("0.5", "4.60")
assert estoque.saldo == Decimal("47.500")
assert estoque.custo_medio == Decimal("4.60")

outro = EstoqueVariante("10", "5")
outro.registrar_retorno("10", "7")
assert outro.custo_medio == Decimal("6.00")

vazio = EstoqueVariante()
vazio.registrar_retorno("1", "4.60")
assert (vazio.saldo, vazio.custo_medio) == (Decimal("1.000"), Decimal("4.60"))
```
- [x] **Ciclo 8** `deve_avisar_quando_abaixo_do_minimo`: `EstoqueVariante("4", "1", "5").abaixo_do_minimo() is True`; `EstoqueVariante("5", "1", "5").abaixo_do_minimo() is False`.
- [x] **Ciclo 9** `nao_deve_aceitar_quantidade_ou_valor_invalido`: `registrar_entrada("0", "1")`, `registrar_saida("-1")`, `registrar_retorno("0", "1")` → `QuantidadeInvalidaError`; `registrar_entrada("1", "-5")` e `EstoqueVariante("-1")` → `ValorInvalidoError`.
- [x] **Ciclo 10** `deve_guardar_o_id_da_variante`: `EstoqueVariante("1", "1", variante_id=10).variante_id == 10`; sem informar → `None`.

---

### Tarefa 6: `Cor` e `Categoria`

**Files:**
- Create: `backend/apps/cadastros/dominio.py`, `backend/apps/cadastros/tests/test_dominio.py`

**Interfaces:**
- Consumes: `texto_obrigatorio`, `Arquivavel`, `ValorInvalidoError`
- Produces:
  - `Cor(nome: str, codigo_hex: str | None = None)` (herda `Arquivavel`) com `nome`, `codigo_hex` (maiúsculo ou `None`), `rotulo() -> str`, `chave() -> str` (nome em minúsculas, usado para comparar). Exceção `CorInvalidaError`.
  - `Categoria(nome: str, tipo: str)` com `nome`, `tipo`; constantes `Categoria.MATERIAL = "M"`, `Categoria.PRODUCAO = "P"`. Exceção `CategoriaIncompativelError` (usada pelas Tarefas 7 e 8).

- [x] **Ciclo 1** `deve_guardar_nome_limpo_e_hex_em_maiusculas`: `Cor("  Azul ", "#315a81")` → `nome == "Azul"`, `codigo_hex == "#315A81"`, `rotulo() == "Azul"`.
- [x] **Ciclo 2** `deve_aceitar_cor_sem_hex`: `Cor("Branco").codigo_hex is None`.
- [x] **Ciclo 3** `nao_deve_aceitar_hex_fora_do_formato`: parametrizado com `"azul"`, `"#12345"`, `"#GGGGGG"`, `"315A81"` → `CorInvalidaError`. Regex `^#[0-9A-Fa-f]{6}$`.
- [x] **Ciclo 4** `nao_deve_aceitar_nome_vazio`: `Cor("   ")` e `Categoria("", "M")` → `ValorObrigatorioError`.
- [x] **Ciclo 5** `deve_criar_categoria_de_material_ou_producao`: `Categoria(" Tecido ", "M")` → `nome == "Tecido"`, `tipo == "M"`; `Categoria("Saia", "X")` → `ValorInvalidoError`.
- [x] **Ciclo 6** `deve_arquivar_e_reativar_cor`: `ativo` começa `True`, `arquivar()` → `False`, `reativar()` → `True`.

---

### Tarefa 7: `Material`

**Files:**
- Modify: `backend/apps/cadastros/dominio.py`, `backend/apps/cadastros/tests/test_dominio.py`

**Interfaces:**
- Consumes: `Cor`, `Categoria`, `CategoriaIncompativelError` (Tarefa 6), `EstoqueVariante` (Tarefa 5), `Arquivavel`
- Produces: `Material(nome: str, categoria: Categoria, unidade_estoque_id: int, descricao: str = "")` (herda `Arquivavel`) com `adicionar_cor(cor: Cor, qtd_estoque_minimo="0", qtd_inicial="0", vl_unitario_inicial="0") -> EstoqueVariante`, `cores() -> list[str]` (ordem de inclusão), `estoque_da_cor(cor: Cor) -> EstoqueVariante`. Exceções `VarianteDuplicadaError`, `VarianteNaoEncontradaError`.

Nos testes: `TECIDO = Categoria("Tecido", "M")`, `SAIA = Categoria("Saia", "P")`, `METRO = 1`.

- [x] **Ciclo 1** `deve_criar_material_ativo_com_categoria_de_material`: `Material("Tecido Oxford", TECIDO, METRO)` → `nome == "Tecido Oxford"`, `ativo is True`, `cores() == []`.
- [x] **Ciclo 2** `nao_deve_aceitar_categoria_de_producao`: `Material("Tecido Oxford", SAIA, METRO)` → `CategoriaIncompativelError`.
- [x] **Ciclo 3** `deve_adicionar_cor_com_estoque_proprio`: `adicionar_cor(Cor("Azul"), "5", "10", "7")` devolve estoque com `saldo == Decimal("10.000")`, `custo_medio == Decimal("7.00")`, `qtd_estoque_minimo == Decimal("5.000")`; `cores() == ["Azul"]`.
- [x] **Ciclo 4** `nao_deve_repetir_a_mesma_cor_no_material` (Review Focus 5): `adicionar_cor(Cor("Azul"))` e depois `adicionar_cor(Cor(" azul "))` → `VarianteDuplicadaError`; `cores() == ["Azul"]`.
- [x] **Ciclo 5** `deve_manter_estoque_separado_por_cor`: com Azul (10 m) e Branco (0 m), `estoque_da_cor(Cor("Branco")).registrar_entrada("10", "20")` → Azul continua `Decimal("10.000")`, Branco `Decimal("10.000")`.
- [x] **Ciclo 6** `nao_deve_achar_estoque_de_cor_nao_cadastrada`: `estoque_da_cor(Cor("Verde"))` → `VarianteNaoEncontradaError`.
- [x] **Ciclo 7** `deve_arquivar_sem_perder_as_cores`: `arquivar()` → `ativo is False`, `cores() == ["Azul"]`.

---

### Tarefa 8: `Producao` — uso e retorno

**Files:**
- Create: `backend/apps/producoes/dominio.py`, `backend/apps/producoes/tests/test_dominio.py`

**Interfaces:**
- Consumes: `EstoqueVariante` (Tarefa 5), `Categoria`, `CategoriaIncompativelError` (Tarefa 6), `numeros`, `erros`
- Produces:
  - `MovimentacaoMaterial` (`@dataclass(frozen=True)`): `id: str` (uuid4), `tipo: str` (`"U"` ou `"R"`), `variante_id: int`, `quantidade: Decimal`, `custo_unitario: Decimal`, `quando: datetime`, `id_uso_origem: str | None`; `valor_total() -> Decimal` (`dinheiro(quantidade × custo_unitario)`).
  - `Producao(nome_peca: str, categoria: Categoria, usuario_id: int, vl_mao_obra="0", vl_venda="0", pasta_id: int | None = None, descricao: str = "")` com `registrar_uso(estoque: EstoqueVariante, qtd, quando: datetime) -> MovimentacaoMaterial`, `registrar_retorno(id_uso_origem: str, estoque: EstoqueVariante, qtd, quando: datetime) -> MovimentacaoMaterial`, `quantidade_devolvivel(id_uso: str) -> Decimal`, `movimentacoes() -> tuple[MovimentacaoMaterial, ...]`.
  - Exceções `RetornoExcedeUsoError`, `UsoNaoEncontradoError`, `VarianteDiferenteError`, `ProducaoConcluidaError`, `ProducaoNaoConcluidaError` (as duas últimas usadas na Tarefa 9).

Nos testes: `SAIA = Categoria("Saia", "P")`, `T1 = datetime(2026, 9, 18, 17, 15, tzinfo=timezone.utc)`, `T2 = T1 + timedelta(minutes=5)`; fixture `saia()` = `Producao("Saia midi", SAIA, usuario_id=1, vl_mao_obra="60", vl_venda="220")`; fixture `azul()` = `EstoqueVariante("50", "4.60", variante_id=10)`.

- [x] **Ciclo 1** `deve_criar_producao_sem_pasta_e_so_com_categoria_de_producao`: `saia().pasta_id is None`; `Producao("Saia midi", Categoria("Tecido", "M"), 1)` → `CategoriaIncompativelError`; `Producao("  ", SAIA, 1)` → `ValorObrigatorioError`.
- [x] **Ciclo 2** `deve_registrar_uso_com_o_custo_medio_vigente`: `uso = saia.registrar_uso(azul, "3", T1)` → `uso.tipo == "U"`, `uso.variante_id == 10`, `uso.quantidade == Decimal("3.000")`, `uso.custo_unitario == Decimal("4.60")`, `uso.id_uso_origem is None`; `azul.saldo == Decimal("47.000")`. Estoque sem `variante_id` → `ValorObrigatorioError`.
- [x] **Ciclo 3** `deve_manter_o_custo_do_uso_quando_chega_compra_nova`: depois do uso, `azul.registrar_entrada("10", "100")` → `uso.custo_unitario == Decimal("4.60")`.
- [x] **Ciclo 4** `nao_deve_usar_mais_que_o_saldo`: `EstoqueVariante("2", "5", variante_id=10)`, uso de `"2.5"` → `SaldoInsuficienteError`; `saia.movimentacoes() == ()`.
- [x] **Ciclo 5** `deve_registrar_retorno_apontando_para_o_uso`: `r = saia.registrar_retorno(uso.id, azul, "0.5", T2)` → `r.tipo == "R"`, `r.id_uso_origem == uso.id`, `r.custo_unitario == Decimal("4.60")`; `azul.saldo == Decimal("47.500")`; `len(saia.movimentacoes()) == 2` e o uso continua lá.
- [x] **Ciclo 6** `deve_calcular_quanto_ainda_pode_voltar`: depois do retorno de 0,5 → `quantidade_devolvivel(uso.id) == Decimal("2.500")`.
- [x] **Ciclo 7** `nao_deve_devolver_mais_que_o_devolvivel` (Review Focus 2):
```python
uso = saia.registrar_uso(azul, "3", T1)
with pytest.raises(RetornoExcedeUsoError):
    saia.registrar_retorno(uso.id, azul, "3.5", T2)
saia.registrar_retorno(uso.id, azul, "2.5", T2)
with pytest.raises(RetornoExcedeUsoError):
    saia.registrar_retorno(uso.id, azul, "0.501", T2)
assert azul.saldo == Decimal("49.500")
assert len(saia.movimentacoes()) == 2
```
- [x] **Ciclo 8** `deve_devolver_com_o_custo_do_uso_de_origem` (D05 com dois custos diferentes):
```python
azul = EstoqueVariante("10", "4", variante_id=10)
uso1 = saia.registrar_uso(azul, "2", T1)          # 4,00
azul.registrar_entrada("10", "100")               # (8×4 + 100) ÷ 18 = 7,33
uso2 = saia.registrar_uso(azul, "2", T2)          # 7,33
retorno = saia.registrar_retorno(uso1.id, azul, "1", T2)
assert uso2.custo_unitario == Decimal("7.33")
assert retorno.custo_unitario == Decimal("4.00")
assert azul.saldo == Decimal("17.000")
assert azul.custo_medio == Decimal("7.13")        # (16×7,33 + 1×4,00) ÷ 17
```
- [x] **Ciclo 9** `nao_deve_devolver_uso_inexistente_nem_retorno`: `registrar_retorno("nao-existe", …)` → `UsoNaoEncontradoError`; usar o `id` de um **retorno** como origem → `UsoNaoEncontradoError`.
- [x] **Ciclo 10** `nao_deve_devolver_para_outra_cor`: uso no Azul (`variante_id=10`), retorno passando `EstoqueVariante("5", "3", variante_id=11)` → `VarianteDiferenteError`; os dois saldos ficam como estavam.

Regra de ouro desta tarefa: **validar tudo antes de mexer no estoque**, para que um erro nunca deixe o saldo alterado pela metade.

---

### Tarefa 9: `Producao` — custos, conclusão, reabertura e vitrine

**Files:**
- Modify: `backend/apps/producoes/dominio.py`, `backend/apps/producoes/tests/test_dominio.py`

**Interfaces:**
- Consumes: tudo da Tarefa 8
- Produces: em `Producao`: `custo_materiais() -> Decimal`, `custo_total() -> Decimal`, `concluir(data: date) -> None`, `concluida: bool` (property), `dt_finalizacao: date | None`, `reabrir(motivo: str, usuario_id: int, quando: datetime) -> EventoReabertura`, `historico_reaberturas() -> tuple[EventoReabertura, ...]`, `publicada: bool`, `publicar_na_vitrine()`, `retirar_da_vitrine()`, `dados_publicos() -> dict`. `EventoReabertura` (`@dataclass(frozen=True)`): `usuario_id: int`, `motivo: str`, `quando: datetime`, `dt_finalizacao_anterior: date`.

Nos testes: `CONCLUSAO = date(2026, 10, 20)`.

- [x] **Ciclo 1** `deve_calcular_os_custos_da_saia_midi`: uso de 3 m e retorno de 0,5 m no Azul a R$ 4,60 → `custo_materiais() == Decimal("11.50")`, `custo_total() == Decimal("71.50")`.
- [x] **Ciclo 2** `deve_ter_custo_so_de_mao_de_obra_sem_movimentacoes`: `custo_materiais() == Decimal("0.00")`, `custo_total() == Decimal("60.00")`.
- [x] **Ciclo 3** `deve_bloquear_uso_e_retorno_depois_de_concluir`: `concluir(CONCLUSAO)` → `concluida is True`, `dt_finalizacao == CONCLUSAO`; `registrar_uso` e `registrar_retorno` → `ProducaoConcluidaError`; `azul.saldo` inalterado.
- [x] **Ciclo 4** `nao_deve_concluir_duas_vezes` → `ProducaoConcluidaError`.
- [x] **Ciclo 5** `deve_reabrir_com_motivo_e_guardar_historico`:
```python
saia.concluir(CONCLUSAO)
evento = saia.reabrir("Cliente pediu ajuste na barra", usuario_id=1, quando=T2)
assert saia.concluida is False and saia.dt_finalizacao is None
assert evento.motivo == "Cliente pediu ajuste na barra"
assert evento.dt_finalizacao_anterior == CONCLUSAO
saia.registrar_uso(azul, "1", T2)                     # voltou a aceitar uso
saia.concluir(date(2026, 10, 25))
saia.reabrir("Trocar botões", usuario_id=1, quando=T2)
assert [e.motivo for e in saia.historico_reaberturas()] == ["Cliente pediu ajuste na barra", "Trocar botões"]
```
- [x] **Ciclo 6** `nao_deve_reabrir_sem_motivo_ou_sem_estar_concluida`: produção em andamento → `ProducaoNaoConcluidaError`; concluída com motivo `"   "` → `ValorObrigatorioError` e continua concluída.
- [x] **Ciclo 7** `deve_publicar_so_producao_concluida`: em andamento → `ProducaoNaoConcluidaError`; concluída → `publicar_na_vitrine()` → `publicada is True`; `retirar_da_vitrine()` → `False`.
- [x] **Ciclo 8** `deve_tirar_da_vitrine_quando_reabrir` (decisão do plano): concluída e publicada, `reabrir(...)` → `publicada is False`.
- [x] **Ciclo 9** `deve_expor_so_os_dados_publicos`:
```python
dados = saia.dados_publicos()
assert dados == {"nome_peca": "Saia midi", "categoria": "Saia",
                 "descricao": "", "vl_venda": Decimal("220.00")}
```
Imagens entram na Fase 2 (vêm de `Imagem_Producao`).

---

### Tarefa 10: Fechamento da fase

**Files:**
- Modify: `docs/CONTEXTO.md` (seções 4, 7 e 10), `README.md` (tabela de resultados), `docs/requisitos.md` (se alguma assinatura mudou durante os refactors)

- [x] Rodar `pytest apps -v` (na máquina local, com Django, rodar `pytest` inteiro) → todos passando.
- [x] Rodar `pytest apps --cov=apps --cov-report=term-missing` na máquina local → anotar cobertura dos `dominio.py` (meta: **≥ 95%**).
- [x] Anotar no CONTEXTO os "bugs que os testes pegaram" durante a fase (vira material da `analise-beneficios.md`).
- [x] Atualizar o README (número de testes e cobertura) e commitar: `Fecha a fase 1: domínio completo e diário atualizado`.
- [ ] Escrever o plano detalhado da Fase 2 a partir do roteiro.
