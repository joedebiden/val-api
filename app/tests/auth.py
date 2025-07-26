import pytest
from starlette.testclient import TestClient

from app.schemas.auth import AuthResponse


@pytest.fixture(name="user_data")
def user_data() -> dict[str, str]:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "supermegapassword"
    }

@pytest.fixture(name="second_user_data")
def second_user_data() -> dict[str, str]:
    return {
        "username": "seconduser",
        "email": "second@example.com",
        "password": "anothersecurepassword"
    }

@pytest.fixture(name="registered_user")
def registered_user(client: TestClient, user_data: dict[str, str]) -> dict[str, str]:
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 200
    return user_data


@pytest.fixture(name="authenticated_user")
def authenticated_user(client: TestClient, registered_user: dict[str, str]) -> AuthResponse:
    response = client.post("/auth/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })

    assert response.status_code == 200
    assert "token" in response.json()
    return AuthResponse(**response.json())


@pytest.fixture(name="auth_token")
def auth_token(authenticated_user: AuthResponse) -> str:
    """Fixture qui retourne uniquement le token d'authentification."""
    return authenticated_user.token


@pytest.fixture(name="auth_headers")
def auth_headers(auth_token: str) -> dict[str, str]:
    """Fixture qui retourne les headers d'authentification prets à utiliser."""
    return {"Authorization": f"Bearer {auth_token}"}



def test_user_registration(client: TestClient, user_data: dict[str, str]):
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "account created successfully."}


def test_user_login(client: TestClient, registered_user: dict[str, str]):
    response = client.post("/auth/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })

    assert response.status_code == 200
    assert "token" in response.json()

    auth_response = AuthResponse(**response.json())
    assert auth_response.token
    assert len(auth_response.token) > 0


def test_token_validation(client: TestClient, auth_token: str):
    response = client.post("/auth/token", json={"token": auth_token})
    assert response.status_code == 200
    assert response.json() == {"valid": True}
