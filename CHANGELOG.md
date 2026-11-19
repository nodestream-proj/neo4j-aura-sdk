# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Added `AuraClient.get_organization_project` (v2beta1), covering the newly-published `GET /organizations/{organization_id}/projects/{project_id}` endpoint. Returns a `ProjectResponse` wrapping `ProjectDetails` (`id`, `name`).
- Added v2beta1 project instance lifecycle support: `pause_project_instance`, `resume_project_instance`, `get_project_instance_restore_point`, and `restore_project_instance` (Multi Database instances only), with new `InstanceRestorePoint`, `InstanceRestoreResponse`, and `RestoreInstanceRequest` models.
- Added full v2beta1 agent evaluation support (a new upstream feature area): evaluation dataset CRUD (`list_agent_evaluation_datasets`, `create_agent_evaluation_dataset`, `get_agent_evaluation_dataset`, `update_agent_evaluation_dataset`, `delete_agent_evaluation_dataset`) and evaluation run lifecycle (`list_agent_evaluation_runs`, `start_agent_evaluation_run`, `get_agent_evaluation_run`, `delete_agent_evaluation_run`, `cancel_agent_evaluation_run`), plus their request/response models. Per-question agent responses reuse the existing `InvokeAgentResponse`/`InvokeAgentContentBlock`/`InvokeAgentError`/`InvokeAgentUsage` models rather than duplicating them, since the spec's `EvaluationAgentResponse` schema is structurally identical.
- Added v2beta1 project CRUD: `create_organization_project`, `update_organization_project`, `delete_organization_project`, `restore_organization_project` (a project is restorable for 30 days after a delete request), with new `CreateProjectRequest`, `UpdateProjectRequest`, `CreateProjectResponse`, `ProjectDeletion`/`ProjectDeletionResponse` models.
- Added `AuraClient.create_project_instance_backup` (v2beta1): requests a whole-instance Restore Point backup for a Multi Database instance. 202/no body.
- Added `AuraClient.promote_project_database` (v2beta1): promotes a replica database to standalone. Reuses the existing `ProjectDatabaseResponse`/`ProjectDatabaseSummary` models.
- Added v2beta1 agent evaluation dataset versioning: `list_agent_evaluation_dataset_versions`, `get_agent_evaluation_dataset_version`, with new `EvaluationDatasetVersion`/`EvaluationDatasetVersionDetail` models.
- Added v2beta1 Document Intelligence (unstructured) import jobs: `create_unstructured_import_job`, `get_unstructured_import_job`, `get_unstructured_import_job_operation`. The upstream spec doesn't yet document a response schema for the two GET endpoints, so they return the raw parsed JSON (`dict`) rather than a typed model.

