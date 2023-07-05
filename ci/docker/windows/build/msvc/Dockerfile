# escape=`

ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8

FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE}

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

# First install Visual Studio Build Tools

COPY ci/docker/shared/startup.bat c:\temp\startup.bat
RUN Invoke-WebRequest https://aka.ms/vs/17/release/vs_buildtools.exe -OutFile ${Env:TEMP}\\vs_buildtools.exe ; `
    Invoke-WebRequest https://aka.ms/vs/17/release/channel -OutFile ${Env:TEMP}\\VisualStudio.chman ; `
    Invoke-WebRequest https://aka.ms/vscollect.exe  -OutFile ${Env:TEMP}\\collect.exe ; `
    Write-Host "Installing Visual Studio Build Tools" ; `
    Start-Process -NoNewWindow -FilePath $Env:TEMP\\vs_buildtools.exe -ArgumentList '--quiet  --installPath "C:\\BuildTools"  --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.CLI.Support --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.18362' -Wait  ; `
    Write-Host "Installing Visual Studio Build Tools - Done" ; `
    Write-Host "Testing for VsDevCmd.bat" ; `
    if (! (Test-Path "C:\BuildTools\Common7\Tools\VsDevCmd.bat")) `
    { `
        Start-Process -NoNewWindow -FilePath $Env:TEMP\\collect.exe -ArgumentList \"-nologo -zip:${Env:TEMP}\\vslogs.zip\" -Wait; `
        Expand-Archive -Path $Env:TEMP\\vslogs.zip -DestinationPath $Env:TEMP\\logs\\ ; `
        Get-Content -LiteralPath \"${Env:TEMP}\\logs\\[Content_Types].xml\" ; `
        throw 'VsDevCmd.bat not found' ; `
    } ; `
    Write-Host "Testing for VsDevCmd.bat - Found" ; `
    Write-Host "Adding VsDevCmd.bat to cmd.exe startup" ; `
    Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat" ; `
    Write-Host "Adding VsDevCmd.bat to cmd.exe startup - Done" ; `
    Write-Host "Cleaning up $Env:TEMP" ; `
    Remove-Item -Force -Recurse $Env:TEMP\* ; `
    Write-Host "Cleaning up $Env:TEMP - Done"


ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ADD ci/docker/shared/chocolatey/install_choco.ps1 choco/install_choco.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\"; `
        choco source remove -n=chocolatey ;`
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    Write-Host "Removing chocolatey's deprecated cpack utlity to avoid confusion with cmake's cpack utlity" ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Write-Host "Cleaning up ${Env:TEMP}" ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    Write-Host "Cleaning up ${Env:TEMP} - Done"


ADD ci/docker/shared/chocolatey/packages.config choco/packages.config

RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey"

COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe
RUN Invoke-WebRequest $Env:PYTHON_INSTALLER_URL -OutFile c:\python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-installer.exe -Force ; `
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User') ; `
    python --version

#ADD ci/docker/windows/build/msvc/Profile.ps1 C:\Windows\System32\WindowsPowerShell\v1.0\Profile.ps1
ARG PIP_EXTRA_INDEX_URL
RUN python -m pip install --upgrade pip ; `
    pip install --upgrade setuptools ; `
    pip install wheel

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/temp/
ENV PIP_NO_CACHE_DIR=1
RUN pip wheel --wheel-dir=c:\wheels `
        -r c:/temp/requirements.txt `
        -r c:/temp/requirements-ci.txt ; `
    pip wheel --wheel-dir=c:\wheels -r c:/temp/requirements-extra.txt ; `
    pip install --no-index --find-links c:\wheels\ `
        -r c:/temp/requirements.txt `
        -r c:/temp/requirements-ci.txt
ENV PIP_FIND_LINKS=c:\wheels\
