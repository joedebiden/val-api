import pytest
from starlette.testclient import TestClient

from app.schemas.auth import AuthResponse


@pytest.fixture(name="user_data")
def user_data() -> dict[str, str]:
    return {
        "username": "testfollowuser",
        "email": "testfollow@example.com",
        "password": "supermegapasswordyipi"
    }

@pytest.fixture(name="client_data")
def client_data() -> dict[str, str]:
    return {
        "username": "testfollowclient",
        "email": "clientfollow@example.com",
        "password": "supermegapasswordyipi"
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


def test_follow_user(client: TestClient, auth_headers: dict[str, str], user_data, client_data):
    register_client = client.post("/auth/register", json=client_data)
    assert register_client.status_code == 200

    response = client.put(f"/follow/{client_data["username"]}", headers=auth_headers) # headers du user_data qui follow un autre user (client_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"]
    assert data["follow_id"]
    assert data["followed_id"]
    assert data["created_at"]


def test_follow_user_twice_raises(
        client: TestClient,
        auth_headers: dict[str, str],
        client_data: dict[str, str]
):
    client.post("/auth/register", json=client_data)

    # Premier follow
    response1 = client.put(f"/follow/{client_data['username']}", headers=auth_headers)
    assert response1.status_code == 200

    # Deuxième follow => erreur
    response2 = client.put(f"/follow/{client_data['username']}", headers=auth_headers)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Already following"


def test_unfollow_user(
        client: TestClient,
        auth_headers: dict[str, str],
        client_data: dict[str, str]
):
    client.post("/auth/register", json=client_data)
    client.put(f"/follow/{client_data['username']}", headers=auth_headers)

    response = client.put(f"/follow/unfollow/{client_data['username']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Unfollowed successfully"


def test_get_followers(
        client: TestClient,
        auth_headers: dict[str, str],
        registered_user: dict[str, str],
        client_data: dict[str, str]
):
    # Enregistrer client (celui qui va follow)
    client.post("/auth/register", json=client_data)
    login_response = client.post("/auth/login", json={
        "username": client_data["username"],
        "password": client_data["password"]
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # client_data follow registered_user
    client.put(f"/follow/{registered_user['username']}", headers=headers)

    # get followers du registered_user
    response = client.get(f"/follow/get-follow/{registered_user['username']}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["followers"], list)
    assert data["count"] == 1
    assert data["followers"][0]["username"] == client_data["username"]


def test_get_followed(
        client: TestClient,
        auth_headers: dict[str, str],
        client_data: dict[str, str]
):
    # Enregistrer la personne à suivre
    client.post("/auth/register", json=client_data)
    client.put(f"/follow/{client_data['username']}", headers=auth_headers)

    # get followings de l’utilisateur connecté
    response = client.get(f"/follow/get-followed/testfollowuser")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["followed"], list)
    assert data["count"] == 1
    assert data["followed"][0]["username"] == client_data["username"]


def test_remove_follower(
        client: TestClient,
        user_data: dict[str, str],
        client_data: dict[str, str],
        auth_token: str,
        auth_headers: dict[str, str]
):
    # Enregistrer et connecter le follower (client_data)
    client.post("/auth/register", json=client_data)
    login_response = client.post("/auth/login", json={
        "username": client_data["username"],
        "password": client_data["password"]
    })
    assert login_response.status_code == 200
    client_token = login_response.json()["token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # client_data follow user_data
    follow_response = client.put(f"/follow/{user_data['username']}", headers=client_headers)
    assert follow_response.status_code == 200

    # user_data (l'utilisateur suivi) supprime client_data comme follower
    response = client.delete(f"/follow/remove-follower/{client_data['username']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Follower removed successfully"


