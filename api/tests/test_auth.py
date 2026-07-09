import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import engine
from app.models.base import Base


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register(client):
    res = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "secret123",
        "name": "Test User",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/auth/register", json={
        "email": "dup@example.com", "password": "secret123", "name": "Dup",
    })
    res = await client.post("/auth/register", json={
        "email": "dup@example.com", "password": "secret123", "name": "Dup",
    })
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={
        "email": "login@example.com", "password": "secret123", "name": "Login",
    })
    res = await client.post("/auth/login", json={
        "email": "login@example.com", "password": "secret123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wrong@example.com", "password": "secret123", "name": "Wrong",
    })
    res = await client.post("/auth/login", json={
        "email": "wrong@example.com", "password": "wrongpass",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client):
    reg = await client.post("/auth/register", json={
        "email": "refresh@example.com", "password": "secret123", "name": "Refresh",
    })
    refresh_token = reg.json()["refresh_token"]
    res = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
