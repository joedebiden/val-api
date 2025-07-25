import io
from uuid import UUID
from PIL import Image

# Helpers
def register_and_login(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    res = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    token = res.json()["token"]
    user_id = res.json()["user_id"]
    return token, user_id

def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}

# --- TESTS ---

def test_get_own_profile(client):
    token, _ = register_and_login(client)
    response = client.get("/user/profile", headers=auth_header(token))

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert UUID(data["id"])
    assert "email" in data


def test_edit_profile_success(client):
    token, _ = register_and_login(client)

    payload = {
        "username": "newname",
        "email": "normal@email.com",
        "bio": "my updated bio",
        "website": "https://test.com",
        "gender": "other"
    }

    response = client.post("/user/edit", headers=auth_header(token), json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newname"
    assert data["bio"] == "my updated bio"
    assert data["website"] == "https://test.com"


def test_upload_profile_picture(client):
    token, _ = register_and_login(client)

    file = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="red")
    image.save(file, "JPEG")
    file.name = "profile.jpg"
    file.seek(0)

    response = client.post(
        "/user/upload-profile-picture",
        headers=auth_header(token),
        files={"file": ("profile.jpg", file, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "file_url" in data
    assert data["message"] == "File uploaded successfully"


def test_get_profile_by_username(client):
    token, _ = register_and_login(client)

    response = client.get("/user/profile/testuser", headers=auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_get_profile_by_username_not_found(client):
    token, _ = register_and_login(client)

    response = client.get("/user/profile/unknownuser", headers=auth_header(token))
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_search_users_found(client):
    token, _ = register_and_login(client)

    response = client.get("/user/search/test", headers=auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Users found"
    assert isinstance(data["users"], list)
    assert any(u["username"] == "testuser" for u in data["users"])


def test_search_users_not_found(client):
    token, _ = register_and_login(client)

    response = client.get("/user/search/nouserhere", headers=auth_header(token))
    assert response.status_code == 404
    assert response.json()["detail"] == "No user found"
