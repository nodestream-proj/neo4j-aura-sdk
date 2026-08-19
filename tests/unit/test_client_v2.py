import pytest
import respx
from pydantic import ValidationError

from neo4j_aura_sdk import AuraClient, models

clientId = "mockId"
clientSecret = "mockSecret"
baseUrl = "https://api.neo4j.io/"
org_id = "org1"
proj_id = "proj1"
inst_id = "inst1"
deployment_id = "deploy1"
server_id = "server1"
agent_id = "agent1"


@respx.mock
@pytest.mark.asyncio
async def test_list_organizations():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(f"{baseUrl}v2beta1/organizations").respond(
        status_code=200,
        json={
            "data": [
                {"id": "org1", "name": "MetaCortex"},
                {"id": "org2", "name": "Zion"},
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_organizations()
        assert isinstance(resp, list)
        assert resp[0]["id"] == "org1"
        assert resp[0]["name"] == "MetaCortex"
        assert resp[1]["id"] == "org2"
        assert resp[1]["name"] == "Zion"


@respx.mock
@pytest.mark.asyncio
async def test_v2_guard_raises():
    # default client is v1; v2 methods should raise ValueError before any network call
    async with AuraClient(clientId, clientSecret) as client:
        with pytest.raises(ValueError):
            await client.list_organization_ip_filters("org-id")


# === Organization & Projects Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_get_organization():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}").respond(
        status_code=200,
        json={"data": {"id": org_id, "name": "My Organization"}},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_organization(org_id)
        assert resp.data["id"] == org_id
        assert resp.data["name"] == "My Organization"


@respx.mock
@pytest.mark.asyncio
async def test_list_organization_projects():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/projects").respond(
        status_code=200,
        json={"data": [{"id": proj_id, "name": "My Project"}]},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_organization_projects(org_id)
        assert resp[0]["id"] == proj_id
        assert resp[0]["name"] == "My Project"


# === IP Filter Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_list_organization_ip_filters_v2():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    ip_filters = [
        {
            "id": "filter-123",
            "name": "My IP filter",
            "organization_id": org_id,
            "allow_list": [
                {"address": "192.168.1.1", "prefix_len": 24, "description": "Office"}
            ],
            "filtering_disabled": False,
            "filtered_entities": {
                "instances": [inst_id],
                "projects": [],
                "organizations": [],
            },
            "updated_at": "2025-11-14T00:00:00Z",
        }
    ]

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/ip-filters").respond(
        status_code=200, json=ip_filters
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_organization_ip_filters(org_id)
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert resp[0].id == "filter-123"


@respx.mock
@pytest.mark.asyncio
async def test_create_organization_ip_filter():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    ip_filter = {
        "id": "filter-123",
        "name": "My IP filter",
        "organization_id": org_id,
        "allow_list": [
            {"address": "192.168.1.0", "prefix_len": 24, "description": "Office"}
        ],
        "filtering_disabled": False,
        "filtered_entities": {"instances": [], "projects": [], "organizations": []},
    }

    respx.post(f"{baseUrl}v2beta1/organizations/{org_id}/ip-filters").respond(
        status_code=200, json=ip_filter
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.IpFilter(
            name="My IP filter",
            organization_id=org_id,
            allow_list=[
                models.IpFilterAllowListItem(
                    address="192.168.1.0", prefix_len=24, description="Office"
                )
            ],
        )
        resp = await client.create_organization_ip_filter(org_id, req)
        assert resp.id == "filter-123"


@respx.mock
@pytest.mark.asyncio
async def test_get_organization_ip_filter():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    ip_filter = {
        "id": "filter-123",
        "name": "My IP filter",
        "organization_id": org_id,
        "allow_list": [{"address": "192.168.1.0", "prefix_len": 24}],
        "filtering_disabled": False,
        "filtered_entities": {"instances": [], "projects": [], "organizations": []},
    }

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/ip-filters/filter-123").respond(
        status_code=200, json=ip_filter
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_organization_ip_filter(org_id, "filter-123")
        assert resp.id == "filter-123"
        assert resp.name == "My IP filter"


@respx.mock
@pytest.mark.asyncio
async def test_update_organization_ip_filter():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    updated_filter = {
        "id": "filter-123",
        "name": "Updated Filter",
        "organization_id": org_id,
        "allow_list": [{"address": "10.0.0.0", "prefix_len": 8}],
        "filtering_disabled": False,
        "filtered_entities": {"instances": [], "projects": [], "organizations": []},
    }

    respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/ip-filters/filter-123"
    ).respond(status_code=200, json=updated_filter)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.IpFilter(name="Updated Filter")
        resp = await client.update_organization_ip_filter(org_id, "filter-123", req)
        assert resp.name == "Updated Filter"


@respx.mock
@pytest.mark.asyncio
async def test_delete_organization_ip_filter():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/ip-filters/filter-123"
    ).respond(status_code=204)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.delete_organization_ip_filter(org_id, "filter-123")
        assert resp is None


@respx.mock
@pytest.mark.asyncio
async def test_get_instance_ip_filter_status():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    ip_filter_with_status = {
        "id": "filter-123",
        "name": "My IP filter",
        "organization_id": org_id,
        "allow_list": [{"address": "192.168.1.0", "prefix_len": 24}],
        "filtering_disabled": False,
        "filtered_entities": {"instances": [], "projects": [], "organizations": []},
        "status": "ACTIVE",
    }

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances/{inst_id}/ip-filters"
    ).respond(status_code=200, json=ip_filter_with_status)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_instance_ip_filter_status(org_id, proj_id, inst_id)
        assert resp.status == "ACTIVE"


