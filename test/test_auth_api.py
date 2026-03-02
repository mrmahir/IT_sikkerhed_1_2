import os
import pytest
from fastapi.testclient import TestClient
import auth_api
from db.database import FlatFileDB


@pytest.fixture(autouse=True)
def setup(monkeypatch, tmp_path):
    # use a temporary database file for each test
    db_file = tmp_path / "auth_test_db.json"
    monkeypatch.setattr(auth_api, "db", FlatFileDB(str(db_file)))
    # set environment variables for secrets
    monkeypatch.setenv("JWT_SECRET", "testsecret")
    monkeypatch.setenv("ADMIN_PASS", "adminpass")
    monkeypatch.setenv("ADMIN_ID", "admin")
    # re-read config in module
    auth_api.SECRET_KEY = os.environ.get("JWT_SECRET")
    auth_api.ADMIN_ID = os.environ.get("ADMIN_ID")
    # ensure startup event runs manually
    auth_api.ensure_admin()
    return


def get_token(client, username, password):
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_admin_can_get_token_and_register():
    client = TestClient(auth_api.app)
    token = get_token(client, "admin", "adminpass")
    # register new user
    resp = client.post(
        "/users/register",
        json={"person_id": "u1", "first_name": "U", "last_name": "One", "address": "", "password": "pw"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["person_id"] == "u1"


def test_user_can_change_own_password_and_login():
    client = TestClient(auth_api.app)
    admin_token = get_token(client, "admin", "adminpass")
    # create user
    client.post(
        "/users/register",
        json={"person_id": "u2", "first_name": "U2", "last_name": "Two", "address": "", "password": "pw"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # login as user
    user_token = get_token(client, "u2", "pw")
    # change password
    resp = client.post(
        "/users/u2/password",
        json={"new_password": "newpw"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    # old token still works until expiry, but new login must use new password
    with pytest.raises(AssertionError):
        get_token(client, "u2", "pw")
    new_token = get_token(client, "u2", "newpw")
    assert new_token


def test_self_deactivate_and_admin_reactivate():
    client = TestClient(auth_api.app)
    admin_token = get_token(client, "admin", "adminpass")
    # create user
    client.post(
        "/users/register",
        json={"person_id": "u3", "first_name": "U3", "last_name": "Three", "address": "", "password": "pw"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_token = get_token(client, "u3", "pw")
    # deactivate self
    resp = client.post(
        "/users/u3/deactivate",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.json()["status"] == "deactivated"
    # now login fails
    resp = client.post("/token", data={"username": "u3", "password": "pw"})
    assert resp.status_code == 400
    # admin reactivate
    resp = client.post(
        "/users/u3/activate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.json()["status"] == "activated"
    # user can login again
    get_token(client, "u3", "pw")
