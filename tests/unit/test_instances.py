import pytest
import respx
import httpx
import json
import os

from neo4j_aura_sdk import AuraClient,models

clientId = "mockId"
clientSecret = "mockSecret"
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, 'responses.json')
with open(file_path,'r') as f:
    jsonResp = json.load(f)

tid = "tenant2"
iid = "instance2"

def patch_instance(req,route):
    body = jsonResp['createInstance']
    reqBody = json.load(respx.calls.last.request)  #this bring back the prev call not the current call
    print(body)
    if(reqBody['name']):
        body['name'] = reqBody['name']
    print(body)
    
    return httpx.Response(200,json=body)


respx.post('https://api.neo4j.io/oauth/token').respond(status_code=200,json={'access_token':'mockToken','expires_in':3600,'token_type':'access'})
#TODO: Add missing creds use case
#TODO: Add bad creds use case

respx.get('https://api.neo4j.io/v1/tenants').respond(status_code=200, json=jsonResp['tenants'])
respx.get(f'https://api.neo4j.io/v1/tenants/{tid}').respond(status_code=200, json=jsonResp['tenant'])
respx.get('https://api.neo4j.io/v1/instances').respond(status_code=200, json=jsonResp['instances'])
respx.post('https://api.neo4j.io/v1/instances').respond(status_code=200, json=jsonResp['createInstance'])
respx.get(f'https://api.neo4j.io/v1/instances/{iid}').respond(status_code=200, json=jsonResp['instance'])
respx.patch(f'https://api.neo4j.io/v1/instances/{iid}').mock(side_effect=patch_instance)
respx.get(f'https://api.neo4j.io/v1/instances/{iid}/snapshots').respond(status_code=200, json=jsonResp['snapshots'])
respx.get(f'https://api.neo4j.io/v1/instances/{iid}/snapshots?date=2024-06-30').respond(status_code=200, json=jsonResp['snapshotsByDate'])
respx.get(f'https://api.neo4j.io/v1/instances/{iid}/snapshots/snapshot2').respond(status_code=200, json=jsonResp['snapshot'])

@respx.mock
@pytest.mark.asyncio
async def test_tenants():

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.tenants()
        assert len(resp.data) == 2

        resp = await client.tenant("tenant2")
        assert resp.data.name == "Tenant 2"


@respx.mock
@pytest.mark.asyncio
async def test_instances():

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.instances()
        assert len(resp.data) == 2
        resp = await client.instance(iid)
        assert resp.data.name == "Instance 2"
        req = models.InstanceRequest( name="Test 1",memory="2GB",version="5",region="us-west-2",cloud_provider="aws",tenant_id=tid,type="enterprise-db")
        resp = await client.createInstance(req)
        assert resp.data.password == 'Neo4j123'
        resp = await client.renameInstance(iid,"Test Renamed 2")
        assert resp.data.name == 'Test Renamed 2'
        
        # instance = await client.resizeInstance("7c544190","4GB")
        # print(instance)

        # instance = await client.resumeInstance("7c544190")
        # print(instance)

        # instance = await client.renameAndResizeInstance("7c544190","MPA-Test-1","2GB")
        # print(instance)

        # instance = await client.resizeInstanceSecondaryCount("7c544190",1)
        # print(instance)

        # instance = await client.updateInstanceCDCMode("7c544190","FULL")
        # print(instance)


@respx.mock
@pytest.mark.asyncio
async def test_snapshots():

    async with AuraClient(clientId,clientSecret) as client:
        resp = await client.snapshots(iid)
        assert len(resp.data) == 2
        resp = await client.snapshots(iid,"2024-06-30")
        assert len(resp.data) == 2
        resp = await client.snapshot(iid,"snapshot2")
        assert resp.data.status == 'Completed'



        # instance = await client.snapshotInstance("7c544190")
        # print(instance)
        
        # instance = await client.restoreInstance("7c544190","d91a3d78-288a-4372-83de-b62ee10d06d5")
        # print(instance)
        

        # iid = "223ddb77"
        # instance = await client.instance(iid)
        # print(instance)

        # instance = await client.deleteInstance(iid)
        # print(f"Deleted={instance}")

        # instance = await client.instance(iid)
        # print(instance)

        # req = models.InstanceSizingRequest(node_count=100000,relationship_count=100000,instance_type="enterprise-ds",algorithm_categories=["node-embedding"])
        # sizing = await client.instanceSizing(req)
        # print(sizing)
