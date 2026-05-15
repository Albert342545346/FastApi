import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app.user_api import app, db


@pytest.fixture(autouse=True)
def isolate_state():
    db.clear()
    yield
    db.clear()

faker = Faker()

@pytest.mark.asyncio
class TestUserEndpoints:
    async def test_create_user(self):
        payload = {"username": faker.user_name(), "age": faker.random_int(min=18, max=60)}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/users", json=payload)
            assert res.status_code == 201
            data = res.json()
            assert data["username"] == payload["username"]
            assert data["age"] == payload["age"]
            assert "id" in data

    async def test_get_existing_user(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            create_res = await ac.post("/users", json={"username": "alice", "age": 25})
            user_id = create_res.json()["id"]
            get_res = await ac.get(f"/users/{user_id}")
            assert get_res.status_code == 200
            assert get_res.json()["username"] == "alice"

    async def test_get_non_existing_user(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/users/9999")
            assert res.status_code == 404
            assert res.json()["detail"] == "User not found"

    async def test_delete_existing_user(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            create_res = await ac.post("/users", json={"username": "bob", "age": 30})
            user_id = create_res.json()["id"]
            del_res = await ac.delete(f"/users/{user_id}")
            assert del_res.status_code == 204
            check_res = await ac.get(f"/users/{user_id}")
            assert check_res.status_code == 404

    async def test_delete_non_existing_user(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.delete("/users/9999")
            assert res.status_code == 404
            assert res.json()["detail"] == "User not found"