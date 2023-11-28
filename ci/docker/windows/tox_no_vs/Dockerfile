# escape=`
ARG PIPX_HOME=c:\pipx
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

FROM BASE_BUILDER AS CHOCOLATEY_BASE
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
COPY ci/docker/shared/chocolatey/install_choco.ps1 c:/choco/install_choco.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    c:/choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\"; `
        choco source remove -n=chocolatey ;`
    }; `
    choco feature disable --name="showDownloadProgress" ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*

COPY ci/docker/shared/chocolatey/packages.config c:/choco/packages.config
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose c:/choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey" \

COPY ci/docker/shared/chocolatey/python.xml c:/choco/python.config
RUN C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose c:/choco/python.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    py --list ;`
    py -3.8 --version ; `
    py -3.9 --version ; `
    py -3.10 --version ; `
    py -3.11 --version ; `
    py -3.12 --version ; `
    Write-Host "Installing Python with Chocolatey - Done"

COPY --from=certsgen c:/roots.sst c:/roots.sst
RUN certutil -addstore -f root c:/roots.sst ; `
    del c:/roots.sst
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

# ==============================================================================
FROM CHOCOLATEY_BASE

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY requirements-dev.txt c:/python_requirments/
COPY requirements/ c:/python_requirments/requirements
RUN python -m pip install --no-cache-dir pip --upgrade ; pip install --no-cache-dir -r c:/python_requirments/requirements-dev.txt


ARG PIP_DOWNLOAD_CACHE
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}\bin


RUN py -3 -m pip install --no-cache-dir pipx ; `
    py -3 -m pipx ensurepath
RUN py -3 -m pipx install 'devpi-client<7.0'


WORKDIR C:/src
CMD ["tox", "--workdir", "${Env:TEMP}\tox\\", "-vv",  "--recreate"]
