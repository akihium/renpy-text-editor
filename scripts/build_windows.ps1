$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$Python = Join-Path (Get-Location) '.venv/Scripts/python.exe'
if (-not (Test-Path $Python)) { throw 'Create .venv with Python 3.12 and install requirements first.' }
& $Python -m PyInstaller --noconfirm --clean --windowed --onedir --name 'RenPy Text Editor' --collect-data adv_editor --collect-all docx --collect-all reportlab --distpath dist --workpath build main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
& $Python scripts/prepare_distribution.py 'dist/RenPy Text Editor'
if ($LASTEXITCODE -ne 0) { throw 'Release content preparation failed.' }
$Verification = Join-Path $env:TEMP ('renpy-check-' + [guid]::NewGuid().ToString('N'))
$Process = Start-Process -FilePath 'dist/RenPy Text Editor/RenPy Text Editor.exe' -ArgumentList @('--verify-exports', $Verification) -Wait -PassThru
if ($Process.ExitCode -ne 0 -or -not (Test-Path "$Verification/result.json")) { throw 'Packaged EXE export check failed.' }
$Result = Get-Content "$Verification/result.json" -Raw | ConvertFrom-Json
if (-not $Result.ok) { throw 'Packaged EXE check returned failure.' }
$Archive = 'dist/RenPy Text Editor-Windows-x64.zip'
Compress-Archive -Path 'dist/RenPy Text Editor' -DestinationPath $Archive -Force
Write-Host "Created $Archive (extract the whole folder, then run RenPy Text Editor.exe)"
