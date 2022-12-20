# escape=`
ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator
ARG VS_INSTALL_PATH="C:\BuildTools\"
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019
FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} as BASE_BUILDER

COPY ci/docker/shared/startup.bat c:/startup/startup.bat
ARG VS_INSTALL_PATH
RUN Invoke-WebRequest https://aka.ms/vs/17/release/vs_buildtools.exe -OutFile vs_buildtools.exe ; `
    Write-Host \"Installing Visual Studio Build Tools to ${Env:VS_INSTALL_PATH}\" ; `
    $ARGS_LIST = @(`
        '--quiet', `
        '--wait', `
        '--norestart', `
        '--nocache', `
        '--installPath', `
         ${Env:VS_INSTALL_PATH},`
        '--add Microsoft.VisualStudio.Workload.VCTools', `
        '--add Microsoft.VisualStudio.Component.VC.CLI.Support', `
        '--add Microsoft.VisualStudio.Component.VC.CoreBuildTools', `
        '--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64', `
        '--add Microsoft.VisualStudio.ComponentGroup.VC.Tools.142.x86.x64', `
        '--add Microsoft.VisualStudio.Component.Windows10SDK.18362', `
        '--remove Microsoft.VisualStudio.Component.Windows10SDK.10240',`
        '--remove Microsoft.VisualStudio.Component.Windows10SDK.10586', `
        '--remove Microsoft.VisualStudio.Component.Windows10SDK.14393', `
        '--remove Microsoft.VisualStudio.Component.Windows81SDK'`
        ) ;`
    $process = Start-Process -NoNewWindow -PassThru -FilePath vs_buildtools.exe  `
    -ArgumentList $ARGS_LIST -Wait  ; `
    if ( $process.ExitCode -eq 0) `
    { `
        Write-Host 'Installing Visual Studio Build Tools - Done' ; `
    } `
    else `
    { `
        Get-ChildItem c:\\ ; `
        Get-ChildItem ${Env:ProgramFiles(x86)} ; `
        Get-ChildItem ${Env:VS_INSTALL_PATH} ; `
        Get-ChildItem ${Env:VS_INSTALL_PATH}\\Common7\\Tools ; `
        $message = \"Installing Visual Studio Build Tools exited with code $($process.ExitCode) \"; `
        Write-Host $message ;  `
        throw 'unable to continue' ; `
    } ; `
    Write-Host 'Testing for VsDevCmd.bat' ; `
    if (! (Test-Path "${Env:VS_INSTALL_PATH}\Common7\Tools\VsDevCmd.bat")) `
    { `
        Write-Host 'Testing for VsDevCmd.bat - Failed' ; `
        Start-Process -NoNewWindow -FilePath $Env:TEMP\\collect.exe -ArgumentList '-nologo -zip:${Env:TEMP}\\vslogs.zip' -Wait; `
        if (! (Test-Path '${Env:TEMP}\\vslogs.zip')) `
        { `
            throw 'VsDevCmd.bat not found and ${Env:TEMP}\\vslogs.zip never generated' ; `
        } ; `
        Expand-Archive -Path vslogs.zip -DestinationPath $Env:TEMP\\logs\\ ; `
        Get-Content -LiteralPath '$Env:TEMP\\logs\\[Content_Types].xml' ; `
        throw 'VsDevCmd.bat not found' ; `
    } ; `
    Write-Host "Testing for VsDevCmd.bat - Found" ; `
    Write-Host "Setting up compiler environment to run every time a command is run from CMD" ; `
    Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\startup\startup.bat" ; `
    Write-Host "Testing for CL" ; `
    cmd /S /C where cl ; `
    Write-Host "Testing for CL - Success"; `
    Write-Host "Removing build tools installer" ; `
    Remove-Item vs_buildtools.exe ; `
    Write-Host "Removing build tools installer - Done" ; `
    Write-Host "Finished installing Visual Studio Build Tools"

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
    Remove-Item -Force -Recurse ${Env:TEMP}\*



