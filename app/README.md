# App do ateliê (Flutter)

Aplicativo para celular (Android) e navegador (web). Guarda os dados num SQLite local
(via Drift) para funcionar sem internet e sincroniza com a API Django quando houver conexão.

## Primeira vez na máquina

As pastas de plataforma (`android/`, `web/`) já estão no repositório (geradas com o
Flutter 3.47.6). Dentro desta pasta `app/`, basta:

```bash
flutter pub get
```

> No GitHub Codespaces isso já acontece sozinho quando o ambiente é criado.

## Rodando os testes

```bash
flutter test --coverage
```

## Organização

```
lib/
  main.dart               # casca do app
  src/
    core/                 # coisas compartilhadas (tema, formatação de dinheiro, erros)
    features/
      cadastros/          # material, cor, unidade, fornecedor
      compras/            # nova compra com vários itens
      estoque/            # saldo por material e cor, histórico
      producoes/          # peças, uso, retorno, conclusão, reabertura
    sincronizacao/        # fila local + PUSH/PULL com o Django
test/                     # espelha a estrutura de lib/src
```
