import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('msi_preprocess', ROOT / 'res/msi/preprocess.py')
assert spec is not None and spec.loader is not None
preprocess = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess)


@unittest.skipIf(os.name == 'nt', 'Local executable fixture uses a POSIX shell; CI probes the real Windows EXE')
class MsiExecutableProbe(unittest.TestCase):
    def test_probes_executable_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='Nimbus packaging ', dir=os.environ.get('TMPDIR')) as directory:
            exe = Path(directory) / 'Nimbus Connect.exe'
            exe.write_text('#!/bin/sh\ncase "$1" in\n--version) echo 1.5.0;;\n--build-date) echo "2026-10-20 08:00";;\nesac\n')
            exe.chmod(0o700)
            args = preprocess.make_parser().parse_args(['--revision-version', '1'])
            self.assertTrue(preprocess.init_global_vars(Path(directory), 'Nimbus Connect', args))
            self.assertEqual(preprocess.g_version, '1.5.0.1')
            self.assertEqual(preprocess.g_build_date, '2026-10-20 08:00')
    def test_rejects_failed_version_probe(self):
        with tempfile.TemporaryDirectory(prefix='Nimbus packaging ', dir=os.environ.get('TMPDIR')) as directory:
            exe = Path(directory) / 'Nimbus Connect.exe'
            exe.write_text('#!/bin/sh\necho 1.5.0\nexit 7\n')
            exe.chmod(0o700)
            args = preprocess.make_parser().parse_args([])
            with self.assertRaises(subprocess.CalledProcessError):
                preprocess.init_global_vars(Path(directory), 'Nimbus Connect', args)


@unittest.skipUnless(os.environ.get('NIMBUS_CLIENT_PROBE') == '1', 'Requires the built Windows client')
class BuiltWindowsClientProbe(unittest.TestCase):
    def test_real_windows_client_metadata(self):
        args = preprocess.make_parser().parse_args([])
        self.assertTrue(preprocess.init_global_vars(ROOT / 'rustdesk', 'NimbusConnect', args))
        self.assertTrue(preprocess.g_version.startswith('1.5.0.'))


class PackagingWorkflowContracts(unittest.TestCase):
    def test_portable_upload_precedes_msi(self):
        text = (ROOT / '.github/workflows/nimbus-windows.yml').read_text()
        self.assertLess(text.index('name: Upload Nimbus Connect portable'), text.index('name: Build msi'))
        self.assertIn('if ($LASTEXITCODE -ne 0)', text)
        self.assertIn('NIMBUS_CLIENT_PROBE', text)


if __name__ == '__main__':
    unittest.main()
