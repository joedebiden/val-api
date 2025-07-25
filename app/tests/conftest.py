import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Base
from app.main import app


@pytest.fixture(name="session_db")
def get_db_test():
    testing_engine = create_engine(settings.DATABASE_URL_TEST)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=testing_engine)
    # init de la db test
    Base.metadata.drop_all(bind=testing_engine)
    Base.metadata.create_all(bind=testing_engine)
    db_test = testing_session_local()
    try:
        yield db_test
    finally:
        db_test.close()

@pytest.fixture(name="client")
def client_fixture(session_db: Session):
    def get_session_override():
        return session_db
    app.dependency_overrides[get_db] = get_session_override # Override de la FONCTION de dépendance pas d'une instance (oui)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


