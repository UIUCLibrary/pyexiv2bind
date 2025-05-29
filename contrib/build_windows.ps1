param (
    [string]$DockerImageName = "pyexiv2builder",
    [string]$PythonVersion = "3.11"
)

function Build-DockerImage {
    [CmdletBinding()]
    param (
        [string]$DockerfilePath = "ci/docker/windows/tox/Dockerfile",
        [string]$ImageName = "pyexiv2builder",
        [string]$DockerExec = "docker.exe",
        [string]$DockerIsolation = "process"
    )

    $projectRootDirectory = (Get-Item $PSScriptRoot).Parent.FullName
    $dockerArgsList = @(
        "build",
        "--isolation", $DockerIsolation,
        "--platform windows/amd64",
        "-f", $DockerfilePath,
        "--build-arg PIP_EXTRA_INDEX_URL",
        "--build-arg PIP_INDEX_URL",
        "--build-arg CHOCOLATEY_SOURCE",
        "--build-arg UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv",
        "-t", $ImageName,
        "."
    )

    $local:dockerBuildProcess = Start-Process -FilePath $DockerExec -WorkingDirectory $projectRootDirectory -ArgumentList $dockerArgsList -NoNewWindow -PassThru -Wait
    if ($local:dockerBuildProcess.ExitCode -ne 0)
    {
        throw "An error creating docker image occurred. Exit code: $($local:dockerBuildProcess.ExitCode)"
    }
}

function Build-Wheel {
    [CmdletBinding()]
    param (
        [string]$DockerImageName = "pyexiv2builder",
        [string]$DockerExec = "docker.exe",
        [string]$DockerIsolation = "process",
        [string]$PythonVersion = "3.11",
        [string]$ContainerName = "pyexiv2builder"
    )
    $containerDistPath = "c:\dist"
    $projectRootDirectory = (Get-Item $PSScriptRoot).Parent.FullName
    $outputDirectory = Join-Path -Path $projectRootDirectory -ChildPath "dist"
    if (!(Test-Path -Path $outputDirectory)) {
      New-Item -ItemType Directory -Path $outputDirectory
    }
    $containerSourcePath = "c:\src"
    $containerWorkingPath = "c:\build"
    $containerCacheDir = "C:\Users\ContainerUser\Documents\cache"
    $venv = "${containerCacheDir}\venv"

    $UV_TOOL_DIR = "${containerCacheDir}\uvtools"
    $UV_PYTHON_INSTALL_DIR = "${containerCacheDir}\uvpython"

    # This makes a symlink copy of the files mounted in the source. Any changes to the files will not affect outside the container
    $createShallowCopy = "foreach (`$item in `$(Get-ChildItem -Path $containerSourcePath)) { `
        Write-Host `"Creating symlink for `$item.Name`"; `
        `$LinkPath = Join-Path -Path $containerWorkingPath -ChildPath `$item.Name ; `
        New-Item -ItemType SymbolicLink -Path `$LinkPath -Target `$item.FullName | Out-Null `
    }"

    $dockerArgsList = @(
        "run",
        "--isolation", $DockerIsolation,
        "--platform windows/amd64",
        "--rm",
        "--workdir=${containerWorkingPath}",
        "--mount type=volume,source=${ContainerName}Cache,target=${containerCacheDir}",
        "--mount type=bind,source=$(Resolve-Path $projectRootDirectory),target=${containerSourcePath}",
        "--mount type=bind,source=$(Resolve-Path $outputDirectory),target=${containerDistPath}",
        "-e UV_TOOL_DIR=${UV_TOOL_DIR}",
        "-e UV_PYTHON_INSTALL_DIR=${UV_PYTHON_INSTALL_DIR}",
        '--entrypoint', 'powershell',
        $DockerImageName
        "-c",
        ${createShallowCopy};`
        "uv build --build-constraints=${containerSourcePath}\requirements-dev.txt --python=${PythonVersion} --wheel --out-dir=${containerDistPath} --config-setting=conan_cache=C:/Users/ContainerAdministrator/.conan --verbose"
    )

    $local:dockerBuildProcess = Start-Process -FilePath $DockerExec -WorkingDirectory $(Get-Item $PSScriptRoot).Parent.FullName -ArgumentList $dockerArgsList -NoNewWindow -PassThru -Wait
    if ($local:dockerBuildProcess.ExitCode -ne 0)
    {
        throw "An error creating docker image occurred. Exit code: $($local:dockerBuildProcess.ExitCode)"
    }
}



Build-DockerImage -ImageName $DockerImageName

Build-Wheel -PythonVersion $PythonVersion -DockerImageName $DockerImageName