# === Import Job Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_create_import_job_v2():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/import/jobs"
    ).respond(status_code=200, json={"data": {"id": "job-1"}})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.CreateImportJobRequest(importModelId="model-1")
        resp = await client.create_import_job(org_id, proj_id, req)
        assert resp.data["id"] == "job-1"


@respx.mock
@pytest.mark.asyncio
async def test_get_import_job():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/import/jobs/job-1"
    ).respond(
        status_code=200,
        json={
            "data": {
                "id": "job-1",
                "import_type": "cloud",
                "info": {"state": "Completed", "percentage_complete": 100.0},
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_import_job(org_id, proj_id, "job-1")
        assert resp.data.id == "job-1"
        assert resp.data.info.percentage_complete == 100.0


@respx.mock
@pytest.mark.asyncio
async def test_get_import_job_with_progress():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/import/jobs/job-1",
        params={"progress": "true"},
    ).respond(
        status_code=200,
        json={
            "data": {
                "id": "job-1",
                "import_type": "cloud",
                "info": {
                    "state": "Running",
                    "percentage_complete": 50.0,
                    "progress": {
                        "nodes": [
                            {"id": "n:1", "labels": ["Node1"], "processed_rows": 100}
                        ],
                        "relationships": [],
                    },
                },
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_import_job(org_id, proj_id, "job-1", progress=True)
        assert resp.data.info.progress.nodes[0].id == "n:1"


@respx.mock
@pytest.mark.asyncio
async def test_cancel_import_job():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/import/jobs/job-1/cancellation"
    ).respond(status_code=200, json={"data": {"id": "job-1"}})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.cancel_import_job(org_id, proj_id, "job-1")
        assert resp.data["id"] == "job-1"


# === Deployment Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_list_deployments():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments"
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "id": deployment_id,
                    "name": "My Deployment",
                    "status": "running",
                    "connection_url": "bolt://localhost:7687",
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_deployments(org_id, proj_id)
        assert resp[0].id == deployment_id


@respx.mock
@pytest.mark.asyncio
async def test_create_deployment():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments"
    ).respond(status_code=201, json={"id": deployment_id})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.CreateDeploymentRequest(name="My Deployment")
        resp = await client.create_deployment(org_id, proj_id, req)
        assert resp.id == deployment_id


@respx.mock
@pytest.mark.asyncio
async def test_get_deployment():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}"
    ).respond(
        status_code=200,
        json={
            "data": {
                "id": deployment_id,
                "name": "My Deployment",
                "status": "running",
                "connection_url": "bolt://localhost:7687",
                "dbms": {"edition": "enterprise", "packaging": "docker"},
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_deployment(org_id, proj_id, deployment_id)
        assert resp.data.id == deployment_id
        assert resp.data.dbms.edition == "enterprise"


@respx.mock
@pytest.mark.asyncio
async def test_delete_deployment():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}"
    ).respond(status_code=204)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.delete_deployment(org_id, proj_id, deployment_id)
        assert resp is None


@respx.mock
@pytest.mark.asyncio
async def test_get_deployment_databases():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/databases"
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "node_count": 1000,
                    "relationship_count": 5000,
                    "default": True,
                    "access": "read_write",
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_deployment_databases(org_id, proj_id, deployment_id)
        assert resp.data[0].node_count == 1000


@respx.mock
@pytest.mark.asyncio
async def test_get_deployment_servers():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/servers"
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "address": "192.168.1.1",
                    "name": "server-1",
                    "status": "ONLINE",
                    "version": "5.0.0",
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_deployment_servers(org_id, proj_id, deployment_id)
        assert resp.data[0].name == "server-1"


@respx.mock
@pytest.mark.asyncio
async def test_get_deployment_server_databases():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/servers/{server_id}/databases"
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "name": "neo4j",
                    "role": "PRIMARY",
                    "current_status": "RUNNING",
                    "writer": True,
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_deployment_server_databases(
            org_id, proj_id, deployment_id, server_id
        )
        assert resp.data[0].name == "neo4j"


@respx.mock
@pytest.mark.asyncio
async def test_create_deployment_token():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/token"
    ).respond(status_code=201, json={"token": "deployment-token-abc123"})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.create_deployment_token(org_id, proj_id, deployment_id)
        assert resp.token == "deployment-token-abc123"


@respx.mock
@pytest.mark.asyncio
async def test_update_deployment_token():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/token"
    ).respond(status_code=200, json={"token": "new-deployment-token-xyz789"})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.update_deployment_token(org_id, proj_id, deployment_id)
        assert resp.token == "new-deployment-token-xyz789"


