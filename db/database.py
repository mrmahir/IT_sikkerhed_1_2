import json
import os

class FlatFileDB:
    def __init__(self, filepath="flat_file_db.json"):
        self.filepath = filepath
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

    def create_user(self, user_data):
        """Adds a new user to the database."""
        data = self._load_data()
        
        # Check if ID already exists
        for user in data["userdb"]:
            if user["person_id"] == user_data["person_id"]:
                raise ValueError(f"User with ID {user_data['person_id']} already exists.")
        
        data["userdb"].append(user_data)
        self._save_data(data)
        return user_data

    def get_user_by_id(self, person_id):
        """Retrieves a single user by their ID."""
        data = self._load_data()
        for user in data["userdb"]:
            if user["person_id"] == person_id:
                return user
        return None

    def update_user_status(self, person_id, enabled_status):
        """Updates the 'enabled' status of a user."""
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