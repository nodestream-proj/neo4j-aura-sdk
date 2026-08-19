from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator


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


class AuraApiUnsupportedActionException(AuraApiException):
    def __init__(self, errors: AuraErrors, status: int):
        self.status = status
        super().__init__(errors)


class AuraApiValidationException(AuraApiException):
    """Raised on HTTP 422 Unprocessable Entity.

    Indicates the request body failed server-side validation, a resource limit
    was reached, or the operation is unsupported for the target resource type.
    """

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
    importConfig: Optional[dict] = None


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


# --- Fleet Manager Deployment Models (v2beta1) ---
class DeploymentToken(BaseModel):
    claimed_time: Optional[str] = None
    created_by: Optional[str] = None
    creation_time: Optional[str] = None
    release_time: Optional[str] = None
    last_used_time: Optional[str] = None
    expiry_time: Optional[str] = None
    auto_rotate: Optional[bool] = None


class DeploymentDBMS(BaseModel):
    edition: Optional[str] = None
    packaging: Optional[str] = None
    metric_collection_enabled: Optional[bool] = None


class Deployment(BaseModel):
    id: str
    name: str
    status: Optional[str] = None
    connection_url: Optional[str] = None
    created_by: Optional[str] = None


class DetailedDeployment(Deployment):
    dbms: Optional[DeploymentDBMS] = None
    token: Optional[DeploymentToken] = None


class Database(BaseModel):
    node_count: Optional[int] = None
    relationship_count: Optional[int] = None
    aliases: Optional[List[str]] = None
    access: Optional[str] = None
    default: Optional[bool] = None
    requested_status: Optional[str] = None
    current_primaries_count: Optional[str] = None
    current_secondaries_count: Optional[str] = None
    requested_primaries_count: Optional[str] = None
    requested_secondaries_count: Optional[str] = None
    creation_time: Optional[str] = None
    last_start_time: Optional[str] = None
    store: Optional[str] = None


class License(BaseModel):
    type: Optional[str] = None
    state: Optional[str] = None
    days_left_on_trial: Optional[int] = None
    total_trial_days: Optional[int] = None


class Plugin(BaseModel):
    filename: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None


class Server(BaseModel):
    address: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    mode_constraints: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    last_ping: Optional[str] = None
    plugin_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    jvm_version: Optional[str] = None
    jvm_vendor: Optional[str] = None
    license: Optional[License] = None
    plugins: Optional[List[Plugin]] = None


class ServerDatabase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    current_status: Optional[str] = None
    status_message: Optional[str] = None
    writer: Optional[bool] = None
    last_committed_txn: Optional[int] = None
    replication_lag: Optional[int] = None
    graph_shards: Optional[List[str]] = None
    property_shards: Optional[List[str]] = None


class CreateDeploymentRequest(BaseModel):
    name: str
    connection_url: Optional[str] = None


# --- Organization & Project Response Models (v2beta1) ---
class OrganizationDetailsEnvelope(BaseModel):
    data: Optional[Union[List[Dict], Dict]] = None


class ProjectsResponse(BaseModel):
    data: Optional[List[dict]] = None


# --- Deployment Models (v2beta1) ---
class DeploymentDbms(BaseModel):
    edition: Optional[str] = None
    packaging: Optional[str] = None


