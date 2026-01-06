#!/usr/bin/env python3
"""
Validate OpenAPI spec files by comparing downloaded versions with local copies.

This script downloads the latest OpenAPI specification files and compares them
with the versions stored in the repository. It can be run periodically via CI/CD
to detect when the API specifications have been updated.
"""

import hashlib
import sys
from pathlib import Path
from typing import Dict

import httpx
import yaml

from specs import BASE_SPEC_URL, SPECS, UNMAPPED_SPECS


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


def validate_yaml(content: str) -> bool:
    """Validate that content is valid YAML."""
    try:
        yaml.safe_load(content)
        return True
    except yaml.YAMLError as e:
        print(f"Invalid YAML: {e}")
        return False


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
        url = spec_info["url"]

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

                if validate_yaml(local_content):
                    spec_yaml = yaml.safe_load(local_content)
                    version_str = spec_yaml.get("info", {}).get(
                        "version", "unknown"
                    )
                    endpoint_count = len(spec_yaml.get("paths", {}))
                    print(f"   ✅ Local file is valid YAML")
                    print(f"      Version: {version_str}")
                    print(f"      Endpoints: {endpoint_count}")
                    results[version] = {
                        "status": "local_only",
                        "message": "Local file is valid, remote unreachable",
                        "version": version_str,
                        "endpoints": endpoint_count,
                    }
                else:
                    print(f"   ❌ Local file has invalid YAML")
                    results[version] = {
                        "status": "invalid",
                        "message": "Local file has invalid YAML",
                    }
            except Exception as e:
                print(f"   ❌ Error reading local file: {e}")
                results[version] = {
                    "status": "error",
                    "message": str(e),
                }
            continue

        # Validate downloaded content is valid YAML
        if not validate_yaml(downloaded_content):
            print(f"❌ Downloaded spec is not valid YAML")
            results[version] = {
                "status": "invalid_yaml",
                "message": "Downloaded content is not valid YAML",
            }
            continue

        print("OK")

        # Read local file
        with open(local_path, "r") as f:
            local_content = f.read()

        # Calculate hashes
        downloaded_hash = hashlib.sha256(
            downloaded_content.encode()
        ).hexdigest()
        local_hash = hashlib.sha256(local_content.encode()).hexdigest()

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
                local_yaml = yaml.safe_load(local_content)
                downloaded_yaml = yaml.safe_load(downloaded_content)

                local_version = local_yaml.get("info", {}).get(
                    "version", "unknown"
                )
                remote_version = downloaded_yaml.get("info", {}).get(
                    "version", "unknown"
                )

                print(f"    Local version:    {local_version}")
                print(f"    Remote version:   {remote_version}")

                # Compare endpoint counts
                local_paths = len(local_yaml.get("paths", {}))
                remote_paths = len(downloaded_yaml.get("paths", {}))
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
