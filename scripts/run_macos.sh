#!/bin/zsh
set -eu
cd "${0:A:h}/.."
# Qt skips hidden plugins; clear hidden flags before launching.
for plugin_dir in .venv/lib/python*/site-packages/PySide6/Qt/plugins(N); do
  chflags -R nohidden "$plugin_dir"
done
exec .venv/bin/python main.py "$@"
