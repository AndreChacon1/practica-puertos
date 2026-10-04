# Práctica: comprobación de puertos con Linux, Docker y PowerShell

Un script recibe un puerto y comprueba si puede establecer una conexión **TCP**.
Se incluyen una versión Bash para Linux, otra PowerShell para Windows y un
programa Python que **invoca los scripts** para consultar múltiples puertos.
Python usa únicamente su biblioteca estándar (Python 3.9 o posterior).

**Entrega:** [repositorio público](https://github.com/AndreChacon1/practica-puertos)
· [video explicativo](demo-puertos.mp4)
· [pruebas automáticas](https://github.com/AndreChacon1/practica-puertos/actions).
El video presenta resultados reales mediante diapositivas con texto, sin voz;
no es una grabación de pantalla. Las pruebas pasaron en Windows y en Linux con Docker.

## Archivos

| Archivo | Función |
| --- | --- |
| `Dockerfile` | Imagen Ubuntu 24.04 con Bash, timeout y Python |
| `scripts/check_port.sh` | Consulta un puerto desde Linux |
| `scripts/check_port.ps1` | Consulta un puerto desde Windows |
| `consultar_puertos.py` | Envía varios puertos al script seleccionado y reúne su JSON |
| `tests/test_ports.py` | Pruebas con sockets TCP locales reales |
| `VIDEO.md` | Guion y comandos para grabar la entrega |

## Qué significa el resultado

- `abierto`: se pudo conectar por TCP.
- `cerrado`: no se pudo conectar dentro del tiempo permitido. También puede indicar
  filtrado por firewall, un equipo inaccesible o un error DNS; una conexión fallida
  no permite distinguir todas estas causas.
- Los scripts devuelven código **0** para abierto, **1** para cerrado y **2** para
  argumentos inválidos o errores de ejecución detectados.
- Python devuelve **0** si todas las consultas se procesaron, aunque haya puertos
  cerrados, y **2** si hubo un error. El estado de cada puerto aparece en el JSON.

La dirección predeterminada es `127.0.0.1` y el tiempo de espera es de 2 segundos.
Solo se aceptan puertos de 1 a 65535 y tiempos de espera de 1 a 60 segundos.
Consulta equipos propios o aquellos para los que tengas autorización.

## 1. Linux con Docker

Instala Docker Desktop y selecciona contenedores Linux. Desde la raíz del repo:

```powershell
docker build -t practica-puertos .
docker network create practica-red
docker run -d --name servidor-practica --network practica-red practica-puertos python3 -m http.server 8000 --bind 0.0.0.0
```

El servidor de prueba escucha en 8000. El puerto 8001 no tiene un servicio.
Estos comandos funcionan desde PowerShell o Bash:

```powershell
docker run --rm --network practica-red practica-puertos bash /lab/scripts/check_port.sh 8000 servidor-practica
docker run --rm --network practica-red practica-puertos bash /lab/scripts/check_port.sh 8001 servidor-practica
```

Salida esperada: `abierto` para 8000 y `cerrado` para 8001.

En un contenedor, `127.0.0.1` identifica ese mismo contenedor. Por eso usamos
una red compartida y el nombre `servidor-practica` para consultar el otro.
Para consultar un servicio de Windows desde Docker Desktop se puede utilizar
`host.docker.internal`; el servicio debe aceptar conexiones desde Docker.

En Linux sin Docker:

```bash
bash scripts/check_port.sh 8000 127.0.0.1 2
```

## 2. Windows con PowerShell

Abre una primera terminal y deja un servidor activo:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

En una segunda terminal, desde la raíz del repo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_port.ps1 -Port 8000
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_port.ps1 -Port 8001
```

`Bypass` se aplica únicamente al proceso iniciado, sin modificar la configuración
permanente del equipo. También puedes usar `pwsh` si tienes PowerShell 7.
Para especificar destino y espera agrega `-TargetHost 127.0.0.1 -TimeoutSeconds 3`.
Si tu instalación usa el lanzador `py`, reemplaza `python` por `py`.

## 3. Python: múltiples puertos

Con el servidor Windows de la sección anterior activo:

```powershell
python consultar_puertos.py --backend powershell 8000 8001 8002
```

Para invocar Bash dentro de Docker desde Python instalado en Windows:

```powershell
python consultar_puertos.py --backend docker --network practica-red --host servidor-practica 8000 8001 8002
```

También puedes ejecutar todo dentro de Linux, sin instalar Python en Windows:

```powershell
docker run --rm --network practica-red practica-puertos python3 /lab/consultar_puertos.py --backend shell --host servidor-practica 8000 8001 8002
```

Cada puerto se envía por separado mediante `subprocess.run`; no se construye
código a partir de la entrada ni se usa `shell=True`. Las consultas son secuenciales.

## 4. Pruebas

```powershell
python -m unittest discover -s tests -v
```

Para probar Bash y Python dentro de la imagen (desde PowerShell):

```powershell
docker run --rm --mount "type=bind,source=$PWD,target=/tests-src,readonly" -w /tests-src practica-puertos python3 -m unittest discover -s tests -v
```

Las pruebas abren un socket local y reservan otro sin escuchar para comprobar
ambos estados de forma reproducible. La prueba del sistema operativo no disponible
se marca como omitida. No requieren acceso a Internet.

## 5. Finalizar la demostración

Detén el servidor Python de Windows con `Ctrl+C`. Para eliminar únicamente
los recursos Docker creados para esta práctica:

```powershell
docker rm -f servidor-practica
docker network rm practica-red
```

## 6. Entrega en GitHub

Una vez creado el commit local y autenticado GitHub CLI:

```powershell
gh auth login --hostname github.com
gh repo create practica-puertos --public --source . --remote origin --push
```

Usa `--private` si la entrega requiere un repositorio privado y concede acceso al
docente. Entrega la URL del repositorio y el enlace del video con permiso de lectura.
Los videos están excluidos del repositorio para evitar archivos pesados,
salvo `demo-puertos.mp4`, que contiene la demostración incluida.
Consulta `VIDEO.md` para la grabación.
