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

@pytest.fixture
def post_data():
    return {
        "title": "Mon post à liker",
        "content": "Contenu pour test like",
    }


@pytest.fixture
def created_post(client: TestClient, auth_headers: dict, post_data: dict):
    response = client.post("/post/upload", json=post_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()


def test_like_post(client: TestClient, auth_headers: dict, created_post: dict):
    response = client.put(f"/like/{created_post['id']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == created_post["id"]
    assert "like_id" in data
    assert "created_at" in data


def test_like_post_twice_should_fail(client: TestClient, auth_headers: dict, created_post: dict):
    client.put(f"/like/{created_post['id']}", headers=auth_headers)
    response = client.put(f"/like/{created_post['id']}", headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "You have already liked this post"


def test_unlike_post(client: TestClient, auth_headers: dict, created_post: dict):
    # Liker d'abord
    client.put(f"/like/{created_post['id']}", headers=auth_headers)
    # Ensuite unliker
    response = client.delete(f"/like/{created_post['id']}/unlike", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["post_id_attached"] == created_post["id"]
    assert "like_id_removed" in data
    assert "user_id_from_like" in data


def test_get_liked_posts_by_user(client: TestClient, auth_headers: dict, authenticated_user: AuthResponse, created_post: dict):
    client.put(f"/like/{created_post['id']}", headers=auth_headers)

    response = client.get(f"/like/liked-posts/{authenticated_user.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["post_id"] == created_post["id"] for p in data)


def test_get_post_likes(client: TestClient, auth_headers: dict, created_post: dict):
    client.put(f"/like/{created_post['id']}", headers=auth_headers)

    response = client.get(f"/like/get-likes/{created_post['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == created_post["id"]
    assert data["likes_count"] == 1
    assert isinstance(data["users"], list)
    assert len(data["users"]) == 1
    assert "username" in data["users"][0]
