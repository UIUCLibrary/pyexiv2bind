# escape=`
ARG PIPX_HOME=c:\pipx
ARG VS_INSTALL_PATH="C:\BuildTools"
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_CACHE_DIR=c:\Users\ContainerUser\Documents\uvcache
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019
ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY ci/docker/windows/tox/msvc/startup.bat c:/startup/startup.bat
COPY ci/docker/windows/tox/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY ci/docker/windows/tox/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH

RUN c:/scripts/install_msvc.ps1 ${Env:VS_INSTALL_PATH} c:/setup/config.vsconfig; `
    Get-ChildItem C:\Users\ContainerAdministrator\AppData\Local\Temp | Remove-Item -Recurse -Force -Verbose
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY ci/docker/shared/chocolatey/install.ps1 c:/choco/install.ps1
COPY ci/docker/shared/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    $chocolateyDownloadUrl = c:/choco/get_latest_chocolatey_url.ps1 -packageRepo $env:CHOCOLATEY_SOURCE; `
    c:/choco/install.ps1 -ChocolateyDownloadUrl $chocolateyDownloadUrl;`
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"${env:CHOCOLATEY_SOURCE}\"; `
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*

COPY ci/docker/shared/chocolatey/packages.config c:/choco/packages.config
COPY ci/docker/shared/chocolatey/verifyenv.ps1 c:/verifyenv.ps1
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress c:/choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey" ;`
    Write-Host "Verifying installed packages" ;`
    $env:Path = [System.Environment]::GetEnvironmentVariable(\"Path\",\"Machine\") + \";\" + [System.Environment]::GetEnvironmentVariable(\"Path\",\"User\") ; `
    c:/verifyenv.ps1

COPY ci/docker/shared/chocolatey/python.xml c:/choco/python.config
COPY ci/docker/shared/chocolatey/Install-Python.ps1 c:/choco/Install-Python.ps1

RUN choco cache remove --confirm;`
    c:/choco/Install-Python.ps1 choco/python.config ;`
    choco cache remove --confirm ; `
    Write-Host "Installing Python with Chocolatey - Done"


# ==============================================================================
FROM BASE_BUILDER AS CONAN_BUILDER
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY requirements-dev.txt c:/requirements/requirements-dev.txt
#RUN python -m pip install --no-cache-dir --upgrade pip ; `
#    pip install --no-cache-dir -r c:/requirements/requirements-dev.txt
COPY ci/docker/windows/tox/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
SHELL ["cmd", "/S", "/C" ]
ENV CONAN_CMAKE_GENERATOR=Ninja
RUN python -m venv venv && `
    call venv\\Scripts\\activate.bat && `
    pip install uv --no-cache-dir && `
    uv pip install -r c:/requirements/requirements-dev.txt && `
    conan config home && `
    conan config init && `
    conan config set general.revisions_enabled=1 && `
    conan install c:/temp/ --build --no-import -pr:b=default && `
    conan remove "*" -b --src -f && `
    conan remove --lock && `
    rmdir /S /Q venv

FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst c:/roots.sst
RUN certutil -addstore -f root c:/roots.sst ; `
    del c:/roots.sst

ARG PIP_DOWNLOAD_CACHE
ARG UV_CACHE_DIR
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}
ENV UV_CACHE_DIR=${UV_CACHE_DIR}

ARG CONAN_USER_HOME
COPY --from=CONAN_BUILDER ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}


WORKDIR C:/src
CMD ["tox", "--workdir", "${Env:TEMP}\tox\\", "-vv",  "--recreate", "-p=auto"]
