"""Pruebas con un listener TCP real; no dependen de servicios externos."""
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PS = shutil.which('pwsh') or shutil.which('powershell')
BASH = shutil.which('bash')


class PortsTest(unittest.TestCase):
    def setUp(self):
        self.listener = socket.socket()
        self.listener.bind(('127.0.0.1', 0))
        self.listener.listen(20)
        self.open_port = self.listener.getsockname()[1]
        # Reservado pero sin listen(): el SO debe rechazar conexiones TCP.
        self.closed = socket.socket()
        self.closed.bind(('127.0.0.1', 0))
        self.closed_port = self.closed.getsockname()[1]

    def tearDown(self):
        self.listener.close()
        self.closed.close()

    def check_backend(self, prefix):
        for port, status, code in ((self.open_port, 'abierto', 0),
                                   (self.closed_port, 'cerrado', 1)):
            run = subprocess.run(prefix + [str(port)], capture_output=True,
                                 text=True, timeout=10)
            self.assertEqual(run.returncode, code, run.stderr)
            self.assertEqual(json.loads(run.stdout),
                             {'host': '127.0.0.1', 'port': port, 'status': status})
        for value in ('0', '65536', 'abc', '1;echo injection'):
            run = subprocess.run(prefix + [value], capture_output=True,
                                 text=True, timeout=10)
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertEqual(run.stdout.strip(), '')

    @unittest.skipUnless(PS, 'PowerShell no disponible')
    def test_powershell(self):
        self.check_backend([PS, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                            '-File', str(ROOT / 'scripts/check_port.ps1')])

    @unittest.skipUnless(BASH and shutil.which('timeout'), 'Bash/timeout no disponibles')
    def test_shell(self):
        self.check_backend([BASH, str(ROOT / 'scripts/check_port.sh')])

    def test_python_multiple_ports(self):
        backend = 'powershell' if PS else 'shell'
        run = subprocess.run([sys.executable, str(ROOT / 'consultar_puertos.py'),
                              '--backend', backend, str(self.open_port), str(self.closed_port)],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr)
        results = json.loads(run.stdout)
        self.assertEqual([r['status'] for r in results], ['abierto', 'cerrado'])
        self.assertEqual([r['port'] for r in results], [self.open_port, self.closed_port])

    def test_python_invalid_port(self):
        run = subprocess.run([sys.executable, str(ROOT / 'consultar_puertos.py'), '65536'],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
