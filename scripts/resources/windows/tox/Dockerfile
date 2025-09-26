# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8.1

ARG VS_INSTALL_PATH="C:\BuildTools"

ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator
ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io

ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG chocolateyVersion

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER


SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY scripts/resources/windows/tox/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY scripts/resources/windows/tox/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH
ARG VS_VERSION="2022"
ARG VS_DevCmdArguments="-arch=amd64"
ARG VS_DevPowershellArguments='-arch=amd64'
RUN c:/scripts/install_msvc.ps1 -InstallPath ${Env:VS_INSTALL_PATH} -VSConfigFile c:/setup/config.vsconfig -DevCmdArguments ${Env:VS_DevCmdArguments} -DevPowershellArguments ${Env:VS_DevPowershellArguments} -VSVersion ${Env:VS_VERSION}; `
    Write-Host "Note: Exporting This layer can take a while."
RUN New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY scripts/resources/windows/tox/chocolatey/install.ps1 c:/choco/install.ps1
COPY scripts/resources/windows/tox/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
COPY scripts/resources/windows/tox/chocolatey/packages.config c:/choco/packages.config
COPY scripts/resources/windows/tox/chocolatey/verifyenv.ps1 c:/verifyenv.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    $chocolateyDownloadUrl = c:/choco/get_latest_chocolatey_url.ps1 -packageRepo $env:CHOCOLATEY_SOURCE; `
    c:/choco/install.ps1 -ChocolateyDownloadUrl $chocolateyDownloadUrl;`
    . $profile;`
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"${env:CHOCOLATEY_SOURCE}\"; `
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    choco sources ; `
    choco install -y --stoponfirstfailure --no-progress c:/choco/packages.config ;`
    refreshenv ; `
    choco cache remove --confirm;`
    Write-Host "Finished install packages with Chocolatey" ;`
    Write-Host "Verifying installed packages" ;`
    c:/verifyenv.ps1 ;`
    Write-Host "Verifying installed packages - Done"


# ==============================================================================
FROM BASE_BUILDER AS CONAN_BUILDER
ARG CONAN_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV UV_FROZEN=1

COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/shared/conan/remotes.json  ${CONAN_HOME}/remotes.json
COPY scripts/resources/windows/tox/conan/profile.ini  ${CONAN_HOME}/profiles/default
COPY scripts/resources/windows/tox/conan/python.ini  ${CONAN_HOME}/profiles/python
ENV UV_PROJECT=c:/temp/
COPY pyproject.toml uv.lock ${UV_PROJECT}/
#SHELL ["cmd", "/S", "/C" ]
ENV CONAN_CMAKE_GENERATOR=Ninja
ARG CONAN_CENTER_PROXY_V2_URL
RUN uv run --only-group conan conan profile detect --exist-ok ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
          Copy-Item -Path "${Env:CONAN_HOME}\remotes.json" -Destination "c:\remotes.json" ; `
          uv run --only-group conan conan remote update conan-center --url ${env:CONAN_CENTER_PROXY_V2_URL}; `
    }; `
    uv run --only-group conan conan install c:/temp/ -pr:h=default -pr:b=python; `
    if ($LASTEXITCODE -ne 0) { `
      throw \"Command 'conan install' failed with exit code: $LASTEXITCODE\"`
    } ;`
    uv run --only-group conan conan cache clean "*" -b --source --build --temp ; `
    uv cache clean --no-progress ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_HOME}\remotes.json" -Force ;`
    }

FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst c:/roots.sst
RUN certutil -addstore -f root c:/roots.sst ; `
    del c:/roots.sst

ARG PIP_DOWNLOAD_CACHE
ARG UV_CACHE_DIR
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force | Out-Null ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force | Out-Null
ARG CONAN_HOME
COPY --from=CONAN_BUILDER ${CONAN_HOME}/ ${CONAN_HOME}/
ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}`
    CONAN_HOME=${CONAN_HOME}`
    PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}`
    UV_CACHE_DIR=${UV_CACHE_DIR}

WORKDIR C:/src
ENV DISTUTILS_USE_SDK=1

# To help mark the image as a CI image so it can be cleaned up more easily
LABEL purpose=ci