@respx.mock
@pytest.mark.asyncio
async def test_delete_deployment_token():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/fleet-manager/deployments/{deployment_id}/token"
    ).respond(status_code=204)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.delete_deployment_token(org_id, proj_id, deployment_id)
        assert resp is None


# === Activity Feed Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_get_organization_activity_feed():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/activity-feed").respond(
        status_code=200,
        json={
            "data": [
                {
                    "id": "activity-1",
                    "action_name": "CREATE_INSTANCE",
                    "status": "completed",
                    "org_id": org_id,
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_organization_activity_feed(org_id)
        assert resp.data[0].id == "activity-1"
        assert isinstance(resp.data[0], models.ActivityLog)


@respx.mock
@pytest.mark.asyncio
async def test_get_organization_activity_feed_with_filters():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/activity-feed",
        params={"start": "2025-01-01T00:00:00Z", "end": "2025-01-31T23:59:59Z"},
    ).respond(
        status_code=200,
        json={"data": [{"id": "activity-1", "action_name": "CREATE_INSTANCE"}]},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_organization_activity_feed(
            org_id,
            start="2025-01-01T00:00:00Z",
            end="2025-01-31T23:59:59Z",
        )
        assert len(resp.data) == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_project_activity_feed():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/activity-feed"
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "id": "activity-2",
                    "action_name": "UPDATE_INSTANCE",
                    "status": "completed",
                    "project_id": proj_id,
                }
            ]
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_project_activity_feed(org_id, proj_id)
        assert resp.data[0].id == "activity-2"
        assert isinstance(resp.data[0], models.ActivityLog)


@respx.mock
@pytest.mark.asyncio
async def test_get_project_activity_feed_with_filters():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/activity-feed",
        params={
            "start": "2025-02-01T00:00:00Z",
            "end": "2025-02-28T23:59:59Z",
            "page_limit": 50,
        },
    ).respond(
        status_code=200,
        json={"data": [{"id": "activity-3", "action_name": "DELETE_INSTANCE"}]},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_project_activity_feed(
            org_id,
            proj_id,
            start="2025-02-01T00:00:00Z",
            end="2025-02-28T23:59:59Z",
            page_limit=50,
        )
        assert len(resp.data) == 1
        assert resp.data[0].id == "activity-3"


# === Billing Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_get_billing_usage():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    start = "2024-01-01T00:00:00Z"
    end = "2024-01-31T23:59:59Z"

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/billing/usage",
        params={"start": start, "end": end},
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "charge_period_start": "2024-01-01T00:00:00Z",
                    "charge_period_end": "2024-01-31T23:59:59Z",
                    "organization_id": org_id,
                    "project_id": proj_id,
                    "resource_type": "aura-db",
                    "consumed_quantity": 100.5,
                    "list_cost": 250.75,
                }
            ],
            "links": {"self": "/organizations/org1/billing/usage", "next": None},
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_billing_usage(org_id, start, end)
        assert resp.data[0].organization_id == org_id
        assert resp.data[0].project_id == proj_id
        assert resp.data[0].consumed_quantity == 100.5
        assert resp.data[0].list_cost == 250.75
        assert resp.links.self == "/organizations/org1/billing/usage"
        assert isinstance(resp.data[0], models.UsageData)


