# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8.1

ARG VS_INSTALL_PATH="C:\BuildTools"

ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V1_URL

ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG chocolateyVersion

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER


SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY ci/docker/windows/tox/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY ci/docker/windows/tox/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH
ARG VS_VERSION="2022"
ARG VS_DevCmdArguments="-arch=amd64"
ARG VS_DevPowershellArguments='-arch=amd64'
RUN c:/scripts/install_msvc.ps1 -InstallPath ${Env:VS_INSTALL_PATH} -VSConfigFile c:/setup/config.vsconfig -DevCmdArguments ${Env:VS_DevCmdArguments} -DevPowershellArguments ${Env:VS_DevPowershellArguments} -VSVersion ${Env:VS_VERSION}; `
    Write-Host "Note: Exporting This layer can take a while."

ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY ci/docker/windows/tox/chocolatey/install.ps1 c:/choco/install.ps1
COPY ci/docker/windows/tox/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
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
    choco cache remove --confirm

COPY ci/docker/windows/tox/chocolatey/packages.config c:/choco/packages.config
COPY ci/docker/windows/tox/chocolatey/verifyenv.ps1 c:/verifyenv.ps1
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress c:/choco/packages.config ;`
    refreshenv ; `
    choco cache remove --confirm;`
    Write-Host "Finished install packages with Chocolatey" ;`
    Write-Host "Verifying installed packages" ;`
    $env:Path = [System.Environment]::GetEnvironmentVariable(\"Path\",\"Machine\") + \";\" + [System.Environment]::GetEnvironmentVariable(\"Path\",\"User\") ; `
    c:/verifyenv.ps1


# ==============================================================================
FROM BASE_BUILDER AS CONAN_BUILDER
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY requirements-dev.txt c:/requirements/requirements-dev.txt
COPY ci/docker/windows/tox/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
#SHELL ["cmd", "/S", "/C" ]
ENV CONAN_CMAKE_GENERATOR=Ninja
ARG CONAN_CENTER_PROXY_V1_URL
RUN uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan config home ; `
    uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan config init ; `
    uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan config set general.revisions_enabled=1 ; `
    if ( -not ([string]::IsNullOrEmpty($Env:CONAN_CENTER_PROXY_V1_URL ))) `
    { `
      Copy-Item -Path "${Env:CONAN_USER_HOME}\.conan\remotes.json" -Destination "c:\remotes.json" ; `
      uvx --constraint=requirements-dev.txt conan remote remove conan-center ; `
      uvx --constraint=requirements-dev.txt conan remote add conan-center-proxy ${Env:CONAN_CENTER_PROXY_V1_URL} ; `
    }; `
    uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan install c:/temp/ --build --no-import -pr:b=default ; `
    uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan remove "*" -b --src -f ; `
    uvx --constraint c:/requirements/requirements-dev.txt --with cmake conan remove --lock ; `
    uv cache clean --no-progress ;`
    if ( -not ([string]::IsNullOrEmpty($Env:CONAN_CENTER_PROXY_V1_URL ))) `
    {`
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_USER_HOME}\.conan\remotes.json" -Force ;`
    }

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
ENV DISTUTILS_USE_SDK=1
CMD ["tox", "--workdir", "${Env:TEMP}\tox\\", "-vv",  "--recreate", "-p=auto"]
