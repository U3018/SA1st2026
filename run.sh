#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

PYTHON=${PYTHON:-python3}

exec "$PYTHON" main.py
