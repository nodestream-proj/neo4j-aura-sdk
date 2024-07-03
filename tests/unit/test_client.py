import pytest
import respx
import httpx
import json
import os
import copy

from neo4j_aura_sdk import AuraClient,models

clientId = 'mockId'
clientSecret = 'mockSecret'
baseUrl = 'https://api.neo4j.io/'
apiUrl = f'{baseUrl}v1/'
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, 'responses.json')
with open(file_path,'r') as f:
    jsonResp = json.load(f)

tid = 'tenant2'
iid = 'instance2'

respx.post(f'{baseUrl}oauth/token').respond(status_code=200,json=jsonResp['token'])

@respx.mock
@pytest.mark.asyncio
async def test_tenants():
    respx.get(f'{apiUrl}tenants').respond(status_code=200, json=jsonResp['tenants'])
    respx.get(f'{apiUrl}tenants/{tid}').respond(status_code=200, json=jsonResp['tenant'])

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.tenants()
        assert len(resp.data) == 2

        resp = await client.tenant(tid)
        assert resp.data.name == 'Tenant 2'


@respx.mock
@pytest.mark.asyncio
async def test_instances():
    respx.get(f'{apiUrl}instances', params={'tenantId':tid}).respond(status_code=200, json=jsonResp['instancesByTenant'])
    respx.get(f'{apiUrl}instances').respond(status_code=200, json=jsonResp['instances'])
    respx.post(f'{apiUrl}instances').respond(status_code=200, json=jsonResp['createInstance'])
    respx.post(f'{apiUrl}instances/sizing').respond(status_code=200, json=jsonResp['instanceSizing'])
    respx.get(f'{apiUrl}instances/{iid}').respond(status_code=200, json=jsonResp['instance'])
    respx.delete(f'{apiUrl}instances/{iid}').respond(status_code=202, json=jsonResp['deleteInstance'])
    respx.post(f'{apiUrl}instances/{iid}/pause').respond(status_code=200, json=jsonResp['pauseInstance'])
    respx.post(f'{apiUrl}instances/{iid}/resume').respond(status_code=200, json=jsonResp['resumeInstance'])
    respx.post(f'{apiUrl}instances/{iid}/overwrite').respond(status_code=200, json=jsonResp['overwriteInstance'])

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.instances()
        assert len(resp.data) == 2
        
        resp = await client.instances(tid)
        assert len(resp.data) == 1

        resp = await client.instance(iid)
        assert resp.data.name == 'Instance 2'
        
        req = models.InstanceSizingRequest(node_count=100000,relationship_count=100000,instance_type='enterprise-ds',algorithm_categories=['node-embedding'])
        resp = await client.instanceSizing(req)
        assert resp.data.min_required_memory == '14GB'

        req = models.InstanceRequest( name='Test 1',memory='2GB',version='5',region='us-west-2',cloud_provider='aws',tenant_id=tid,type='enterprise-db')
        resp = await client.createInstance(req)
        assert resp.data.password == 'Neo4j123'

        resp = await client.pauseInstance(iid)
        assert resp.data.status == 'pausing'

        resp = await client.resumeInstance(iid)
        assert resp.data.status == 'resuming'

        resp = await client.overwriteInstance(iid,'test2')
        assert resp.data.status == 'overwriting'

        resp = await client.overwriteInstanceWithSnapshot(iid,'test2','snapshot3')
        assert resp.data.status == 'overwriting'

        resp = await client.deleteInstance(iid)
        assert resp.data.status == 'deleting'


@respx.mock
@pytest.mark.asyncio
async def test_instances_edit():
    route = respx.patch(f'{apiUrl}instances/{iid}')

    @route
    def respond(request):
        body = copy.deepcopy(jsonResp['createInstance'])
        reqBody = json.load(request)
        print(reqBody)
        if('name' in reqBody):
            body['data']['name'] = reqBody['name']
        if('memory' in reqBody):
            body['data']['memory'] = reqBody['memory']
        if('secondaries_count' in reqBody):
            body['data']['secondaries_count'] = reqBody['secondaries_count']
        if('cdc_enrichment_mode' in reqBody):
            body['data']['cdc_enrichment_mode'] = reqBody['cdc_enrichment_mode']
        print(body)
        return httpx.Response(200,json=body)

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.renameInstance(iid,'Test Renamed 2')
        assert resp.data.name == 'Test Renamed 2'
        
        resp = await client.resizeInstance(iid,'8GB')
        assert resp.data.memory == '8GB'
        assert resp.data.name == 'Test 2'

        resp = await client.renameAndResizeInstance(iid,'Test Rename 2','2GB')
        assert resp.data.memory == '2GB'
        assert resp.data.name == 'Test Rename 2'
        
        resp = await client.resizeInstanceSecondaryCount(iid,1)
        assert resp.data.secondaries_count == 1

        resp = await client.updateInstanceCDCMode(iid,'FULL')
        assert resp.data.cdc_enrichment_mode == 'FULL'


