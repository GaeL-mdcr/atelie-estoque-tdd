#!/usr/bin/env python
"""Atalho do Django para rodar servidor, migrations e afins."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não achei o Django. O ambiente virtual está ativado? "
            "Rode: pip install -r requirements-dev.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
