import os
import tempfile

# Use a temporary SQLite database for the tests
fd, db_path = tempfile.mkstemp(prefix="test_", suffix=".db")
os.close(fd)
os.environ["SQLMODEL_DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["SECRET_KEY"] = "test_secret"

from fastapi.testclient import TestClient
from app.database import init_db
from app.main import app

# Initialize tables
init_db()

client = TestClient(app)

USER_DATA = {"email": "user@example.com", "username": "user", "password": "pass"}


def register_and_login():
    client.post("/auth/register", json=USER_DATA)
    response = client.post("/auth/login", json=USER_DATA)
    assert response.status_code == 200


def test_user_flow():
    register_and_login()
    resp = client.get("/me/")
    assert resp.status_code == 200
    assert resp.json()["email"] == USER_DATA["email"]


def test_album_and_image_flow():
    register_and_login()
    album_resp = client.post("/me/albums/new_album", json={"title": "Album"})
    assert album_resp.status_code == 200
    album_id = album_resp.json()["id"]

    image_resp = client.post(
        f"/me/albums/{album_id}/images/create",
        json={"title": "Img", "description": "desc", "image_path": "path"},
    )
    assert image_resp.status_code == 200
    image_id = image_resp.json()["id"]

    resp = client.get(f"/me/albums/{album_id}/images/{image_id}")
    assert resp.status_code == 200

    resp = client.get(f"/chats/{image_id}")
    assert resp.status_code == 200
    chat_id = resp.json()["id"]

    msg_resp = client.post(
        f"/chats/{chat_id}/messages",
        json={"chat_id": chat_id, "content": "hi"},
    )
    assert msg_resp.status_code == 200
    resp = client.get(f"/chats/{chat_id}/messages")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
