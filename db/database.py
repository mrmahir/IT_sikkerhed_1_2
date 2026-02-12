import json
import os
from security.encryption_hashing import SecurityManager

class FlatFileDB:
    def __init__(self, filepath="flat_file_db.json"):
        self.filepath = filepath
        self.security = SecurityManager() # Starts the security module
        
        # Initialize file if it doesn't exist
        if not os.path.exists(self.filepath):
            self._save_data({"userdb": []})

    def _load_data(self):
        """Helper to read the raw JSON data."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"userdb": []}

    def _save_data(self, data):
        """Helper to write data back to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def add_secure_user(self, user_input):
        """
        Takes raw data, encrypts PII, hashes password, and saves it.
        Replaces the old 'create_user' function for GDPR compliance.
        """
        data = self._load_data()
        
        # Check if ID already exists
        for user in data["userdb"]:
            if user["person_id"] == user_input["person_id"]:
                raise ValueError(f"User with ID {user_input['person_id']} already exists.")
        
        # Create secure user object
        secure_user = {
            "person_id": user_input["person_id"], # ID is often kept visible for indexing
            # PII Data (GDPR) - Encrypted
            "first_name": self.security.encrypt_data(user_input["first_name"]),
            "last_name": self.security.encrypt_data(user_input["last_name"]),
            "address": self.security.encrypt_data(user_input["address"]),
            "email": self.security.encrypt_data(user_input.get("email", "")), # Use .get() in case email is missing
            "street_number": user_input.get("street_number", ""), # Optional fields
            # Password - Hashed (One-way)
            "password": self.security.hash_password(user_input["password"]),
            "enabled": True
        }
        
        # Clear raw memory (Best practice)
        del user_input
        
        data["userdb"].append(secure_user)
        self._save_data(data)
        return secure_user["person_id"]

    def get_decrypted_user(self, person_id):
        """Retrieves a user and decrypts their data so it can be read."""
        data = self._load_data()
        for user in data["userdb"]:
            if user["person_id"] == person_id:
                # Return a COPY with decrypted data
                return {
                    "person_id": user["person_id"],
                    "first_name": self.security.decrypt_data(user["first_name"]),
                    "last_name": self.security.decrypt_data(user["last_name"]),
                    "address": self.security.decrypt_data(user["address"]),
                    "email": self.security.decrypt_data(user.get("email", "")),
                    "street_number": user.get("street_number", ""),
                    "enabled": user["enabled"]
                    # We NEVER return the password field
                }
        return None

    def update_user_status(self, person_id, enabled_status):
        """Updates the 'enabled' status of a user. Works on encrypted users too."""
        data = self._load_data()
        updated = False
        for user in data["userdb"]:
            if user["person_id"] == person_id:
                user["enabled"] = enabled_status
                updated = True
                break
        
        if updated:
            self._save_data(data)
            return True
        return False

    def delete_user(self, person_id):
        """Hard deletes a user from the database."""
        data = self._load_data()
        initial_count = len(data["userdb"])
        # Filter out the user with the given ID
        data["userdb"] = [u for u in data["userdb"] if u["person_id"] != person_id]
        
        if len(data["userdb"]) < initial_count:
            self._save_data(data)
            return True
        return False