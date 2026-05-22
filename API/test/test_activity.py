
from ..models import CategoryType, tblCategory
import pytest
from sqlmodel import select
from .conftest import make_user

@pytest.mark.parametrize("category", [
    CategoryType.leisure,
    CategoryType.social_life,
    CategoryType.productivity
])
def test_post_activity(client_factory, category):
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    response = client.post(f"/api/activity/{category.value}")
    assert response.status_code == 200

@pytest.mark.parametrize("category", [
    CategoryType.leisure,
    CategoryType.social_life,
    CategoryType.productivity
])
def test_post_activity_not_authenticated(client_factory, category):
    client = client_factory()
    response = client.post(f"/api/activity/{category.value}")
    assert response.status_code == 401

def test_post_activity_none(client_factory):
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    response = client.post("/api/activity")
    assert response.status_code == 404

def test_post_activity_invalid(client_factory):
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    response = client.post("/api/activity/gibberish")
    assert response.status_code == 422

def test_get_activity(client_factory):
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    response = client.get("/api/activity/info")
    data = response.json()
    assert response.status_code == 200 
    assert data["timestamp"] is not None
    assert data["leisure"]["percentage"] == 0

def test_get_activity_not_authenticated(client_factory):
    client = client_factory()
    response = client.get("/api/activity/info")
    assert response.status_code == 401

def test_clicks(client_factory, session):
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    client.post(f"/api/activity/{CategoryType.leisure.value}")
    cat = session.exec(select(tblCategory).where(tblCategory.Name==CategoryType.leisure.value)).first()
    assert cat.PeopleClicked == 1

def test_get_activity_percentage(client_factory, session):
    social = session.exec(select(tblCategory).where(tblCategory.Name==CategoryType.social_life.value)).first()
    leisure = session.exec(select(tblCategory).where(tblCategory.Name==CategoryType.leisure.value)).first()
    prod = session.exec(select(tblCategory).where(tblCategory.Name==CategoryType.productivity.value)).first()

    assert social.PeopleClicked == 0
    assert leisure.PeopleClicked == 0
    assert prod.PeopleClicked == 0

    social.PeopleClicked = 10
    leisure.PeopleClicked = 20
    prod.PeopleClicked = 70
    client = client_factory(
        user=make_user(1, "raiymbekzmt")
    )
    response = client.get("/api/activity/info")
    data = response.json()

    assert response.status_code == 200
    assert data["social_life"]["percentage"] == 10
    assert data["leisure"]["percentage"] == 20
    assert data["productivity"]["percentage"] == 70
    
