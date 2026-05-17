$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ToolBin = Join-Path $HOME ".local\bin"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is required. Install it first: https://docs.astral.sh/uv/"
}

Push-Location $ProjectRoot
try {
    $env:UV_LINK_MODE = "copy"
    uv tool install --editable . --force

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathParts = @()
    if ($userPath) {
        $pathParts = $userPath -split ";"
    }

    if ($pathParts -notcontains $ToolBin) {
        $newPath = if ($userPath) { "$userPath;$ToolBin" } else { $ToolBin }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$env:Path;$ToolBin"
        Write-Host "Added $ToolBin to the user PATH."
        Write-Host "Open a new terminal if the current one still cannot find diri."
    }

    Write-Host "DIRI CLI installed. Try: diri --help"
}
finally {
    Pop-Location
}
