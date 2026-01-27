import pytest
import respx

from neo4j_aura_sdk import AuraClient, models

clientId = "mockId"
clientSecret = "mockSecret"
baseUrl = "https://api.neo4j.io/"
org_id = "org1"
proj_id = "proj1"
inst_id = "inst1"
deployment_id = "deploy1"
server_id = "server1"


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
        assert resp.data[0]["id"] == proj_id
        assert resp.data[0]["name"] == "My Project"


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
        assert resp.data[0].id == deployment_id


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
