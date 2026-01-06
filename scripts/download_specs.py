#!/usr/bin/env python3
"""
Download the latest OpenAPI specification files from Neo4j Aura.

This script downloads the latest specifications and updates local copies.
Use this to update specs when the API changes.
"""

import sys
from pathlib import Path

import httpx
import yaml

from specs import BASE_SPEC_URL, SPECS


def download_spec(url: str) -> str:
    """Download spec from URL."""
    try:
        print(f"  Downloading from {url}...")
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        print(f"  ❌ Failed to download: {e}")
        return None


def validate_yaml(content: str) -> bool:
    """Validate that content is valid YAML."""
    try:
        yaml.safe_load(content)
        return True
    except yaml.YAMLError as e:
        print(f"  ❌ Invalid YAML: {e}")
        return False


def update_specs(force: bool = False) -> int:
    """Download and update spec files."""
    repo_root = Path(__file__).parent.parent
    errors = 0

    for version, spec_info in SPECS.items():
        print(f"\nUpdating {version} specification...")
        print(f"  URL: {spec_info['url']}")

        local_path = repo_root / spec_info["local"]

        # Download latest spec
        downloaded_content = download_spec(spec_info["url"])

        if not downloaded_content:
            print(f"  ⚠️  Skipping {version}")
            errors += 1
            continue

        # Validate downloaded content
        if not validate_yaml(downloaded_content):
            print(f"  ⚠️  Skipping {version}")
            errors += 1
            continue

        # Check if it would change
        if local_path.exists():
            with open(local_path, "r") as f:
                local_content = f.read()

            if local_content == downloaded_content:
                print(f"  ✅ {version} is already up-to-date")
                continue

            if not force:
                print(
                    f"  ⚠️  {version} would change. Use --force to update."
                )
                errors += 1
                continue

        # Create directories if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Write new spec
        try:
            with open(local_path, "w") as f:
                f.write(downloaded_content)
            print(f"  ✅ Updated {version}")

            # Parse and show info
            spec_yaml = yaml.safe_load(downloaded_content)
            version_str = spec_yaml.get("info", {}).get("version", "unknown")
            endpoint_count = len(spec_yaml.get("paths", {}))
            print(f"     Version: {version_str}")
            print(f"     Endpoints: {endpoint_count}")
        except Exception as e:
            print(f"  ❌ Failed to write {local_path}: {e}")
            errors += 1

    return errors


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download and update OpenAPI specification files"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if specs would change",
    )

    args = parser.parse_args()

    print("Neo4j Aura SDK - OpenAPI Specification Downloader")
    print("=" * 60)

    errors = update_specs(force=args.force)

    print(f"\n{'=' * 60}")
    if errors == 0:
        print("✅ All specs downloaded successfully!")
        return 0
    else:
        print(f"⚠️  {errors} spec(s) had issues. Review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
