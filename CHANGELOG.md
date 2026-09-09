# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5]
### Changed
- Synced `neo4j_aura_sdk/resources/v2beta1/spec.json` with the latest published v2beta1 OpenAPI spec.
- `models.ProjectDatabaseSummary` (returned by the project instance database list/create/get/delete endpoints) now includes the required `name` field alongside `id`, matching the updated spec.
- Documented the billing `get_billing_usage` / `get_billing_ledger` rate limit (10 requests per organization per 24 hours) and data freshness (refreshed daily, up to 48h lag) in their docstrings.
- Synced `neo4j_aura_sdk/resources/aura_api_spec_v1.yaml` and `neo4j_aura_sdk/resources/beta/aura_api_spec_v5.yaml` with the latest published specs (documentation-only: instance creation timing note). Documented the same note on `create_instance`'s docstring.

### Tests
- Added unit test coverage for `create_project_instance_database`, `get_project_instance_database`, and `delete_project_instance_database`, which previously had none.
- Updated the project instance database list test to assert the new `name` field.

### Security
- Resolved all 13 open Dependabot alerts (1 critical, 5 high, 7 moderate) by bumping dev dependencies (`pytest` 8→9.0.3+, `black` 24→26.3.1+, `requests` →2.33.0+, `python-dotenv` →1.2.2+, `pytest-asyncio` 0.23→1.4.0+ for pytest 9 compatibility) and letting `httpx`/`requests` re-resolve to patched transitive versions (`h11` →0.16.0+, `urllib3` →2.7.0+, `idna` →3.15+). Regenerated `poetry.lock` accordingly.

## [0.1.4] - 2026-07-16
### Added
- Added broad v2beta1 API coverage for organization and project user management, including organization user listing/details/patch/removal, project user listing/add/update/removal, and organization invite list/create/delete operations.
- Added full v2beta1 agent lifecycle support, including list/create/get/update/patch/delete/invoke operations and related request/response models.
- Added v2beta1 graph analytics session support (organization/project session listing, session create/get/delete, and session size estimation).
- Added v2beta1 project instance and database management support, including instance lifecycle endpoints plus project database create/get/delete and backup/restore flows.
- Added v2beta1-specific error and payload models, including validation and unsupported-action exception handling models.

### Changed
- Updated v2beta1 spec sourcing to JSON and added `neo4j_aura_sdk/resources/v2beta1/spec.json`.
- Updated spec tooling (`scripts/specs.py`, `scripts/download_specs.py`, and `scripts/validate_specs.py`) to support mixed YAML/JSON specs, format-aware parsing/validation, and relative/absolute spec URL resolution.
- Updated the agent similarity-search tool contract to align with the latest spec and normalized legacy tool configuration handling.
- Updated package metadata/versioning for the `0.1.4` release and expanded top-level exports for newly introduced models/exceptions.
- Updated CI/release/validate-spec workflow action versions.

### Fixed
- Fixed a `validate_specs.py` comparison bug so local/remote spec checks work correctly when spec formats differ (for example YAML vs JSON) and when a legacy local spec path must be used.
- Fixed spec change detection stability by using canonical semantic hashing for cross-format comparisons.

## [0.1.3] - 2025-11-17
### Added
- Added support for v2beta1 endpoints: IP filters and import jobs (models and client methods).
- Added comprehensive Fleet Manager deployment support (v2beta1):
	- All deployment CRUD operations: list, create, get, delete
	- Deployment database and server retrieval endpoints
	- Deployment token management (create, update, delete)
	- Complete Pydantic models for all deployment-related responses
- Introduced a client-level `api_version` option. The client defaults to `v1` and can be configured with `api_version="v2beta1"` to allow v2 calls.
- `AuraClient.from_env()` now reads `AURA_API_VERSION` (defaults to `v1`).
- Implemented an API-version guard: v2 methods raise a clear `ValueError` if the client is configured for v1.
- Added concise docstrings to v1 and v2 client methods describing inputs and return models.
- Added a non-destructive end-to-end test that verifies the v2 guard behavior.
- Updated `README.md` with API versioning, usage examples, and test instructions.
- Full support for v1beta5 endpoints:
	- Implemented all v1beta5-only client methods (GraphQL Data API CRUD, auth provider management, instance upgrade, project metrics integration, pause/resume).
	- Added Pydantic models for all new v1beta5 request/response types.
	- Enforced strict version guard: v1beta5 methods raise `ValueError` unless `api_version` is set to `v1beta5`.
- Comprehensive unit tests for v1beta5 methods and version guard, including:
	- CRUD and management for GraphQL Data API and auth providers
	- Instance upgrade and project metrics integration
	- Version guard enforcement

### Changed
- Refactored internal HTTP helpers to a single `_request` method that supports API versioning and optional Pydantic model parsing.
- Refactored v1beta5 tests into a dedicated test module for clarity and maintainability.
- Bumped package version to `0.1.3` in `pyproject.toml`.

### Fixed
- All v1beta5 tests now use Pydantic models for request bodies, matching client expectations.

### Notes
- All v2beta1 endpoints from the OpenAPI spec are now fully implemented and tested.

### Notes
- Nested models for some v2 responses (e.g., import job `data_source` / `aura_target`) are currently represented as plain dicts for minimal surface-area changes; they can be expanded to full Pydantic models in a follow-up.
