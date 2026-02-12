import unittest
import os
import json
from db.database import FlatFileDB

class TestSecurityFeatures(unittest.TestCase):
    
    def setUp(self):
        self.test_file = "test_secure_db.json"
        self.db = FlatFileDB(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # --- TEST 1: ENCRYPTION (GDPR) ---
    def test_pii_data_is_encrypted(self):
        """
        Risk: If this fails, personal data (GDPR) is readable by hackers stealing the file.
        """
        # Given: A user with sensitive data
        user_input = {
            "person_id": "1",
            "first_name": "Satoshi",
            "last_name": "Nakamoto",
            "address": "Blockchain Blvd",
            "email": "sat@btc.com",
            "password": "my_secret_password"
        }
        
        # When: We save the user
        self.db.add_secure_user(user_input)

        # Then: The raw file should NOT contain the name "Satoshi"
        with open(self.test_file, 'r') as f:
            raw_content = f.read()
            
        print(f"\n[ENCRYPTION CHECK] Raw Data: {raw_content[:100]}...") 
        self.assertNotIn("Satoshi", raw_content)
        self.assertNotIn("Nakamoto", raw_content)

    # --- TEST 2: HASHING (Password Security) ---
    def test_password_is_hashed(self):
        """
        Risk: If this fails, passwords are stored in plain text (Critical Security Flaw).
        """
        # Given: A user with a known password
        password = "super_secret_password_123"
        user_input = {
            "person_id": "2", "first_name": "Test", "last_name": "User",
            "address": "T", "email": "t@t.com", "password": password
        }

        # When: We save the user
        self.db.add_secure_user(user_input)

        # Then: 
        # 1. The plain password must NOT be in the file
        with open(self.test_file, 'r') as f:
            raw_data = json.load(f)
            stored_user = raw_data["userdb"][0]
            
        stored_password = stored_user["password"]
        
        # Check it is NOT plain text
        self.assertNotEqual(stored_password, password)
        self.assertNotIn(password, str(raw_data))
        
        # Check it IS a hash (structure: salt:hash)
        self.assertIn(":", stored_password)
        self.assertTrue(len(stored_password) > 20) # Hashes are long

    # --- TEST 3: LOGIN (Verify Hash) ---
    def test_password_verification(self):
        """
        Risk: If this fails, valid users cannot log in (Business Critical).
        """
        # Given: A user is created with a password
        password = "login_password_123"
        user_input = {
            "person_id": "3", "first_name": "Login", "last_name": "User",
            "address": "L", "email": "l@l.com", "password": password
        }
        self.db.add_secure_user(user_input)

        # When: We retrieve the raw stored hash to verify it manually
        with open(self.test_file, 'r') as f:
            raw_data = json.load(f)
            stored_hash = raw_data["userdb"][0]["password"]

        # Then: The security manager should verify the correct password...
        is_valid = self.db.security.verify_password(stored_hash, password)
        self.assertTrue(is_valid)

        # ...and reject a wrong password
        is_invalid = self.db.security.verify_password(stored_hash, "wrong_password")
        self.assertFalse(is_invalid)

if __name__ == '__main__':
    unittest.main()