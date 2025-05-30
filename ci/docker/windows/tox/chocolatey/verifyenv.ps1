cmd /S /C '"C:\Program Files\NASM\nasm" --version'
if ($LASTEXITCODE -ne 0) { throw "Exit code for nasm was $LASTEXITCODE" }

cmd /S /C 'git --version'
if ($LASTEXITCODE -ne 0) { throw "Exit code for git was $LASTEXITCODE" }

cmd /S /C 'uv --version'
if ($LASTEXITCODE -ne 0) { throw "Exit code for uv was $LASTEXITCODE" }