@respx.mock
@pytest.mark.asyncio
async def test_get_billing_usage_with_project_filter():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    start = "2024-01-01T00:00:00Z"
    end = "2024-01-31T23:59:59Z"
    project_ids = [
        "550e8400-e29b-41d4-a716-446655440000",
        "5f8f4f31-2a8a-4f84-8e4d-89b67c3f67c4",
    ]

    route = respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/billing/usage",
        params={"start": start, "end": end, "project_id": project_ids},
    ).respond(
        status_code=200,
        json={"data": [], "links": {"self": "/organizations/org1/billing/usage"}},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_billing_usage(
            org_id,
            start,
            end,
            project_id=project_ids,
        )
        assert resp.links.self == "/organizations/org1/billing/usage"
        assert route.calls[0].request.url.params.get_list("project_id") == project_ids
        assert str(route.calls[0].request.url).count("project_id=") == 2


@respx.mock
@pytest.mark.asyncio
async def test_get_billing_ledger():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    start = "2024-01-01T00:00:00Z"
    end = "2024-01-31T23:59:59Z"

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/billing/ledger",
        params={"start": start, "end": end},
    ).respond(
        status_code=200,
        json={
            "data": [
                {
                    "organization_id": org_id,
                    "billing_account_id": "ba-123",
                    "balance_date": "2024-01-15T00:00:00Z",
                    "remaining_credit_quantity": 500.0,
                    "initial_credit_quantity": 1000.0,
                }
            ],
            "links": {"self": "/organizations/org1/billing/ledger"},
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_billing_ledger(org_id, start, end)
        assert resp.data[0].organization_id == org_id
        assert resp.data[0].remaining_credit_quantity == 500.0
        assert resp.data[0].initial_credit_quantity == 1000.0
        assert resp.links.self == "/organizations/org1/billing/ledger"
        assert isinstance(resp.data[0], models.LedgerData)


@respx.mock
@pytest.mark.asyncio
async def test_get_billing_ledger_with_pagination_params():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    start = "2024-02-01T00:00:00Z"
    end = "2024-02-29T23:59:59Z"

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/billing/ledger",
        params={
            "start": start,
            "end": end,
            "page_token": "next-token",
            "page_limit": 10,
        },
    ).respond(
        status_code=200,
        json={"data": [], "links": {"self": "/organizations/org1/billing/ledger"}},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_billing_ledger(
            org_id, start, end, page_token="next-token", page_limit=10
        )
        assert resp.links.self == "/organizations/org1/billing/ledger"


# === Agents Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_list_agents():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents"
    ).respond(
        status_code=200,
        json=[
            {
                "id": agent_id,
                "name": "My Agent",
                "description": "An agent that queries the database",
                "dbid": "a1b2c3d4",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "is_private": False,
                "is_mcp_enabled": False,
                "tools": [
                    {
                        "name": "query-tool",
                        "type": "text2cypher",
                        "description": "Converts natural language to Cypher queries",
                        "enabled": True,
                    }
                ],
                "endpoint_link": "https://example.com/agent",
                "avatar_color": "#4C8EDA",
                "avatar_icon": "robot",
                "enabled": True,
            }
        ],
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_agents(org_id, proj_id)
        assert len(resp) == 1
        assert isinstance(resp[0], models.ListAgentResponse)
        assert resp[0].id == agent_id
        assert resp[0].name == "My Agent"
        assert resp[0].created_at == "2025-01-01T00:00:00Z"
        assert resp[0].updated_at == "2025-01-01T00:00:00Z"
        assert resp[0].endpoint_link == "https://example.com/agent"
        assert resp[0].avatar_color == "#4C8EDA"
        assert resp[0].avatar_icon == "robot"


@respx.mock
@pytest.mark.asyncio
async def test_create_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents"
    ).respond(
        status_code=201,
        json={
            "id": agent_id,
            "project_id": proj_id,
            "organization_id": org_id,
            "name": "My Agent",
            "description": "An agent that queries the database",
            "dbid": "a1b2c3d4",
            "tools": [{"name": "query-tool", "type": "text2cypher", "enabled": True}],
            "is_private": False,
            "enabled": True,
        },
    )

    req = models.CreateAgentRequest(
        name="My Agent",
        description="An agent that queries the database",
        dbid="a1b2c3d4",
        is_private=False,
        tools=[models.AgentTool(name="query-tool", type="text2cypher", enabled=True)],
    )
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.create_agent(org_id, proj_id, req)
        assert isinstance(resp, models.AgentDetails)
        assert resp.id == agent_id


@respx.mock
@pytest.mark.asyncio
async def test_get_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}"
    ).respond(
        status_code=200,
        json={
            "id": agent_id,
            "name": "My Agent",
            "description": "An agent that queries the database",
            "dbid": "a1b2c3d4",
            "is_private": False,
            "tools": [{"name": "query-tool", "type": "text2cypher", "enabled": True}],
            "enabled": True,
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.get_agent(org_id, proj_id, agent_id)
        assert isinstance(resp, models.GetAgentResponse)
        assert resp.id == agent_id


@respx.mock
@pytest.mark.asyncio
async def test_update_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.put(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}"
    ).respond(
        status_code=200,
        json={
            "id": agent_id,
            "project_id": proj_id,
            "organization_id": org_id,
            "name": "My Updated Agent",
            "description": "Updated description",
            "dbid": "a1b2c3d4",
            "tools": [{"name": "query-tool", "type": "text2cypher", "enabled": True}],
            "is_private": False,
            "enabled": True,
        },
    )

    req = models.CreateAgentRequest(
        name="My Updated Agent",
        description="Updated description",
        dbid="a1b2c3d4",
        is_private=False,
        tools=[models.AgentTool(name="query-tool", type="text2cypher", enabled=True)],
    )
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.update_agent(org_id, proj_id, agent_id, req)
        assert isinstance(resp, models.AgentDetails)
        assert resp.name == "My Updated Agent"


@respx.mock
@pytest.mark.asyncio
async def test_delete_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}"
    ).respond(status_code=202, json={})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.delete_agent(org_id, proj_id, agent_id)
        assert resp == {}


