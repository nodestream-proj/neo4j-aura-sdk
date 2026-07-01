import json
import os
import time
from typing import Type

import httpx
import pydantic_core
from pydantic import BaseModel

from .models import (
    ActivityFeedResponse,
    ActivityLog,
    AddProjectUserRequest,
    AgentDetails,
    AuraApiAuthorizationException,
    AuraApiBadRequestException,
    AuraApiException,
    AuraApiInternalException,
    AuraApiNotFoundException,
    AuraApiRateLimitExceededException,
    AuraApiUnsupportedActionException,
    AuraApiValidationException,
    AuraError,
    AuraErrors,
    AuthResponse,
    CreateAgentRequest,
    CreateDeploymentRequest,
    CreateGraphAnalyticsSessionRequest,
    CreateImportJobRequest,
    CreateOrganizationInviteRequest,
    CreateProjectDatabaseBackupResponse,
    CreateProjectDatabaseRequest,
    CreateProjectInstanceRequest,
    CustomerManagedKey,
    CustomerManagedKeyRequest,
    CustomerManagedKeyResponse,
    CustomerManagedKeysResponse,
    DatabasesResponse,
    DeploymentDetailsResponse,
    DeploymentResponse,
    DeploymentsResponse,
    DeploymentTokenResponse,
    GetAgentResponse,
    ImportJobEnvelope,
    InstancePatchRequest,
    InstanceRequest,
    InstanceResponse,
    InstanceSizingRequest,
    InstanceSizingResponse,
    InstancesResponse,
    InvokeAgentRequest,
    InvokeAgentResponse,
    IpFilter,
    IpFilterWithStatus,
    JobIdEnvelope,
    LedgerResponse,
    ListAgentResponse,
    OrganizationDetailsEnvelope,
    OrganizationInviteResponse,
    OrganizationInvitesResponse,
    OrganizationUser,
    OrganizationUserDetails,
    PatchAgentRequest,
    PatchProjectUserRequest,
    ProjectDatabaseBackupResponse,
    ProjectDatabaseBackupsResponse,
    ProjectDatabaseResponse,
    ProjectDatabasesResponse,
    ProjectInstanceResponse,
    ProjectInstancesResponse,
    ProjectsResponse,
    ProjectUser,
    RestoreProjectDatabaseRequest,
    ServerDatabasesResponse,
    ServersResponse,
    SessionEnvelope,
    SessionSizeEnvelope,
    SessionSizingRequest,
    SessionsResponse,
    SnapshotResponse,
    SnapshotsResponse,
    TenantResponse,
    TenantsResponse,
    UsageResponse,
)


