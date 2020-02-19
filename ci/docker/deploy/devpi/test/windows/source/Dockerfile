# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]
RUN mkdir c:\\TEMP

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
ARG CHOCOLATEY_SOURCE="https://chocolatey.org/api/v2"
ADD ci/docker/deploy/devpi/test/windows/source/packages.config packages.config
#RUN If($Env:CHOCOLATEY_SOURCE -ne $null     ){Write-Host "using $Env:CHOCOLATEY_SOURCE" ; & "C:\ProgramData\chocolatey\bin\choco.exe install -y --no-progress --source=$Env:CHOCOLATEY_SOURCE packages.config"} Else {Write-Host "Using Chocholatey Community repository. NOTE: This might fail if the same docker host is running choco install in another container at the same time." ; & "C:\ProgramData\chocolatey\bin\choco.exe install -y --no-progress packages.config"} ; `
#    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
#    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse

RUN $SOURCE = $(if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { \"--source=$Env:CHOCOLATEY_SOURCE\" } `
    else `
    { "" }) ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress $SOURCE packages.config ;`
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse


ADD ci/docker/deploy/devpi/test/windows/source/startup.bat c:\temp\startup.bat
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"
RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe

RUN Invoke-WebRequest $Env:PYTHON_INSTALLER_URL -OutFile c:\python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-installer.exe -Force


RUN python -m pip install --upgrade pip ; `
    pip install --upgrade setuptools ; `
    pip install wheel pipenv sphinx tox devpi-client
