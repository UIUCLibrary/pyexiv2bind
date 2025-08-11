param (
    [Parameter(Mandatory=$true)][String]$InstallPath,
    [Parameter(Mandatory=$true)][String]$VSConfigFile,
    [String]$DevCmdArguments='-arch=amd64',
    [String]$DevPowershellArguments='-arch=amd64',
    [ValidateSet("2022", "2019")][string]$VSVersion
)
$VSBUILDTOOLS_URLS = @{
    '2022' = 'https://aka.ms/vs/17/release/vs_buildtools.exe'
    '2019' = 'https://aka.ms/vs/16/release/vs_buildtools.exe'
}

function CreateHelloWorldSource {
    param(
        [Parameter(Mandatory=$true)][string]$Location
    )

    $local:content = @"
    #include <iostream>
    using namespace std;
    int main(){
        cout << "Hello world\n";
        return 0;
    }
"@
    Set-Content -Path $Location -Value $local:content
}

function TestCompileWithCmd {
    param(
        [Parameter(Mandatory=$true)][string]$SampleFile
    )
    $local:command_description = 'Testing compile hello world in cmd'

    $local:tempDir = Join-Path $([System.IO.Path]::GetTempPath()) $((New-Guid).ToString("N"))
    New-Item -ItemType Directory -Path $local:tempDir | Out-Null

    $local:buildDir = Join-Path $local:tempDir "build"
    New-Item -ItemType Directory -Path $local:buildDir | Out-Null

    $local:binDir = Join-Path $local:tempDir "bin"
    New-Item -ItemType Directory -Path $local:binDir | Out-Null

    Write-Host "Testing compile hello world in cmd"

    $local:compileArgs = @(
        '/S', '/C',
        'cl',
        '/EHsc',
        "/Fo${local:buildDir}",
        "/Fe${local:binDir}\helloworld_cmd",
        $SampleFile
    )
    $local:testClProcess = Start-Process -FilePath cmd -ArgumentList $local:compileArgs -NoNewWindow -PassThru
    Wait-Process -InputObject $local:testClProcess
    if ($local:testClProcess.ExitCode -ne 0)
    {
        throw "${$local:command_description} - Failed"
    }
    Write-Host "${$local:command_description} - Success"

    Write-Host "Test running hello world"
    $local:testRun = Start-Process -FilePath "${local:binDir}\helloworld_cmd.exe" -NoNewWindow -PassThru -RedirectStandardOutput "NUL" -Wait
    if ($local:testRun.ExitCode -ne 0)
    {
        throw "Test running hello world - Failed"
    }
    Write-Host "Test running hello world - Success"
    Remove-Item -Path $local:tempDir -Recurse
}

function TestCompileWithPowershell {
    param(
        [Parameter(Mandatory=$true)][string]$SampleFile
    )
    $local:command_description = 'Testing compile hello world in powershell'

    $local:tempDir = Join-Path $([System.IO.Path]::GetTempPath()) $((New-Guid).ToString("N"))
    New-Item -ItemType Directory -Path $local:tempDir | Out-Null

    $local:buildDir = Join-Path $local:tempDir "build"
    New-Item -ItemType Directory -Path $local:buildDir | Out-Null

    $local:binDir = Join-Path $local:tempDir "bin"
    New-Item -ItemType Directory -Path $local:binDir | Out-Null

    Write-Host "Testing compile hello world in cmd"

    $local:compileArgs = @(
        '-Command',
        'cl',
        '/EHsc',
        "/Fo${local:buildDir}",
        "/Fe${local:binDir}\helloworld_ps",
        $SampleFile
    )
    $local:testClProcess = Start-Process -FilePath powershell -ArgumentList $local:compileArgs -NoNewWindow -PassThru
    Wait-Process -InputObject $local:testClProcess
    if ($local:testClProcess.ExitCode -ne 0)
    {
        throw "${local:command_description} - Failed"
    }
    Write-Host "${local:command_description} - Success"

    Write-Host "Test running hello world"
    $local:testRun = Start-Process -FilePath "${local:binDir}\helloworld_ps.exe" -NoNewWindow -PassThru -RedirectStandardOutput "NUL" -Wait
    if ($local:testRun.ExitCode -ne 0)
    {
        throw "Test running hello world - Failed"
    }
    Write-Host "Test running hello world - Success"
    Remove-Item -Path $local:tempDir -Recurse
}


function TestInstalledProperty {
    param ([Parameter(Mandatory=$true)][String]$InstallPath)

    Write-Host 'Testing for VsDevCmd.bat'
    if (! (Test-Path "${InstallPath}\Common7\Tools\VsDevCmd.bat"))
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

    Write-Host "Finished installing Visual Studio Build Tools"


}

