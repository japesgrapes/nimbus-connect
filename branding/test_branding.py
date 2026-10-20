import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class NimbusBrandingContracts(unittest.TestCase):
    def test_built_in_identity_and_connection_defaults(self):
        source = (ROOT / 'src/common.rs').read_text()
        start = source.index('pub fn load_custom_client() {')
        init = source[start:source.index('#[cfg(debug_assertions)]', start)]
        self.assertIn('"Nimbus Connect".to_owned()', init)
        self.assertIn('("custom-rendezvous-server", "rustdesk.nimbusconnect.co.za")', init)
        self.assertIn('("key", "OiHgteVB1Hk+sBd5WRgNwseYFthBc7LMZu+ESvzaTOk=")', init)
        self.assertIn('("relay-server", "")', init)
        self.assertIn('("api-server", "")', init)

    def test_windows_branding_resources(self):
        rc = (ROOT / 'flutter/windows/runner/Runner.rc').read_text()
        self.assertIn('VALUE "ProductName", "Nimbus Connect"', rc)
        self.assertIn('VALUE "OriginalFilename", "nimbus connect.exe"', rc)
        for name in ['icon.png', 'logo.png', 'logo_light.png', 'logo_dark.png']:
            self.assertTrue((ROOT / 'flutter/assets' / name).is_file(), name)
        self.assertEqual(
            (ROOT / 'res/icon.ico').read_bytes(),
            (ROOT / 'flutter/windows/runner/resources/app_icon.ico').read_bytes())

    def test_isolated_windows_workflow(self):
        path = ROOT / '.github/workflows/nimbus-windows.yml'
        self.assertTrue(path.is_file(), 'Nimbus-only workflow is missing')
        text = path.read_text()
        self.assertNotIn('secrets.', text)
        self.assertNotIn('action-gh-release', text)
        self.assertIn('NimbusConnect-${{ env.VERSION }}-windows-x64.exe', text)
        self.assertIn('Nimbus Connect installers', text)
        self.assertIn('nimbus-1.5.0', text)

if __name__ == '__main__':
    unittest.main()
