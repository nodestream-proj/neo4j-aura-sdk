import os
from datetime import datetime
from time import sleep

import pytest
from dotenv import load_dotenv

from neo4j_aura_sdk import AuraClient, models

load_dotenv()

baseUrl = "https://api.neo4j.io/"
apiUrl = f"{baseUrl}v1/"

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

        req = models.InstanceSizingRequest(
            node_count=100000,
            relationship_count=100000,
            instance_type="enterprise-ds",
            algorithm_categories=["node-embedding"],
        )
        resp = await client.instance_sizing(req)
        assert resp.data.min_required_memory == "1GB"

        req = models.InstanceRequest(
            name="Test 1",
            memory="2GB",
            version="5",
            region="us-west-2",
            cloud_provider="aws",
            tenant_id=tenantId,
            type="enterprise-db",
        )
        resp = await client.create_instance(req)
        assert resp.data.name == "Test 1"

        instanceId = resp.data.id

        # Start a second instance to use for overwriting
        req = models.InstanceRequest(
            name="Test 2",
            memory="2GB",
            version="5",
            region="us-west-2",
            cloud_provider="aws",
            tenant_id=tenantId,
            type="enterprise-db",
        )
        resp = await client.create_instance(req)
        assert resp.data.name == "Test 2"
        overwriteId = resp.data.id

        resp = await client.instance(instanceId)
        assert resp.data.name == "Test 1"
        assert resp.data.status == "creating"

        while resp.data.status == "creating":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == "running"

        resp = await client.rename_instance(instanceId, "Test Renamed 1")
        assert resp.data.name == "Test Renamed 1"

        resp = await client.resize_instance(instanceId, "4GB")
        sleep(10)
        resp = await client.instance(instanceId)
        print(resp)
        assert resp.data.status in ["updating", "resizing"]

        while resp.data.status != "running":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.memory == "4GB"

        resp = await client.rename_and_resize_instance(instanceId, "Test 1", "2GB")
        assert resp.data.name == "Test 1"

        sleep(10)
        resp = await client.instance(instanceId)
        print(resp)
        assert resp.data.status in ["updating", "resizing"]

        while resp.data.status != "running":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.memory == "2GB"

        try:
            resp = await client.resize_instance_secondary_count(instanceId, 1)
            assert resp.data.secondaries_count == 1
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == "tenant-incapable-of-action" for obj in e.errors)

        try:
            resp = await client.update_instance_cdc_mode(instanceId, "FULL")
            assert resp.data.cdc_enrichment_mode == "FULL"
        except models.AuraApiBadRequestException as e:
            assert any(obj.reason == "tenant-incapable-of-action" for obj in e.errors)

        resp = await client.pause_instance(instanceId)
        assert resp.data.status == "pausing"

        while resp.data.status != "paused":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == "paused"

        resp = await client.resume_instance(instanceId)
        assert resp.data.status == "resuming"

        while resp.data.status != "running":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == "running"

        # Check that the Overwrite instance is running
        resp = await client.instance(overwriteId)
        assert resp.data.status == "running"

        resp = await client.overwrite_instance(instanceId, overwriteId)
        assert resp.data.status == "overwriting"

        while resp.data.status != "running":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == "running"

        # Assumes there are snapshots from the resizing operations.
        resp = await client.snapshots(instanceId)
        assert len(resp.data) > 0
        snapshotId = resp.data[0].snapshot_id
        restoreId = resp.data[-1].snapshot_id

        resp = await client.snapshots(instanceId, datetime.now().strftime("%Y-%m-%d"))
        assert len(resp.data) > 0

        resp = await client.snapshot(instanceId, snapshotId)
        assert resp.data.status == "Completed"

        resp = await client.snapshot_instance(overwriteId)
        assert resp.data.snapshot_id is not None

        resp = await client.overwrite_instance_with_snapshot(
            overwriteId, instanceId, snapshotId
        )
        while resp.data.status != "running":
            sleep(30)
            resp = await client.instance(instanceId)
        assert resp.data.status == "running"

        resp = await client.restore_instance(instanceId, restoreId)
        assert resp.data.status in ["restoring", "running"]

        resp = await client.delete_instance(
            instanceId
        )  # To avoid waitng the restore to finish - no assertions for this instance

        resp = await client.delete_instance(overwriteId)
        # This status can sometimes come back as 'loading' - need to investigate
        # assert resp.data.status == 'destroying'

        # resp = await client.customer_managed_keys()
        # assert len(resp.data) == 2

        # resp = await client.customer_managed_keys(tid)
        # assert len(resp.data) == 1

        # resp = await client.customer_managed_key('cmk1')
        # assert resp.data.name == 'Customer Managed Key 1'

        # req = models.CustomerManagedKeyRequest( name='Customer Managed Key 2',key_id='cmk2',region='us-west-2',cloud_provider='aws',tenant_id=tid,instance_type="enterprise-db")
        # resp = await client.create_customer_managed_key(req)
        # assert resp.data.status == 'pending'

        # resp = await client.delete_customer_managed_key('cmk2')
        # assert resp.data.status == 'deleted'