@respx.mock
@pytest.mark.asyncio
async def test_snapshots():
    respx.get(f'{apiUrl}instances/{iid}/snapshots').respond(status_code=200, json=jsonResp['snapshots'])
    respx.post(f'{apiUrl}instances/{iid}/snapshots').respond(status_code=200, json=jsonResp['createSnapshot'])
    respx.post(f'{apiUrl}instances/{iid}/snapshots/snapshot3/restore').respond(status_code=202, json=jsonResp['restoreSnapshot'])
    respx.get(f'{apiUrl}instances/{iid}/snapshots?date=2024-06-30').respond(status_code=200, json=jsonResp['snapshotsByDate'])
    respx.get(f'{apiUrl}instances/{iid}/snapshots/snapshot2').respond(status_code=200, json=jsonResp['snapshot'])

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.snapshots(iid)
        assert len(resp.data) == 2
        
        resp = await client.snapshots(iid,'2024-06-30')
        assert len(resp.data) == 2
        
        resp = await client.snapshot(iid,'snapshot2')
        assert resp.data.status == 'Completed'

        resp = await client.snapshotInstance(iid)
        assert resp.data.snapshot_id == 'snapshot3'
        
        resp = await client.restoreInstance(iid,'snapshot3')
        assert resp.data.status == 'restoring'

@respx.mock
@pytest.mark.asyncio
async def test_customer_managed_keys():
    respx.get(f'{apiUrl}customer-managed-keys', params={'tenantId':tid}).respond(status_code=200, json=jsonResp['customerManagedKeysForTenant'])
    respx.get(f'{apiUrl}customer-managed-keys').respond(status_code=200, json=jsonResp['customerManagedKeys'])
    respx.get(f'{apiUrl}customer-managed-keys/cmk1').respond(status_code=200, json=jsonResp['customerManagedKey'])
    respx.post(f'{apiUrl}customer-managed-keys').respond(status_code=202, json=jsonResp['createCustomerManagedKey'])
    respx.delete(f'{apiUrl}customer-managed-keys/cmk2').respond(status_code=204)

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.customerManagedKeys()
        assert len(resp.data) == 2

        resp = await client.customerManagedKeys(tid)
        assert len(resp.data) == 1

        resp = await client.customerManagedKey('cmk1')
        assert resp.data.name == 'Customer Managed Key 1'

        req = models.CustomerManagedKeyRequest( name='Customer Managed Key 2',key_id='cmk2',region='us-west-2',cloud_provider='aws',tenant_id=tid,instance_type="enterprise-db")
        resp = await client.createCustomerManagedKey(req)
        assert resp.data.status == 'pending'

        resp = await client.deleteCustomerManagedKey('cmk2')
        assert resp.data.status == 'deleted'

@respx.mock
@pytest.mark.asyncio
async def test_exceptions():
    # Test bad creds
    respx.post(f'{baseUrl}oauth/token').respond(status_code=401,json=jsonResp['authError'])
    async with AuraClient(clientId,clientSecret) as client:
        try:
            resp = await client.instances()
            assert not resp
        except models.AuraApiAuthorizationException as e:
            assert len(e.errors) == 1
    # Reset the auth endpoint    
    respx.post(f'{baseUrl}oauth/token').respond(status_code=200,json=jsonResp['token'])

    async with AuraClient(clientId,clientSecret) as client:
        # Test Auth Expired
        respx.get(f'{apiUrl}instances').respond(status_code=401, json=jsonResp['exception'])
        try:
            resp = await client.instances()
            assert not resp
        except models.AuraApiAuthorizationException as e:
            assert len(e.errors) == 1

        # Test Bad Request
        respx.get(f'{apiUrl}instances').respond(status_code=400, json=jsonResp['exception'])
        try:
            resp = await client.instances()
            assert not resp
        except models.AuraApiBadRequestException as e:
            assert len(e.errors) == 1

        # Test Missing Data
        respx.get(f'{apiUrl}instances/{iid}').respond(status_code=404, json=jsonResp['exception'])
        try:
            resp = await client.instance(iid)
            assert not resp
        except models.AuraApiNotFoundException as e:
            assert len(e.errors) == 1

        # Test Rate Limit
        respx.get(f'{apiUrl}instances/{iid}').respond(status_code=429, json=jsonResp['exception'])
        try:
            resp = await client.instance(iid)
            assert not resp
        except models.AuraApiRateLimitExceededException as e:
            assert len(e.errors) == 1

        # Test Internal Error
        respx.get(f'{apiUrl}instances/{iid}').respond(status_code=500, json=jsonResp['exception'])
        try:
            resp = await client.instance(iid)
            assert not resp
        except models.AuraApiInternalException as e:
            assert len(e.errors) == 1
        
        # Test Other Error
        respx.get(f'{apiUrl}instances/{iid}').respond(status_code=418, json=jsonResp['exception'])
        try:
            resp = await client.instance(iid)
            assert not resp
        except models.AuraApiException as e:
            assert len(e.errors) == 1
        
