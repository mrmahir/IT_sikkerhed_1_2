import pytest

# ---------------------------------------------------------
# SUT (System Under Test) - Dummy Logic for the Assignment
# ---------------------------------------------------------

def validate_password_strength(password):
    """
    Simulates Boundary Value & Equivalence logic.
    Rule: Must be 8-64 chars.
    """
    if len(password) < 8:
        return False
    if len(password) > 64:
        return False
    return True

def login_attempt(user_exists, is_locked, password_correct):
    """
    Simulates the Decision Table logic.
    """
    if not user_exists:
        return "Error: Invalid User"
    if is_locked:
        return "Error: Locked"
    if not password_correct:
        return "Error: Invalid Password"
    return "Success"

# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------

# 1. Decision Table Test (Data Driven)
# Maps directly to the table defined in README.md
@pytest.mark.parametrize("user_exists, is_locked, password_correct, expected_output", [
    (False, False, False, "Error: Invalid User"),     # Rule 1
    (True,  True,  False, "Error: Locked"),           # Rule 2
    (True,  False, False, "Error: Invalid Password"), # Rule 3
    (True,  False, True,  "Success"),                 # Rule 4
])
def test_login_decision_table(user_exists, is_locked, password_correct, expected_output):
    result = login_attempt(user_exists, is_locked, password_correct)
    assert result == expected_output

# 2. Boundary Value Test (Data Driven)
# Testing the edges of the password length (7, 8, 64, 65)
@pytest.mark.parametrize("password, expected_validity", [
    ("1234567", False),   # 7 chars (Just below)
    ("12345678", True),   # 8 chars (On boundary)
    ("A" * 64, True),     # 64 chars (On boundary)
    ("A" * 65, False),    # 65 chars (Just above)
])
def test_password_boundaries(password, expected_validity):
    assert validate_password_strength(password) is expected_validity