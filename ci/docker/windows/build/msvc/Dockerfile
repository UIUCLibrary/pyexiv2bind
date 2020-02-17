# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019
FROM ${FROM_IMAGE}

# Reset the shell.
#SHELL ["cmd", "/S", "/C"]
#RUN mkdir c:\\TEMP
#ADD https://aka.ms/vscollect.exe C:/TEMP/collect.exe
#
## Download channel for fixed install.
#ARG CHANNEL_URL=https://aka.ms/vs/16/release/channel
#ADD ${CHANNEL_URL} C:/TEMP/VisualStudio.chman
#
## Download and install Build Tools for Visual Studio 2019 for native desktop workload.
#
#ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:/TEMP/vs_buildtools.exe
#
#RUN (C:\\TEMP\\vs_buildtools.exe `
#    --quiet --wait --norestart --nocache `
#    --channelUri C:\\TEMP\\VisualStudio.chman `
#    --installChannelUri C:\\TEMP\\VisualStudio.chman `
#    --add Microsoft.VisualStudio.Workload.VCTools `
#    --add Microsoft.VisualStudio.Component.Windows10SDK `
#    --add Microsoft.VisualStudio.Component.Windows10SDK.18362 `
#    --add Microsoft.VisualStudio.Component.VC.CMake.Project `
#    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64	 `
#    --includeRecommended `
#    --add Microsoft.VisualStudio.Component.NuGet `
#    --installPath C:\BuildTools `
#  || IF "%ERRORLEVEL%"=="3010" C:\TEMP\collect.exe -zip:C:\vslogs.zip && EXIT 0 )`
#  && C:\TEMP\collect.exe -zip:C:\vslogs.zip `
#  && @echo Cleaning up temp files`
#  && del /S /F /Q %temp% `
#  && del /S /F /Q %Windir%\Temp `
#  && @echo Done cleaning up files in temp directories


#RUN @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" `
#    && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
SHELL ["powershell", "-command"]
RUN $env:chocolateyUseWindowsCompression = 'true' ; Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
ARG CHOCOLATEY_SOURCE=""
ADD ci/docker/windows/build/msvc/packages.config packages.config
RUN If($Env:CHOCOLATEY_SOURCE -ne $null     ){Write-Host "using $Env:CHOCOLATEY_SOURCE" ; choco install -y --no-progress --source=$Env:CHOCOLATEY_SOURCE packages.config} Else {choco install -y --no-progress packages.config} ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse

ADD ci/docker/windows/build/msvc/startup.bat c:\temp\startup.bat
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"
RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe

RUN $ErrorActionPreference = 'Stop'; `
    Invoke-WebRequest $Env:PYTHON_INSTALLER_URL -OutFile c:\python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-installer.exe -Force

ENV PIPENV_CACHE_DIR=c:\pipenv_cache `
    WORKON_HOME=c:\venvs `
    PIPENV_NOSPIN=True `
    PIP_DOWNLOAD_CACHE=c:\pip_cache

#ADD ci/docker/windows/build/msvc/Profile.ps1 C:\Windows\System32\WindowsPowerShell\v1.0\Profile.ps1

RUN python -m pip install --upgrade pip ; `
    pip install --upgrade setuptools ; `
    pip install wheel pipenv sphinx tox mypy lxml pytest flake8 pytest-cov pytest-bdd
#
ADD requirements.txt c:/temp/
RUN cd c:\temp ; pip install -r requirements.txt

