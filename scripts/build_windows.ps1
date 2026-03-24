param (
    [string]$DockerImageName = "pyexiv2builder",
    [string]$PythonVersion = "3.11",
    [string]$outputDirectory = $(Join-Path -Path $($(Get-Item $PSScriptRoot).Parent.FullName) -ChildPath "dist")
)

function Build-DockerImage {
    [CmdletBinding()]
    param (
        [string]$DockerfilePath = "scripts/resources/windows/tox/Dockerfile",
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
        "--build-arg CONAN_CENTER_PROXY_V2_URL",
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
        [string]$ContainerName = "pyexiv2builder",
        [string]$OutputDirectory = $(Join-Path -Path $($(Get-Item $PSScriptRoot).Parent.FullName) -ChildPath "dist")
    )
    $containerDistPath = "c:\dist"
    $projectRootDirectory = (Get-Item $PSScriptRoot).Parent.FullName
    if (!(Test-Path -Path $OutputDirectory)) {
      New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
    }
    $containerSourcePath = "c:\src"
    $containerCacheDir = "C:\Users\ContainerUser\Documents\cache"

    $UV_TOOL_DIR = "${containerCacheDir}\uvtools"
    $UV_PYTHON_CACHE_DIR = "${containerCacheDir}\uvpython"

    $dockerArgsList = @(
        "run",
        "--isolation", $DockerIsolation,
        "--platform windows/amd64",
        "--rm",
        "--mount type=volume,source=${ContainerName}Cache,target=${containerCacheDir}",
        "--mount type=bind,source=$(Resolve-Path $projectRootDirectory),target=${containerSourcePath}",
        "--mount type=bind,source=$(Resolve-Path $OutputDirectory),target=${containerDistPath}",
        "-e UV_TOOL_DIR=${UV_TOOL_DIR}",
        "-e UV_PYTHON_CACHE_DIR=${UV_PYTHON_CACHE_DIR}",
        '--entrypoint', 'powershell',
        $DockerImageName
        "New-Wheels -SourcePath ${containerSourcePath} -OutputDir ${containerDistPath} -PythonVersion ${PythonVersion}"
    )
    $local:dockerBuildProcess = Start-Process -FilePath $DockerExec -WorkingDirectory $(Get-Item $PSScriptRoot).Parent.FullName -ArgumentList $dockerArgsList -NoNewWindow -PassThru -Wait
    if ($local:dockerBuildProcess.ExitCode -ne 0)
    {
        throw "An error creating docker image occurred. Exit code: $($local:dockerBuildProcess.ExitCode)"
    }
}

Build-DockerImage -ImageName $DockerImageName

Build-Wheel -PythonVersion $PythonVersion -DockerImageName $DockerImageName -OutputDirectory $outputDirectory
Write-Host "Check $outputDirectory folder for the output."