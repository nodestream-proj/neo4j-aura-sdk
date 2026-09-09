---
name: check-for-spec-updates
description: Acts as a lead software engineer keeping this repo in sync with its upstream OpenAPI specs. Runs scripts/validate_specs.py, and if it reports drift, re-downloads specs with scripts/download_specs.py --force, diffs them against git, implements any missing or changed functions in neo4j_aura_sdk/client.py and models in neo4j_aura_sdk/models.py, updates pytest/pytest-cov coverage, and runs black + ruff so CI will pass. Produces a markdown report and a local git commit, then stops for human review before pushing or touching any PR. Requires shell + git access (Code mode only) — not usable in claude.ai chat without code execution. Trigger whenever the user says "check for updates", "check for spec updates", "are the specs up to date", or asks to sync/verify the SDK against its specs.
---

# Check for spec updates

Keep this SDK in sync with the upstream Neo4j Aura OpenAPI specs (`v1`,
`v1beta5`, `v2beta1`). Work from the repo root.

## Steps

1. **Validate.** Run `python scripts/validate_specs.py`. It downloads each
   spec fresh and hashes it against the local copy under
   `neo4j_aura_sdk/resources/`. A non-zero exit means at least one spec has
   drifted.
   - On Windows consoles, the script's ✅/⚠️ output can hit a `cp1252`
     `UnicodeEncodeError` — that's an encoding issue, not a real failure. Set
     `PYTHONIOENCODING=utf-8` when running it, or otherwise treat that
     specific traceback as noise.

2. **Confirm a clean tree, then download.** Check `git status --short` is
   clean before overwriting anything (don't clobber uncommitted work). Then
   run `python scripts/download_specs.py --force` to pull the latest specs
   for every drifted version.

3. **Diff against git.** For each changed spec file, run `git diff` and read
   the whole thing — don't skim. Classify each change:
   - A new/changed field, endpoint, or required-ness change → needs a
     `neo4j_aura_sdk/models.py` and/or `neo4j_aura_sdk/client.py` update.
   - A description/example/docs-only change (rate limits, timing notes,
     etc.) → no schema change, but worth mirroring into the relevant client
     method's docstring so it stays discoverable from the SDK itself.
   - Use `python -c "import json; ..."` one-liners against the spec JSON/YAML
     (schemas, `paths`, `required` arrays) to confirm exactly which model or
     endpoint a diff maps to before touching code — don't guess from the
     diff hunk alone.

4. **Implement.** Match the existing conventions in `models.py` (fields the
   spec marks `required` are typed as bare `str`/`int`/etc., not
   `Optional[...] = None`) and in `client.py` (concise docstrings stating
   inputs and the return model, `_get`/`_post`/`_delete`/`_patch` helpers,
   `self._ensure_api_is_v2()` guard for v2beta1-only methods). Don't refactor
   unrelated pre-existing gaps you notice along the way — flag them in the
   report instead of fixing them silently.

5. **Update tests and coverage.** Update any test fixtures/mocks whose JSON
   now needs new required fields. While in the area, check whether the
   method(s) you just touched already have test coverage at all — if not,
   add it now rather than deferring it.

6. **Lint and test.** Run, in order:
   ```
   python -m black neo4j_aura_sdk tests --check
   python -m ruff check neo4j_aura_sdk tests
   python -m pytest -m "not e2e" -q
   ```
   All three must pass before moving on. If the dev venv is missing any of
   `black`/`ruff`/`pydantic`/`respx`/`pyhamcrest`/`python-dotenv`/`pyyaml`,
   install versions matching the constraints in `pyproject.toml` rather than
   grabbing latest — the project pins them deliberately, and bumping a pin
   itself is a separate, out-of-scope task (e.g. resolving a Dependabot
   alert), not something to do incidentally while checking specs.

7. **Changelog.** Add an entry to `CHANGELOG.md` under the current
   unreleased/top section — `### Changed` for spec/behavior changes,
   `### Tests` for coverage additions.

8. **Report and stop.** Produce a markdown report: which specs drifted, what
   changed (schema vs. docs-only), which files were touched, and the
   lint/test results. Then create **one local commit** with a clear,
   specific message (not "update specs"). **Do not push, open a PR, or touch
   an existing PR** — stop here for human review. If the user separately
   asks to push, that's a distinct, explicit request.

## Notes

- This file lives in the repo (`.claude/skills/check-for-spec-updates/`) on
  purpose, instead of only as an account-level skill: it's tightly coupled
  to this repo's actual file paths and scripts, so it needs to travel with
  the code and stay reviewable via normal PR diffs. Update it in the same
  commit/PR as any change to `scripts/validate_specs.py`,
  `scripts/download_specs.py`, or `scripts/specs.py` that changes what this
  workflow should do.
- Absolute local paths (e.g. a specific clone directory) don't belong here —
  always operate relative to the repo root so this works for any
  collaborator's checkout.
