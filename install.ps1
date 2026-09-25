# Install Token Visualizer on Windows from the latest GitHub release.
#
#   irm https://raw.githubusercontent.com/Mattbusel/Token-Visualizer/main/install.ps1 | iex
#
# It downloads the Windows zip, checks it against the release's SHA256SUMS.txt,
# puts token-visualizer.exe in %LOCALAPPDATA%\Programs\token-visualizer and adds that folder to
# your user PATH. To remove it later: delete that folder and the PATH entry.
# Set $env:INSTALL_VERSION = 'v1.2.3' first to install a specific release.

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Repo   = 'Mattbusel/Token-Visualizer'
$Prefix = 'token-visualizer'
$Bin    = 'token-visualizer'
$Cmd    = 'token-visualizer'
$Dest   = Join-Path $env:LOCALAPPDATA "Programs\$Cmd"

if ($env:INSTALL_VERSION) {
    $tag = $env:INSTALL_VERSION
} else {
    try {
        $tag = (Invoke-RestMethod -UseBasicParsing "https://api.github.com/repos/$Repo/releases/latest").tag_name
    } catch {
        throw "Could not look up the latest release of $Repo ($($_.Exception.Message)). Check your connection, or set `$env:INSTALL_VERSION = 'vX.Y.Z' and retry."
    }
}

$name = "$Prefix-$tag-windows-x86_64"
$base = "https://github.com/$Repo/releases/download/$tag"
$tmp  = Join-Path ([IO.Path]::GetTempPath()) ("$Cmd-install-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    Write-Host "Downloading $name.zip ..."
    Invoke-WebRequest -UseBasicParsing "$base/$name.zip" -OutFile "$tmp\$name.zip"
    Invoke-WebRequest -UseBasicParsing "$base/SHA256SUMS.txt" -OutFile "$tmp\SHA256SUMS.txt"

    $line = Get-Content "$tmp\SHA256SUMS.txt" | Where-Object { $_ -match "\s\*?$([regex]::Escape("$name.zip"))$" } | Select-Object -First 1
    if (-not $line) { throw "$name.zip is not listed in SHA256SUMS.txt; not installing." }
    $expected = ($line -split '\s+')[0].ToLower()
    $actual = (Get-FileHash -Algorithm SHA256 "$tmp\$name.zip").Hash.ToLower()
    if ($expected -ne $actual) { throw "Checksum mismatch for $name.zip (expected $expected, got $actual); not installing." }
    Write-Host "Checksum OK."

    Expand-Archive -Path "$tmp\$name.zip" -DestinationPath $tmp -Force
    $exe = Join-Path $tmp "$name\$Bin.exe"
    if (-not (Test-Path $exe)) { throw "The archive did not contain $Bin.exe." }

    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Copy-Item $exe (Join-Path $Dest "$Cmd.exe") -Force
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $userPath) { $userPath = '' }
if (($userPath -split ';') -notcontains $Dest) {
    [Environment]::SetEnvironmentVariable('Path', (($userPath.TrimEnd(';') + ";$Dest").TrimStart(';')), 'User')
    Write-Host "Added $Dest to your user PATH."
}
if (($env:Path -split ';') -notcontains $Dest) { $env:Path = "$env:Path;$Dest" }

Write-Host "Installed $Cmd $tag to $Dest\$Cmd.exe"
Write-Host "Try it: token-visualizer --help   (open a new terminal if the command is not found)"