### Changed
- Synced `neo4j_aura_sdk/resources/v2beta1/spec.json` with the latest published v2beta1 OpenAPI spec (52 → 60 endpoints).
- `models.VirtualGraph` gained 3 new optional fields matching the updated spec: `private_access_enabled`, `private_bolt_url`, `public_access_enabled`. `bolt_url`'s description was also clarified to "Public Bolt connection URL" (no schema change).
- `models.ProjectInstanceDetails` gained `graph_analytics` (was already present and required in the spec's `InstanceDetails` schema for the existing get/create project-instance endpoints, but missing from this model — filled in while reusing this model for the new pause/resume endpoints, which return the same schema).
- `models.ListAgentResponse`/`GetAgentResponse` gained `is_graph_engine` and `availability` (new `AgentAvailability` model), matching the spec's `AgentSummary`/`AgentDetails` schemas.
- `models.InvokeAgentContentBlock` gained `thought_signature`, matching the spec's `InvokeAgentContent` schema.
- `models.OrganizationInvite`'s fields are now all required (previously all `Optional`), matching the spec newly marking every one of them as required.
- `models.EvaluationDatasetSummary`/`EvaluationDatasetDetail` gained required `current_version_id`/`current_version_label` fields (plus `added_question_count`/`deleted_question_count`/`changed_question_count` on `EvaluationDatasetDetail`); `models.EvaluationRunQuestionResult` gained a required `question_id` field. All matching the spec's new evaluation-dataset-versioning feature.
- `pause_instance`/`resume_instance` (v1) docstrings now note that upstream marked their endpoints `deprecated: true`, pointing callers to the v2beta1 `pause_project_instance`/`resume_project_instance` equivalents added last round.

### Tests
- Added unit test coverage for `get_organization_project`, which previously had none (the endpoint itself is new).
- Added unit test coverage for the new instance lifecycle methods (pause/resume/restore-point/restore) and all ten new agent evaluation methods.
- Added unit test coverage for all new v2beta1 methods added this round: project CRUD, instance backup, database promote, evaluation dataset versions, and unstructured import jobs.
- Updated `test_organization_invites_crud`'s mocked response to include all of `OrganizationInvite`'s newly-required fields.

### Fixed (Copilot review follow-up on PR #13)
- `AuraClient.create_organization_project`, `create_agent_evaluation_dataset`, and `update_agent_evaluation_dataset` now serialize their request bodies with `exclude_none=True`, instead of sending `null` for every unset optional field (including nested ones, e.g. `expected_tool_calls`). `CreateProjectRequest`'s and the evaluation-dataset request schemas have `additionalProperties: false` with no nullable variant for their optional string/array fields, so the previous behavior would have gotten these calls rejected by the real API for the common case of omitting optional fields. Added `exclude_none: bool = False` as an opt-in parameter on `_post`/`_patch`/`_request`, defaulting to the prior behavior everywhere else — this is deliberately **not** a global change, since other (pre-existing) PATCH endpoints may rely on explicit `null` meaning "clear this field". Added outgoing-JSON assertions to the relevant tests to lock this in.
- `models.AgentAvailability.status` is now `Optional[str]` instead of required `str`, matching the spec (no `required` list on this schema). The prior required typing meant an agent response with an `availability` object missing `status` would fail to parse entirely. Added a test covering this case.

### Notes
- The evaluation dataset create/update request models deliberately use a dedicated "question" model without a `question_id` field for create (`EvaluationDatasetQuestionInput`), separate from the one with optional `question_id` used for update/responses (`EvaluationDatasetQuestion`). The create endpoint's schema has `additionalProperties: false` and doesn't allow `question_id` at all; combined with the `exclude_none=True` fix above, this ensures create payloads never contain the key.
- The spec's `JobCreatedBy`, `JobResponse`, and `RunResponse` schemas changed (a `user_id`→`console_user_id` rename, and new fields respectively), but all three are orphaned schemas not referenced by any endpoint or other schema in the spec — same as `ModelMeta` previously. No corresponding client/model code exists, so no action was needed.
- The new `X-Trace-Id` optional request header (present on most of this round's new endpoints) is not threaded through the client. It's purely optional tracing support; can be added later if there's a need to correlate client requests with Aura support tickets.
- `ImportJob`'s `import_type` enum gained `online`/`bulk` values upstream; no code change needed since `models.ImportJobData.import_type` is already a plain `str`. `models.OrganizationDetails` was already typed with required `id`/`name`, matching the spec now formally requiring them too — no change needed there either.
- `CreateUnstructuredImportJobRequest.schema` triggers a (harmless) Pydantic `UserWarning` that it shadows a `BaseModel` attribute, since the spec genuinely names this field `schema`. Not aliased to a different Python name, since this client's shared request-serialization path doesn't support per-field aliasing without a broader change.

### Security
- Resolved a newly-published Dependabot alert: `urllib3` 2.7.0 was in the vulnerable range (>=2.6.2, <2.8.0) for [GHSA-gh4c-6fx4-qh6g](https://github.com/urllib3/urllib3/security/advisories/GHSA-gh4c-6fx4-qh6g) (infinite loop on malformed chunked+Deflate streaming responses). Bumped to 2.8.0 via `poetry lock --regenerate`, which also picked up routine patch bumps for `black`, `charset-normalizer`, `coverage`, `idna`, `iniconfig`, `librt`, `platformdirs`, `python-dotenv`, and `tomli`.
- Resolved two more Dependabot alerts found on a later check: `certifi` 2026.7.22 bundled a compromised emSign intermediate CA (critical; fixed in 2026.10.23), and `black` 26.10.0 had a GitHub Action that installs an unvalidated `required-version` from `pyproject.toml` (high; fixed in 26.10.1, though this project doesn't use that Action). Two more `urllib3` alerts (a TLS-proxy-config issue and an unbounded chunk-size-line buffering issue, both fixed in 2.8.0) were already covered by the prior bump. `poetry lock --regenerate` also picked up `anyio`, `click`, `librt`, `mypy-extensions`, `pluggy`, `pydantic`/`pydantic-core`, `pytest`, `pytest-asyncio`, and `typing-inspection` — none required a `pyproject.toml` constraint change.

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

### Removed (Breaking)
- Removed `AuraClient.invoke_agent_invocation_api` (v2beta1). Its endpoint, `POST /organizations/{org_id}/projects/{project_id}/agent-invocation/{agent_id}/invoke`, was removed from the upstream v2beta1 spec with no replacement. Use `invoke_agent` (`POST /agents/{agentId}/invoke`), which is unaffected and was already the canonical way to invoke an agent.

### Fixed
- Fixed `scripts/download_specs.py` and `scripts/validate_specs.py` to read/write spec files with an explicit `encoding="utf-8"`. Without it, Python defaults to the OS locale encoding, which on Windows silently corrupted non-ASCII characters (e.g. `'` became invalid UTF-8) in every downloaded spec file. All three committed spec files had this corruption baked in from prior runs; re-downloading with the fix restored the correct text with no other content change.
- `models.ProjectDatabaseResponse.data` (returned by `create_project_instance_database`, `get_project_instance_database`) is now typed as `Optional[ProjectDatabaseSummary]` instead of `Optional[dict]`, so callers get the same typed object as the list endpoint instead of raw dict access.
- `models.CreateVirtualGraphRequest` now marks `cloud_provider`, `data_source_id`, `import_model_id`, `name`, and `region` as required (`str`, no default) to match the spec, so invalid creates fail at construction instead of at the API. `memory` and `maximum_bytes_billed` remain optional, matching the spec.
- `update_virtual_graph` and `restore_project_instance_database` no longer declare a response model; both endpoints return 202 with no body, and the declared model was previously unreachable dead code that misrepresented the return type as non-`None`.

### Tests (review follow-up)
- Added unit test coverage for `restore_project_instance_database`, which previously had none.

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
