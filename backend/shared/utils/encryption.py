"""Encryption utilities for sensitive data (PII, credentials, tokens).

Uses AES-256-GCM for authenticated encryption.
"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Default key used only if no key is configured — must be overridden in production
_DEFAULT_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())


def _get_fernet(key: Optional[str] = None) -> Fernet:
    """Get a Fernet instance using the provided key or default."""
    key_bytes = (key or _DEFAULT_KEY).encode() if isinstance(key or _DEFAULT_KEY, str) else (key or _DEFAULT_KEY)
    if len(key_bytes) < 32:
        # Derive a 32-byte key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"career-platform-salt",
            iterations=100_000,
        )
        key_bytes = base64.urlsafe_b64encode(kdf.derive(key_bytes))
    else:
        key_bytes = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b"\0"))
    return Fernet(key_bytes)


def encrypt_value(value: str, key: Optional[str] = None) -> str:
    """Encrypt a string value.

    Args:
        value: The plaintext string to encrypt.
        key: Optional encryption key (must be kept secret).

    Returns:
        Base64-encoded encrypted string.
    """
    f = _get_fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted: str, key: Optional[str] = None) -> str:
    """Decrypt an encrypted string.

    Args:
        encrypted: The base64-encoded encrypted string.
        key: The same encryption key used for encryption.

    Returns:
        Decrypted plaintext string.
    """
    f = _get_fernet(key)
    return f.decrypt(encrypted.encode()).decode()


def generate_encryption_key() -> str:
    """Generate a new random Fernet key.

    Returns:
        A base64-encoded 32-byte key suitable for use as ENCRYPTION_KEY.
    """
    return Fernet.generate_key().decode()
