# Neo4j Aura SDK for Python

This SDK provides a thin, async client for the Neo4j Aura HTTP API.

Highlights in this branch
- Support for both v1 and v2beta1 endpoints.
- Client-level API versioning and guards so v2 endpoints can't be called by a v1-configured client.
- Models and helper methods for import jobs and IP filters (v2beta1).

## Installation

Install from PyPI (when published) or install locally for development:

Using pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
# install test/runtime deps
pip install pytest httpx pydantic
```

Using poetry:

```bash
poetry install
```

## API versioning

The client defaults to the v1 API surface. To call v2 endpoints (v2beta1) you must construct the client with an API version that begins with `v2`.

- Constructor option: pass `api_version="v2beta1"` to `AuraClient`.
- Environment helper: `AuraClient.from_env()` will read `AURA_API_VERSION` (defaults to `v1`).

The client enforces a guard for v2 endpoints: calling a v2 method when the client is configured for `v1` will raise a clear `ValueError` indicating the API version mismatch. This prevents accidental use of v2 endpoints when the client is not configured for them.

Examples

Default (v1) client — v2 methods will be blocked:

```python
from neo4j_aura_sdk import AuraClient

async with AuraClient.from_env() as client:  # AURA_API_VERSION default is 'v1'
    tenants = await client.tenants()
    # The following will raise ValueError because the client is v1:
    # await client.list_organization_ip_filters("org-id")

```

Create a v2beta1 client (allows v2 calls):

```python
from neo4j_aura_sdk import AuraClient

async with AuraClient("id", "secret", api_version="v2beta1") as client:
    # Calls to v2beta1 endpoints (IP filters, import jobs) are allowed
    filters = await client.list_organization_ip_filters("org-id")
```

You can also set the environment variable `AURA_API_VERSION=v2beta1` before calling `AuraClient.from_env()`.

## Usage

Minimal example (uses environment variables for credentials):

```python
from neo4j_aura_sdk import AuraClient
import asyncio

async def main():
    async with AuraClient.from_env() as client:
        tenants = await client.tenants()
        print(tenants)

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

Run tests

With poetry:

```bash
poetry run pytest -q
```

With pip/venv:

```bash
source .venv/bin/activate
pytest -q
```

Build/publish

```bash
poetry build
poetry publish
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guidelines.

## Notes

- The repository now exposes an `api_version` property on `AuraClient` and provides clear guards for attempting v2 calls on a v1-configured client.
- Several v1 and v2 methods include concise docstrings describing inputs and return models.