@respx.mock
@pytest.mark.asyncio
async def test_invoke_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}/invoke"
    ).respond(
        status_code=200,
        json={
            "id": "inv-123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Here are the movies..."}],
            "end_reason": "end_turn",
            "status": "completed",
            "usage": {"request_tokens": 10, "response_tokens": 20, "total_tokens": 30},
        },
    )

    req = models.InvokeAgentRequest(input="What movies are in the database?")
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.invoke_agent(org_id, proj_id, agent_id, req)
        assert isinstance(resp, models.InvokeAgentResponse)
        assert resp.id == "inv-123"
        assert resp.content[0].text == "Here are the movies..."


def test_similarity_search_tool_requires_parameters():
    with pytest.raises(ValidationError):
        models.AgentTool(name="similarity-search", type="similaritySearch")


def test_similarity_search_tool_accepts_parameters():
    tool = models.AgentTool(
        name="similarity-search",
        type="similaritySearch",
        parameters={
            "provider": "openai",
            "model": "text-embedding-3-small",
            "index": "my-index",
            "top_k": 10,
            "dimension": 1536,
        },
    )

    assert isinstance(tool.parameters, models.SimilaritySearchToolParameters)
    assert tool.parameters.provider == "openai"
    assert tool.parameters.model == "text-embedding-3-small"
    assert tool.parameters.index == "my-index"
    assert tool.parameters.top_k == 10
    assert tool.parameters.dimension == 1536


def test_similarity_search_tool_legacy_config_is_normalized():
    tool = models.AgentTool(
        name="similarity-search",
        type="similaritySearch",
        config={
            "provider": "openai",
            "model": "text-embedding-3-small",
            "index": "my-index",
        },
    )

    assert tool.parameters is None
    assert tool.config is not None
    assert tool.config["provider"] == "openai"
    assert tool.config["model"] == "text-embedding-3-small"
    assert tool.config["index"] == "my-index"


def test_similarity_search_tool_config_serializes_as_config():
    tool = models.AgentTool(
        name="similarity-search",
        type="similaritySearch",
        config={
            "provider": "openai",
            "model": "text-embedding-3-small",
            "index": "my-index",
            "dimensions": 1536,
            "top_k": 10,
        },
    )

    payload = tool.model_dump(exclude_none=True)
    assert "config" in payload
    assert "parameters" not in payload
    assert payload["config"]["dimensions"] == 1536
    assert payload["config"]["top_k"] == 10


