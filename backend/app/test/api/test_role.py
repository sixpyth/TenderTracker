import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
from app.main import app
from app.core.config import settings

url = "http://fastapi.localhost/api/v1"


@pytest.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=url) as client:
        yield client


def extract_token(login_resp_data) -> str:
    if isinstance(login_resp_data, str):
        return login_resp_data
    return login_resp_data.get("access_token", "")


@pytest.mark.asyncio
class TestRoleAPI:
    async def test_get_roles(self, test_client):
        client = test_client
        credentials = {
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        response = await client.post("/login", json=credentials)
        assert response.status_code == 200
        token = extract_token(response.json()["data"])
        headers = {"Authorization": f"Bearer {token}"}

        roles_resp = await client.get("/role", headers=headers)
        assert roles_resp.status_code == 200
        data = roles_resp.json()["data"]
        assert "items" in data
        assert len(data["items"]) >= 1
