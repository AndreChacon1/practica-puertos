# Compatible con Windows PowerShell 5.1 y PowerShell 7.
# 0=abierto, 1=cerrado/no accesible, 2=argumento o error de ejecucion.
param(
    [string]$Port,
    [string]$TargetHost = '127.0.0.1',
    [string]$TimeoutSeconds = '2'
)

$ErrorActionPreference = 'Stop'
if ($args.Count -gt 0 -or $Port -notmatch '^[0-9]{1,5}$' -or
    [int]$Port -lt 1 -or [int]$Port -gt 65535) {
    [Console]::Error.WriteLine('Port debe ser un entero entre 1 y 65535.')
    exit 2
}
if ($TimeoutSeconds -notmatch '^[0-9]{1,2}$' -or
    [int]$TimeoutSeconds -lt 1 -or [int]$TimeoutSeconds -gt 60) {
    [Console]::Error.WriteLine('TimeoutSeconds debe estar entre 1 y 60.')
    exit 2
}
if ($TargetHost -notmatch '^[a-zA-Z0-9_.:-]+$' -or $TargetHost.StartsWith('-')) {
    [Console]::Error.WriteLine('TargetHost debe ser una IP o un nombre DNS valido.')
    exit 2
}

$client = New-Object System.Net.Sockets.TcpClient
$status = 'cerrado'
$code = 1
try {
    $connection = $client.ConnectAsync($TargetHost, [int]$Port)
    if ($connection.Wait([int]$TimeoutSeconds * 1000) -and $client.Connected) {
        $status = 'abierto'
        $code = 0
    }
} catch {
    # Una conexion rechazada o un fallo de DNS se considera no accesible.
    $status = 'cerrado'
} finally {
    $client.Dispose()
}
[ordered]@{ host = $TargetHost; port = [int]$Port; status = $status } |
    ConvertTo-Json -Compress
exit $code
