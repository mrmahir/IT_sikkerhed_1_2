from cryptography.fernet import Fernet
import hashlib
import os

class SecurityManager:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Load existing key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_data(self, plain_text):
        """Encrypts personal data (for GDPR)."""
        if not plain_text: return ""
        # Fernet requires bytes, so we encode
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt_data(self, encrypted_text):
        """Decrypts data when the system needs to use it."""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return "DATA_CORRUPTED"

    def hash_password(self, password):
        """
        Hash password with salt.
        We use PBKDF2-HMAC-SHA256 which is NIST recommended.
        """
        salt = os.urandom(16) # Random salt
        # 100,000 iterations make it slow for hackers to brute-force
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        # Store salt + hash together (hex format)
        return salt.hex() + ":" + pwd_hash.hex()

    def verify_password(self, stored_password, provided_password):
        """Checks if a password matches the hash."""
        try:
            salt_hex, hash_hex = stored_password.split(':')
            salt = bytes.fromhex(salt_hex)
            # We hash the provided password with the SAME salt
            new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100_000)
            return new_hash.hex() == hash_hex
        except ValueError:
            return False