# App do ateliê (Flutter)

Aplicativo para celular (Android) e navegador (web). Guarda os dados num SQLite local
(via Drift) para funcionar sem internet e sincroniza com a API Django quando houver conexão.

## Primeira vez na máquina

As pastas de plataforma (`android/`, `web/`) não vão no primeiro commit porque são geradas
pelo próprio Flutter. Dentro desta pasta `app/`, rode uma vez:

```bash
flutter create --platforms=android,web --project-name atelie .
flutter pub get
```

> O `flutter create .` não apaga o `lib/main.dart` nem o `pubspec.yaml` que já existem.
> Ele cria um `test/widget_test.dart` de exemplo que procura um `MyApp` que não existe aqui:
> **apague esse arquivo** antes de rodar os testes.
> Se o `pub get` reclamar de versão, rode `flutter pub upgrade --major-versions`.

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