# === Organization Users Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_list_organization_users():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    users = [
        {
            "user_id": "user1",
            "email": "alice@example.com",
            "organization_roles": ["admin"],
            "exempt_from_automatic_removal": True,
            "mfa_enrollment_status": "enrolled",
            "mfa_enrolled_methods": [
                {"id": "totp", "enrolled_at": "2024-01-01T00:00:00Z"}
            ],
            "last_activity_at": "2024-04-22T10:00:00Z",
        },
        {
            "user_id": "user2",
            "email": "bob@example.com",
            "organization_roles": ["member"],
            "exempt_from_automatic_removal": False,
            "mfa_enrollment_status": "not_enrolled",
            "mfa_enrolled_methods": [],
            "last_activity_at": "2024-04-20T15:30:00Z",
        },
    ]

    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/users").respond(
        status_code=200, json={"data": users}
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_organization_users(org_id)
        assert isinstance(resp, list)
        assert len(resp) == 2
        assert isinstance(resp[0], models.OrganizationUser)
        assert resp[0].user_id == "user1"
        assert resp[0].email == "alice@example.com"
        assert resp[0].organization_roles == ["admin"]
        assert resp[0].mfa_enrollment_status == "enrolled"
        assert len(resp[0].mfa_enrolled_methods) == 1
        assert resp[1].user_id == "user2"
        assert resp[1].email == "bob@example.com"
        assert resp[1].organization_roles == ["member"]


@respx.mock
@pytest.mark.asyncio
async def test_remove_organization_user():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    user_id = "user1"
    respx.delete(f"{baseUrl}v2beta1/organizations/{org_id}/users/{user_id}").respond(
        status_code=204
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.remove_organization_user(org_id, user_id)
        # 204 No Content returns None as default
        assert resp is None


# === Additional v2beta1 Coverage (new JSON spec) ===


@respx.mock
@pytest.mark.asyncio
async def test_patch_organization_user():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    user_id = "user1"
    route = respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/users/{user_id}"
    ).respond(
        status_code=200,
        json={
            "data": {
                "user_id": user_id,
                "email": "alice@example.com",
                "organization_roles": ["organization-member"],
                "exempt_from_automatic_removal": False,
                "mfa_enrollment_status": "not_enrolled",
                "mfa_enrolled_methods": [],
                "last_activity_at": "2026-01-01T00:00:00Z",
                "projects": [],
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.patch_organization_user(org_id, user_id)
        assert isinstance(resp, models.OrganizationUserDetails)
        assert resp.user_id == user_id
        assert route.calls[0].request.content == b""


@respx.mock
@pytest.mark.asyncio
async def test_list_agents_allows_similarity_search_summary_tools():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents"
    ).respond(
        status_code=200,
        json=[
            {
                "id": agent_id,
                "name": "My Agent",
                "tools": [{"name": "sim-search", "type": "similaritySearch"}],
            }
        ],
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.list_agents(org_id, proj_id)
        assert len(resp) == 1
        assert resp[0].tools is not None
        assert resp[0].tools[0].type == "similaritySearch"


@respx.mock
@pytest.mark.asyncio
async def test_add_project_user():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    user_id = "user1"
    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/users"
    ).respond(
        status_code=201,
        json={
            "data": {
                "user_id": user_id,
                "email": "alice@example.com",
                "project_roles": ["namespace-member"],
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        req = models.AddProjectUserRequest(
            user_id=user_id,
            project_roles=["project-member"],
        )
        resp = await client.add_project_user(org_id, proj_id, user_id, req)
        assert isinstance(resp, models.ProjectUser)
        assert resp.user_id == user_id


@respx.mock
@pytest.mark.asyncio
async def test_add_project_user_without_body():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    user_id = "user1"
    route = respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/users"
    ).respond(
        status_code=201,
        json={
            "data": {
                "user_id": user_id,
                "email": "alice@example.com",
                "project_roles": ["namespace-member"],
            }
        },
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.add_project_user(org_id, proj_id, user_id)
        assert isinstance(resp, models.ProjectUser)
        assert resp.user_id == user_id
        assert b'"user_id":"user1"' in route.calls[0].request.content


@respx.mock
@pytest.mark.asyncio
async def test_add_project_user_requires_user_id():
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        with pytest.raises(ValueError):
            await client.add_project_user(org_id, proj_id)


@respx.mock
@pytest.mark.asyncio
async def test_invoke_agent_invocation_api():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agent-invocation/{agent_id}/invoke"
    ).respond(
        status_code=200,
        json={
            "id": "inv-456",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Stream-compatible response"}],
            "end_reason": "end_turn",
            "status": "completed",
        },
    )

    req = models.InvokeAgentRequest(input="hello")
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.invoke_agent_invocation_api(org_id, proj_id, agent_id, req)
        assert isinstance(resp, models.InvokeAgentResponse)
        assert resp.id == "inv-456"


@respx.mock
@pytest.mark.asyncio
async def test_virtual_graph_methods():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    vg_id = "ge82059a"
    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs"
    ).respond(
        status_code=200,
        json={
            "data": [{"id": vg_id, "name": "sales-analytics", "memory": "4Gi"}],
            "links": {"self": "self-url", "first": "first-url", "next": None},
        },
    )

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs"
    ).respond(
        status_code=202,
        json={
            "data": {
                "id": vg_id,
                "name": "sales-analytics",
                "memory": "4Gi",
                "plain_password": "initial-secret",
            }
        },
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs/allowed-configs"
    ).respond(
        status_code=200,
        json={
            "data": {
                "configs": [{"memory": "4Gi"}, {"memory": "8Gi"}],
                "default_memory": "4Gi",
            }
        },
    )

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs/{vg_id}"
    ).respond(status_code=200, json={"data": {"id": vg_id, "name": "sales-analytics"}})

    respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs/{vg_id}"
    ).respond(status_code=202)

    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/virtual-graphs/{vg_id}"
    ).respond(status_code=202)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        listed = await client.list_virtual_graphs(org_id, proj_id)
        assert listed.data[0].id == vg_id

        create_req = models.CreateVirtualGraphRequest(
            name="sales-analytics",
            cloud_provider="gcp",
            region="europe-west1",
            data_source_id="ds-1",
            import_model_id="im-1",
        )
        created = await client.create_virtual_graph(org_id, proj_id, create_req)
        assert created.data.id == vg_id
        assert created.data.plain_password == "initial-secret"

        allowed = await client.get_virtual_graph_allowed_configs(org_id, proj_id)
        assert allowed.data.default_memory == "4Gi"

        fetched = await client.get_virtual_graph(org_id, proj_id, vg_id)
        assert fetched.data.id == vg_id

        update_req = models.UpdateVirtualGraphRequest(name="updated-name")
        updated = await client.update_virtual_graph(org_id, proj_id, vg_id, update_req)
        assert updated is None

        deleted = await client.delete_virtual_graph(org_id, proj_id, vg_id)
        assert deleted is None


