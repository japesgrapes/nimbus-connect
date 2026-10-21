import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class NimbusBrandingContracts(unittest.TestCase):
    def test_internal_name_is_accepted_by_windows_installer_policy(self):
        source = (ROOT / 'src/common.rs').read_text()
        match = re.search(r'APP_NAME\.write\(\)\.unwrap\(\) = "([^"]+)"', source)
        self.assertIsNotNone(match)
        assert match is not None
        name = match.group(1)
        self.assertRegex(name, r'^[a-zA-Z0-9-]+$')
        self.assertEqual(name, 'NimbusConnect')

    def test_built_in_identity_and_connection_defaults(self):
        source = (ROOT / 'src/common.rs').read_text()
        start = source.index('pub fn load_custom_client() {')
        init = source[start:source.index('#[cfg(debug_assertions)]', start)]
        self.assertIn('"NimbusConnect".to_owned()', init)
        self.assertIn('("custom-rendezvous-server", "rustdesk.nimbusconnect.co.za")', init)
        self.assertIn('("key", "OiHgteVB1Hk+sBd5WRgNwseYFthBc7LMZu+ESvzaTOk=")', init)
        self.assertIn('("relay-server", "")', init)
        self.assertIn('("api-server", "")', init)

    def test_windows_branding_resources(self):
        rc = (ROOT / 'flutter/windows/runner/Runner.rc').read_text()
        self.assertIn('VALUE "ProductName", "Nimbus Connect"', rc)
        self.assertIn('VALUE "OriginalFilename", "nimbusconnect.exe"', rc)
        for name in ['icon.png', 'logo.png', 'logo_light.png', 'logo_dark.png']:
            self.assertTrue((ROOT / 'flutter/assets' / name).is_file(), name)
        self.assertEqual(
            (ROOT / 'res/icon.ico').read_bytes(),
            (ROOT / 'flutter/windows/runner/resources/app_icon.ico').read_bytes())

    def test_isolated_windows_workflow(self):
        path = ROOT / '.github/workflows/nimbus-windows.yml'
        self.assertTrue(path.is_file(), 'Nimbus-only workflow is missing')
        text = path.read_text()
        self.assertIn('secrets.NIMBUS_ARTIFACT_KEY', text)
        self.assertNotIn('path: SignOutput/', text)
        self.assertNotIn('path: PortableOutput/', text)
        self.assertIn('path: EncryptedOutput/NimbusConnect-1.5.0-windows-x64.zip.aesgcm', text)
        self.assertIn('path: EncryptedOutput/NimbusConnect-1.5.0-windows-x64-portable.zip.aesgcm', text)
        self.assertNotIn('action-gh-release', text)
        self.assertIn('NimbusConnect-${{ env.VERSION }}-windows-x64.exe', text)
        self.assertIn('Nimbus Connect installers', text)
        self.assertIn('nimbus-1.5.0', text)

if __name__ == '__main__':
    unittest.main()
