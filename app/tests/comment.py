import io

import pytest
from PIL import Image
from starlette.testclient import TestClient
from app.schemas.auth import AuthResponse

@pytest.fixture
def comment_payload():
    return {"content": "Ceci est un commentaire de test."}


@pytest.fixture
def created_comment(client: TestClient, created_post: dict, auth_headers: dict, comment_payload: dict):
    response = client.put(f"/comment/{created_post['id']}", json=comment_payload, headers=auth_headers)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(name="user_data")
def user_data() -> dict[str, str]:
    return {
        "username": "testuser",
        "email": "testultra@example.com",
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

@pytest.fixture(name="picture")
def fake_image_file(filename="test.png"):
    file = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="white")
    image.save(file, "JPEG")
    file.seek(0)
    return {
        "file": (filename, file, "image/jpeg")
    }

@pytest.fixture
def created_post(client: TestClient, auth_headers: dict, post_data: dict):
    response = client.post("/post/upload", json=post_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()



def test_comment_post(client: TestClient, created_post: dict, comment_payload: dict, auth_headers: dict):
    response = client.put(f"/comment/{created_post['id']}", json=comment_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == created_post["id"]
    assert data["content"] == comment_payload["content"]
    assert "id" in data
    assert "created_at" in data


def test_comment_post_not_found(client: TestClient, comment_payload: dict, auth_headers: dict):
    response = client.put("/comment/00000000-0000-0000-0000-000000000000", json=comment_payload, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_comment_too_long(client: TestClient, created_post: dict, auth_headers: dict):
    payload = {"content": "x" * 1001}
    response = client.put(f"/comment/{created_post['id']}", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Comment too long"


def test_get_post_comments(client: TestClient, created_post: dict, created_comment: dict, auth_headers: dict):
    response = client.get(f"/comment/{created_post['id']}/contents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["count"] == 1
    assert data["content"][0]["content"] == created_comment["content"]


def test_get_all_user_comments(client: TestClient, created_comment: dict, auth_headers: dict):
    response = client.get("/comment/all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["count"] >= 1
    assert any(c["id"] == created_comment["id"] for c in data["content"])


def test_delete_comment_success(client: TestClient, created_comment: dict, auth_headers: dict):
    response = client.delete(f"/comment/delete/{created_comment['id']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Comment deleted"
    assert data["comment_id"] == created_comment["id"]


def test_delete_comment_not_found(client: TestClient, auth_headers: dict):
    response = client.delete("/comment/delete/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_unauthorized(client: TestClient, created_comment: dict, user_data: dict, client_data: dict):
    # Register et login un autre utilisateur
    client.post("/auth/register", json=client_data)
    login = client.post("/auth/login", json={
        "username": client_data["username"],
        "password": client_data["password"]
    })
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Essaye de supprimer un commentaire qu'il n'a pas écrit
    response = client.delete(f"/comment/delete/{created_comment['id']}", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized to delete"
