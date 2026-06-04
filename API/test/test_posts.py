import pytest
from .conftest import make_user
from ..models import CategoryType, tblUsersText, categories
from sqlmodel import select

@pytest.mark.parametrize("category", list(CategoryType))
def test_post_activity(client_factory, category):
    user = make_user()
    client = client_factory(user=user)
    r = client.post("/api/posts/activity", params={"text": "test post", "category": category.value})
    assert r.status_code == 200
    assert r.json() == {"details": "OK"}

@pytest.mark.parametrize("category", list(CategoryType))
def test_post_activity_not_authenticated(client_factory, category):
    client = client_factory()
    r = client.post("/api/posts/activity", params={"text": "test post", "category": category.value})
    assert r.status_code == 401

def test_post_activity_no_text(client_factory):
    user = make_user()
    client = client_factory(user=user)
    r = client.post("/api/posts/activity", params={"category": CategoryType.leisure.value})
    assert r.status_code == 422

def test_post_activity_invalid_category(client_factory):
    user = make_user()
    client = client_factory(user=user)
    r = client.post("/api/posts/activity", params={"text": "x", "category": "invalid"})
    assert r.status_code == 422


def test_get_activity(client_factory, session):
    user = make_user()
    client = client_factory(user=user)
    for i in range(6):
        session.add(tblUsersText(Text=f"post {i}", Activity=categories[CategoryType.leisure], Author=user.UserId))
    session.commit()

    r = client.get(f"/api/posts/{CategoryType.leisure.value}")
    assert r.status_code == 200
    assert len(r.json()) == 5

def test_get_activity_page2(client_factory, session):
    user = make_user()
    client = client_factory(user=user)
    for i in range(6):
        session.add(tblUsersText(Text=f"post {i}", Activity=categories[CategoryType.leisure], Author=user.UserId))
    session.commit()

    r = client.get(f"/api/posts/{CategoryType.leisure.value}", params={"page": 2})
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_get_activity_empty(client_factory):
    user = make_user()
    client = client_factory(user=user)
    r = client.get(f"/api/posts/{CategoryType.leisure.value}")
    assert r.status_code == 200
    assert r.json() == []

def test_get_activity_not_authenticated(client_factory):
    client = client_factory()
    r = client.get(f"/api/posts/{CategoryType.leisure.value}")
    assert r.status_code == 401

def test_get_activity_invalid_category(client_factory):
    user = make_user()
    client = client_factory(user=user)
    r = client.get("/api/posts/invalid_category")
    assert r.status_code == 422

def test_get_activity_invalid_page(client_factory):
    user = make_user()
    client = client_factory(user=user)
    r = client.get(f"/api/posts/{CategoryType.leisure.value}", params={"page": 0})
    assert r.status_code == 422

def test_delete_posts(client_factory, session):
    user = make_user()
    client = client_factory(user=user)
    for i in range(3):
        session.add(tblUsersText(Text=f"post {i}", Activity=categories[CategoryType.leisure], Author=user.UserId))
    session.commit()

    r = client.delete("/api/posts/")
    assert r.status_code == 200
    assert r.json() == {"details": "Deleted."}
    remaining = session.exec(select(tblUsersText).where(tblUsersText.Author == user.UserId)).all()
    assert remaining == []

def test_delete_posts_only_own(client_factory, session):
    user = make_user(user_id=1, username="user")
    other = make_user(user_id=2, username="other")
    session.add(user)
    session.add(other)
    for i in range(2):
        session.add(tblUsersText(Text=f"post {i}", Activity=categories[CategoryType.leisure], Author=user.UserId))
        session.add(tblUsersText(Text=f"post {i}", Activity=categories[CategoryType.leisure], Author=other.UserId))
    session.commit()

    client = client_factory(user=user)
    client.delete("/api/posts/")

    other_posts = session.exec(select(tblUsersText).where(tblUsersText.Author == other.UserId)).all()
    assert len(other_posts) == 2

def test_delete_posts_not_authenticated(client_factory):
    client = client_factory()
    r = client.delete("/api/posts/")
    assert r.status_code == 401