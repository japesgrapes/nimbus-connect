"""Authenticated encryption for owner-only build artifacts (AES-256-GCM).

The 32-byte key is supplied as hex via NIMBUS_ARTIFACT_KEY or --key-file.
Never put a key in source, command-line arguments, logs or an uploaded artifact.
"""
import argparse
import os
from pathlib import Path
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b'NIMBUS-AESGCM-1\n'


def encrypt_bytes(plain: bytes, key: bytes) -> bytes:
    if len(key) != 32:
        raise ValueError('A 32-byte key is required')
    nonce = secrets.token_bytes(12)
    return MAGIC + nonce + AESGCM(key).encrypt(nonce, plain, MAGIC)


def decrypt_bytes(envelope: bytes, key: bytes) -> bytes:
    if len(key) != 32:
        raise ValueError('A 32-byte key is required')
    if not envelope.startswith(MAGIC) or len(envelope) < len(MAGIC) + 12 + 16:
        raise ValueError('Invalid encrypted artifact envelope')
    start = len(MAGIC)
    return AESGCM(key).decrypt(envelope[start:start + 12], envelope[start + 12:], MAGIC)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['encrypt', 'decrypt'])
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--key-file', type=Path)
    args = parser.parse_args()
    encoded = args.key_file.read_text().strip() if args.key_file else os.environ.get('NIMBUS_ARTIFACT_KEY', '')
    if len(encoded) != 64:
        raise ValueError('Missing or invalid encryption key')
    key = bytes.fromhex(encoded)
    if args.input.stat().st_size > 512 * 1024 * 1024:
        raise ValueError('Artifact exceeds the bounded in-memory size limit')
    operation = encrypt_bytes if args.mode == 'encrypt' else decrypt_bytes
    result = operation(args.input.read_bytes(), key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(result)
    print(f'{args.mode} completed: {len(result)} bytes')


if __name__ == '__main__':
    main()
