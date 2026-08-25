# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Changed
- Synced `neo4j_aura_sdk/resources/v2beta1/spec.json` with the latest published v2beta1 OpenAPI spec.
- `models.ProjectDatabaseSummary` (returned by the project instance database list/create/get/delete endpoints) now includes the required `name` field alongside `id`, matching the updated spec.
- Documented the billing `get_billing_usage` / `get_billing_ledger` rate limit (10 requests per organization per 24 hours) and data freshness (refreshed daily, up to 48h lag) in their docstrings.

### Tests
- Added unit test coverage for `create_project_instance_database`, `get_project_instance_database`, and `delete_project_instance_database`, which previously had none.
- Updated the project instance database list test to assert the new `name` field.

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



[Unreleased]: https://example.com/compare/v0.1.2...v0.1.3
