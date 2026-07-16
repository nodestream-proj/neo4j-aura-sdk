#!/usr/bin/env python3
"""
Validate OpenAPI spec files by comparing downloaded versions with local copies.

This script downloads the latest OpenAPI specification files and compares them
with the versions stored in the repository. It can be run periodically via CI/CD
to detect when the API specifications have been updated.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict

import httpx
import yaml

from specs import SPECS, UNMAPPED_SPECS


def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_spec(url: str) -> str:
    """Download spec from URL."""
    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        print(f"Failed to download {url}: {e}")
        return None


def _resolve_format(spec_info: Dict[str, str]) -> str:
    """Determine format from explicit metadata or file extension."""
    if spec_info.get("format") in {"yaml", "json"}:
        return spec_info["format"]

    local_path = spec_info.get("local", "")
    if local_path.endswith(".json"):
        return "json"
    return "yaml"


def validate_content(content: str, spec_format: str) -> bool:
    """Validate that content is valid YAML or JSON."""
    try:
        if spec_format == "json":
            json.loads(content)
        else:
            yaml.safe_load(content)
        return True
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Invalid {spec_format.upper()}: {e}")
        return False


def parse_spec(content: str, spec_format: str) -> Dict:
    """Parse spec content into a dictionary."""
    if spec_format == "json":
        return json.loads(content)
    return yaml.safe_load(content)


def _canonical_spec_hash(spec_data: Dict) -> str:
    """Create deterministic semantic hash for spec comparison."""
    canonical = json.dumps(
        spec_data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def compare_specs() -> Dict[str, Dict]:
    """Compare downloaded specs with local versions."""
    repo_root = Path(__file__).parent.parent
    results = {}

    for version, spec_info in SPECS.items():
        print(f"\n{'=' * 60}")
        print(f"Validating {version} specification")
        print(f"  {spec_info.get('description', '')}")
        print(f"{'=' * 60}")

        local_path = repo_root / spec_info["local"]
        local_format = _resolve_format(spec_info)
        legacy_local = spec_info.get("legacy_local")
        if not local_path.exists() and legacy_local:
            legacy_path = repo_root / legacy_local
            if legacy_path.exists():
                print(
                    f"Using legacy local file for {version}: {legacy_local}"
                )
                local_path = legacy_path
                local_format = "yaml"

        url = spec_info["url"]
        remote_format = _resolve_format(spec_info)
        parser_name = local_format.upper()

        if not local_path.exists():
            print(f"❌ Local file not found: {local_path}")
            results[version] = {
                "status": "error",
                "message": f"Local file not found: {local_path}",
            }
            continue

        # Download latest spec
        print(f"Remote URL: {url}")
        print(f"Downloading...", end=" ")
        downloaded_content = download_spec(url)

        if not downloaded_content:
            print(
                f"\n⚠️  Remote API unreachable (may require authentication)"
            )
            print(f"   Validating local file structure only...")

            # At least validate the local file is valid YAML
            try:
                with open(local_path, "r") as f:
                    local_content = f.read()

                if validate_content(local_content, local_format):
                    parsed_spec = parse_spec(local_content, local_format)
                    version_str = parsed_spec.get("info", {}).get(
                        "version", "unknown"
                    )
                    endpoint_count = len(parsed_spec.get("paths", {}))
                    print(f"   ✅ Local file is valid {parser_name}")
                    print(f"      Version: {version_str}")
                    print(f"      Endpoints: {endpoint_count}")
                    results[version] = {
                        "status": "local_only",
                        "message": f"Local file is valid {parser_name}, remote unreachable",
                        "version": version_str,
                        "endpoints": endpoint_count,
                    }
                else:
                    print(f"   ❌ Local file has invalid {parser_name}")
                    results[version] = {
                        "status": "invalid",
                        "message": f"Local file has invalid {parser_name}",
                    }
            except Exception as e:
                print(f"   ❌ Error reading local file: {e}")
                results[version] = {
                    "status": "error",
                    "message": str(e),
                }
            continue

        # Validate downloaded content against expected spec format
        if not validate_content(downloaded_content, remote_format):
            print(f"❌ Downloaded spec is not valid {remote_format.upper()}")
            results[version] = {
                "status": "invalid_content",
                "message": f"Downloaded content is not valid {remote_format.upper()}",
            }
            continue

        print("OK")

        # Read local file
        with open(local_path, "r") as f:
            local_content = f.read()

        # Calculate hashes. If formats differ, compare semantic hashes.
        if local_format == remote_format:
            downloaded_hash = hashlib.sha256(
                downloaded_content.encode()
            ).hexdigest()
            local_hash = hashlib.sha256(local_content.encode()).hexdigest()
        else:
            local_spec = parse_spec(local_content, local_format)
            downloaded_spec = parse_spec(downloaded_content, remote_format)
            local_hash = _canonical_spec_hash(local_spec)
            downloaded_hash = _canonical_spec_hash(downloaded_spec)
            print(
                f"Comparing semantically across formats ({local_format.upper()} -> {remote_format.upper()})"
            )

        print(f"Local hash:      {local_hash[:16]}...")
        print(f"Remote hash:     {downloaded_hash[:16]}...")

        if downloaded_hash == local_hash:
            print(f"✅ {version} spec is up-to-date")
            results[version] = {
                "status": "ok",
                "message": "Spec is up-to-date",
                "local_hash": local_hash,
            }
        else:
            print(f"⚠️  {version} spec has changed!")
            print(f"    Update available at: {url}")

            # Show version comparison
            try:
                local_spec = parse_spec(local_content, local_format)
                downloaded_spec = parse_spec(downloaded_content, remote_format)

                local_version = local_spec.get("info", {}).get(
                    "version", "unknown"
                )
                remote_version = downloaded_spec.get("info", {}).get(
                    "version", "unknown"
                )

                print(f"    Local version:    {local_version}")
                print(f"    Remote version:   {remote_version}")

                # Compare endpoint counts
                local_paths = len(local_spec.get("paths", {}))
                remote_paths = len(downloaded_spec.get("paths", {}))
                print(f"    Local endpoints:  {local_paths}")
                print(f"    Remote endpoints: {remote_paths}")
            except Exception as e:
                print(f"    Could not parse versions: {e}")

            results[version] = {
                "status": "outdated",
                "message": "Spec has been updated",
                "local_hash": local_hash,
                "remote_hash": downloaded_hash,
            }

    return results


def main():
    """Main entry point."""
    print("Neo4j Aura SDK - OpenAPI Specification Validator")
    print("=" * 60)

    results = compare_specs()

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    all_ok = True
    
    # Check for unmapped specs
    if UNMAPPED_SPECS:
        print(f"❌ Configuration error - unmapped specs found:")
        for unmapped in UNMAPPED_SPECS:
            print(f"   - {unmapped['name']} ({unmapped['url']})")
        print("   Please update version_mapping in scripts/specs.py\n")
        all_ok = False
    
    for version, result in results.items():
        status = result["status"]
        message = result["message"]

        if status == "ok":
            print(f"✅ {version:10} - {message}")
        elif status == "local_only":
            print(f"ℹ️  {version:10} - {message}")
        elif status == "outdated":
            print(f"⚠️  {version:10} - {message}")
            all_ok = False
        else:
            print(f"❌ {version:10} - {message}")
            all_ok = False

    if all_ok:
        print(f"\n✅ All specs are up-to-date or valid!")
        return 0
    else:
        print(
            f"\n⚠️  Some specs need attention. Review the details above."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
