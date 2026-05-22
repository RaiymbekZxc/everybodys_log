
import pytest 

from ..main import app
from ..models import tblUser, CategoryType, tblCategory
from ..database import get_session
from ..auth import get_current_user

from fastapi.testclient import TestClient

from sqlmodel import SQLModel, Session, create_engine, StaticPool

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for category in CategoryType:
            session.add(tblCategory(Name=category.value, PeopleClicked=0))
        session.commit()
        yield session

def make_user(user_id: int = 1, username: str = "user"):
    return tblUser(
        UserId=user_id,
        Username=username,
        hashed_password="fake_hash"
    )

@pytest.fixture
def client_factory(session):
    def _make_client(user=None):
        def override_get_session():
            return session

        app.dependency_overrides[get_session] = override_get_session

        if user is not None:
            def override_get_current_user():
                return user
            app.dependency_overrides[get_current_user] = override_get_current_user

        return TestClient(app)

    yield _make_client
    app.dependency_overrides.clear()

