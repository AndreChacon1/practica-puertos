# Guion de video (3–5 minutos)

Este archivo es un guion; no es una grabación ni evidencia de ejecución en Docker.

Se incluye además [demo-puertos.mp4](demo-puertos.mp4): un video de aproximadamente
2 minutos con diapositivas explicativas y resultados de ejecuciones reales de
Bash en Docker, PowerShell en Windows y Python. No contiene voz ni captura de
pantalla. Si el docente pide una grabación personal, utiliza el siguiente guion.

1. **Presentación (20 segundos).** Muestra el repositorio y explica: “Esta práctica
   comprueba conexiones TCP. Preparé un script Bash para Linux, uno PowerShell
   para Windows y un programa Python que envía múltiples puertos”.
2. **Linux y Docker (1 minuto).** Ejecuta la construcción de la imagen y crea
   `practica-red` y `servidor-practica` con los comandos del README. Ejecuta Bash
   para los puertos 8000 y 8001. Muestra los resultados reales y explica que
   ambos contenedores se comunican por el nombre del servidor dentro de la red.
3. **Explicar Bash (30 segundos).** Abre `scripts/check_port.sh`. Señala el argumento
   del puerto, su validación, la conexión `/dev/tcp` y `timeout`, que limita la espera.
4. **Windows (1 minuto).** Inicia `python -m http.server 8000 --bind 127.0.0.1`
   en otra terminal. Ejecuta PowerShell para 8000 y 8001. Muestra
   `TcpClient.ConnectAsync` y el tiempo de espera en el archivo `.ps1`.
5. **Python (40 segundos).** Ejecuta las dos variantes del README:
   `--backend powershell` y `--backend docker`, con 8000, 8001 y 8002.
   Explica que `subprocess.run` consume el script y lee su salida JSON.
6. **Validación y cierre (30 segundos).** Ejecuta las pruebas y una consulta con
   puerto 65536 para mostrar la validación. Explica que “cerrado” significa que
   no se logró conectar y también puede deberse a un firewall. Muestra la URL
   final de GitHub y termina los servicios de prueba.

Graba la pantalla con tu grabador habitual, con letra de terminal legible y voz.
Evita mostrar credenciales durante la autenticación de GitHub. Sube el video a
la plataforma de entrega o comparte un enlace con acceso para el docente.

## Lista de entrega

- [ ] Imagen Docker construida y demostración Linux realizada.
- [ ] Demostración PowerShell realizada.
- [ ] Python consulta múltiples puertos mediante los scripts.
- [ ] Repositorio publicado y accesible para el docente.
- [ ] Video grabado y enlace accesible.
- [ ] Entregar ambos enlaces antes de la hora indicada por el docente.
