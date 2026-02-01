#!/bin/bash
# Syncs pyproject.toml dependencies to install/requirements.txt for Raspberry Pi compatibility

# Ensure we are in the project root
cd "$(dirname "$0")/.."

echo "Exporting dependencies from uv lock file to install/requirements.txt..."
uv export --no-hashes --format requirements-txt --output-file install/requirements.txt

echo "Done. install/requirements.txt has been updated."
