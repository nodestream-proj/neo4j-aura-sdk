import os 
from dotenv import load_dotenv
import pytest
from time import sleep
from datetime import datetime
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
async def test_create_instances():

    async with AuraClient.from_env() as client:
        # Assumes there is at least 1 instance for the given Tenant
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

        instanceId = resp.data.id

        # Start a second instance to use for overwriting
        req = models.InstanceRequest( name='Test 2',memory='2GB',version='5',region='us-west-2',cloud_provider='aws',tenant_id=tenantId,type='enterprise-db')
        resp = await client.createInstance(req)
        assert resp.data.name == 'Test 2'
        overwriteId = resp.data.id

        resp = await client.instance(instanceId)
        assert resp.data.name == 'Test 1'
        assert resp.data.status == 'creating'
        
        while(resp.data.status == 'creating'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == 'running'
        
        resp = await client.renameInstance(instanceId,'Test Renamed 1')
        assert resp.data.name == 'Test Renamed 1'
        
        resp = await client.resizeInstance(instanceId,'4GB')
        sleep(10)
        resp = await client.instance(instanceId)
        print(resp)
        assert resp.data.status in ['updating','resizing']

        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.memory == '4GB'
        
        resp = await client.renameAndResizeInstance(instanceId,'Test 1','2GB')
        assert resp.data.name == 'Test 1'

        sleep(10)
        resp = await client.instance(instanceId)
        print(resp)
        assert resp.data.status in ['updating','resizing']
        
        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.memory == '2GB'

        try:
            resp = await client.resizeInstanceSecondaryCount(instanceId,1)
            assert resp.data.secondaries_count == 1
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == 'tenant-incapable-of-action' for obj in e.errors)
        
        try:
            resp = await client.updateInstanceCDCMode(instanceId,'FULL')
            assert resp.data.cdc_enrichment_mode == 'FULL'
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == 'tenant-incapable-of-action' for obj in e.errors)

        resp = await client.pauseInstance(instanceId)
        assert resp.data.status == 'pausing'

        while(resp.data.status != 'paused'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == 'paused'

        resp = await client.resumeInstance(instanceId)
        assert resp.data.status == 'resuming'

        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == 'running'

        # Check that the Overwrite instance is running
        resp = await client.instance(overwriteId)
        assert resp.data.status == 'running'

        resp = await client.overwriteInstance(instanceId,overwriteId)
        assert resp.data.status == 'overwriting'

        while(resp.data.status != 'running'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == 'running'

        # Assumes there are snapshots from the resizing operations.
        resp = await client.snapshots(instanceId)
        assert len(resp.data) > 0
        snapshotId = resp.data[0].snapshot_id
        restoreId = resp.data[-1].snapshot_id

        resp = await client.snapshots(instanceId,datetime.now().strftime("%Y-%m-%d"))
        assert len(resp.data) > 0
        
        resp = await client.snapshot(instanceId,snapshotId)
        assert resp.data.status == 'Completed'

        resp = await client.snapshotInstance(overwriteId)
        assert resp.data.status == 'Scheduled'
        
        resp = await client.overwriteInstanceWithSnapshot(overwriteId,instanceId,snapshotId)
        while(resp.data.status != 'overwriting'):
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == 'running'

        resp = await client.restoreInstance(instanceId,restoreId)
        assert resp.data.status == 'restoring'

        resp = await client.deleteInstance(instanceId)
        assert resp.data.status == 'destroying'

        resp = await client.deleteInstance(overwriteId)
        assert resp.data.status == 'destroying'


        # resp = await client.customerManagedKeys()
        # assert len(resp.data) == 2

        # resp = await client.customerManagedKeys(tid)
        # assert len(resp.data) == 1

        # resp = await client.customerManagedKey('cmk1')
        # assert resp.data.name == 'Customer Managed Key 1'

        # req = models.CustomerManagedKeyRequest( name='Customer Managed Key 2',key_id='cmk2',region='us-west-2',cloud_provider='aws',tenant_id=tid,instance_type="enterprise-db")
        # resp = await client.createCustomerManagedKey(req)
        # assert resp.data.status == 'pending'

        # resp = await client.deleteCustomerManagedKey('cmk2')
        # assert resp.data.status == 'deleted'
