import pytest
from httpx import AsyncClient
from app.main import app
from typing import AsyncGenerator
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
class TestUserAPI:
    @pytest.mark.parametrize(
        "method, endpoint, data, expected_status, expected_response",
        [
            ("get", "/user", None, 200, None),
            ("get", "/user/list", None, 200, None),
            (
                "get",
                "/user/list/by_role_name?user_status=active&page=1&size=50",
                None,
                200,
                None,
            ),
        ],
    )
    async def test(
        self, test_client, method, endpoint, data, expected_status, expected_response
    ):
        client = test_client
        credentials = {
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        response = await client.post("/login", json=credentials)
        token = extract_token(response.json()["data"])
        headers = {"Authorization": f"Bearer {token}"}
        if method == "get":
            response = await client.get(endpoint, headers=headers)
        elif method == "put":
            response = await client.put(endpoint, json=data, headers=headers)
        elif method == "delete":
            response = await client.delete(endpoint, headers=headers)
        else:
            response = await client.post(endpoint, json=data, headers=headers)

        assert response.status_code == expected_status
        if expected_response is not None:
            assert response.json() == expected_response
