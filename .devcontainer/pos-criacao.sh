#!/usr/bin/env bash
# Roda uma vez, quando o Codespace é criado: prepara o backend e baixa o Flutter.
set -euo pipefail

raiz="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Backend: criando o venv e instalando as dependências de teste"
cd "$raiz/backend"
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements-dev.txt

echo "==> Flutter: baixando o canal stable (só na primeira vez)"
if [ ! -x "$HOME/flutter/bin/flutter" ]; then
  git clone --depth 1 --branch stable https://github.com/flutter/flutter.git "$HOME/flutter"
fi
export PATH="$PATH:$HOME/flutter/bin"
flutter config --no-analytics --enable-web
flutter --version

echo "==> App: baixando os pacotes do pubspec"
cd "$raiz/app"
flutter pub get

echo
echo "Pronto. Para conferir:"
echo "  cd backend && source .venv/bin/activate && pytest"
echo "  cd app && flutter test"
