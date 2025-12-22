import pytest
import respx

from neo4j_aura_sdk import AuraClient, models

clientId = "mockId"
clientSecret = "mockSecret"
baseUrl = "https://api.neo4j.io/"


@respx.mock
@pytest.mark.asyncio
async def test_v2_guard_raises():
    # default client is v1; v2 methods should raise ValueError before any network call
    async with AuraClient(clientId, clientSecret) as client:
        with pytest.raises(ValueError):
            await client.list_organization_ip_filters("org-id")


@respx.mock
@pytest.mark.asyncio
async def test_list_organization_ip_filters_v2():
    # Mock token
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    ip_filters = [
        {
            "id": "123",
            "name": "My IP filter",
            "organization_id": "org1",
            "allow_list": [
                {"address": "192.168.1.1", "prefix_len": 24, "description": "Office"}
            ],
            "filtering_disabled": False,
            "filtered_entities": {
                "instances": ["inst1"],
                "projects": [],
                "organizations": [],
            },
            "updated_at": "2025-11-14T00:00:00Z",
        }
    ]

    respx.get(f"{baseUrl}v2beta1/organizations/org1/ip-filters").respond(
        status_code=200, json=ip_filters
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_organization_ip_filters("org1")
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert resp[0].id == "123"


@respx.mock
@pytest.mark.asyncio
async def test_create_import_job_v2():
    # Mock token
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/org1/projects/proj1/import/jobs"
    ).respond(status_code=200, json={"data": {"id": "job-1"}})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.CreateImportJobRequest(importModelId="model-1")
        resp = await client.create_import_job("org1", "proj1", req)
        assert resp.data["id"] == "job-1"
