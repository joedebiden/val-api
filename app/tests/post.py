import io

import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.schemas.auth import AuthResponse
from app.schemas.post import FeedResponse, PostDetailResponse, FeedDetailResponse


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


def test_upload_post(client: TestClient, auth_headers: dict[str, str], picture):
    response = client.post(
        "/post/upload",
        headers=auth_headers,
        data={"caption": "My caption"},
        files=picture
    )
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert "caption" in data


def test_global_feed(client: TestClient, auth_headers: dict):
    response = client.get("/post/feed/global", headers=auth_headers)
    assert response.status_code == 200
    feed = FeedResponse(**response.json())
    assert isinstance(feed.content, list)


def test_edit_post_caption(client: TestClient, auth_headers: dict, picture):
    # Upload post first
    upload_response = client.post(
        "/post/upload",
        headers=auth_headers,
        data={"caption": "Before edit"},
        files=picture
    )
    assert upload_response.status_code == 200
    post_id = upload_response.json()["id"]

    # Edit caption
    edit_response = client.post(
        f"/post/edit/{post_id}",
        headers=auth_headers,
        json={"caption": "After edit", "hidden_tag": False}
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["caption"] == "After edit"


def test_delete_post(client: TestClient, auth_headers: dict, picture):
    # Upload post first
    upload_response = client.post(
        "/post/upload",
        headers=auth_headers,
        data={"caption": "To delete"},
        files=picture
    )
    post_id = upload_response.json()["id"]

    # Delete it
    delete_response = client.delete(f"/post/delete/{post_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Post deleted successfully"

    # Try to fetch it
    get_response = client.get(f"/post/{post_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_personal_feed(client: TestClient, auth_headers: dict):
    response = client.get("/post/feed", headers=auth_headers)
    assert response.status_code == 200
    data = FeedResponse(**response.json())
    assert isinstance(data.content, list)


def test_user_feed(client: TestClient, auth_headers: dict, registered_user: dict, picture):
    username = registered_user["username"]

    # Upload a post first
    client.post(
        "/post/upload",
        headers=auth_headers,
        data={"caption": "user_feed"},
        files=picture
    )

    response = client.get(f"/post/feed/{username}", headers=auth_headers)
    assert response.status_code == 200
    data = FeedDetailResponse(**response.json())
    assert isinstance(data.content, list)


def test_post_details(client: TestClient, auth_headers: dict, picture):
    # Upload post
    upload_response = client.post(
        "/post/upload",
        headers=auth_headers,
        data={"caption": "Details"},
        files=picture
    )
    post_id = upload_response.json()["id"]

    response = client.get(f"/post/{post_id}", headers=auth_headers)
    assert response.status_code == 200
    detail = PostDetailResponse(**response.json())
    assert str(detail.post.id) == post_id
    assert isinstance(detail.likes, dict)
    assert isinstance(detail.comments, dict)
