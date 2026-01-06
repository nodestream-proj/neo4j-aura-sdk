"""Centralized specification URLs and local paths for scripts.

This module provides a single place to update the base spec URL and the
mapping of versions to remote and local file locations used by the
management scripts in `scripts/`.
"""

BASE_SPEC_URL = "https://neo4j.com/docs/aura/platform/api/specification"

SPECS = {
    "v1": {
        "url": f"{BASE_SPEC_URL}/aura_api_spec_v1.yaml",
        "local": "neo4j_aura_sdk/resouces/aura_api_spec_v1.yaml",
        "description": "Core Aura API v1",
    },
    "v2beta1": {
        "url": f"{BASE_SPEC_URL}/aura_api_spec_v2beta1.yaml",
        "local": "neo4j_aura_sdk/resouces/aura_api_spec_v2beta1.yaml",
        "description": "Aura API v2beta1 (Fleet Manager)",
    },
    "v1beta5": {
        "url": f"{BASE_SPEC_URL}/beta/aura_api_spec_v5.yaml",
        "local": "neo4j_aura_sdk/resouces/beta/aura_api_spec_v5.yaml",
        "description": "Aura API v1beta5 (GraphQL Data API)",
    },
}
