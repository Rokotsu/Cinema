# tests/unit_tests/test_api.py

import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.api.main import app


@pytest.mark.asyncio
async def test_create_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_data = {
            "email": "test_api@example.com",
            "username": "testapi",
            "password": "secret123"
        }
        response = await client.post("/users/", json=user_data)
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_login_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Сначала создаем пользователя для логина
        user_data = {
            "email": "login_api@example.com",
            "username": "loginapi",
            "password": "secret123"
        }
        create_resp = await client.post("/users/", json=user_data)
        assert create_resp.status_code == 201, create_resp.text

        # Теперь выполняем логин; в ручке login ожидаются только поля username и password.
        login_data = {
            "username": "loginapi",
            "password": "secret123"
        }
        login_resp = await client.post("/users/login", json=login_data)
        assert login_resp.status_code == 200, login_resp.text
        data = login_resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_data = {
            "email": "getuser_api@example.com",
            "username": "getuserapi",
            "password": "secret123"
        }
        create_resp = await client.post("/users/", json=user_data)
        assert create_resp.status_code == 201, create_resp.text
        user_id = create_resp.json()["id"]
        resp = await client.get(f"/users/{user_id}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_update_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_data = {
            "email": "updateuser_api@example.com",
            "username": "updateuserapi",
            "password": "secret123"
        }
        create_resp = await client.post("/users/", json=user_data)
        assert create_resp.status_code == 201, create_resp.text
        user_id = create_resp.json()["id"]
        update_data = {"email": "updated_api@example.com"}
        resp = await client.put(f"/users/{user_id}", json=update_data)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == "updated_api@example.com"


@pytest.mark.asyncio
async def test_create_movie():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        movie_data = {
            "title": "Test Movie",
            "description": "A test movie",
            "duration": 120,
            "rating": 7.5
        }
        resp = await client.post("/movies/", json=movie_data)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["title"] == movie_data["title"]


@pytest.mark.asyncio
async def test_update_movie():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        movie_data = {
            "title": "Another Test Movie",
            "description": "Another test movie",
            "duration": 100,
            "rating": 6.5
        }
        create_resp = await client.post("/movies/", json=movie_data)
        assert create_resp.status_code == 201, create_resp.text
        movie_id = create_resp.json()["id"]
        update_data = {"title": "Updated Test Movie", "rating": 8.0}
        resp = await client.put(f"/movies/{movie_id}", json=update_data)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "Updated Test Movie"


@pytest.mark.asyncio
async def test_create_subscription_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Если не передан токен, ожидается 401 Unauthorized
        sub_data = {
            "user_id": 0,  # в конечном итоге это будет заменено, но при прямой отправке, может вызвать ошибку
            "plan": "Premium"
        }
        resp = await client.post("/subscriptions/", json=sub_data)
        assert resp.status_code == 401
