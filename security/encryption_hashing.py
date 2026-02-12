from cryptography.fernet import Fernet
import hashlib
import os

class SecurityManager:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Loader eksisterende nøgle eller laver en ny."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_data(self, plain_text):
        """Krypterer personlig data (til GDPR)."""
        if not plain_text: return ""
        # Fernet kræver bytes, så vi encoder
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt_data(self, encrypted_text):
        """Dekrypterer data når systemet skal bruge det."""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return "DATA_CORRUPTED"

    def hash_password(self, password):
        """
        Hasher password med salt. 
        Vi bruger PBKDF2-HMAC-SHA256 som er NIST anbefalet.
        """
        salt = os.urandom(16) # Tilfældig salt
        # 100.000 iterationer gør det langsomt for hackere at brute-force
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        # Gemmer salt + hash sammen (hex format)
        return salt.hex() + ":" + pwd_hash.hex()

    def verify_password(self, stored_password, provided_password):
        """Tjekker om et password matcher hashen."""
        try:
            salt_hex, hash_hex = stored_password.split(':')
            salt = bytes.fromhex(salt_hex)
            # Vi hasher det indtastede password med SAMME salt
            new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100_000)
            return new_hash.hex() == hash_hex
        except ValueError:
            return False