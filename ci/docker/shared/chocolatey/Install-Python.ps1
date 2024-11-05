param (
    [Parameter(Mandatory=$true)]
    [string]$XmlFilePath
)
choco.exe install -y --stoponfirstfailure --no-progress --verbose $XmlFilePath
refreshenv ;
#Write-Host "installing python with choclatey"
try {
    # Attempt to load the XML file
    [xml]$xmlContent = Get-Content -Path $XmlFilePath -ErrorAction Stop

    if ($xmlContent.SelectNodes("//packages")) {
        # Iterate over each <package> within <packages>
        foreach ($package in $xmlContent.packages.package) {
            Write-Host "Testing version for $($package.id)"
            if ($package.id -match "python(\d)(\d+)")
            {
                $majorVersion = $matches[1]
                $minorVersion = $matches[2]
                $formattedVersion = "$majorVersion.$minorVersion"
                py -$formattedVersion --version
            }
            Write-Host "-----------------------------"
        }
    } else {
        Write-Host "The XML file does not contain any <packages> tags."
    }
}
catch {
    Write-Host "The file $XmlFilePath does not exist or could not be loaded."
    exit
}
