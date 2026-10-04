#!/usr/bin/env bash
# Comprueba una conexion TCP. 0=abierto, 1=cerrado/no accesible, 2=error.
set -u

fail() { printf '%s\n' "$1" >&2; exit 2; }
[[ $# -ge 1 && $# -le 3 ]] || fail 'Uso: check_port.sh PUERTO [HOST=127.0.0.1] [TIMEOUT=2]'
port=$1
host=${2:-127.0.0.1}
seconds=${3:-2}
[[ $port =~ ^[0-9]{1,5}$ ]] || fail 'El puerto debe ser un entero entre 1 y 65535.'
port=$((10#$port))
(( port >= 1 && port <= 65535 )) || fail 'El puerto debe estar entre 1 y 65535.'
[[ $seconds =~ ^[0-9]{1,2}$ ]] || fail 'TIMEOUT debe ser un entero entre 1 y 60 segundos.'
seconds=$((10#$seconds))
(( seconds >= 1 && seconds <= 60 )) || fail 'TIMEOUT debe estar entre 1 y 60 segundos.'
[[ $host =~ ^[a-zA-Z0-9_.:-]+$ && $host != -* ]] || fail 'HOST debe ser una IP o un nombre DNS valido.'
command -v timeout >/dev/null 2>&1 || fail 'Falta timeout (paquete coreutils).'

# Los argumentos se pasan por separado; no se interpolan como codigo shell.
timeout "${seconds}s" bash -c 'exec 3<>"/dev/tcp/$1/$2"' _ "$host" "$port" 2>/dev/null
result=$?
if (( result == 0 )); then
    status=abierto
    code=0
else
    status=cerrado
    code=1
fi
printf '{"host":"%s","port":%d,"status":"%s"}\n' "$host" "$port" "$status"
exit "$code"
