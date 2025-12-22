import pytest
import respx

from neo4j_aura_sdk import AuraClient

clientId = "mockId"
clientSecret = "mockSecret"
baseUrl = "https://api.neo4j.io/"


class TestAuraClientV1Beta5:
    def _mock_oauth_token(self):
        respx.post(f"{baseUrl}oauth/token").respond(
            status_code=200,
            json={
                "access_token": "mockToken",
                "expires_in": 3600,
                "token_type": "access",
            },
        )

    @respx.mock
    @pytest.mark.asyncio
    async def test_version_guard(self):
        self._mock_oauth_token()
        instance_id = "instance2"
        tenant_id = "tenant2"
        data_api_id = "dataapi1"
        auth_provider_id = "authprov1"
        async with AuraClient(clientId, clientSecret, api_version="v1") as client:
            with pytest.raises(ValueError):
                await client.list_graphql_data_apis(instance_id)
            with pytest.raises(ValueError):
                await client.create_graphql_data_api(instance_id, {})
            with pytest.raises(ValueError):
                await client.get_graphql_data_api(instance_id, data_api_id)
            with pytest.raises(ValueError):
                await client.update_graphql_data_api(instance_id, data_api_id, {})
            with pytest.raises(ValueError):
                await client.delete_graphql_data_api(instance_id, data_api_id)
            with pytest.raises(ValueError):
                await client.pause_graphql_data_api(instance_id, data_api_id)
            with pytest.raises(ValueError):
                await client.resume_graphql_data_api(instance_id, data_api_id)
            with pytest.raises(ValueError):
                await client.list_graphql_auth_providers(instance_id, data_api_id)
            with pytest.raises(ValueError):
                await client.create_graphql_auth_provider(instance_id, data_api_id, {})
            with pytest.raises(ValueError):
                await client.get_graphql_auth_provider(
                    instance_id, data_api_id, auth_provider_id
                )
            with pytest.raises(ValueError):
                await client.update_graphql_auth_provider(
                    instance_id, data_api_id, auth_provider_id, {}
                )
            with pytest.raises(ValueError):
                await client.delete_graphql_auth_provider(
                    instance_id, data_api_id, auth_provider_id
                )
            with pytest.raises(ValueError):
                await client.upgrade_instance(instance_id, {})
            with pytest.raises(ValueError):
                await client.get_project_metrics_integration(tenant_id)

    @respx.mock
    @pytest.mark.asyncio
    async def test_graphql_data_api_crud(self):
        from pydantic import BaseModel

        self._mock_oauth_token()
        instance_id = "instance2"
        data_api_id = "dataapi1"
        v1beta5_url = f"{baseUrl}v1beta5/"
        respx.get(f"{v1beta5_url}instances/{instance_id}/data-apis/graphql").respond(
            200, json={"data": []}
        )
        respx.post(f"{v1beta5_url}instances/{instance_id}/data-apis/graphql").respond(
            201, json={"data": {"id": data_api_id}}
        )
        respx.get(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}"
        ).respond(200, json={"data": {"id": data_api_id}})
        respx.patch(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}"
        ).respond(200, json={"data": {"id": data_api_id, "name": "updated"}})
        respx.delete(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}"
        ).respond(204)

        class DummyGraphQLDataAPI(BaseModel):
            name: str

        async with AuraClient(clientId, clientSecret, api_version="v1beta5") as client:
            await client.list_graphql_data_apis(instance_id)
            await client.create_graphql_data_api(
                instance_id, DummyGraphQLDataAPI(name="test")
            )
            await client.get_graphql_data_api(instance_id, data_api_id)
            await client.update_graphql_data_api(
                instance_id, data_api_id, DummyGraphQLDataAPI(name="updated")
            )
            await client.delete_graphql_data_api(instance_id, data_api_id)

    @respx.mock
    @pytest.mark.asyncio
    async def test_graphql_auth_providers(self):
        from pydantic import BaseModel

        self._mock_oauth_token()
        instance_id = "instance2"
        data_api_id = "dataapi1"
        auth_provider_id = "authprov1"
        v1beta5_url = f"{baseUrl}v1beta5/"
        respx.get(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/auth-providers"
        ).respond(200, json={"data": []})
        respx.post(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/auth-providers"
        ).respond(201, json={"data": {"id": auth_provider_id}})
        respx.get(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/auth-providers/{auth_provider_id}"
        ).respond(200, json={"data": {"id": auth_provider_id}})
        respx.patch(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/auth-providers/{auth_provider_id}"
        ).respond(200, json={"data": {"id": auth_provider_id, "name": "updated"}})
        respx.delete(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/auth-providers/{auth_provider_id}"
        ).respond(204)

        class DummyAuthProvider(BaseModel):
            name: str

        async with AuraClient(clientId, clientSecret, api_version="v1beta5") as client:
            await client.list_graphql_auth_providers(instance_id, data_api_id)
            await client.create_graphql_auth_provider(
                instance_id, data_api_id, DummyAuthProvider(name="test")
            )
            await client.get_graphql_auth_provider(
                instance_id, data_api_id, auth_provider_id
            )
            await client.update_graphql_auth_provider(
                instance_id,
                data_api_id,
                auth_provider_id,
                DummyAuthProvider(name="updated"),
            )
            await client.delete_graphql_auth_provider(
                instance_id, data_api_id, auth_provider_id
            )

    @respx.mock
    @pytest.mark.asyncio
    async def test_graphql_data_api_pause_resume(self):
        self._mock_oauth_token()
        instance_id = "instance2"
        data_api_id = "dataapi1"
        v1beta5_url = f"{baseUrl}v1beta5/"
        respx.post(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/pause"
        ).respond(200, json={"data": {"status": "paused"}})
        respx.post(
            f"{v1beta5_url}instances/{instance_id}/data-apis/graphql/{data_api_id}/resume"
        ).respond(200, json={"data": {"status": "active"}})
        async with AuraClient(clientId, clientSecret, api_version="v1beta5") as client:
            await client.pause_graphql_data_api(instance_id, data_api_id)
            await client.resume_graphql_data_api(instance_id, data_api_id)

    @respx.mock
    @pytest.mark.asyncio
    async def test_instance_upgrade(self):
        from neo4j_aura_sdk.models import InstanceUpgradeRequest

        self._mock_oauth_token()
        instance_id = "instance2"
        v1beta5_url = f"{baseUrl}v1beta5/"
        respx.post(f"{v1beta5_url}instances/{instance_id}/upgrade").respond(
            200, json={"data": {"status": "upgraded"}}
        )
        async with AuraClient(clientId, clientSecret, api_version="v1beta5") as client:
            await client.upgrade_instance(
                instance_id, InstanceUpgradeRequest(memory="16GB")
            )

    @respx.mock
    @pytest.mark.asyncio
    async def test_project_metrics_integration(self):
        self._mock_oauth_token()
        tenant_id = "tenant2"
        v1beta5_url = f"{baseUrl}v1beta5/"
        respx.get(f"{v1beta5_url}tenants/{tenant_id}/metrics-integration").respond(
            200, json={"url": "https://metrics", "enabled": True}
        )
        async with AuraClient(clientId, clientSecret, api_version="v1beta5") as client:
            resp = await client.get_project_metrics_integration(tenant_id)
            assert resp["url"] == "https://metrics"
            assert resp["enabled"] is True
