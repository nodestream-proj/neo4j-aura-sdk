from typing import List, Optional

from pydantic import BaseModel
# --- v1beta5 GraphQL Data API models ---
class ProjectMetricsIntegrationResponse(BaseModel):
    url: str
    enabled: bool
    # Add other fields as per v1beta5 spec if needed

class InstanceUpgradeRequest(BaseModel):
    memory: Optional[str] = None
    storage: Optional[str] = None
    version: Optional[str] = None
    # Add other upgradable fields as per v1beta5 spec if needed

class GraphQLDataAPISummary(BaseModel):
    id: str
    name: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None

class GraphQLDataAPI(GraphQLDataAPISummary):
    type_definitions: Optional[str] = None
    security: Optional[dict] = None

class GraphQLDataAPISummaryWithAuthProviders(GraphQLDataAPISummary):
    authentication_providers: Optional[list] = None

class DataApiAuthProviderSummary(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    enabled: Optional[bool] = None

class DataApiApiKeyAuthProvider(DataApiAuthProviderSummary):
    key: Optional[str] = None

class DataApiJwksAuthProvider(DataApiAuthProviderSummary):
    url: Optional[str] = None

class DataApiAuthProviderWithApiKey(DataApiApiKeyAuthProvider):
    pass

class DataApiAuthProviderCreateInput(BaseModel):
    name: str
    type: str
    url: Optional[str] = None

class DataApiApiKeyAuthProviderEditInput(BaseModel):
    name: Optional[str] = None

class DataApiJwksAuthProviderEditInput(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


# PATCH /instances/{instanceId} request model (all fields optional)
class InstancePatchRequest(BaseModel):
    name: Optional[str] = None
    memory: Optional[str] = None
    storage: Optional[str] = None
    vector_optimized: Optional[bool] = None
    graph_analytics_plugin: Optional[bool] = None
    secondaries_count: Optional[int] = None
    cdc_enrichment_mode: Optional[str] = None

# Model Defintion Here:
#   https://neo4j.com/docs/aura/platform/api/specification/#/


class AuraError(BaseModel):
    message: str
    reason: Optional[str] = None
    field: Optional[str] = None


class AuraErrors(BaseModel):
    errors: List[AuraError]


# TODO: Exactly what interfaces should be exposed on this exception is TBD.
#       This is just a starting point.
class AuraApiException(Exception):
    errors: List[AuraError]

    def __init__(self, errors: AuraErrors):
        self.errors = errors.errors
        super().__init__(errors)


class AuraApiAuthorizationException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuraApiNotFoundException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuraApiBadRequestException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuraApiInternalException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuraApiRateLimitExceededException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


class TenantSummary(BaseModel):
    id: str
    name: str


class TenantsResponse(BaseModel):
    data: List[TenantSummary]


class InstanceConfiguration(BaseModel):
    region: str
    region_name: str
    type: str
    memory: str
    version: str
    cloud_provider: str


class Tenant(TenantSummary):
    instance_configurations: List[InstanceConfiguration]


class TenantResponse(BaseModel):
    data: Tenant


class InstanceSummary(BaseModel):
    id: str
    name: str
    tenant_id: str
    cloud_provider: str


class InstancesResponse(BaseModel):
    data: List[InstanceSummary]


class Instance(InstanceSummary):
    connection_url: Optional[str] = None
    memory: Optional[str] = None
    metrics_integration_url: Optional[str] = None
    region: str
    secondaries_count: Optional[int] = None
    cdc_enrichment_mode: Optional[str] = None
    status: Optional[str] = None
    storage: Optional[str] = None
    type: str
    customer_managed_key_id: Optional[str] = None
    graph_nodes: Optional[str] = None
    graph_relationships: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    vector_optimized: Optional[bool] = None
    graph_analytics_plugin: Optional[bool] = None


class InstanceSizingRequest(BaseModel):
    node_count: int
    relationship_count: int
    instance_type: str
    algorithm_categories: List[str]


class InstanceSizing(BaseModel):
    did_exceed_maximum: bool
    min_required_memory: str
    recommended_size: str


class InstanceSizingResponse(BaseModel):
    data: InstanceSizing


class InstanceResponse(BaseModel):
    data: Instance


class InstanceRequest(BaseModel):
    name: str
    tenant_id: str
    cloud_provider: str
    memory: str
    region: str
    type: str
    version: str


class Snapshot(BaseModel):
    snapshot_id: str
    exportable: bool = False
    instance_id: Optional[str] = None
    profile: Optional[str] = None
    status: Optional[str] = None
    timestamp: Optional[str] = None


class SnapshotsResponse(BaseModel):
    data: List[Snapshot]


class SnapshotResponse(BaseModel):
    data: Snapshot


class CustomerManagedKeySummary(BaseModel):
    id: str
    name: Optional[str] = None
    tenant_id: Optional[str] = None


class CustomerManagedKeysResponse(BaseModel):
    data: List[CustomerManagedKeySummary]


class CustomerManagedKey(CustomerManagedKeySummary):
    created: Optional[str] = None
    cloud_provider: Optional[str] = None
    key_id: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class CustomerManagedKeyResponse(BaseModel):
    data: CustomerManagedKey


class CustomerManagedKeyRequest(BaseModel):
    key_id: str
    name: str
    cloud_provider: str
    instance_type: str
    region: str
    tenant_id: str


# --- Models from v2beta1 OpenAPI spec ---
class IpFilterAllowListItem(BaseModel):
    address: str
    prefix_len: int
    description: Optional[str] = None


class FilteredEntities(BaseModel):
    instances: Optional[List[str]] = []
    projects: Optional[List[str]] = []
    organizations: Optional[List[str]] = []


class IpFilter(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    organization_id: Optional[str] = None
    allow_list: Optional[List[IpFilterAllowListItem]] = []
    filtering_disabled: Optional[bool] = False
    filtered_entities: Optional[FilteredEntities] = FilteredEntities()
    updated_at: Optional[str] = None


class IpFilterWithStatus(IpFilter):
    status: Optional[str] = None


class CreateImportJobRequest(BaseModel):
    importModelId: str
    auraCredentials: Optional[dict] = None


class ImportExitStatus(BaseModel):
    state: Optional[str] = None
    message: Optional[str] = None


class NodeProgress(BaseModel):
    id: Optional[str] = None
    labels: Optional[List[str]] = None
    total_rows: Optional[int] = None
    processed_rows: Optional[int] = None
    created_nodes: Optional[int] = None
    created_constraints: Optional[int] = None
    created_indexes: Optional[int] = None


class RelationshipProgress(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    total_rows: Optional[int] = None
    processed_rows: Optional[int] = None
    created_relationships: Optional[int] = None
    created_constraints: Optional[int] = None
    created_indexes: Optional[int] = None


class ImportJobProgress(BaseModel):
    nodes: Optional[List[NodeProgress]] = None
    relationships: Optional[List[RelationshipProgress]] = None


class ImportJobInfo(BaseModel):
    state: Optional[str] = None
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    exit_status: Optional[ImportExitStatus] = None
    cancellation_requested_time: Optional[str] = None
    submitted_time: Optional[str] = None
    last_update_time: Optional[str] = None
    percentage_complete: Optional[float] = None
    progress: Optional[ImportJobProgress] = None


class ImportJobData(BaseModel):
    id: Optional[str] = None
    import_type: Optional[str] = None
    info: Optional[ImportJobInfo] = None
    data_source: Optional[dict] = None
    aura_target: Optional[dict] = None
    user_id: Optional[str] = None


class ImportJobEnvelope(BaseModel):
    data: Optional[ImportJobData] = None


class JobIdEnvelope(BaseModel):
    data: Optional[dict] = None

