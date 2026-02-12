import unittest
import os
import json
from db.database import FlatFileDB

class TestFlatFileDB(unittest.TestCase):
    
    def setUp(self):
        """Runs before every test. Creates a temporary test DB."""
        self.test_file = "test_db_temp.json"
        self.db = FlatFileDB(self.test_file)
        
        # Seed initial data
        initial_data = {
            "userdb": [
                {
                    "person_id": "999",
                    "first_name": "Test",
                    "last_name": "User",
                    "address": "Test Lane",
                    "street_number": "1",
                    "password": "hashed_test",
                    "enabled": True
                }
            ]
        }
        with open(self.test_file, 'w') as f:
            json.dump(initial_data, f)

    def tearDown(self):
        """Runs after every test. Cleans up the file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_create_new_user_success(self):
        """
        Risk: If this test fails, new users cannot sign up, halting the system's growth.
        """
        # Given: A valid new user object that does not currently exist in the DB
        new_user = {
            "person_id": "100",
            "first_name": "Alice",
            "last_name": "Wonder",
            "address": "Rabbit Hole",
            "street_number": "1",
            "password": "hash_123",
            "enabled": True
        }

        # When: The create_user function is called
        self.db.create_user(new_user)

        # Then: The user should be retrievable from the database
        stored_user = self.db.get_user_by_id("100")
        self.assertEqual(stored_user["first_name"], "Alice")

    def test_read_existing_user(self):
        """
        Risk: If this test fails, users cannot log in or view their profiles, causing critical service usage issues.
        """
        # Given: An existing user ID ("999") that we seeded in setUp
        user_id = "999"

        # When: We request the user by ID
        result = self.db.get_user_by_id(user_id)

        # Then: The returned object must match the seeded data
        self.assertIsNotNone(result)
        self.assertEqual(result["last_name"], "User")

    def test_update_user_enabled_status(self):
        """
        Risk: If this test fails, admins cannot ban/enable users, leading to security vulnerabilities or access lockout.
        """
        # Given: An existing user who is currently enabled (True)
        user_id = "999"

        # When: We update their status to disabled (False)
        self.db.update_user_status(user_id, False)

        # Then: The user's enabled status in the DB should be False
        updated_user = self.db.get_user_by_id(user_id)
        self.assertFalse(updated_user["enabled"])

    def test_delete_user_removes_record(self):
        """
        Risk: If this test fails, GDPR compliance is violated (right to be forgotten) and the DB retains stale data.
        """
        # Given: An existing user in the database
        user_id = "999"

        # When: The delete function is called
        success = self.db.delete_user(user_id)

        # Then: The function returns True and the user can no longer be found
        self.assertTrue(success)
        missing_user = self.db.get_user_by_id(user_id)
        self.assertIsNone(missing_user)

if __name__ == '__main__':
    unittest.main()