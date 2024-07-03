import os 
from dotenv import load_dotenv
import pytest
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
        print(iid)
        resp = await client.instance(iid)
        assert resp.data.name == 'Test 1'
        
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