class AuraClient:
    """An API Client for the Neo4j Aura service.

    This client provides a low-ish level interface to the Neo4j Aura service.
    It is intended to be used by higher level libraries that provide a more
    user-friendly interface.

    This client is not thread-safe. If you need to use it in a multi-threaded
    environment, you should create a new client for each thread.

    Usage:

    ```python
    from neo4j_aura_sdk import AuraClient

    client_id = "..."
    client_secret = "..."

    async with AuraClient(client_id, client_secret) as client:
        # Do stuff with the client
    ```
    """

    # --- v1beta5-only methods ---

    # GraphQL Data API CRUD
    async def list_graphql_data_apis(self, instanceId: str):
        """List GraphQL Data APIs for an instance (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._get(
            f"instances/{instanceId}/data-apis/graphql",
            model=None,
            api_version="v1beta5",
        )

    async def create_graphql_data_api(self, instanceId: str, details):
        """Create a new GraphQL Data API for an instance (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._post(
            f"instances/{instanceId}/data-apis/graphql",
            body=details,
            model=None,
            api_version="v1beta5",
        )

    async def get_graphql_data_api(self, instanceId: str, dataApiId: str):
        """Get details of a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._get(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}",
            model=None,
            api_version="v1beta5",
        )

    async def update_graphql_data_api(self, instanceId: str, dataApiId: str, details):
        """Update a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._patch(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}",
            body=details,
            model=None,
            api_version="v1beta5",
        )

    async def delete_graphql_data_api(self, instanceId: str, dataApiId: str):
        """Delete a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._delete(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}",
            model=None,
            api_version="v1beta5",
        )

    async def pause_graphql_data_api(self, instanceId: str, dataApiId: str):
        """Pause a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._post(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/pause",
            model=None,
            api_version="v1beta5",
        )

    async def resume_graphql_data_api(self, instanceId: str, dataApiId: str):
        """Resume a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._post(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/resume",
            model=None,
            api_version="v1beta5",
        )

    # GraphQL Data API Auth Providers
    async def list_graphql_auth_providers(self, instanceId: str, dataApiId: str):
        """List auth providers for a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._get(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/auth-providers",
            model=None,
            api_version="v1beta5",
        )

    async def create_graphql_auth_provider(
        self, instanceId: str, dataApiId: str, details
    ):
        """Create an auth provider for a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._post(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/auth-providers",
            body=details,
            model=None,
            api_version="v1beta5",
        )

    async def get_graphql_auth_provider(
        self, instanceId: str, dataApiId: str, authProviderId: str
    ):
        """Get details of an auth provider for a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._get(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/auth-providers/{authProviderId}",
            model=None,
            api_version="v1beta5",
        )

    async def update_graphql_auth_provider(
        self, instanceId: str, dataApiId: str, authProviderId: str, details
    ):
        """Update an auth provider for a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._patch(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/auth-providers/{authProviderId}",
            body=details,
            model=None,
            api_version="v1beta5",
        )

    async def delete_graphql_auth_provider(
        self, instanceId: str, dataApiId: str, authProviderId: str
    ):
        """Delete an auth provider for a GraphQL Data API (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._delete(
            f"instances/{instanceId}/data-apis/graphql/{dataApiId}/auth-providers/{authProviderId}",
            model=None,
            api_version="v1beta5",
        )

    # Instance upgrade
    async def upgrade_instance(self, instanceId: str, details=None):
        """Upgrade an AuraDB Professional instance to Business Critical (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._post(
            f"instances/{instanceId}/upgrade",
            body=details,
            model=None,
            api_version="v1beta5",
        )

    # Project metrics integration
    async def get_project_metrics_integration(self, tenantId: str):
        """Get metrics integration details for a project (v1beta5 only)."""
        self._ensure_api_is_v1beta5()
        return await self._get(
            f"tenants/{tenantId}/metrics-integration", model=None, api_version="v1beta5"
        )

    def _ensure_api_is_v1beta5(self):
        """Raise ValueError if the client is not configured for v1beta5 endpoints."""
        if self._api_version != "v1beta5":
            raise ValueError(
                "This method is only available when api_version is set to 'v1beta5'."
            )

    async def patch_instance(self, instanceId: str, patch: InstancePatchRequest):
        """Generic PATCH for an instance (v1). Allows updating name, memory, storage, vector_optimized, graph_analytics_plugin, secondaries_count, cdc_enrichment_mode in one call.

        Args:
            instanceId: The ID of the instance to update.
            patch: InstancePatchRequest with any fields to update.

        Returns: InstanceResponse for the updated instance.
        """
        return await self._patch(
            f"instances/{instanceId}",
            body=patch,
            model=InstanceResponse,
        )

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.neo4j.io",
        api_version: str = "v1",
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        # Exposed API version for the client. Use 'v1', 'v2beta1', etc.
        self._api_version = api_version
        self._token = None
        self._token_expiration = 0
        self._client = httpx.AsyncClient(timeout=30)

    @classmethod
    def from_env(cls):
        client_id = os.environ["AURA_API_CLIENT_TOKEN"]
        client_secret = os.environ["AURA_API_CLIENT_SECRET"]
        api_version = os.environ.get("AURA_API_VERSION", "v1")
        return cls(client_id, client_secret, api_version=api_version)

    # AsyncClient is a context manager, so we need to implement __aenter__ and
    # __aexit__ to make this class a context manager as well. This allows us to
    # use the `async with` syntax.

    async def __aenter__(self):
        """Enter async context for the underlying HTTP client."""
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit async context for the underlying HTTP client."""
        await self._client.__aexit__(exc_type, exc, tb)

    def _checkResponseStatus(self, response: httpx.Response):
        if response.status_code < 400:
            return
        elif response.status_code in [400, 415]:
            raise AuraApiBadRequestException(
                AuraErrors(**response.json()), response.status_code
            )
        elif response.status_code in [401, 403]:
            # HACK: the oauth endpoint returns a single object with different properties
            try:
                errors = AuraErrors(**response.json())
            except pydantic_core._pydantic_core.ValidationError:
                body = response.json()
                reason = None
                if "error_description" in body:
                    reason = body["error_description"]
                errors = AuraErrors(
                    errors=[AuraError(message=body["error"], reason=reason)]
                )
            raise AuraApiAuthorizationException(errors, response.status_code)
        elif response.status_code == 404:
            raise AuraApiNotFoundException(
                AuraErrors(**response.json()), response.status_code
            )
        elif response.status_code == 429:
            raise AuraApiRateLimitExceededException(
                AuraErrors(**response.json()), response.status_code
            )
        elif response.status_code == 420:
            raise AuraApiUnsupportedActionException(
                AuraErrors(**response.json()), response.status_code
            )
        elif response.status_code == 422:
            raise AuraApiValidationException(
                AuraErrors(**response.json()), response.status_code
            )
        elif response.status_code >= 500:
            raise AuraApiInternalException(
                AuraErrors(**response.json()), response.status_code
            )
        else:
            raise AuraApiException(AuraErrors(**response.json()))

    async def _get_token(self):
        """Fetch an OAuth2 token using client credentials and cache it until expiration.

        Returns the access token string.
        """
        # NOTE: This method is a bit complex because it handles token
        #       expiration. We could simplify it through refactoring or
        #       by using a custom authentication class.
        current_time = time.monotonic()
        if current_time < self._token_expiration:
            return self._token

        response = await self._client.post(
            f"{self._base_url}/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
        )

        self._checkResponseStatus(response)

        auth_response = AuthResponse(**response.json())
        self._token = auth_response.access_token
        self._token_expiration = (
            current_time + auth_response.expires_in - 50
        )  # 50s buffer
        return self._token

    async def _get(
        self,
        path: str,
        model: Type[BaseModel] | None = None,
        api_version: str | None = None,
        params: dict | None = None,
    ):
        """Perform a GET request to the API.

        - path: relative path (without leading slash)
        - model: optional Pydantic model to parse the response into (or None for raw JSON)
        - api_version: optional API version override (defaults to client's configured version)
        - params: optional dict of query parameters
        """
        return await self._request(
            "GET", path, model=model, api_version=api_version, params=params
        )

    async def _post(
        self,
        path: str,
        model: Type[BaseModel] | None = None,
        body: BaseModel | None = None,
        api_version: str | None = None,
    ):
        """Perform a POST request to the API. See `_get` for parameter semantics."""
        return await self._request(
            "POST", path, model=model, body=body, api_version=api_version
        )

    async def _delete(
        self,
        path: str,
        model: Type[BaseModel] | None = None,
        default: BaseModel | None = None,
        api_version: str | None = None,
    ):
        """Perform a DELETE request to the API. Returns `default` when response has no JSON."""
        return await self._request(
            "DELETE", path, model=model, default=default, api_version=api_version
        )

    async def _patch(
        self,
        path: str,
        body: BaseModel,
        model: Type[BaseModel] | None = None,
        api_version: str | None = None,
    ):
        """Perform a PATCH request to the API. See `_get` for parameter semantics."""
        return await self._request(
            "PATCH", path, model=model, body=body, api_version=api_version
        )

    async def _put(
        self,
        path: str,
        body: BaseModel,
        model: Type[BaseModel] | None = None,
        api_version: str | None = None,
    ):
        """Perform a PUT request to the API. See `_get` for parameter semantics."""
        return await self._request(
            "PUT", path, model=model, body=body, api_version=api_version
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        model: Type[BaseModel] | None = None,
        body: BaseModel | None = None,
        default: BaseModel | None = None,
        api_version: str | None = None,
        params: dict | None = None,
    ):
        """Generic request helper that supports API versioning and optional model parsing.

        - method: HTTP method (GET/POST/PATCH/DELETE)
        - path: relative path without leading slash (e.g. 'tenants' or 'organizations/...')
        - model: optional Pydantic model class to parse response into
        - body: optional Pydantic model to send as JSON body
        - default: value to return if response has no JSON (useful for 204 responses)
        - api_version: API version segment to use (defaults to 'v1')
        - params: optional dict of query parameters
        """
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        if method in ("POST", "PATCH", "PUT"):
            headers.update(
                {"Content-Type": "application/json", "accept": "application/json"}
            )

        effective_api_version = api_version or self._api_version
        url = f"{self._base_url}/{effective_api_version}/{path}"
        content = None
        if body:
            content = body.model_dump_json()

        response = await self._client.request(
            method, url, headers=headers, content=content, params=params
        )
        self._checkResponseStatus(response)

        # Handle 204 No Content or empty response body
        if (
            response.status_code == 204
            or not response.content
            or response.text.strip() == ""
        ):
            return default

        if model:
            return model(**response.json())

        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            return default

    def _ensure_api_is_v2(self):
        """Raise a clear error when attempting to call v2 endpoints on a v1-configured client."""
        if not str(self._api_version).startswith("v2"):
            raise ValueError(
                f"Client is configured for API version '{self._api_version}'; v2 endpoints are not available."
            )

    @property
    def api_version(self) -> str:
        """Return the API version configured for this client (e.g. 'v1', 'v2beta1')."""
        return self._api_version

    async def tenants(self):
        """Get a list of tenants (v1).

        Returns: TenantsResponse parsed from the v1 `/v1/tenants` endpoint.
        """
        return await self._get("tenants", model=TenantsResponse)

    async def tenant(self, tenantId: str):
        """Get a single tenant by ID (v1).

        Args:
            tenantId: tenant identifier

        Returns: TenantResponse parsed from `/v1/tenants/{tenantId}`.
        """
        return await self._get(f"tenants/{tenantId}", model=TenantResponse)

    async def instances(self, tenantId: str = ""):
        """List instances. By default lists all instances; if tenantId is provided,
        lists instances for that tenant (v1).

        Args:
            tenantId: optional tenant id to scope instances

        Returns: InstancesResponse parsed from `/v1/instances`.
        """
        path = "instances"
        params = {}
        if tenantId:
            params["tenantId"] = tenantId
        return await self._get(
            path, model=InstancesResponse, params=params if params else None
        )

    async def instance(self, instanceId: str):
        """Get a single instance by id (v1).

        Returns: InstanceResponse parsed from `/v1/instances/{instanceId}`.
        """
        return await self._get(f"instances/{instanceId}", model=InstanceResponse)

    async def create_instance(self, details: InstanceRequest):
        """Create a new instance (v1).

        Args:
            details: InstanceRequest model describing the instance to create

        Returns: InstanceResponse for the created instance.
        """
        return await self._post("instances", body=details, model=InstanceResponse)

    async def delete_instance(self, instanceId: str):
        """Delete an instance by id (v1).

        Returns: InstanceResponse for the deleted instance when available.
        """
        return await self._delete(f"instances/{instanceId}", model=InstanceResponse)

    async def rename_instance(self, instanceId: str, name: str):
        """Rename an instance (v1).

        Returns: InstanceResponse for the updated instance.
        """

        class _Rename(BaseModel):
            name: str

        return await self._patch(
            f"instances/{instanceId}", body=_Rename(name=name), model=InstanceResponse
        )

    async def resize_instance(self, instanceId: str, memory: str):
        """Resize an instance's memory (v1).

        Args:
            memory: new memory size string (e.g. '4GB')

        Returns: InstanceResponse for the resizing operation.
        """

        class _Resize(BaseModel):
            memory: str

        return await self._patch(
            f"instances/{instanceId}",
            body=_Resize(memory=memory),
            model=InstanceResponse,
        )

    async def rename_and_resize_instance(self, instanceId: str, name: str, memory: str):
        """Rename and resize an instance in a single request (v1).

        Returns: InstanceResponse.
        """

        class _RenameResize(BaseModel):
            name: str
            memory: str

        return await self._patch(
            f"instances/{instanceId}",
            body=_RenameResize(name=name, memory=memory),
            model=InstanceResponse,
        )

    async def resize_instance_secondary_count(self, instanceId: str, count: int):
        """Update the secondary count for an instance (v1).

        Returns: InstanceResponse or raises AuraApiBadRequestException on invalid action.
        """

        class _Resize(BaseModel):
            secondaries_count: int

        return await self._patch(
            f"instances/{instanceId}",
            body=_Resize(secondaries_count=count),
            model=InstanceResponse,
        )

    async def update_instance_cdc_mode(self, instanceId: str, mode: str):
        """Update an instance's CDC enrichment mode (v1).

        Args:
            mode: CDC mode string (e.g. 'FULL')

        Returns: InstanceResponse or raises AuraApiBadRequestException.
        """

        class _Resize(BaseModel):
            cdc_enrichment_mode: str

        return await self._patch(
            f"instances/{instanceId}",
            body=_Resize(cdc_enrichment_mode=mode),
            model=InstanceResponse,
        )

    async def overwrite_instance(self, instanceId: str, sourceId: str):
        """Overwrite an instance from another instance (v1).

        Returns: InstanceResponse indicating overwrite status.
        """

        class _Overwrite(BaseModel):
            source_instance_id: str

        return await self._post(
            f"instances/{instanceId}/overwrite",
            body=_Overwrite(source_instance_id=sourceId),
            model=InstanceResponse,
        )

    async def overwrite_instance_with_snapshot(
        self, instanceId: str, sourceId: str, snapshotId: str
    ):
        """Overwrite an instance from a snapshot of another instance (v1).

        Returns: InstanceResponse.
        """

        class _Overwrite(BaseModel):
            source_instance_id: str
            source_snapshot_id: str

        return await self._post(
            f"instances/{instanceId}/overwrite",
            body=_Overwrite(source_instance_id=sourceId, source_snapshot_id=snapshotId),
            model=InstanceResponse,
        )

    async def pause_instance(self, instanceId: str):
        """Pause an instance (v1). Returns InstanceResponse with pausing status."""
        return await self._post(f"instances/{instanceId}/pause", model=InstanceResponse)

    async def resume_instance(self, instanceId: str):
        """Resume a paused instance (v1). Returns InstanceResponse with resuming status."""
        return await self._post(
            f"instances/{instanceId}/resume", model=InstanceResponse
        )

    async def restore_instance(self, instanceId: str, snapshotId: str):
        """Restore an instance from a snapshot (v1)."""
        return await self._post(
            f"instances/{instanceId}/snapshots/{snapshotId}/restore",
            model=InstanceResponse,
        )

    async def snapshot_instance(self, instanceId: str):
        """Create a snapshot for an instance (v1). Returns SnapshotResponse."""
        return await self._post(
            f"instances/{instanceId}/snapshots", model=SnapshotResponse
        )

    async def instance_sizing(self, details: InstanceSizingRequest):
        """Estimate instance sizing based on node/relationship counts (v1).

        Args:
            details: InstanceSizingRequest containing node/relationship counts and instance type

        Returns: InstanceSizingResponse with sizing recommendation.
        """
        return await self._post(
            "instances/sizing", body=details, model=InstanceSizingResponse
        )

    async def snapshots(self, instanceId: str, date: str = ""):
        """List snapshots for an instance (v1). Optionally filter by date.

        Returns: SnapshotsResponse.
        """
        path = f"instances/{instanceId}/snapshots"
        params = {}
        if date:
            params["date"] = date
        return await self._get(
            path, model=SnapshotsResponse, params=params if params else None
        )

    async def snapshot(self, instanceId: str, snapshotId: str):
        """Get a single snapshot by id (v1). Returns SnapshotResponse."""
        return await self._get(
            f"instances/{instanceId}/snapshots/{snapshotId}", model=SnapshotResponse
        )

    async def get_customer_managed_keys(self, tenantId: str = ""):
        """List customer managed keys (v1). Optionally filter by tenantId."""
        path = "customer-managed-keys"
        params = {}
        if tenantId:
            params["tenantId"] = tenantId
        return await self._get(
            path, model=CustomerManagedKeysResponse, params=params if params else None
        )

    async def get_customer_managed_key(self, customerManagedKeyId: str):
        """Get a specific customer managed key by id (v1)."""
        return await self._get(
            f"customer-managed-keys/{customerManagedKeyId}",
            model=CustomerManagedKeyResponse,
        )

    async def create_customer_managed_key(self, details: CustomerManagedKeyRequest):
        """Create a new customer managed key (v1). Returns CustomerManagedKeyResponse."""
        return await self._post(
            "customer-managed-keys", body=details, model=CustomerManagedKeyResponse
        )

    async def delete_customer_managed_key(self, customerManagedKeyId: str):
        """Delete a customer managed key (v1). Returns a default deleted response if empty."""
        default = CustomerManagedKeyResponse(
            data=CustomerManagedKey(id=customerManagedKeyId, status="deleted")
        )
        resp = await self._delete(
            f"customer-managed-keys/{customerManagedKeyId}",
            model=CustomerManagedKeyResponse,
            default=default,
        )
        # If the response is None (e.g., 204 No Content), return the default deleted response
        if resp is None:
            return default
        return resp

    # --- v2beta1 endpoints from OpenAPI spec ---

    # Organization & Projects
    async def get_organization(self, organizationId: str):
        """Get an organization by its ID (v2beta1).

        Args:
            organizationId: the organization id

        Returns: OrganizationDetailsEnvelope with organization details containing id and name.
        """
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}",
            model=OrganizationDetailsEnvelope,
            api_version="v2beta1",
        )

    async def list_organization_projects(self, organizationId: str, status: str = None):
        """List projects for an organization (v2beta1).

        Args:
            organizationId: the organization id
            status: optional filter by project status ('active', 'deleted', 'deletion_requested')

        Returns: ProjectsResponse with 'data' key containing list of projects.
        """
        self._ensure_api_is_v2()
        params = {}
        if status:
            params["status"] = status
        return await self._get(
            f"organizations/{organizationId}/projects",
            model=ProjectsResponse,
            api_version="v2beta1",
            params=params if params else None,
        )

    async def list_organizations(self):
        """List all organizations (v2beta1).

        Returns: OrganizationDetailsEnvelope with a list of organizations.
        """
        self._ensure_api_is_v2()
        return await self._get(
            "organizations",
            model=OrganizationDetailsEnvelope,
            api_version="v2beta1",
        )

    # Organization Users
    async def list_organization_users(self, organizationId: str):
        """List all users in an organization (v2beta1).

        Args:
            organizationId: the organization id

        Returns: List of OrganizationUser objects.
        """
        self._ensure_api_is_v2()
        items = await self._get(
            f"organizations/{organizationId}/users",
            model=None,
            api_version="v2beta1",
        )
        return [OrganizationUser(**item) for item in items] if items else []

    async def get_organization_user(self, organizationId: str, userId: str):
        """Get detailed information about a user in an organization (v2beta1).

        Args:
            organizationId: the organization id
            userId: the UUID of the user

        Returns: OrganizationUserDetails including project memberships.
        """
        self._ensure_api_is_v2()
        result = await self._get(
            f"organizations/{organizationId}/users/{userId}",
            model=None,
            api_version="v2beta1",
        )
        return OrganizationUserDetails(**result["data"])

    async def remove_organization_user(self, organizationId: str, user_id: str):
        """Remove a user from an organization (v2beta1).

        Args:
            organizationId: the organization id
            user_id: the user id to remove

        Returns: None on success (204 No Content).
        """
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/users/{user_id}",
            api_version="v2beta1",
        )

    async def patch_organization_user(self, organizationId: str, userId: str):
        """Patch an organization user (v2beta1).

        The current API does not require a request body for this operation.
        Returns the updated OrganizationUserDetails.
        """
        self._ensure_api_is_v2()
        result = await self._patch(
            f"organizations/{organizationId}/users/{userId}",
            body=JobIdEnvelope(),
            model=None,
            api_version="v2beta1",
        )
        data = result.get("data", result) if isinstance(result, dict) else result
        return OrganizationUserDetails(**data)

    # Project Users
    async def list_project_users(self, organizationId: str, projectId: str):
        """List all users in a project (v2beta1).

        Args:
            organizationId: the organization id
            projectId: the project id

        Returns: List of ProjectUser objects.
        """
        self._ensure_api_is_v2()
        result = await self._get(
            f"organizations/{organizationId}/projects/{projectId}/users",
            model=None,
            api_version="v2beta1",
        )
        data = result.get("data", []) if isinstance(result, dict) else result
        return [ProjectUser(**item) for item in data] if data else []

    async def update_project_user(
        self,
        organizationId: str,
        projectId: str,
        userId: str,
        details: PatchProjectUserRequest,
    ):
        """Update a project user's role (v2beta1).

        Args:
            organizationId: the organization id
            projectId: the project id
            userId: the UUID of the user
            details: PatchProjectUserRequest with the role to assign

        Returns: ProjectUser with updated role.
        """
        self._ensure_api_is_v2()
        result = await self._patch(
            f"organizations/{organizationId}/projects/{projectId}/users/{userId}",
            body=details,
            model=None,
            api_version="v2beta1",
        )
        return ProjectUser(**result["data"])

    async def add_project_user(
        self,
        organizationId: str,
        projectId: str,
        userId: str,
        details: AddProjectUserRequest | None = None,
    ):
        """Add a user to a project (v2beta1)."""
        self._ensure_api_is_v2()
        result = await self._post(
            f"organizations/{organizationId}/projects/{projectId}/users/{userId}",
            body=details or JobIdEnvelope(),
            model=None,
            api_version="v2beta1",
        )
        data = result.get("data", result) if isinstance(result, dict) else result
        return ProjectUser(**data)

    async def remove_project_user(
        self, organizationId: str, projectId: str, userId: str
    ):
        """Remove a user from a project (v2beta1).

        Args:
            organizationId: the organization id
            projectId: the project id
            userId: the UUID of the user

        Returns: None on success (204 No Content).
        """
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/users/{userId}",
            api_version="v2beta1",
        )

    # Organization invites
    async def list_organization_invites(self, organizationId: str):
        """List organization invites (v2beta1)."""
        self._ensure_api_is_v2()
        result = await self._get(
            f"organizations/{organizationId}/invites",
            model=OrganizationInvitesResponse,
            api_version="v2beta1",
        )
        return result.data or []

    async def create_organization_invite(
        self, organizationId: str, details: CreateOrganizationInviteRequest
    ):
        """Create an organization invite (v2beta1)."""
        self._ensure_api_is_v2()
        result = await self._post(
            f"organizations/{organizationId}/invites",
            body=details,
            model=OrganizationInviteResponse,
            api_version="v2beta1",
        )
        return result.data

    async def delete_organization_invite(self, organizationId: str, inviteId: str):
        """Delete an organization invite (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/invites/{inviteId}",
            api_version="v2beta1",
        )

    # Billing
    async def get_billing_usage(
        self,
        organizationId: str,
        start: str,
        end: str,
        page_token: str = None,
        page_limit: int = None,
        project_id: list[str] = None,
    ):
        """Get billed usage for an organization (v2beta1).

        Args:
            organizationId: the organization id
            start: RFC3339 timestamp (e.g., '2024-01-02T00:00:00Z')
            end: RFC3339 timestamp (e.g., '2024-01-31T23:59:59Z')
            project_id: optional list of project UUIDs to filter usage rows

        Returns: UsageResponse with 'data' containing list of UsageData objects and optional 'links' for pagination.
        """
        self._ensure_api_is_v2()
        params = {"start": start, "end": end}
        if page_token:
            params["page_token"] = page_token
        if page_limit:
            params["page_limit"] = page_limit
        if project_id:
            params["project_id"] = project_id
        return await self._get(
            f"organizations/{organizationId}/billing/usage",
            model=UsageResponse,
            api_version="v2beta1",
            params=params,
        )

    async def get_billing_ledger(
        self,
        organizationId: str,
        start: str,
        end: str,
        page_token: str = None,
        page_limit: int = None,
    ):
        """Get credit ledger for an organization (v2beta1).

        Args:
            organizationId: the organization id
            start: RFC3339 timestamp (e.g., '2024-01-02T00:00:00Z')
            end: RFC3339 timestamp (e.g., '2024-01-31T23:59:59Z')

        Returns: LedgerResponse with 'data' containing list of LedgerData objects and optional 'links' for pagination.
        """
        self._ensure_api_is_v2()
        params = {"start": start, "end": end}
        if page_token:
            params["page_token"] = page_token
        if page_limit:
            params["page_limit"] = page_limit
        return await self._get(
            f"organizations/{organizationId}/billing/ledger",
            model=LedgerResponse,
            api_version="v2beta1",
            params=params,
        )

    # IP Filters
    async def list_organization_ip_filters(self, organizationId: str):
        """List IP filters for an organization (v2beta1). Returns a list of IpFilter models."""
        self._ensure_api_is_v2()
        items = await self._get(
            f"organizations/{organizationId}/ip-filters",
            model=None,
            api_version="v2beta1",
        )
        return [IpFilter(**i) for i in items]

    async def create_organization_ip_filter(
        self, organizationId: str, details: IpFilter
    ):
        """Create an IP filter for an organization."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/ip-filters",
            model=IpFilter,
            body=details,
            api_version="v2beta1",
        )

    async def get_organization_ip_filter(self, organizationId: str, ipFilterId: str):
        """Retrieve a specific IP filter by id for an organization (v2beta1).

        Args:
            organizationId: the organization id
            ipFilterId: the ip filter id

        Returns: IpFilter model parsed from the v2beta1 endpoint.
        """
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/ip-filters/{ipFilterId}",
            model=IpFilter,
            api_version="v2beta1",
        )

    async def update_organization_ip_filter(
        self, organizationId: str, ipFilterId: str, details: IpFilter
    ):
        """Update an existing IP filter for an organization (v2beta1).

        Args:
            details: IpFilter model with updated fields

        Returns: IpFilter parsed from the response.
        """
        self._ensure_api_is_v2()
        return await self._patch(
            f"organizations/{organizationId}/ip-filters/{ipFilterId}",
            body=details,
            model=IpFilter,
            api_version="v2beta1",
        )

    async def delete_organization_ip_filter(self, organizationId: str, ipFilterId: str):
        """Delete an IP filter (v2beta1).

        Returns: IpFilter when response includes body, otherwise None for 204 No Content.
        """
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/ip-filters/{ipFilterId}",
            model=IpFilter,
            default=None,
            api_version="v2beta1",
        )

    async def get_instance_ip_filter_status(
        self, organizationId: str, projectId: str, instanceId: str
    ):
        """Get the IP filter applied to a specific instance including status (v2beta1).

        Returns: IpFilterWithStatus or None when no filter is applied.
        """
        self._ensure_api_is_v2()
        body = await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/ip-filters",
            model=IpFilterWithStatus,
            api_version="v2beta1",
        )
        return body

    # Import jobs
    async def create_import_job(
        self, organizationId: str, projectId: str, details: CreateImportJobRequest
    ):
        """Create an import job for a project (v2beta1).

        Args:
            details: CreateImportJobRequest describing the model id and optional credentials.

        Returns: JobIdEnvelope containing the created job id.
        """
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/import/jobs",
            model=JobIdEnvelope,
            body=details,
            api_version="v2beta1",
        )

    async def get_import_job(
        self, organizationId: str, projectId: str, jobId: str, progress: bool = False
    ):
        """Retrieve an import job by ID (v2beta1).

        Args:
            progress: when True include detailed progress info for nodes/relationships.

        Returns: ImportJobEnvelope.
        """
        self._ensure_api_is_v2()
        path = (
            f"organizations/{organizationId}/projects/{projectId}/import/jobs/{jobId}"
        )
        params = {"progress": "true"} if progress else None
        return await self._get(
            path, model=ImportJobEnvelope, api_version="v2beta1", params=params
        )

    async def cancel_import_job(self, organizationId: str, projectId: str, jobId: str):
        """Cancel an existing import job (v2beta1). Returns JobIdEnvelope on success."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/import/jobs/{jobId}/cancellation",
            model=JobIdEnvelope,
            api_version="v2beta1",
        )

    # Graph analytics sessions
    async def list_organization_graph_analytics_sessions(
        self,
        organizationId: str,
        list_only_owned: bool | None = None,
        include_deleted: bool | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ):
        """List graph analytics sessions for an organization (v2beta1)."""
        self._ensure_api_is_v2()
        params = {}
        if list_only_owned is not None:
            params["list_only_owned"] = str(list_only_owned).lower()
        if include_deleted is not None:
            params["include_deleted"] = str(include_deleted).lower()
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return await self._get(
            f"organizations/{organizationId}/graph-analytics/sessions",
            model=SessionsResponse,
            api_version="v2beta1",
            params=params if params else None,
        )

    async def list_project_graph_analytics_sessions(
        self, organizationId: str, projectId: str
    ):
        """List graph analytics sessions for a project (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/graph-analytics/sessions",
            model=SessionsResponse,
            api_version="v2beta1",
        )

    async def create_project_graph_analytics_session(
        self,
        organizationId: str,
        projectId: str,
        details: CreateGraphAnalyticsSessionRequest,
    ):
        """Create a graph analytics session for a project (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/graph-analytics/sessions",
            body=details,
            model=SessionEnvelope,
            api_version="v2beta1",
        )

    async def get_project_graph_analytics_session(
        self,
        organizationId: str,
        projectId: str,
        sessionId: str,
    ):
        """Get a graph analytics session by id (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/graph-analytics/sessions/{sessionId}",
            model=SessionEnvelope,
            api_version="v2beta1",
        )

    async def delete_project_graph_analytics_session(
        self,
        organizationId: str,
        projectId: str,
        sessionId: str,
    ):
        """Delete a graph analytics session by id (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/graph-analytics/sessions/{sessionId}",
            api_version="v2beta1",
        )

    async def estimate_project_graph_analytics_session_size(
        self,
        organizationId: str,
        projectId: str,
        details: SessionSizingRequest,
    ):
        """Estimate project graph analytics session size (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/graph-analytics/sessions/sizing",
            body=details,
            model=SessionSizeEnvelope,
            api_version="v2beta1",
        )

    # Project instances and databases
    async def list_project_instances(self, organizationId: str, projectId: str):
        """List project instances (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances",
            model=ProjectInstancesResponse,
            api_version="v2beta1",
        )

    async def create_project_instance(
        self,
        organizationId: str,
        projectId: str,
        details: CreateProjectInstanceRequest,
    ):
        """Create a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/instances",
            body=details,
            model=ProjectInstanceResponse,
            api_version="v2beta1",
        )

    async def get_project_instance(
        self, organizationId: str, projectId: str, instanceId: str
    ):
        """Get a project instance by id (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}",
            model=ProjectInstanceResponse,
            api_version="v2beta1",
        )

    async def delete_project_instance(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
    ):
        """Delete a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}",
            api_version="v2beta1",
        )

    async def list_project_instance_databases(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
    ):
        """List databases for a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases",
            model=ProjectDatabasesResponse,
            api_version="v2beta1",
        )

    async def create_project_instance_database(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        details: CreateProjectDatabaseRequest,
    ):
        """Create a database for a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases",
            body=details,
            model=ProjectDatabaseResponse,
            api_version="v2beta1",
        )

    async def get_project_instance_database(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
    ):
        """Get a database by id for a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}",
            model=ProjectDatabaseResponse,
            api_version="v2beta1",
        )

    async def delete_project_instance_database(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
    ):
        """Delete a database from a project instance (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}",
            api_version="v2beta1",
        )

    async def list_project_database_backups(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
    ):
        """List backups for a project instance database (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}/backups",
            model=ProjectDatabaseBackupsResponse,
            api_version="v2beta1",
        )

    async def create_project_database_backup(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
    ):
        """Create/schedule a backup for a project instance database (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}/backups",
            model=CreateProjectDatabaseBackupResponse,
            api_version="v2beta1",
        )

    async def get_project_database_backup(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
        backupId: str,
    ):
        """Get a backup by id for a project instance database (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}/backups/{backupId}",
            model=ProjectDatabaseBackupResponse,
            api_version="v2beta1",
        )

    async def restore_project_instance_database(
        self,
        organizationId: str,
        projectId: str,
        instanceId: str,
        databaseId: str,
        details: RestoreProjectDatabaseRequest,
    ):
        """Restore a project instance database (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/instances/{instanceId}/databases/{databaseId}/restore",
            body=details,
            model=ProjectDatabaseResponse,
            api_version="v2beta1",
        )

    # --- Fleet Manager Deployment Methods (v2beta1) ---

    async def list_deployments(self, organizationId: str, projectId: str):
        """List all Fleet Manager deployments for a project (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments",
            model=DeploymentsResponse,
            api_version="v2beta1",
        )

    async def create_deployment(
        self, organizationId: str, projectId: str, details: CreateDeploymentRequest
    ):
        """Create a new Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments",
            body=details,
            model=DeploymentResponse,
            api_version="v2beta1",
        )

    async def get_deployment(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Get details of a specific Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}",
            model=DeploymentDetailsResponse,
            api_version="v2beta1",
        )

    async def delete_deployment(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Delete/unregister a Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}",
            api_version="v2beta1",
        )

    async def get_deployment_databases(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Get logical databases for a deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/databases",
            model=DatabasesResponse,
            api_version="v2beta1",
        )

    async def get_deployment_servers(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Get servers for a deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/servers",
            model=ServersResponse,
            api_version="v2beta1",
        )

    async def get_deployment_server_databases(
        self, organizationId: str, projectId: str, deploymentId: str, serverId: str
    ):
        """Get physical databases for a server on a deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/servers/{serverId}/databases",
            model=ServerDatabasesResponse,
            api_version="v2beta1",
        )

    async def create_deployment_token(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Create a token for a Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/token",
            model=DeploymentTokenResponse,
            api_version="v2beta1",
        )

    async def update_deployment_token(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Update/rotate a token for a Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._patch(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/token",
            body=JobIdEnvelope(),
            model=DeploymentTokenResponse,
            api_version="v2beta1",
        )

    async def delete_deployment_token(
        self, organizationId: str, projectId: str, deploymentId: str
    ):
        """Delete a token for a Fleet Manager deployment (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/fleet-manager/deployments/{deploymentId}/token",
            api_version="v2beta1",
        )

    # --- Activity Feed Methods (v2beta1) ---

    async def get_organization_activity_feed(
        self,
        organizationId: str,
        start: str = None,
        end: str = None,
        page_limit: int = None,
        page_token: str = None,
    ):
        """Get activity feed for an organization (v2beta1).

        Args:
            organizationId: the organization id
            start: ISO 8601 datetime to filter by start time (optional)
            end: ISO 8601 datetime to filter by end time (optional)
            page_limit: number of items per page (optional)
            page_token: pagination token (optional, cannot be combined with other query params)

        Returns: ActivityFeedResponse with 'data' key containing list of ActivityLog objects.
        """
        self._ensure_api_is_v2()
        path = f"organizations/{organizationId}/activity-feed"
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_limit:
            params["page_limit"] = page_limit
        if page_token:
            params["page_token"] = page_token
        result = await self._get(
            path,
            model=ActivityFeedResponse,
            api_version="v2beta1",
            params=params if params else None,
        )
        if result and result.data:
            result.data = [ActivityLog(**item) for item in result.data]
        return result

    async def get_project_activity_feed(
        self,
        organizationId: str,
        projectId: str,
        start: str = None,
        end: str = None,
        page_limit: int = None,
        page_token: str = None,
    ):
        """Get activity feed for a project (v2beta1).

        Args:
            organizationId: the organization id
            projectId: the project id
            start: ISO 8601 datetime to filter by start time (optional)
            end: ISO 8601 datetime to filter by end time (optional)
            page_limit: number of items per page (optional)
            page_token: pagination token (optional, cannot be combined with other query params)

        Returns: ActivityFeedResponse with 'data' key containing list of ActivityLog objects.
        """
        self._ensure_api_is_v2()
        path = f"organizations/{organizationId}/projects/{projectId}/activity-feed"
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_limit:
            params["page_limit"] = page_limit
        if page_token:
            params["page_token"] = page_token

        result = await self._get(
            path,
            model=ActivityFeedResponse,
            api_version="v2beta1",
            params=params if params else None,
        )
        if result and result.data:
            result.data = [ActivityLog(**item) for item in result.data]
        return result

    # --- Agents Methods (v2beta1) ---

    async def list_agents(self, organizationId: str, projectId: str):
        """List all agents for a project (v2beta1)."""
        self._ensure_api_is_v2()
        items = await self._get(
            f"organizations/{organizationId}/projects/{projectId}/agents",
            model=None,
            api_version="v2beta1",
        )
        return [ListAgentResponse(**item) for item in items]

    async def create_agent(
        self, organizationId: str, projectId: str, details: CreateAgentRequest
    ):
        """Create an agent for a project (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/agents",
            body=details,
            model=AgentDetails,
            api_version="v2beta1",
        )

    async def get_agent(self, organizationId: str, projectId: str, agentId: str):
        """Get a specific agent by ID (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._get(
            f"organizations/{organizationId}/projects/{projectId}/agents/{agentId}",
            model=GetAgentResponse,
            api_version="v2beta1",
        )

    async def update_agent(
        self,
        organizationId: str,
        projectId: str,
        agentId: str,
        details: CreateAgentRequest,
    ):
        """Update an existing agent (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._put(
            f"organizations/{organizationId}/projects/{projectId}/agents/{agentId}",
            body=details,
            model=AgentDetails,
            api_version="v2beta1",
        )

    async def patch_agent(
        self,
        organizationId: str,
        projectId: str,
        agentId: str,
        details: PatchAgentRequest,
    ):
        """Partially update an existing agent (v2beta1).

        This method allows updating only the fields provided in the request.

        Args:
            organizationId: the organization id
            projectId: the project id
            agentId: the agent id to patch
            details: PatchAgentRequest with only the fields to update

        Returns: AgentDetails with the updated agent information.
        """
        self._ensure_api_is_v2()
        return await self._patch(
            f"organizations/{organizationId}/projects/{projectId}/agents/{agentId}",
            body=details,
            model=AgentDetails,
            api_version="v2beta1",
        )

    async def delete_agent(self, organizationId: str, projectId: str, agentId: str):
        """Delete an agent by ID (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._delete(
            f"organizations/{organizationId}/projects/{projectId}/agents/{agentId}",
            api_version="v2beta1",
        )

    async def invoke_agent(
        self,
        organizationId: str,
        projectId: str,
        agentId: str,
        details: InvokeAgentRequest,
    ):
        """Invoke an agent with input text or chat messages (v2beta1)."""
        self._ensure_api_is_v2()
        return await self._post(
            f"organizations/{organizationId}/projects/{projectId}/agents/{agentId}/invoke",
            body=details,
            model=InvokeAgentResponse,
            api_version="v2beta1",
        )
