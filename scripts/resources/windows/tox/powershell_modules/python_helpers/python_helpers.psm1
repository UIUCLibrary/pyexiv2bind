$CONTAINER_WORKING_PATH = "c:\build"
$CONAN_CACHE_DIR = "C:\Users\ContainerAdministrator\.conan2"

function ShadowCopy{
    param(
        [Parameter(Mandatory=$true)]
        [string]$ContainerSourcePath,
        [Parameter(Mandatory=$true)]
        [string]$ContainerWorkingPath
    )
    if (!(Test-Path -Path $ContainerWorkingPath)) {
        New-Item -ItemType Directory -Path $ContainerWorkingPath | Out-Null
    }
    foreach ($item in $(Get-ChildItem -Path $ContainerSourcePath)) {
        Write-Host "Creating symlink for $($item.Name)"
        $LinkPath = Join-Path -Path $ContainerWorkingPath -ChildPath $item.Name
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $item.FullName | Out-Null
    }
}

function CreateNewWheel {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourcePath,
        [Parameter(Mandatory = $true)]
        [string]$PythonVersion,
        [Parameter(Mandatory = $true)]
        [string]$OutputDir

    )
    uv build --python=$PythonVersion --wheel --out-dir=$OutputDir --config-setting=conan_cache=$CONAN_CACHE_DIR --verbose $SourcePath
    if ($LASTEXITCODE -ne 0) {
        throw "An error creating Wheel for Python version $PythonVersion."
    }
    Write-Host "Wheel for Python $PythonVersion created successfully."

}

function New-Wheels {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$SourcePath,
        [Parameter(Mandatory=$true)]
        [string[]]$PythonVersion,
        [Parameter(Mandatory=$true)]
        [string]$OutputDir

    )
    ShadowCopy -ContainerSourcePath $SourcePath -ContainerWorkingPath $CONTAINER_WORKING_PATH
    foreach ($PythonVer in $PythonVersion) {
        Write-Host "Creating wheel for Python $PythonVer"
        CreateNewWheel -SourcePath $CONTAINER_WORKING_PATH -PythonVersion $PythonVer -OutputDir $OutputDir
    }
}

Export-ModuleMember -Function New-Wheels
