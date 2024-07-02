from typing import List

from pydantic import BaseModel


# Model Defintion Here:
#   https://neo4j.com/docs/aura/platform/api/specification/#/


class AuraError(BaseModel):
    message: str
    reason: str
    field: str=""


class AuraErrors(BaseModel):
    errors: List[AuraError]


# TODO: Exactly what interfaces should be exposed on this exception is TBD.
#       This is just a starting point.
class AuraApiException(Exception):
    def __init__(self, errors: AuraErrors):
        self.errors = errors
        super().__init__(errors)

class AuraApiAuthorizationException(AuraApiException):
    def __init__(self, errors: AuraErrors,status:int):
        self.status = status
        super().__init__(errors)

class AuraApiNotFoundException(AuraApiException):
    def __init__(self, errors: AuraErrors,status:int):
        self.status = status
        super().__init__(errors)

class AuraApiBadRequestException(AuraApiException):
    def __init__(self, errors: AuraErrors,status:int):
        self.status = status
        super().__init__(errors)

class AuraApiInternalException(AuraApiException):
    def __init__(self, errors: AuraErrors,status:int):
        self.status = status
        super().__init__(errors)

class AuraApiRateLimitExceededException(AuraApiException):
    def __init__(self, errors: AuraErrors,status:int):
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
    connection_url: str=""
    memory: str=""
    metrics_integration_url: str=""
    region: str
    secondaries_count: int=0
    cdc_enrichment_mode: str=""
    status: str=""
    storage: str=""
    type: str
    customer_managed_key_id: str=""
    graph_nodes: str=""
    graph_relationships: str=""
    username: str=""
    password: str=""

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
    exportable: bool=False
    instance_id: str=""
    profile: str=""
    status: str=""
    timestamp: str=""

class SnapshotsResponse(BaseModel):
    data: List[Snapshot]

class SnapshotResponse(BaseModel):
    data: Snapshot

class CustomerManagedKeySummary(BaseModel):
    id: str
    name: str=""
    tenant_id: str=""

class CustomerManagedKeysResponse(BaseModel):
    data: List[CustomerManagedKeySummary]

class CustomerManagedKey(CustomerManagedKeySummary):
    created: str=""
    cloud_provider: str=""
    key_id: str=""
    region: str=""
    type: str=""
    status: str=""

class CustomerManagedKeyResponse(BaseModel):
    data: CustomerManagedKey

class CustomerManagedKeyRequest(BaseModel):
    key_id: str
    name: str
    cloud_provider: str
    instance_type: str
    region: str
    tenant_id: str
