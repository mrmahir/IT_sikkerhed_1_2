# ---------------------------------------------------------
# CRUD LOGIC (System Under Test)
# ---------------------------------------------------------

class UserManager:
    def __init__(self):
        self.db = {} # Fake database

    def create_user(self, username, password):
        if username in self.db:
            return False # User already exists
        self.db[username] = password
        return True

    def read_user(self, username):
        return self.db.get(username)

    def update_user(self, username, new_password):
        if username not in self.db:
            return False
        self.db[username] = new_password
        return True

    def delete_user(self, username):
        if username in self.db:
            del self.db[username]
            return True
        return False

# ---------------------------------------------------------
# CRUD TESTS
# ---------------------------------------------------------

def test_crud_cycle():
    # Setup
    manager = UserManager()
    user = "test_user"
    pw = "secret123"
    new_pw = "newsecret456"

    # 1. CREATE
    assert manager.create_user(user, pw) is True
    assert manager.read_user(user) == pw

    # 2. READ (Verify create worked)
    assert manager.read_user("non_existent") is None

    # 3. UPDATE
    assert manager.update_user(user, new_pw) is True
    assert manager.read_user(user) == new_pw

    # 4. DELETE
    assert manager.delete_user(user) is True
    assert manager.read_user(user) is None