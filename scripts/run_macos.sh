#!/bin/zsh
set -eu
cd "${0:A:h}/.."
# iCloud 可能再次附加 hidden 屬性；Qt 的外掛掃描會略過隱藏檔。
for plugin_dir in .venv/lib/python*/site-packages/PySide6/Qt/plugins(N); do
  chflags -R nohidden "$plugin_dir"
done
exec .venv/bin/python main.py "$@"
