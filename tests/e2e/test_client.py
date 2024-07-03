import os 
from dotenv import load_dotenv
import pytest
from time import sleep
from neo4j_aura_sdk import AuraClient,models

load_dotenv()

baseUrl = 'https://api.neo4j.io/'
apiUrl = f'{baseUrl}v1/'

tenantId = os.getenv("AURA_API_TENANT_ID")
tenantName = os.getenv("AURA_API_TENANT_NAME")

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_tenants():

    async with AuraClient.from_env() as client:
        resp = await client.tenants()
        assert any(obj.id == tenantId for obj in resp.data)

        resp = await client.tenant(tenantId)
        assert resp.data.name == tenantName

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_instances():

    async with AuraClient.from_env() as client:
        resp = await client.instances()
        assert any(obj.tenant_id == tenantId for obj in resp.data)

        resp = await client.instances(tenantId)
        assert all(obj.tenant_id == tenantId for obj in resp.data)

        req = models.InstanceSizingRequest(node_count=100000,relationship_count=100000,instance_type='enterprise-ds',algorithm_categories=['node-embedding'])
        resp = await client.instanceSizing(req)
        assert resp.data.min_required_memory == '1GB'

        req = models.InstanceRequest( name='Test 1',memory='2GB',version='5',region='us-west-2',cloud_provider='aws',tenant_id=tenantId,type='enterprise-db')
        resp = await client.createInstance(req)
        assert resp.data.name == 'Test 1'

        iid = resp.data.id

        resp = await client.instance(iid)
        assert resp.data.name == 'Test 1'
        assert resp.data.status == 'creating'
        
        while(resp.data.status == 'creating'):
            sleep(30)
            resp = await client.instance(iid)
        assert resp.data.status == 'running'
        
        resp = await client.renameInstance(iid,'Test Renamed 1')
        assert resp.data.name == 'Test Renamed 1'
        
        resp = await client.resizeInstance(iid,'4GB')
        sleep(10)
        resp = await client.instance(iid)
        print(resp)
        assert resp.data.status in ['updating','resizing']

        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(iid)
        assert resp.data.memory == '4GB'
        
        resp = await client.renameAndResizeInstance(iid,'Test 1','2GB')
        assert resp.data.name == 'Test 1'

        sleep(10)
        resp = await client.instance(iid)
        print(resp)
        assert resp.data.status in ['updating','resizing']
        
        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(iid)
        assert resp.data.memory == '2GB'

        try:
            resp = await client.resizeInstanceSecondaryCount(iid,1)
            assert resp.data.secondaries_count == 1
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == 'tenant-incapable-of-action' for obj in e.errors)
        
        try:
            resp = await client.updateInstanceCDCMode(iid,'FULL')
            assert resp.data.cdc_enrichment_mode == 'FULL'
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == 'tenant-incapable-of-action' for obj in e.errors)

        # resp = await client.pauseInstance(iid)
        # assert resp.data.status == 'pausing'

        # resp = await client.resumeInstance(iid)
        # assert resp.data.status == 'resuming'

        # resp = await client.overwriteInstance(iid,'test2')
        # assert resp.data.status == 'overwriting'

        # resp = await client.overwriteInstanceWithSnapshot(iid,'test2','snapshot3')
        # assert resp.data.status == 'overwriting'

        resp = await client.deleteInstance(iid)
        assert resp.data.status == 'destroying'
