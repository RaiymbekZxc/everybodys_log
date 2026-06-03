import pytest
from .conftest import make_user
from ..models import tblUser

def test_give_admin(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    target = make_user(user_id=2, username="target")
    session.add(admin)
    session.add(target)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/target/giveadmin")
    assert r.status_code == 200
    session.refresh(target)
    assert target.IsAdmin == True

def test_give_admin_not_admin(client_factory, session):
    user = make_user(user_id=1, username="user")
    target = make_user(user_id=2, username="target")
    session.add(user)
    session.add(target)
    session.commit()

    client = client_factory(user=user)
    r = client.put("/api/admin/user/target/giveadmin")
    assert r.status_code == 403

def test_give_admin_not_authenticated(client_factory, session):
    target = make_user(user_id=2, username="target")
    session.add(target)
    session.commit()

    client = client_factory()
    r = client.put("/api/admin/user/target/giveadmin")
    assert r.status_code == 401

def test_give_admin_self(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/admin/giveadmin")
    assert r.status_code == 400

def test_give_admin_user_not_found(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/nonexistent/giveadmin")
    assert r.status_code == 404

def test_deactivate(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    target = make_user(user_id=2, username="target")
    session.add(admin)
    session.add(target)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/target/deactivate")
    assert r.status_code == 200
    session.refresh(target)
    assert target.IsActive == False

def test_deactivate_not_admin(client_factory, session):
    user = make_user(user_id=1, username="user")
    target = make_user(user_id=2, username="target")
    session.add(user)
    session.add(target)
    session.commit()

    client = client_factory(user=user)
    r = client.put("/api/admin/user/target/deactivate")
    assert r.status_code == 403

def test_deactivate_self(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/admin/deactivate")
    assert r.status_code == 400

def test_deactivate_user_not_found(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.put("/api/admin/user/nonexistent/deactivate")
    assert r.status_code == 404

def test_delete_user(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    target = make_user(user_id=2, username="target")
    session.add(admin)
    session.add(target)
    session.commit()

    client = client_factory(user=admin)
    r = client.delete("/api/admin/user/target/delete")
    assert r.status_code == 200
    deleted = session.get(tblUser, 2)
    assert deleted is None

def test_delete_user_not_admin(client_factory, session):
    user = make_user(user_id=1, username="user")
    target = make_user(user_id=2, username="target")
    session.add(user)
    session.add(target)
    session.commit()

    client = client_factory(user=user)
    r = client.delete("/api/admin/user/target/delete")
    assert r.status_code == 403

def test_delete_user_self(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.delete("/api/admin/user/admin/delete")
    assert r.status_code == 400

def test_delete_user_not_found(client_factory, session):
    admin = make_user(user_id=1, username="admin", admin=True)
    session.add(admin)
    session.commit()

    client = client_factory(user=admin)
    r = client.delete("/api/admin/user/nonexistent/delete")
    assert r.status_code == 404

def test_delete_not_authenticated(client_factory, session):
    target = make_user(user_id=2, username="target")
    session.add(target)
    session.commit()

    client = client_factory()
    r = client.delete("/api/admin/user/target/delete")
    assert r.status_code == 401