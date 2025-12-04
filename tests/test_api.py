from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import pytest
from src.main import app
from src.database import Base, get_db
from src import database 
from src import main

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
main.engine = test_engine
database.engine = test_engine

mock_redis = MagicMock()
mock_redis.get.return_value = None
main.redis_client = mock_redis

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# --- TESTS ---

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200

def test_create_url(client):
    payload = {"target_url": "https://www.google.com", "custom_key": "testlink"}
    response = client.post("/url", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "testlink"

def test_create_duplicate_url(client):
    payload = {"target_url": "https://www.google.com", "custom_key": "testlink"}
    response = client.post("/url", json=payload)
    assert response.status_code == 400

def test_redirect(client):
    response = client.get("/testlink", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://www.google.com/"