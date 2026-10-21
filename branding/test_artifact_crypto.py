import importlib.util
from pathlib import Path
import unittest
from cryptography.exceptions import InvalidTag

path = Path(__file__).with_name('artifact_crypto.py')
spec = importlib.util.spec_from_file_location('artifact_crypto', path)
assert spec is not None and spec.loader is not None
crypto = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crypto)


class ArtifactEncryption(unittest.TestCase):
    def test_round_trip_and_randomized_envelopes(self):
        key = bytes(range(32))
        plain = b'MZ private executable payload\x00' * 20
        first = crypto.encrypt_bytes(plain, key)
        second = crypto.encrypt_bytes(plain, key)
        self.assertNotEqual(first, second)
        self.assertNotIn(plain, first)
        self.assertEqual(crypto.decrypt_bytes(first, key), plain)

    def test_wrong_key_rejected(self):
        blob = crypto.encrypt_bytes(b'private payload', bytes(range(32)))
        with self.assertRaises(InvalidTag):
            crypto.decrypt_bytes(blob, bytes(reversed(range(32))))

    def test_tampered_ciphertext_rejected(self):
        key = bytes(range(32))
        blob = bytearray(crypto.encrypt_bytes(b'private payload', key))
        blob[-1] ^= 1
        with self.assertRaises(InvalidTag):
            crypto.decrypt_bytes(bytes(blob), key)


if __name__ == '__main__':
    unittest.main()
