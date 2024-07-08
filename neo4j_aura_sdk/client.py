import os
import time
import json
from typing import Type

import httpx
from pydantic import BaseModel
import pydantic_core

from .models import *


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

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.neo4j.io",
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._token = None
        self._token_expiration = 0
        self._client = httpx.AsyncClient()

    @classmethod
    def from_env(cls):
        client_id = os.environ["AURA_API_CLIENT_TOKEN"]
        client_secret = os.environ["AURA_API_CLIENT_SECRET"]
        return cls(client_id, client_secret)

    # AsyncClient is a context manager, so we need to implement __aenter__ and
    # __aexit__ to make this class a context manager as well. This allows us to
    # use the `async with` syntax.

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)

    def _checkResponseStatus(self, response: httpx.Response):
        if(response.status_code < 400):
            return
        elif(response.status_code in [400,415]):
            raise AuraApiBadRequestException(AuraErrors(**response.json()),response.status_code)
        elif(response.status_code in [401,403]):
            # HACK: the oauth endpoint returns a single object with different properties
            try:
                errors = AuraErrors(**response.json())
            except pydantic_core._pydantic_core.ValidationError:
                body = response.json()
                reason = None
                if("error_description" in body):
                    reason = body['error_desctiprion']
                errors = AuraErrors(errors = [AuraError(message=body['error'],reason=reason)])
            raise AuraApiAuthorizationException(errors,response.status_code)
        elif(response.status_code == 404):
            raise AuraApiNotFoundException(AuraErrors(**response.json()),response.status_code)
        elif(response.status_code == 429):
            raise AuraApiRateLimitExceededException(AuraErrors(**response.json()),response.status_code)
        elif(response.status_code >= 500):
            raise AuraApiInternalException(AuraErrors(**response.json()),response.status_code)
        else:
            raise AuraApiException(AuraErrors(**response.json()))

    async def _get_token(self):
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

    async def _get(self, path: str, model: Type[BaseModel]):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get(f"{self._base_url}/v1/{path}", headers=headers)
        self._checkResponseStatus(response)
        return model(**response.json())

    async def _post(self, path: str, model: Type[BaseModel], body: Type[BaseModel]=None):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json","accept":"application/json"}
        data = "{}"
        if(body):
            data= body.model_dump_json()
        response = await self._client.post(f"{self._base_url}/v1/{path}", 
            headers=headers,
            content=data)
        self._checkResponseStatus(response)
        return model(**response.json())

    async def _delete(self, path: str, model: Type[BaseModel], default: BaseModel = {}):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.delete(f"{self._base_url}/v1/{path}", headers=headers)
        self._checkResponseStatus(response)
        try:
            return model(**response.json())
        except json.decoder.JSONDecodeError:
            return default

    async def _patch(self, path: str, body: Type[BaseModel], model: Type[BaseModel]):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json","accept":"application/json"}
        response = await self._client.patch(f"{self._base_url}/v1/{path}", 
            headers=headers,
            content=body.model_dump_json())
        self._checkResponseStatus(response)
        return model(**response.json())

    async def tenants(self):
        return await self._get("tenants", model=TenantsResponse)

    async def tenant(self, tenantId: str):
        return await self._get(f"tenants/{tenantId}", model=TenantResponse)

    async def instances(self, tenantId: str = ""):
        path = "instances"
        if tenantId:
            path+=f"?tenantId={tenantId}"
        return await self._get(path, model=InstancesResponse)

    async def instance(self, instanceId: str):
        return await self._get(f"instances/{instanceId}", model=InstanceResponse)

    async def createInstance(self, details: InstanceRequest):
        return await self._post("instances", body=details, model=InstanceResponse)

    async def deleteInstance(self, instanceId: str):
        return await self._delete(f"instances/{instanceId}",model=InstanceResponse)

    async def renameInstance(self, instanceId: str, name:str):
        class _Rename(BaseModel):
            name: str
        return await self._patch(f"instances/{instanceId}",body=_Rename(name=name),model=InstanceResponse)

    async def resizeInstance(self, instanceId: str, memory:str):
        class _Resize(BaseModel):
            memory: str
        return await self._patch(f"instances/{instanceId}",body=_Resize(memory=memory),model=InstanceResponse)

    async def renameAndResizeInstance(self, instanceId: str, name: str, memory:str):
        class _RenameResize(BaseModel):
            name: str
            memory: str
        return await self._patch(f"instances/{instanceId}",body=_RenameResize(name=name,memory=memory),model=InstanceResponse)

    async def resizeInstanceSecondaryCount(self, instanceId: str, count:int):
        class _Resize(BaseModel):
            secondaries_count: int
        return await self._patch(f"instances/{instanceId}",body=_Resize(secondaries_count=count),model=InstanceResponse)

    async def updateInstanceCDCMode(self, instanceId: str, mode:str):
        class _Resize(BaseModel):
            cdc_enrichment_mode: str
        return await self._patch(f"instances/{instanceId}",body=_Resize(cdc_enrichment_mode=mode),model=InstanceResponse)

    async def overwriteInstance(self, instanceId: str, sourceId: str):
        class _Overwrite(BaseModel):
            source_instance_id: str
        return await self._post(f"instances/{instanceId}/overwrite",body=_Overwrite(source_instance_id=sourceId),model=InstanceResponse)

    async def overwriteInstanceWithSnapshot(self, instanceId: str, sourceId: str, snapshotId:str):
        class _Overwrite(BaseModel):
            source_instance_id: str
            source_snapshot_id: str
        return await self._post(f"instances/{instanceId}/overwrite",body=_Overwrite(source_instance_id=sourceId,source_snapshot_id=snapshotId),model=InstanceResponse)

    async def pauseInstance(self, instanceId: str):
        return await self._post(f"instances/{instanceId}/pause",model=InstanceResponse)

    async def resumeInstance(self, instanceId: str):
        return await self._post(f"instances/{instanceId}/resume",model=InstanceResponse)

    async def restoreInstance(self, instanceId: str, snapshotId: str):
        return await self._post(f"instances/{instanceId}/snapshots/{snapshotId}/restore",model=InstanceResponse)

    async def snapshotInstance(self, instanceId: str):
        return await self._post(f"instances/{instanceId}/snapshots",model=SnapshotResponse)

    async def instanceSizing(self, details: InstanceSizingRequest):
        return await self._post("instances/sizing",body=details, model=InstanceSizingResponse)

    async def snapshots(self, instanceId: str, date: str = ""):
        path = f"instances/{instanceId}/snapshots"
        if date:
            path+=f"?date={date}"
        return await self._get(path, model=SnapshotsResponse)

    async def snapshot(self, instanceId: str, snapshotId: str):
        return await self._get(f"instances/{instanceId}/snapshots/{snapshotId}", model=SnapshotResponse)

    async def customerManagedKeys(self, tenantId: str = ""):
        path = "customer-managed-keys"
        if tenantId:
            path+=f"?tenantId={tenantId}"
        return await self._get(path, model=CustomerManagedKeysResponse)

    async def customerManagedKey(self, customerManagedKeyId: str):
        return await self._get(f"customer-managed-keys/{customerManagedKeyId}", model=CustomerManagedKeyResponse)

    async def createCustomerManagedKey(self, details: CustomerManagedKeyRequest):
        return await self._post("customer-managed-keys",body=details, model=CustomerManagedKeyResponse)

    async def deleteCustomerManagedKey(self, customerManagedKeyId: str):
        default = CustomerManagedKeyResponse(data = CustomerManagedKey(id=customerManagedKeyId,status='deleted'))
        return await self._delete(f"customer-managed-keys/{customerManagedKeyId}", model=CustomerManagedKeyResponse, default=default)
