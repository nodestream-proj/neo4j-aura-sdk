"""Centralized specification URLs and local paths for scripts.

This module fetches the SPECS variable from the Neo4j Aura swagger initializer
and maps it to local file locations used by the management scripts in `scripts/`.
"""

import json
import re
from typing import Dict

import httpx

BASE_SPEC_URL = "https://neo4j.com/docs/aura/platform/api/specification"
SWAGGER_INITIALIZER_URL = (
    f"{BASE_SPEC_URL}/swagger-initializer.js"
)


def _build_spec_url(spec_url: str) -> str:
    """Resolve spec URL whether it is relative or absolute."""
    if spec_url.startswith(("http://", "https://")):
        return spec_url
    return f"{BASE_SPEC_URL}/{spec_url}"


def fetch_specs_from_swagger() -> Dict[str, Dict]:
    """Fetch the specs array from swagger-initializer.js and map to local paths."""
    try:
        response = httpx.get(SWAGGER_INITIALIZER_URL, timeout=10.0)
        response.raise_for_status()
        content = response.text

        # Extract the specs array from JavaScript
        # Looking for: const specs = [ {...}, {...}, ... ];
        match = re.search(r"const\s+specs\s*=\s*(\[.*?\]);", content, re.DOTALL)
        if not match:
            raise ValueError("Could not find 'const specs' in swagger-initializer.js")

        specs_json_str = match.group(1)

        # Convert JavaScript object syntax to JSON
        # Replace JavaScript object notation with JSON format
        # Handle multiline and whitespace
        specs_json_str = re.sub(r'^\s+', '', specs_json_str, flags=re.MULTILINE)
        specs_json_str = re.sub(r',\s*}', '}', specs_json_str)
        specs_json_str = re.sub(r',\s*]', ']', specs_json_str)
        # Quote unquoted keys: url: and name:
        specs_json_str = re.sub(r'(\{|,)\s*(\w+)\s*:', r'\1"\2":', specs_json_str)

        specs_array = json.loads(specs_json_str)

        # Map version names to descriptions and local paths
        version_mapping = {
            "Aura v1": {
                "key": "v1",
                "description": "Core Aura API v1",
                "local": "neo4j_aura_sdk/resources/aura_api_spec_v1.yaml",
                "format": "yaml",
            },
            "Aura v2beta1": {
                "key": "v2beta1",
                "description": "Aura API v2beta1 (Fleet Manager)",
                "local": "neo4j_aura_sdk/resources/v2beta1/spec.json",
                "legacy_local": "neo4j_aura_sdk/resources/aura_api_spec_v2beta1.yaml",
                "format": "json",
            },
            "Aura v1beta5": {
                "key": "v1beta5",
                "description": "Aura API v1beta5 (GraphQL Data API)",
                "local": "neo4j_aura_sdk/resources/beta/aura_api_spec_v5.yaml",
                "format": "yaml",
            },
        }

        specs = {}
        unmapped_specs = []
        
        for spec in specs_array:
            spec_name = spec.get("name")
            spec_url = spec.get("url")

            if spec_name not in version_mapping:
                unmapped_specs.append({"name": spec_name, "url": spec_url})
                continue

            mapping = version_mapping[spec_name]
            key = mapping["key"]
            specs[key] = {
                "url": _build_spec_url(spec_url),
                "local": mapping["local"],
                "description": mapping["description"],
                "format": mapping["format"],
            }
            if "legacy_local" in mapping:
                specs[key]["legacy_local"] = mapping["legacy_local"]
        
        # Notify about unmapped specs and store them globally
        if unmapped_specs:
            print("⚠️  Warning: Found unmapped API specs in swagger-initializer.js:")
            for unmapped in unmapped_specs:
                print(f"   - {unmapped['name']} ({unmapped['url']})")
            print("   Please add mappings in scripts/specs.py if needed.\n")
            global UNMAPPED_SPECS
            UNMAPPED_SPECS = unmapped_specs

        return specs

    except Exception as e:
        print(f"Warning: Could not fetch specs from swagger-initializer.js: {e}")
        print("Falling back to hardcoded specs.")
        return _get_fallback_specs()


def _get_fallback_specs() -> Dict[str, Dict]:
    """Fallback specs in case swagger-initializer.js is unreachable."""
    return {
        "v1": {
            "url": f"{BASE_SPEC_URL}/aura_api_spec_v1.yaml",
            "local": "neo4j_aura_sdk/resources/aura_api_spec_v1.yaml",
            "description": "Core Aura API v1",
            "format": "yaml",
        },
        "v2beta1": {
            "url": f"{BASE_SPEC_URL}/aura_api_spec_v2beta1.json",
            "local": "neo4j_aura_sdk/resources/v2beta1/spec.json",
            "legacy_local": "neo4j_aura_sdk/resources/aura_api_spec_v2beta1.yaml",
            "description": "Aura API v2beta1 (Fleet Manager)",
            "format": "json",
        },
        "v1beta5": {
            "url": f"{BASE_SPEC_URL}/beta/aura_api_spec_v5.yaml",
            "local": "neo4j_aura_sdk/resources/beta/aura_api_spec_v5.yaml",
            "description": "Aura API v1beta5 (GraphQL Data API)",
            "format": "yaml",
        },
    }


# Track unmapped specs for validation
UNMAPPED_SPECS: list = []

# Fetch specs at module load time
SPECS = fetch_specs_from_swagger()