class DeploymentSummary(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    connection_url: Optional[str] = None


class Deployment(DeploymentSummary):
    dbms: Optional[DeploymentDbms] = None


class DeploymentsResponse(BaseModel):
    data: Optional[List[Deployment]] = None


# For create_deployment response which returns the deployment directly
class DeploymentResponse(Deployment):
    pass


# For get_deployment response which wraps in data envelope
class DeploymentDetailsResponse(BaseModel):
    data: Optional[Deployment] = None


class DatabasesResponse(BaseModel):
    data: Optional[List[Database]] = None


class ServersResponse(BaseModel):
    data: Optional[List[Server]] = None


class ServerDatabasesResponse(BaseModel):
    data: Optional[List[ServerDatabase]] = None


class DeploymentTokenResponse(BaseModel):
    token: Optional[str] = None


class ActivityFeedResponse(BaseModel):
    data: Optional[List] = None


# --- Activity Feed Models (v2beta1) ---
class ActivityLog(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[int] = None
    logged_at: Optional[str] = None
    status: Optional[str] = None
    org_id: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    action_id: Optional[str] = None
    action_name: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    payload: Optional[str] = None


# --- Billing Models (v2beta1) ---
class UsageData(BaseModel):
    charge_period_start: Optional[str] = None
    charge_period_end: Optional[str] = None
    organization_id: Optional[str] = None
    billing_account_id: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    tier: Optional[str] = None
    cloud_service_provider: Optional[str] = None
    region_id: Optional[str] = None
    billable_size_unit: Optional[str] = None
    billable_size: Optional[int] = None
    consumed_quantity: Optional[float] = None
    consumed_unit: Optional[str] = None
    pricing_currency: Optional[str] = None
    list_cost: Optional[float] = None
    list_unit_price: Optional[float] = None
    service_name: Optional[str] = None
    billing_account_type: Optional[str] = None
    payment_method: Optional[str] = None
    invoice_issuer_name: Optional[str] = None


class LedgerData(BaseModel):
    organization_id: Optional[str] = None
    billing_account_id: Optional[str] = None
    balance_date: Optional[str] = None
    remaining_credit_quantity: Optional[float] = None
    initial_credit_quantity: Optional[float] = None


class Links(BaseModel):
    self: Optional[str] = None
    next: Optional[str] = None
    first: Optional[str] = None


class UsageResponse(BaseModel):
    data: Optional[List[UsageData]] = None
    links: Optional[Links] = None


class LedgerResponse(BaseModel):
    data: Optional[List[LedgerData]] = None
    links: Optional[Links] = None


# --- Agents Models (v2beta1) ---
class AgentInputMessage(BaseModel):
    role: str
    content: str


class SimilaritySearchToolParameters(BaseModel):
    provider: str
    model: str
    index: str
    top_k: Optional[int] = None
    dimension: Optional[int] = None
    dimensions: Optional[int] = None
    post_processing_cypher: Optional[str] = None


class AgentToolSummary(BaseModel):
    name: str
    type: str


class AgentTool(AgentToolSummary):
    enabled: Optional[bool] = None
    description: Optional[str] = None
    parameters: Optional[Union[SimilaritySearchToolParameters, Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    extra_params: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_similarity_search_tool(self):
        if self.type != "similaritySearch":
            return self

        if self.parameters is None and self.config is None:
            raise ValueError(
                "similaritySearch tools require `parameters` or `config` with provider, model, and index"
            )

        if isinstance(self.parameters, dict):
            self.parameters = SimilaritySearchToolParameters(**self.parameters)

        if self.config is not None:
            self.config = SimilaritySearchToolParameters(**self.config).model_dump(
                exclude_none=True
            )

        return self


class CreateAgentRequest(BaseModel):
    name: str
    description: str
    dbid: str
    is_private: bool
    tools: List[AgentTool]
    system_prompt: Optional[str] = None
    is_mcp_enabled: Optional[bool] = None
    enabled: Optional[bool] = None


class ListAgentResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    project_id: Optional[str] = None
    organization_id: Optional[str] = None
    system_prompt: Optional[str] = None
    dbid: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_private: Optional[bool] = None
    is_mcp_enabled: Optional[bool] = None
    tools: Optional[List[AgentToolSummary]] = None
    endpoint_link: Optional[str] = None
    mcp_endpoint_link: Optional[str] = None
    avatar_color: Optional[str] = None
    avatar_icon: Optional[str] = None
    enabled: Optional[bool] = None


class GetAgentResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    project_id: Optional[str] = None
    organization_id: Optional[str] = None
    system_prompt: Optional[str] = None
    dbid: Optional[str] = None
    is_private: Optional[bool] = None
    is_mcp_enabled: Optional[bool] = None
    tools: Optional[List[AgentTool]] = None
    enabled: Optional[bool] = None


class AgentDetails(GetAgentResponse):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    endpoint_link: Optional[str] = None
    avatar_color: Optional[str] = None
    avatar_icon: Optional[str] = None


class InvokeAgentRequest(BaseModel):
    input: Union[str, List[AgentInputMessage]]
    stream: Optional[bool] = None


class InvokeAgentContentBlock(BaseModel):
    type: Optional[str] = None
    text: Optional[str] = None
    thinking: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    tool_use_id: Optional[str] = None


class InvokeAgentError(BaseModel):
    message: Optional[str] = None
    type: Optional[str] = None
    status_code: Optional[int] = None


class InvokeAgentUsage(BaseModel):
    request_tokens: Optional[int] = None
    response_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class InvokeAgentResponse(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None
    content: Optional[List[InvokeAgentContentBlock]] = None
    end_reason: Optional[str] = None
    status: Optional[str] = None
    error: Optional[InvokeAgentError] = None
    usage: Optional[InvokeAgentUsage] = None


# --- Organization User Models (v2beta1) ---
class MfaEnrolledMethod(BaseModel):
    id: str
    enrolled_at: str


class OrganizationUser(BaseModel):
    user_id: str
    email: str
    organization_roles: List[str]
    exempt_from_automatic_removal: bool
    mfa_enrollment_status: str
    mfa_enrolled_methods: Optional[List[MfaEnrolledMethod]] = None
    last_activity_at: Optional[str] = None


class OrganizationUserProject(BaseModel):
    id: str
    name: str
    project_roles: List[str]


class OrganizationUserDetails(OrganizationUser):
    projects: List[OrganizationUserProject]


# --- Organization Details Model (v2beta1) ---
class OrganizationDetails(BaseModel):
    id: str
    name: str


# --- Project Details Model (v2beta1) ---
class ProjectDetails(BaseModel):
    id: str
    name: str


# --- Project User Models (v2beta1) ---
class ProjectUser(BaseModel):
    user_id: str
    email: str
    project_roles: List[str]


class PatchProjectUserRequest(BaseModel):
    project_roles: List[str]


# --- Cypher Template Tool Models (v2beta1) ---
class CypherParameterConfig(BaseModel):
    name: str
    data_type: str
    description: str


class CypherTemplateTool(BaseModel):
    type: str = "cypherTemplate"
    name: str
    enabled: Optional[bool] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    extra_params: Optional[Dict[str, Any]] = None


# --- Text2Cypher Tool Model (v2beta1) ---
class Text2CypherTool(BaseModel):
    type: str = "text2cypher"
    name: str
    enabled: Optional[bool] = None
    description: Optional[str] = None


# --- Patch Agent Request Model (v2beta1) ---
class PatchAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    dbid: Optional[str] = None
    is_private: Optional[bool] = None
    is_mcp_enabled: Optional[bool] = None
    tools: Optional[List[AgentTool]] = None
    enabled: Optional[bool] = None


# --- Billing Error Models (v2beta1) ---
class BillingErrorItem(BaseModel):
    error: str
    message: str


class BillingErrorResponse(BaseModel):
    errors: List[BillingErrorItem]


# --- Newly added v2beta1 models from JSON spec ---
class OpenRequestModel(BaseModel):
    """Request model that accepts additional fields to stay forward-compatible."""

    model_config = ConfigDict(extra="allow")


class CreateOrganizationInviteRequest(OpenRequestModel):
    email: str
    roles: Optional[List[str]] = None
    project_invites: Optional[List[dict]] = None


class OrganizationInvite(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    invited_by: Optional[str] = None
    organization_id: Optional[str] = None
    organization_roles: Optional[List[str]] = None
    project_invites: Optional[List[dict]] = None
    status: Optional[str] = None
    expires_at: Optional[str] = None


class OrganizationInvitesResponse(BaseModel):
    data: Optional[List[OrganizationInvite]] = None


class OrganizationInviteResponse(BaseModel):
    data: Optional[OrganizationInvite] = None


class AddProjectUserRequest(OpenRequestModel):
    user_id: Optional[str] = None
    project_roles: Optional[List[str]] = None


class GDSError(BaseModel):
    id: Optional[str] = None
    message: Optional[str] = None
    reason: Optional[str] = None


class SessionCreatedBy(BaseModel):
    type: Optional[str] = None
    console_user_id: Optional[str] = None
    database_username: Optional[str] = None
    database_uuid: Optional[str] = None


class SessionResponse(BaseModel):
    id: Optional[str] = None
    instance_id: Optional[str] = None
    database_id: Optional[str] = None
    name: Optional[str] = None
    memory: Optional[str] = None
    status: Optional[str] = None
    host: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[SessionCreatedBy] = None
    cloud_provider: Optional[str] = None
    region: Optional[str] = None
    expiry_date: Optional[str] = None
    ttl: Optional[str] = None


class SessionsResponse(BaseModel):
    data: Optional[List[SessionResponse]] = None
    errors: Optional[List[GDSError]] = None


class SessionEnvelope(BaseModel):
    data: Optional[SessionResponse] = None
    errors: Optional[List[GDSError]] = None


class SessionSizeResponse(BaseModel):
    recommended_size: Optional[str] = None
    estimated_memory: Optional[str] = None


class SessionSizeEnvelope(BaseModel):
    data: Optional[SessionSizeResponse] = None
    errors: Optional[List[GDSError]] = None


class CreateGraphAnalyticsSessionRequest(OpenRequestModel):
    name: Optional[str] = None
    memory: Optional[str] = None
    instance_id: Optional[str] = None
    database_id: Optional[str] = None
    ttl: Optional[str] = None


class SessionSizingRequest(OpenRequestModel):
    instance_id: Optional[str] = None
    database_id: Optional[str] = None


class VirtualGraphPrice(BaseModel):
    amount: Optional[str] = None
    metric_unit: Optional[str] = None
    sku: Optional[str] = None


class VirtualGraphAllowedConfig(BaseModel):
    memory: Optional[str] = None
    price: Optional[VirtualGraphPrice] = None


class VirtualGraphAllowedConfigs(BaseModel):
    configs: Optional[List[VirtualGraphAllowedConfig]] = None
    default_memory: Optional[str] = None


class VirtualGraph(BaseModel):
    bolt_url: Optional[str] = None
    cloud_provider: Optional[str] = None
    created_at: Optional[str] = None
    data_source_id: Optional[str] = None
    data_source_type: Optional[str] = None
    error_detail: Optional[str] = None
    id: Optional[str] = None
    maximum_bytes_billed: Optional[int] = None
    memory: Optional[str] = None
    name: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = None


class VirtualGraphCreateData(VirtualGraph):
    plain_password: Optional[str] = None


class VirtualGraphsResponse(BaseModel):
    data: Optional[List[VirtualGraph]] = None
    links: Optional[Links] = None


class VirtualGraphResponse(BaseModel):
    data: Optional[VirtualGraph] = None


class VirtualGraphCreateResponse(BaseModel):
    data: Optional[VirtualGraphCreateData] = None


class VirtualGraphAllowedConfigsResponse(BaseModel):
    data: Optional[VirtualGraphAllowedConfigs] = None


class CreateVirtualGraphRequest(OpenRequestModel):
    cloud_provider: Optional[str] = None
    data_source_id: Optional[str] = None
    import_model_id: Optional[str] = None
    maximum_bytes_billed: Optional[int] = None
    memory: Optional[str] = None
    name: Optional[str] = None
    region: Optional[str] = None


class UpdateVirtualGraphRequest(OpenRequestModel):
    import_model_id: Optional[str] = None
    memory: Optional[str] = None
    name: Optional[str] = None


class CreateProjectInstanceRequest(OpenRequestModel):
    name: Optional[str] = None
    cloud_provider: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = None
    memory: Optional[str] = None
    storage: Optional[str] = None


class ProjectInstanceSummary(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    cloud_provider: Optional[str] = None
    created_at: Optional[str] = None


class ProjectInstancesResponse(BaseModel):
    data: Optional[List[ProjectInstanceSummary]] = None


class ProjectInstanceDetails(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    cloud_provider: Optional[str] = None
    region: Optional[str] = None
    memory: Optional[str] = None
    storage: Optional[str] = None
    vector_optimized: Optional[bool] = None
    multi_database: Optional[bool] = None
    legacy_status: Optional[str] = None
    connection_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ProjectInstanceResponse(BaseModel):
    data: Optional[ProjectInstanceDetails] = None


class CreateProjectDatabaseRequest(OpenRequestModel):
    name: Optional[str] = None


class ProjectDatabaseSummary(BaseModel):
    id: Optional[str] = None


class ProjectDatabasesResponse(BaseModel):
    data: Optional[List[ProjectDatabaseSummary]] = None


class ProjectDatabaseResponse(BaseModel):
    data: Optional[dict] = None


class ProjectDatabaseBackup(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    exportable: Optional[bool] = None


class ProjectDatabaseBackupsResponse(BaseModel):
    data: Optional[List[ProjectDatabaseBackup]] = None


class ProjectDatabaseBackupResponse(BaseModel):
    data: Optional[ProjectDatabaseBackup] = None


class CreateProjectDatabaseBackupResponse(BaseModel):
    data: Optional[dict] = None


class RestoreProjectDatabaseRequest(OpenRequestModel):
    source_instance_id: Optional[str] = None
    source_snapshot_id: Optional[str] = None
