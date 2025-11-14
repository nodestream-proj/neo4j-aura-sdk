# Changelog

All notable changes to this project will be documented in this file.

## [0.1.3] - 2025-11-14
### Added
- Added support for v2beta1 endpoints: IP filters and import jobs (models and client methods).
- Introduced a client-level `api_version` option. The client defaults to `v1` and can be configured with `api_version="v2beta1"` to allow v2 calls.
- `AuraClient.from_env()` now reads `AURA_API_VERSION` (defaults to `v1`).
- Implemented an API-version guard: v2 methods raise a clear `ValueError` if the client is configured for v1.
- Added concise docstrings to v1 and v2 client methods describing inputs and return models.
- Added a non-destructive end-to-end test that verifies the v2 guard behavior.
- Updated `README.md` with API versioning, usage examples, and test instructions.

### Changed
- Refactored internal HTTP helpers to a single `_request` method that supports API versioning and optional Pydantic model parsing.
- Bumped package version to `0.1.3` in `pyproject.toml`.

### Notes
- Nested models for some v2 responses (e.g., import job `data_source` / `aura_target`) are currently represented as plain dicts for minimal surface-area changes; they can be expanded to full Pydantic models in a follow-up.



[Unreleased]: https://example.com/compare/v0.1.2...v0.1.3
