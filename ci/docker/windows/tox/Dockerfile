# escape=`
ARG PYTHON_36_VERSION=3.6.8
ARG PYTHON_37_VERSION=3.7.9
ARG PYTHON_38_VERSION=3.8.5
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE} as BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

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
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*


ADD ci/docker/shared/chocolatey/visual_studio.config choco/visual_studio.config
RUN $CocoPackageInstallConfig = \"choco\\visual_studio.config\" ; `
    C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    Get-Content -Path $CocoPackageInstallConfig ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose $CocoPackageInstallConfig; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (! (Test-Path 'C:\BuildTools\Common7\Tools\VsDevCmd.bat')) `
    { `
        throw 'VsDevCmd.bat not found' ; `
    }

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

ADD ci/docker/shared/startup.bat c:\temp\startup.bat
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY36
ARG PYTHON_36_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_36_VERSION}
SHELL ["cmd", "/S", "/C" ]
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-extra.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY37
ARG PYTHON_37_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_37_VERSION}
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-extra.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY38
ARG PYTHON_38_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_38_VERSION}
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-extra.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER

ARG PYTHON_36_VERSION
RUN choco install python3 --version ${Env:PYTHON_36_VERSION} -my

ARG PYTHON_37_VERSION
RUN choco install python3 --version ${Env:PYTHON_37_VERSION} -my

ARG PYTHON_38_VERSION
RUN choco install python3 --version ${Env:PYTHON_38_VERSION} -my

COPY --from=WHEEL_BUilDER_PY36 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY37 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY38 c:/wheels/ c:/wheels/
ENV PIP_FIND_LINKS=c:\wheels

RUN python -m pip install pip --upgrade ; pip install tox