#!/bin/zsh
set -eu
cd "${0:A:h}/.."
if [[ "$(uname -m)" != arm64 ]]; then
  echo '請在 Apple Silicon 原生 arm64 終端執行。'
  exit 1
fi
# 在非 iCloud 暫存目錄產生及簽章，避免 File Provider 持續附加 FinderInfo。
staging=$(mktemp -d /private/tmp/adv-build.XXXXXX)
export PYINSTALLER_CONFIG_DIR="$staging/cache"
.venv/bin/python -m PyInstaller --noconfirm --clean --windowed --name 'RenPy Text Editor' --osx-bundle-identifier com.advscript.editor --target-architecture arm64 --collect-data adv_editor --collect-all docx --collect-all reportlab --distpath "$staging/dist" --workpath "$staging/work" main.py
chflags -R nohidden "$staging/dist/RenPy Text Editor.app"
xattr -cr "$staging/dist/RenPy Text Editor.app"
codesign --force --deep --sign - "$staging/dist/RenPy Text Editor.app"
codesign --verify --deep --strict "$staging/dist/RenPy Text Editor.app"
# Verify the frozen app before packaging the public bundle.
QT_QPA_PLATFORM=offscreen "$staging/dist/RenPy Text Editor.app/Contents/MacOS/RenPy Text Editor" --verify-exports "$staging/smoke"
[[ -f "$staging/smoke/result.json" ]]
package="$staging/package/RenPy Text Editor"
mkdir -p "$package" dist
.venv/bin/python scripts/prepare_distribution.py "$package"
ditto "$staging/dist/RenPy Text Editor.app" "$package/RenPy Text Editor.app"
codesign --verify --deep --strict "$package/RenPy Text Editor.app"
ditto -c -k --keepParent "$package" 'dist/RenPy Text Editor-macOS-arm64.zip' 
echo "已打包：dist/RenPy Text Editor-macOS-arm64.zip"
echo "已驗證的 .app：$staging/dist/RenPy Text Editor.app"
