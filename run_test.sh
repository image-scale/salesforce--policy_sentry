#!/usr/bin/env bash
set -eo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true

rm -rf .pytest_cache

pytest test/ -v --tb=short -p no:cacheprovider

