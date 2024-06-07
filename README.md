# Neo4j Aura SDK for Python

This is an SDK for interacting with the Neo4j Aura service from Python. 

## Installation

```bash
pip install neo4j-aura-sdk
```

## Usage

```python
from neo4j_aura_sdk import AuraClient


async def main():
    async with AuraClient.from_env() as client:
        tenants = await client.tenants()
        print(tenants)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```


## Development

### Running tests

```bash
make test
```

### Building the package

```bash
poetry build
```

### Publishing the package

```bash
poetry publish
```

## License

LICENSING INFORMATION TBD

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more information.
