import pytest
from .conftest import make_user
from ..models import UpdateType
from ..auth import get_password_hash, blacklisted_tokens
from fastapi.testclient import TestClient
from ..main import app
from ..database import get_session


@pytest.fixture
def client_no_auth(session):
    def override_get_session():
        return session
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

def login(client, username, password):
    r = client.post("/api/auth/token", data={"username": username, "password": password})
    return r.json()["access_token"]

def test_get_me(client_factory, session):
    user = make_user(user_id=1, username="user")
    session.add(user)
    session.commit()

    client = client_factory(user=user)
    r = client.get("/api/auth/users/me")
    assert r.status_code == 200
    assert r.json()["Username"] == "user"

def test_get_me_not_authenticated(client_factory):
    client = client_factory()
    r = client.get("/api/auth/users/me")
    assert r.status_code == 401

def test_login(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("password123")
    session.add(user)
    session.commit()

    r = client_no_auth.post("/api/auth/token", data={"username": "user", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"

def test_login_wrong_password(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("password123")
    session.add(user)
    session.commit()

    r = client_no_auth.post("/api/auth/token", data={"username": "user", "password": "wrong"})
    assert r.status_code == 400

def test_login_wrong_username(client_no_auth):
    r = client_no_auth.post("/api/auth/token", data={"username": "nonexistent", "password": "password123"})
    assert r.status_code == 400

def test_register(client_no_auth):
    r = client_no_auth.post("/api/auth/register", json={"Username": "newuser", "Password": "pass123", "Email": "new@test.com"})
    assert r.status_code == 201
    assert r.json() == {"detail": "user created."}

def test_register_duplicate_username(client_no_auth, session):
    user = make_user(user_id=1, username="existing")
    session.add(user)
    session.commit()

    r = client_no_auth.post("/api/auth/register", json={"Username": "existing", "Password": "pass123", "Email": "new@test.com"})
    assert r.status_code == 409

def test_register_duplicate_email(client_no_auth, session):
    user = make_user(user_id=1, username="existing")
    session.add(user)
    session.commit()

    r = client_no_auth.post("/api/auth/register", json={"Username": "newuser", "Password": "pass123", "Email": "existing@test.com"})
    assert r.status_code == 409

def test_register_missing_fields(client_no_auth):
    r = client_no_auth.post("/api/auth/register", json={"Username": "newuser"})
    assert r.status_code == 422

# ── POST /api/auth/logout ─────────────────────────────────────────

def test_logout(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("password123")
    session.add(user)
    session.commit()

    token = login(client_no_auth, "user", "password123")
    r = client_no_auth.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert token in blacklisted_tokens

def test_logout_not_authenticated(client_no_auth):
    r = client_no_auth.post("/api/auth/logout")
    assert r.status_code == 401

def test_update_password(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("oldpass")
    session.add(user)
    session.commit()

    token = login(client_no_auth, "user", "oldpass")
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.password.value, "Password": "oldpass", "NewPassword": "newpass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200

def test_update_password_wrong(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("oldpass")
    session.add(user)
    session.commit()

    token = login(client_no_auth, "user", "oldpass")
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.password.value, "Password": "wrongpass", "NewPassword": "newpass"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 401

def test_update_username(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("pass")
    session.add(user)
    session.commit()

    token = login(client_no_auth, "user", "pass")
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.username.value, "Username": "newusername"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    session.refresh(user)
    assert user.Username == "newusername"

def test_update_username_taken(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("pass")
    other = make_user(user_id=2, username="taken")
    session.add(user)
    session.add(other)
    session.commit()

    token = login(client_no_auth, "user", "pass")
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.username.value, "Username": "taken"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 409

def test_update_username_empty(client_no_auth, session):
    user = make_user(user_id=1, username="user")
    user.hashed_password = get_password_hash("pass")
    session.add(user)
    session.commit()

    token = login(client_no_auth, "user", "pass")
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.username.value},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 422

def test_update_not_authenticated(client_no_auth):
    r = client_no_auth.put("/api/auth/users/me",
        json={"TypeOfInteraction": UpdateType.username.value, "Username": "newusername"}
    )
    assert r.status_code == 401