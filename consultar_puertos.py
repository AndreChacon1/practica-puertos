#!/usr/bin/env python3
"""Invoca el script Shell o PowerShell una vez por puerto, sin shell=True."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def port_number(value):
    if not re.fullmatch(r"[0-9]{1,5}", value) or not 1 <= int(value) <= 65535:
        raise argparse.ArgumentTypeError("el puerto debe estar entre 1 y 65535")
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ports", nargs="+", type=port_number)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--timeout", type=int, choices=range(1, 61), default=2,
                        metavar="1..60")
    parser.add_argument("--backend", choices=("shell", "powershell", "docker"),
                        default="powershell" if sys.platform == "win32" else "shell")
    parser.add_argument("--image", default="practica-puertos", help="imagen Docker")
    parser.add_argument("--network", help="red Docker opcional")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_.:-]+", args.host) or args.host.startswith("-"):
        parser.error("host debe ser una IP o un nombre DNS valido")

    results = []
    had_error = False
    for port in args.ports:
        if args.backend == "powershell":
            executable = shutil.which("pwsh") or shutil.which("powershell")
            cmd = [executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(ROOT / "scripts/check_port.ps1"), "-Port", str(port),
                   "-TargetHost", args.host, "-TimeoutSeconds", str(args.timeout)]
        elif args.backend == "shell":
            executable = shutil.which("bash")
            cmd = [executable, str(ROOT / "scripts/check_port.sh"), str(port),
                   args.host, str(args.timeout)]
        else:
            executable = shutil.which("docker")
            cmd = [executable, "run", "--rm"]
            if args.network:
                cmd += ["--network", args.network]
            cmd += [args.image, "bash", "/lab/scripts/check_port.sh", str(port),
                    args.host, str(args.timeout)]
        try:
            if not executable:
                raise RuntimeError(f"No se encontro el ejecutable para {args.backend}")
            completed = subprocess.run(cmd, capture_output=True, text=True,
                                       timeout=args.timeout + 30)
            if completed.returncode not in (0, 1):
                raise RuntimeError(completed.stderr.strip() or
                                   f"El script termino con codigo {completed.returncode}")
            result = json.loads(completed.stdout)
            expected_status = "abierto" if completed.returncode == 0 else "cerrado"
            if (result.get("host") != args.host or result.get("port") != port
                    or result.get("status") != expected_status):
                raise ValueError("respuesta del script no valida")
        except (OSError, RuntimeError, ValueError, AttributeError, subprocess.TimeoutExpired) as exc:
            had_error = True
            result = {"host": args.host, "port": port, "status": "error", "detail": str(exc)}
        results.append(result)
    print(json.dumps(results, ensure_ascii=True, indent=2))
    return 2 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