@respx.mock
@pytest.mark.asyncio
async def test_organization_invites_crud():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    invite_id = "invite-1"
    respx.get(f"{baseUrl}v2beta1/organizations/{org_id}/invites").respond(
        status_code=200,
        json={
            "data": [
                {
                    "id": invite_id,
                    "email": "new-user@example.com",
                    "status": "active",
                }
            ]
        },
    )
    respx.post(f"{baseUrl}v2beta1/organizations/{org_id}/invites").respond(
        status_code=201,
        json={
            "data": {
                "id": invite_id,
                "email": "new-user@example.com",
                "status": "active",
            }
        },
    )
    respx.delete(
        f"{baseUrl}v2beta1/organizations/{org_id}/invites/{invite_id}"
    ).respond(status_code=204)

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        invites = await client.list_organization_invites(org_id)
        assert len(invites) == 1
        assert isinstance(invites[0], models.OrganizationInvite)

        req = models.CreateOrganizationInviteRequest(
            email="new-user@example.com",
            roles=["organization-member"],
        )
        created = await client.create_organization_invite(org_id, req)
        assert created.id == invite_id

        deleted = await client.delete_organization_invite(org_id, invite_id)
        assert deleted is None


@respx.mock
@pytest.mark.asyncio
async def test_graph_analytics_session_methods():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    session_id = "session-1"
    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/graph-analytics/sessions"
    ).respond(
        status_code=200,
        json={"data": [{"id": session_id, "name": "analytics-session"}], "errors": []},
    )
    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/graph-analytics/sessions"
    ).respond(
        status_code=200,
        json={"data": {"id": session_id, "name": "analytics-session"}, "errors": []},
    )
    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/graph-analytics/sessions"
    ).respond(
        status_code=200,
        json={"data": [{"id": session_id, "name": "analytics-session"}], "errors": []},
    )
    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/graph-analytics/sessions/sizing"
    ).respond(
        status_code=200,
        json={"data": {"recommended_size": "2GB", "estimated_memory": "1.6GB"}},
    )

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        org_sessions = await client.list_organization_graph_analytics_sessions(org_id)
        assert org_sessions[0].id == session_id

        project_sessions = await client.list_project_graph_analytics_sessions(
            org_id, proj_id
        )
        assert project_sessions[0].id == session_id

        create_req = models.CreateGraphAnalyticsSessionRequest(
            name="analytics-session", memory="2GB", instance_id=inst_id
        )
        created = await client.create_project_graph_analytics_session(
            org_id, proj_id, create_req
        )
        assert created.data.id == session_id

        sizing_req = models.SessionSizingRequest(instance_id=inst_id)
        sizing = await client.estimate_project_graph_analytics_session_size(
            org_id, proj_id, sizing_req
        )
        assert sizing.data.recommended_size == "2GB"


