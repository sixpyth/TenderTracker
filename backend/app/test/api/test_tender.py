import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
from app.main import app
from app.core.config import settings
from app.enums import TenderStatus

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
class TestTenderAPI:
    async def test_tender_lifecycle(self, test_client):
        client = test_client
        # 1. Login as admin/superuser
        credentials = {
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        login_resp = await client.post("/login", json=credentials)
        assert login_resp.status_code == 200
        token = extract_token(login_resp.json()["data"])
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Tender
        create_payload = {
            "title": "Тестовый тендер на поставку оборудования",
            "description": "Закупка 100 серверов для ЦОД",
            "status": "draft",
        }
        create_resp = await client.post("/tender", json=create_payload, headers=headers)
        assert create_resp.status_code == 200
        tender_data = create_resp.json()["data"]
        tender_id = tender_data["id"]
        assert tender_data["title"] == create_payload["title"]
        assert tender_data["status"] == TenderStatus.DRAFT.value

        # 3. Get Tender by ID (includes history)
        get_resp = await client.get(f"/tender/{tender_id}", headers=headers)
        assert get_resp.status_code == 200
        get_data = get_resp.json()["data"]
        assert len(get_data["status_history"]) == 1
        first_history = get_data["status_history"][0]
        assert first_history["old_status"] is None
        assert first_history["new_status"] == TenderStatus.DRAFT.value
        assert first_history["reason"] == "Тендер создан"

        # 4. Change status to ACTIVE
        patch_payload_1 = {
            "new_status": "active",
            "reason": "Тендер опубликован и открыт для заявок",
        }
        patch_resp_1 = await client.patch(
            f"/tender/{tender_id}/status", json=patch_payload_1, headers=headers
        )
        assert patch_resp_1.status_code == 200
        assert patch_resp_1.json()["data"]["status"] == TenderStatus.ACTIVE.value

        # 5. Change status to WON
        patch_payload_2 = {
            "new_status": "won",
            "reason": "Подписан контракт с победителем",
        }
        patch_resp_2 = await client.patch(
            f"/tender/{tender_id}/status", json=patch_payload_2, headers=headers
        )
        assert patch_resp_2.status_code == 200
        assert patch_resp_2.json()["data"]["status"] == TenderStatus.WON.value

        # 6. Fetch full status history log
        history_resp = await client.get(f"/tender/{tender_id}/history", headers=headers)
        assert history_resp.status_code == 200
        history_list = history_resp.json()["data"]
        assert len(history_list) == 3

        # Check history entries details
        assert history_list[0]["old_status"] is None
        assert history_list[0]["new_status"] == TenderStatus.DRAFT.value

        assert history_list[1]["old_status"] == TenderStatus.DRAFT.value
        assert history_list[1]["new_status"] == TenderStatus.ACTIVE.value
        assert history_list[1]["reason"] == patch_payload_1["reason"]

        assert history_list[2]["old_status"] == TenderStatus.ACTIVE.value
        assert history_list[2]["new_status"] == TenderStatus.WON.value
        assert history_list[2]["reason"] == patch_payload_2["reason"]
