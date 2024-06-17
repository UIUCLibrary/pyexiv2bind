param (
    [Parameter(Mandatory=$true)][String]$InstallPath,
    [Parameter(Mandatory=$true)][String]$VSConfigFile,
    [String]$VsbuildtoolsURL='https://aka.ms/vs/17/release/vs_buildtools.exe'

)

function TestInstalledProperty ($VS_INSTALL_PATH) {
    Write-Host 'Testing for VsDevCmd.bat'
    if (! (Test-Path "${VS_INSTALL_PATH}\Common7\Tools\VsDevCmd.bat"))
    {
        Write-Host 'Testing for VsDevCmd.bat - Failed'
        Start-Process -NoNewWindow -FilePath ${Env:TEMP}\collect.exe -ArgumentList "-nologo -zip:${Env:TEMP}\vslogs.zip" -Wait
        if (! (Test-Path "${Env:TEMP}\vslogs.zip"))
        {
            throw "VsDevCmd.bat not found and ${Env:TEMP}\vslogs.zip never generated"
        }
        Expand-Archive -Path vslogs.zip -DestinationPath ${Env:TEMP}\logs\
        Get-Content -LiteralPath "${Env:TEMP}\logs\[Content_Types].xml"
        throw 'VsDevCmd.bat not found'
    }

    Write-Host "Testing for VsDevCmd.bat - Found"
    Write-Host "Setting up compiler environment to run every time a command is run from CMD"
    Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\startup\startup.bat"
    Write-Host "Testing for CL"
    cmd /S /C where cl
    Write-Host "Testing for CL - Success"
    Write-Host "Finished installing Visual Studio Build Tools"
}
function InstallMSVC ($VS_INSTALL_PATH, $ConfigFile) {
    Invoke-WebRequest $VsbuildtoolsURL -OutFile vs_buildtools.exe
    Write-Host "Installing Visual Studio Build Tools to ${VS_INSTALL_PATH}"
    $ARGS_LIST = @(`
        '--quiet', `
        '--wait', `
        '--norestart', `
        '--nocache', `
        '--installPath', ${VS_INSTALL_PATH},`
         '--config', ${ConfigFile}

    )
    $process = Start-Process -NoNewWindow -PassThru -FilePath vs_buildtools.exe  -ArgumentList $ARGS_LIST -Wait
    if ( $process.ExitCode -eq 0) {
        Write-Host 'Installing Visual Studio Build Tools - Done'
    } else {
        Get-ChildItem c:\
        Get-ChildItem ${Env:ProgramFiles(x86)}
        Get-ChildItem ${VS_INSTALL_PATH}
        Get-ChildItem ${VS_INSTALL_PATH}\Common7\Tools
        $message = "Installing Visual Studio Build Tools exited with code $($process.ExitCode)"
        Write-Host $message
        throw 'unable to continue'
    }

    $resultingConfigFile="c:\setup\myconfig.vsconfig"
    $exportArgs = @(`
        'export',
        '--quiet',
        '--nocache',
        '--force',
        '--config', ${resultingConfigFile},
        '--installPath', ${VS_INSTALL_PATH}
    )
    $exportProcess = Start-Process -NoNewWindow -PassThru -FilePath 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\setup.exe'  -ArgumentList $exportArgs   -Wait
    if ( $exportProcess.ExitCode -eq 0) {
        Get-Content $resultingConfigFile
    } else
    {
        Write-Host "Exporting config with Visual Studio Build Tools exited with code $( $exportProcess.ExitCode )"
        throw "Failed Exporting config file"
    }
    Remove-Item $resultingConfigFile

    Write-Host "Removing build tools installer"
    Remove-Item vs_buildtools.exe
    Write-Host "Removing build tools installer - Done"
}
InstallMSVC $InstallPath $VSConfigFile

TestInstalledProperty $InstallPath