function RemoveApplications {
    param (
        [string[]]$AppList
    )
    $local:query = "SELECT * FROM Win32_Product WHERE " + ($($AppList | ForEach-Object { "Name = '$_'" }) -join " OR ")
    $local:installedApps = Get-WmiObject -Query $local:query
    foreach ($app in $local:installedApps | Sort-Object Name) {
        Write-Host "Uninstall $($app.Name)"
        $local:result = $app.Uninstall()
        if ($local:result.ReturnValue -eq 0) {
            Write-Host "Uninstall $($app.Name) - Success"
        } else {
            Write-Host "Failed to uninstall $($app.Name). Return value: $($local:result.ReturnValue)"
        }
    }
}


function InstallMSVC{
    param (
        [string]$VsbuildtoolsURL,
        [string]$VsInstallPath,
        [string]$ConfigFile
    )
    $InstallerFile = "vs_buildtools.exe"
    Invoke-WebRequest $VsbuildtoolsURL -OutFile $InstallerFile
    Write-Host "Installing Visual Studio Build Tools to ${VsInstallPath}"
    $ARGS_LIST = @(`
        '--quiet', `
        '--wait', `
        '--norestart', `
        '--nocache', `
        '--installPath', ${VsInstallPath},`
         '--config', ${ConfigFile}

    )
    $process = Start-Process -NoNewWindow -PassThru -FilePath $InstallerFile  -ArgumentList $ARGS_LIST -Wait
    if ( $process.ExitCode -eq 0) {
        Write-Host 'Installing Visual Studio Build Tools - Done'
    } else {
        Get-ChildItem c:\
        Get-ChildItem ${Env:ProgramFiles(x86)}
        Get-ChildItem ${VsInstallPath}
        Get-ChildItem ${VsInstallPath}\Common7\Tools
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
    '--installPath', ${VsInstallPath}
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

    # ======== build tools installer ========
    Write-Host "Removing build tools installer"
    Remove-Item $InstallerFile
    Write-Host "Removing build tools installer - Done"

    # ====== Remove build tools installer installer ========
    $InstalledInstallerPath = Join-Path -Path ${Env:ProgramFiles(x86)} -ChildPath "Microsoft Visual Studio\Installer"
    if (!(Test-Path "$InstalledInstallerPath")){
        Write-Host "Removing installed build tools installer" ;
        $rmInstallerArgsList = @(
            '/S', '/C',
            'rmdir /S /Q', "`"$InstalledInstallerPath`""
        )

        $local:rmInstallerProcess = Start-Process -FilePath cmd -ArgumentList $rmInstallerArgsList -NoNewWindow -PassThru -Wait
        if ($local:rmInstallerProcess.ExitCode -ne 0)
        {
            throw "Removing installed build tools installer - Failed"
        }
        Write-Host "Removing installed build tools installer - Done"
    }

    # ======== Cleanup temporary files ========
    Write-Host "Cleaning up temporary files"
    Get-ChildItem "C:\Users\ContainerAdministrator\AppData\Local\Temp" | Remove-Item -Recurse -Force
    Write-Host "Cleaning up temporary files - Done"
    $Local:packageCachePath = "C:\ProgramData\Package Cache"

    Write-Host "Cleaning up Package Cache"
    if (Test-Path "$Local:packageCachePath"){
        Get-ChildItem $Local:packageCachePath | Remove-Item -Recurse -Force
    }
    Write-Host "Cleaning up Package Cache - Done"


    # ======== Cleanup SoftwareDistribution folder ========
    $SoftwareDistributionDownloadPath = "C:\Windows\SoftwareDistribution\Download"
    if (Test-Path "$SoftwareDistributionDownloadPath"){
        Write-Host "Cleaning up files generated in $SoftwareDistributionDownloadPath" ;
        $rmdirSoftDistDlArgsList = @(
            '/S', '/C',
            'rmdir /S /Q ', "`"$SoftwareDistributionDownloadPath`""
        )
        $local:rmdirProcess = Start-Process -FilePath cmd -ArgumentList $rmdirSoftDistDlArgsList -NoNewWindow -PassThru -Wait
        if ($local:rmdirProcess.ExitCode -ne 0)
        {
            throw "Cleaning up files generated in $SoftwareDistributionDownloadPath - Failed"
        }
        Write-Host "Cleaning up files generated in $SoftwareDistributionDownloadPath - Done"
    } else {
        Write-Host "No need to clean up $SoftwareDistributionDownloadPath. It does not exist"
    }
}

function AddVsStudioToCMD {
    param (
        [Parameter(Mandatory=$true)][string]$VSInstallPath,
        [string]$DevCmdArguments = '-arch=amd64'
    )
    $VsDevCmdPath = Join-Path -Path $VSInstallPath -ChildPath "Common7\Tools\VsDevCmd.bat"
    $autoRunCmd = "@if not defined DevEnvDir ( CALL ${VsDevCmdPath} ${DevCmdArguments} )"
    Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value $autoRunCmd
    Write-Host "Testing for CL in cmd.exe"

    $testArgsList = @(
        '/S', '/C',
        'where cl'
    )
    $local:testClProcess = Start-Process -FilePath cmd -ArgumentList $testArgsList -NoNewWindow -PassThru -Wait
    if ($local:testClProcess.ExitCode -ne 0)
    {
        throw "Testing for CL in cmd.exe - Failed"
    }
    Write-Host "Testing for CL in cmd.exe - Success"
}

function AddVsStudioToPowershell{
    param (
        [Parameter(Mandatory=$true)][string]$VSInstallPath,
        [string]$DevCmdArguments = '-arch=amd64'
    )
    if (!(Test-Path "C:/Users/ContainerAdministrator/Documents/WindowsPowerShell")){
        New-Item -ItemType Directory -Path "C:/Users/ContainerAdministrator/Documents/WindowsPowerShell" | Out-Null
    }

    $modulePath = Join-Path -Path $VSInstallPath -ChildPath "Common7\Tools\Microsoft.VisualStudio.DevShell.dll"
    $powershellScript = @(
        "if (Test-Path -Path ${modulePath}) {",
        "Import-Module `'$modulePath`'",
        "Enter-VsDevShell -VsInstallPath ${VSInstallPath} -DevCmdArguments ${DevCmdArguments}",
        '} else {',
        '   Write-Host "Visual Studio Build Tools not found"',
        '}'
    )
    $powershellScript >> "C:/Users/ContainerAdministrator/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"

    Write-Host "Testing for CL in Powershell"
    $testArgsList = @(
        '-command', 'Get-Command cl | Out-Null'
    )
    $local:testClProcess = Start-Process -FilePath powershell -ArgumentList $testArgsList -NoNewWindow -PassThru -Wait
    if ($local:testClProcess.ExitCode -ne 0)
    {
        throw "Testing for CL in Powershell - Failed"
    }
    Write-Host "Testing for CL in Powershell - Success"
}

function AddStartupScripts{
    param (
        [Parameter(Mandatory=$true)][string]$VSInstallPath,
        [string]$DevPowershellArguments = '-arch=amd64',
        [string]$DevCmdArguments = '-arch=amd64'
    )
    Write-Host "Configuring Visual Studio development environment for shells"



    # ========== Cmd startup ==========
    Write-Host "Setting up compiler environment to run every time a command is run from CMD"
    AddVsStudioToCMD -VSInstallPath $VSInstallPath -DevCmdArguments $DevCmdArguments

    $newDirPath = Join-Path $([System.IO.Path]::GetTempPath()) $((New-Guid).ToString("N"))
    $sourceFile = Join-Path $newDirPath "helloworld.cpp"
    New-Item -ItemType Directory -Path $newDirPath | Out-Null
    CreateHelloWorldSource -Location $sourceFile
    TestCompileWithCmd -SampleFile $sourceFile
    Write-Host "Setting up compiler environment to run every time a command is run from CMD - Done"

    # ========== Powershell Profile ==========
    Write-Host "Adding setup Visual Studio development environment scripts to Powershell Profile"
    AddVsStudioToPowershell -VSInstallPath $VSInstallPath -DevCmdArguments $DevPowershellArguments
    TestCompileWithPowershell -SampleFile $sourceFile
    Write-Host "Adding setup Visual Studio development environment scripts to Powershell Profile - Done"

    Remove-Item -Path $local:newDirPath -Recurse

}

# ========== Main ==========
InstallMSVC `
  -VsbuildtoolsURL $VSBUILDTOOLS_URLS[$VSVersion] `
  -VsInstallPath $InstallPath `
  -ConfigFile $VSConfigFile

TestInstalledProperty -InstallPath $InstallPath

AddStartupScripts `
  -VSInstallPath $InstallPath `
  -DevCmdArguments $DevCmdArguments `
  -DevPowershellArguments $DevPowershellArguments

Write-Host '*************************************************'
Write-Host '* Finished installing Visual Studio Build Tools *'
Write-Host '*************************************************'

