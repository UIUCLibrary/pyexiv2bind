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

ARG SAMPLE_IMAGES_URL=https://nexus.library.illinois.edu/repository/sample-data/images/sample_images.tar.gz

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS base_builder


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

COPY scripts/resources/windows/tox/scoop c:/scoopinstall
RUN irm get.scoop.sh -outfile 'install.ps1' ; `
    .\install.ps1 -RunAsAdmin ; `
    Remove-Item -Path ".\install.ps1" ; `
    scoop install git ; `
    scoop bucket add versions ; `
    scoop import c:/scoopinstall/scoopfile.json ; `
    scoop cache show ; `
    Write-Host "Cleaning up cache" ;`
    scoop cache clean ; `
    Write-Host "Cleaning up cache - Done" ;`
    Write-Host "Verifying installed packages" ;`
    c:/scoopinstall/verifyenv.ps1 ;`
    Write-Host "Verifying installed packages - Done"
# ==============================================================================
FROM base_builder AS sample_files_downloader
ARG SAMPLE_IMAGES_URL
ENV EXPECTED_SHA256="0461f57db3806ca47d9063151eec4bc0720c66a83153dda04e230f838b64f063"
ENV downloadPath="C:/sampledata/"
RUN if (-not (Test-Path -Path ${env:downloadPath} -PathType Container)) {`
        New-Item -Path ${env:downloadPath} -ItemType Directory -Force`
    }; `
    Invoke-WebRequest -Uri ${env:SAMPLE_IMAGES_URL} -OutFile "${env:downloadPath}\sample_images.tar.gz"

# ==============================================================================
FROM base_builder AS conan_builder
ARG CONAN_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV UV_FROZEN=1

COPY conanfile.py conan.lock c:/temp/
COPY ci/docker/shared/conan/remotes.json  ${CONAN_HOME}/remotes.json
COPY scripts/resources/windows/tox/conan/profile.ini  ${CONAN_HOME}/profiles/default
COPY scripts/resources/windows/tox/conan/python.ini  ${CONAN_HOME}/profiles/python
ENV UV_PROJECT=c:/temp/
COPY pyproject.toml uv.lock ${UV_PROJECT}/
#SHELL ["cmd", "/S", "/C" ]
ENV CONAN_CMAKE_GENERATOR=Ninja
ARG CONAN_CENTER_PROXY_V2_URL
RUN uv run --only-group=conan conan profile detect --exist-ok ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
          Copy-Item -Path "${Env:CONAN_HOME}\remotes.json" -Destination "c:\remotes.json" ; `
          uv run --only-group=conan conan remote update conan-center --url ${env:CONAN_CENTER_PROXY_V2_URL}; `
    }; `
    uv run --only-group=conan conan install c:/temp/ -pr:h=default -pr:b=python -of c:/temp/delme -c tools.graph:skip_test=True; `
    if ($LASTEXITCODE -ne 0) { `
      throw \"Command 'conan install' failed with exit code: $LASTEXITCODE\"`
    } ;`
    Remove-Item -Path "c:\temp\delme" -Recurse -Force ; `
    uv run --only-group=conan conan cache clean "*" -b --source --build --temp -vdebug; `
    Remove-Item -Path "${env:UV_PROJECT}\.venv" -Recurse -Force ; `
    uv cache clean --no-progress ; `
    if (Test-Path -Path "c:\remotes.json" ) { `
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_HOME}\remotes.json" -Force ;`
    }

FROM base_builder
COPY --from=certsgen c:/roots.sst c:/roots.sst
RUN certutil -addstore -f root c:/roots.sst ; `
    del c:/roots.sst

ARG PIP_DOWNLOAD_CACHE
ARG UV_CACHE_DIR
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force | Out-Null ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force | Out-Null
ARG CONAN_HOME
COPY --from=conan_builder ${CONAN_HOME}/ ${CONAN_HOME}/
COPY --from=sample_files_downloader c:/sampledata/ C:/sampledata/

ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}`
    CONAN_HOME=${CONAN_HOME}`
    PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}`
    UV_CACHE_DIR=${UV_CACHE_DIR}`
    SAMPLE_IMAGES_ARCHIVE=C:/sampledata/sample_images.tar.gz

WORKDIR C:/src
ENV DISTUTILS_USE_SDK=1

COPY ["scripts/resources/windows/tox/powershell_modules", "c:/Program Files/WindowsPowerShell/Modules/"]
# To help mark the image as a CI image so it can be cleaned up more easily
LABEL purpose=ci
