Get-Command git
Get-Command wget
cmd /S /C '"C:\Program Files\NASM\nasm" --version'
if ($LASTEXITCODE -eq 1) { throw "Exit code is 1" }