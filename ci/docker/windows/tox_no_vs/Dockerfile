# escape=`

ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} as BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

FROM BASE_BUILDER as CHOCOLATEY_BASE
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
    choco feature disable --name="showDownloadProgress" ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*

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

ARG PYTHON_36_VERSION=3.6.8
ARG PYTHON_37_VERSION=3.7.9
ARG PYTHON_38_VERSION=3.8.10
ARG PYTHON_39_VERSION=3.9.7
ARG PYTHON_310_VERSION=3.10.0

RUN $PYTHON_VERSIONS = @(${Env:PYTHON_36_VERSION}, ${Env:PYTHON_37_VERSION}, ${Env:PYTHON_38_VERSION}, ${Env:PYTHON_39_VERSION} , ${Env:PYTHON_310_VERSION}) ; `
    foreach( $PYTHON_VERSION in $PYTHON_VERSIONS ){ `
        Write-Host "Installing Python $PYTHON_VERSION with Chocolatey" ; `
        $process = start-process -NoNewWindow -PassThru -FilePath C:\ProgramData\chocolatey\bin\choco.exe -ArgumentList 'install -y --stoponfirstfailure --no-progress --verbose python3', "--version=$PYTHON_VERSION", "-my" -Wait ;`
        if ( $process.ExitCode -eq 0) `
        { `
            Write-Host "Installing Python $PYTHON_VERSION with Chocolatey - Done" ; `
        } else { `
            throw "Installing packages with Chocolatey - Failed with exit code ($process.ExitCode)" ;  `
        };`
    } ; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    py --list ;`
    py -3.6 --version ; `
    py -3.7 --version ; `
    py -3.8 --version ; `
    py -3.9 --version ; `
    py -3.10 --version ; `
    Write-Host "Installing Python with Chocolatey - Done"
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
# ==============================================================================
FROM CHOCOLATEY_BASE as WHEEL_BUILDER_PY36
SHELL ["cmd", "/S", "/C" ]
COPY ci/docker/shared/python/requirements-ci.txt requirements-dev.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.6
ENV PIP_NO_CACHE_DIR=off
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM CHOCOLATEY_BASE as WHEEL_BUILDER_PY37
SHELL ["cmd", "/S", "/C" ]
COPY ci/docker/shared/python/requirements-ci.txt requirements-dev.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.7
ENV PIP_NO_CACHE_DIR=off
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM CHOCOLATEY_BASE as WHEEL_BUILDER_PY38
SHELL ["cmd", "/S", "/C" ]
COPY ci/docker/shared/python/requirements-ci.txt requirements-dev.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.8
ENV PIP_NO_CACHE_DIR=off
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM CHOCOLATEY_BASE as WHEEL_BUILDER_PY39
SHELL ["cmd", "/S", "/C" ]
COPY ci/docker/shared/python/requirements-ci.txt requirements-dev.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.9
ENV PIP_NO_CACHE_DIR=off
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM CHOCOLATEY_BASE as WHEEL_BUILDER_PY310
SHELL ["cmd", "/S", "/C" ]
COPY ci/docker/shared/python/requirements-ci.txt requirements-dev.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.10
ENV PIP_NO_CACHE_DIR=off
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM CHOCOLATEY_BASE
COPY --from=WHEEL_BUILDER_PY36 C:/wheels/ c:/wheels/
COPY --from=WHEEL_BUILDER_PY37 C:/wheels/ c:/wheels/
COPY --from=WHEEL_BUILDER_PY38 C:/wheels/ c:/wheels/
COPY --from=WHEEL_BUILDER_PY39 C:/wheels/ c:/wheels/
COPY --from=WHEEL_BUILDER_PY310 C:/wheels/ c:/wheels/
RUN python -m pip install pip --upgrade ; pip install tox devpi_client
ENV PIP_FIND_LINKS=c:\wheels
WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate
