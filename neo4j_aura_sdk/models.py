from typing import List, Optional

from pydantic import BaseModel

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