ADD ci/docker/shared/chocolatey/packages.config choco/packages.config
ADD ci/docker/shared/chocolatey/verifyenv.ps1 verifyenv.ps1
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/packages.config ;`
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
    ./verifyenv.ps1

ARG PYTHON_37_VERSION=3.7.9
ARG PYTHON_38_VERSION=3.8.10
ARG PYTHON_39_VERSION=3.9.13
ARG PYTHON_310_VERSION=3.10.8
ARG PYTHON_311_VERSION=3.11.0

RUN $PYTHON_VERSIONS = @(${Env:PYTHON_37_VERSION}, ${Env:PYTHON_38_VERSION}, ${Env:PYTHON_39_VERSION}, ${Env:PYTHON_310_VERSION}, ${Env:PYTHON_311_VERSION}) ; `
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
    py -3.7 --version ; `
    py -3.8 --version ; `
    py -3.9 --version ; `
    py -3.10 --version ; `
    py -3.11 --version ; `
    Write-Host "Installing Python with Chocolatey - Done"


# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY37
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.7
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel build && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt `
    -r c:/requirements/requirements-extra.txt `
    -r c:/requirements/requirements.txt `
    -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY38
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL-
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.8
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel build && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt `
    -r c:/requirements/requirements-extra.txt `
    -r c:/requirements/requirements.txt `
    -r c:/requirements/requirements-dev.txt
# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY39
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.9
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel build && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt `
    -r c:/requirements/requirements-extra.txt `
    -r c:/requirements/requirements.txt `
    -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY310
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.10
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel build && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt `
    -r c:/requirements/requirements-extra.txt `
    -r c:/requirements/requirements.txt `
    -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY311
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt requirements-dev.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.11
RUN py -m pip install --upgrade pip && `
    py -m pip install wheel build && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt `
    -r c:/requirements/requirements-extra.txt `
    -r c:/requirements/requirements.txt `
    -r c:/requirements/requirements-dev.txt

# ==============================================================================
FROM BASE_BUILDER as CONAN_BUILDER
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN python -m pip install --upgrade pip ; `
    pip install wheel ; `
    pip install conan cmake

COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY ci/docker/windows/tox/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
SHELL ["cmd", "/S", "/C" ]
RUN conan config home

RUN conan config init && ; `
    conan config set general.revisions_enabled=1

ENV CONAN_CMAKE_GENERATOR=Ninja
RUN conan install c:/temp/ --build --no-import  && `
    conan remove "*" -b --src -f && `
    conan remove --lock

FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ENV PIP_FIND_LINKS=c:\wheels
COPY requirements requirements
COPY --from=WHEEL_BUilDER_PY37 c:/wheels/ c:/wheels/
RUN py -3.7 -m pip install pip --upgrade ; py -3.7 -m pip install wheel --upgrade ; py -3.7 -m pip install -r requirements/requirements_tox.txt conan wheel build
COPY --from=WHEEL_BUilDER_PY38 c:/wheels/ c:/wheels/
RUN py -3.8 -m pip install pip --upgrade ; py -3.8 -m pip install wheel --upgrade ; py -3.8 -m pip install -r requirements/requirements_tox.txt conan wheel build
COPY --from=WHEEL_BUilDER_PY39 c:/wheels/ c:/wheels/
RUN py -3.9 -m pip install pip --upgrade ; py -3.9 -m pip install wheel --upgrade ; py -3.9 -m pip install -r requirements/requirements_tox.txt conan wheel build
COPY --from=WHEEL_BUilDER_PY310 c:/wheels/ c:/wheels/
RUN py -3.10 -m pip install pip --upgrade ; py -3.10 -m pip install wheel --upgrade ; py -3.10 -m pip install -r requirements/requirements_tox.txt conan wheel build
COPY --from=WHEEL_BUilDER_PY311 c:/wheels/ c:/wheels/
RUN py -3.11 -m pip install pip --upgrade ; py -3.11 -m pip install wheel --upgrade ; py -3.11 -m pip install -r requirements/requirements_tox.txt conan wheel build


RUN python -m pip install pip --upgrade ; pip install -r requirements/requirements_tox.txt conan wheel build
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst
ARG CONAN_USER_HOME
COPY --from=CONAN_BUILDER ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY conanfile.py c:/temp/conanfile.py
RUN conan config home

RUN conan config init ; `
    conan config set general.revisions_enabled=1

RUN conan install c:/temp/ --build outdated --no-import  ; `
    conan remove "*" -b --src -f ; `
    conan remove --locks

RUN python -m pip install pip --upgrade ; pip install pip install -r requirements/requirements_tox.txt devpi_client
WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate -p=auto
