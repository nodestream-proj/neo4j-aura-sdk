# Specification Management Scripts

This directory contains scripts for managing OpenAPI specification files.

## Scripts

### `validate_specs.py`

Validates that the local OpenAPI specification files match the latest versions from the Neo4j Aura API.

**Usage:**
```bash
poetry run python scripts/validate_specs.py
```

**Output:**
- Lists each specification (v1, v1beta5, v2beta1)
- Shows local and remote hashes
- Reports if specs are up-to-date or have changes
- Shows version and endpoint count comparisons

**Exit codes:**
- `0` - All specs are up-to-date
- `1` - One or more specs have changes or errors

### `download_specs.py`

Downloads the latest OpenAPI specification files from Neo4j Aura and updates local copies.

**Usage:**
```bash
# Check what would change (dry-run)
poetry run python scripts/download_specs.py

# Force update specs
poetry run python scripts/download_specs.py --force
```

**Options:**
- `--force` - Update specs without prompting (use with caution)

## Automated Validation

A GitHub Actions workflow runs automated validation and notifies the team when
specs change. Details:

- Workflow file: `.github/workflows/validate-specs.yml`
- Schedule: weekly on Sundays at 06:00 UTC (also triggers on `push` to `main` and via `workflow_dispatch`)
- What it does: runs `scripts/validate_specs.py`, uploads the validation output as an artifact if the check fails, and creates a GitHub issue labeled `specs` and `automation` when changes are detected.
- Duplicate-issue guard: the workflow checks for an existing open issue with the same title and labels and will skip creating a duplicate.

Note: the workflow uses `GITHUB_TOKEN` to create issues and upload artifacts; ensure repository-level permissions allow workflows to create issues if you change defaults.

## API Endpoints

The scripts attempt to download from these endpoints:

- **v1**: `https://neo4j.com/docs/aura/platform/api/specification/aura_api_spec_v1.yaml`
- **v1beta5**: `https://neo4j.com/docs/aura/platform/api/specification/beta/aura_api_spec_v5.yaml`
- **v2beta1**: `https://neo4j.com/docs/aura/platform/api/specification/aura_api_spec_v2beta1.yaml`

**Note:** These endpoints may require authentication or may not be publicly accessible. If the validation script cannot reach them, it will still validate local files for YAML correctness and structure.

If you need to access authenticated endpoints, consider:
- Using an API key via environment variables
- Running the script from within the Neo4j infrastructure
- Checking with the Neo4j team for public API specification endpoints

## Local Spec Files

Specifications are stored at:

- `neo4j_aura_sdk/resources/aura_api_spec_v1.yaml`
- `neo4j_aura_sdk/resources/aura_api_spec_v2beta1.yaml`
- `neo4j_aura_sdk/resources/beta/aura_api_spec_v5.yaml`

## Integration with Client

The `AuraClient` can load specifications from local files for validation and introspection:

```python
from neo4j_aura_sdk import AuraClient
import yaml

# Load spec
with open("neo4j_aura_sdk/resources/aura_api_spec_v1.yaml") as f:
    spec = yaml.safe_load(f)

# Inspect endpoints
print(f"Available endpoints: {len(spec['paths'])}")
```