@respx.mock
@pytest.mark.asyncio
async def test_project_instance_and_database_methods():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    database_id = "db-1"
    backup_id = "bkp-1"

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances"
    ).respond(status_code=200, json={"data": [{"id": inst_id, "name": "inst"}]})

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances"
    ).respond(status_code=201, json={"data": {"id": inst_id, "name": "inst"}})

    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances/{inst_id}/databases"
    ).respond(status_code=200, json={"data": [{"id": database_id}]})
    respx.get(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances/{inst_id}/databases/{database_id}/backups"
    ).respond(status_code=200, json={"data": [{"id": backup_id}]})

    respx.post(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/instances/{inst_id}/databases/{database_id}/backups"
    ).respond(status_code=202, json={"data": {"id": backup_id}})

    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        instances = await client.list_project_instances(org_id, proj_id)
        assert instances[0].id == inst_id

        create_req = models.CreateProjectInstanceRequest(name="inst")
        created = await client.create_project_instance(org_id, proj_id, create_req)
        assert created.data.id == inst_id

        databases = await client.list_project_instance_databases(
            org_id, proj_id, inst_id
        )
        assert databases[0].id == database_id

        backups = await client.list_project_database_backups(
            org_id, proj_id, inst_id, database_id
        )
        assert backups[0].id == backup_id

        backup = await client.create_project_database_backup(
            org_id, proj_id, inst_id, database_id
        )
        assert backup.data["id"] == backup_id


# === Agent Patch Tests ===


@respx.mock
@pytest.mark.asyncio
async def test_patch_agent():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}"
    ).respond(
        status_code=200,
        json={
            "id": agent_id,
            "project_id": proj_id,
            "organization_id": org_id,
            "name": "My Patched Agent",
            "description": "Original description",
            "dbid": "a1b2c3d4",
            "tools": [{"name": "query-tool", "type": "text2cypher", "enabled": True}],
            "is_private": False,
            "enabled": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-04-22T10:00:00Z",
        },
    )

    patch_req = models.PatchAgentRequest(name="My Patched Agent", enabled=False)
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.patch_agent(org_id, proj_id, agent_id, patch_req)
        assert isinstance(resp, models.AgentDetails)
        assert resp.id == agent_id
        assert resp.name == "My Patched Agent"
        assert resp.enabled is False


@respx.mock
@pytest.mark.asyncio
async def test_patch_agent_partial_update():
    respx.post(f"{baseUrl}oauth/token").respond(
        status_code=200,
        json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
    )

    respx.patch(
        f"{baseUrl}v2beta1/organizations/{org_id}/projects/{proj_id}/agents/{agent_id}"
    ).respond(
        status_code=200,
        json={
            "id": agent_id,
            "project_id": proj_id,
            "organization_id": org_id,
            "name": "Original Agent",
            "description": "Updated description",
            "dbid": "a1b2c3d4",
            "tools": [{"name": "query-tool", "type": "text2cypher", "enabled": True}],
            "is_private": False,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-04-22T10:00:00Z",
        },
    )

    # Only update description, leaving other fields untouched
    patch_req = models.PatchAgentRequest(description="Updated description")
    async with AuraClient(clientId, clientSecret, api_version="v2beta1") as client:
        resp = await client.patch_agent(org_id, proj_id, agent_id, patch_req)
        assert isinstance(resp, models.AgentDetails)
        assert resp.description == "Updated description"
        assert resp.name == "Original Agent"  # Should remain unchanged
        assert resp.enabled is True  # Should remain unchanged
